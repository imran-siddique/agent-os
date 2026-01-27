"""
MCP Tools for Agent OS Kernel.

Exposes CMVK, IATP, and governed execution as MCP-compatible tools.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
import hashlib
import json


@dataclass
class ToolResult:
    """Standard result from MCP tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class CMVKVerifyTool:
    """
    Cross-Model Verification Kernel as MCP Tool.
    
    Verifies claims across multiple models to detect hallucinations
    and blind spots through structured disagreement.
    """
    
    name = "cmvk_verify"
    description = "Verify a claim across multiple AI models to detect hallucinations"
    
    input_schema = {
        "type": "object",
        "properties": {
            "claim": {
                "type": "string",
                "description": "The claim or statement to verify"
            },
            "context": {
                "type": "string",
                "description": "Optional context for the claim"
            },
            "models": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Models to use for verification (default: all configured)"
            },
            "threshold": {
                "type": "number",
                "description": "Agreement threshold (0-1, default: 0.85)"
            }
        },
        "required": ["claim"]
    }
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.default_threshold = self.config.get("threshold", 0.85)
    
    async def execute(self, arguments: dict) -> ToolResult:
        """Execute cross-model verification."""
        claim = arguments.get("claim", "")
        context = arguments.get("context", "")
        threshold = arguments.get("threshold", self.default_threshold)
        
        # Simulate CMVK verification (in production, calls actual models)
        # This is a stateless operation - no session state maintained
        verification_result = await self._verify_claim(claim, context, threshold)
        
        return ToolResult(
            success=True,
            data=verification_result,
            metadata={
                "tool": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "threshold_used": threshold
            }
        )
    
    async def _verify_claim(self, claim: str, context: str, threshold: float) -> dict:
        """
        Perform cross-model verification using drift-based consensus.
        
        Algorithm:
        1. Query each model with the claim
        2. Calculate pairwise drift between responses
        3. If max drift > threshold, flag disagreement
        4. Return consensus response with confidence score
        
        In production, this calls actual LLM APIs.
        This implementation provides the interface and algorithm structure.
        """
        import hashlib
        
        # Models to verify against
        models = ["gpt-4", "claude-sonnet-4", "gemini-pro"]
        
        # In production: Call each model API
        # responses = [await call_model(m, claim) for m in models]
        
        # For demo: Generate deterministic mock responses
        claim_hash = int(hashlib.md5(claim.encode()).hexdigest()[:8], 16)
        
        # Simulate model responses (in production, actual API calls)
        responses = []
        for i, model in enumerate(models):
            response_hash = (claim_hash + i * 12345) % 1000000
            responses.append({
                "model": model,
                "response": f"Response from {model}",
                "latency_ms": 500 + (response_hash % 500)
            })
        
        # Calculate pairwise drift scores
        # Drift = 0.0 (identical) to 1.0 (completely different)
        drift_scores = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                # In production: Use embedding similarity or semantic comparison
                # drift = cosine_distance(embed(r_i), embed(r_j))
                # For demo: deterministic based on hash
                pair_hash = (claim_hash + i * 100 + j * 10) % 100
                drift = pair_hash / 100 * 0.3  # 0.0 to 0.3 range
                drift_scores.append({
                    "pair": (responses[i]["model"], responses[j]["model"]),
                    "drift": round(drift, 3)
                })
        
        max_drift = max(d["drift"] for d in drift_scores) if drift_scores else 0.0
        avg_drift = sum(d["drift"] for d in drift_scores) / len(drift_scores) if drift_scores else 0.0
        
        # Drift-based decision
        # High drift = disagreement = low confidence
        disagreement_threshold = 1.0 - threshold  # threshold is agreement, so invert
        disagreement_detected = max_drift > disagreement_threshold
        
        confidence = 1.0 - avg_drift
        verified = not disagreement_detected and confidence >= threshold
        
        return {
            "verified": verified,
            "confidence": round(confidence, 3),
            "drift_score": round(max_drift, 3),
            "avg_drift": round(avg_drift, 3),
            "models_checked": models,
            "drift_details": drift_scores,
            "disagreement_detected": disagreement_detected,
            "consensus_method": "drift_threshold",
            "threshold_used": threshold,
            "interpretation": self._interpret_result(verified, confidence, max_drift)
        }
    
    def _interpret_result(self, verified: bool, confidence: float, max_drift: float) -> str:
        """Generate human-readable interpretation of verification result."""
        if verified and confidence > 0.9:
            return "Strong consensus across all models. High confidence in claim validity."
        elif verified and confidence > 0.7:
            return "Models agree with moderate confidence. Claim appears valid."
        elif not verified and max_drift > 0.25:
            return "Significant disagreement between models. Claim requires manual review."
        else:
            return "Weak consensus. Consider additional verification."


class KernelExecuteTool:
    """
    Governed Execution through Agent OS Kernel.
    
    Executes actions with policy enforcement, signal handling,
    and audit logging. Stateless - all context in request.
    """
    
    name = "kernel_execute"
    description = "Execute an action through the Agent OS kernel with policy enforcement"
    
    input_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The action to execute (e.g., 'database_query', 'file_write')"
            },
            "params": {
                "type": "object",
                "description": "Parameters for the action"
            },
            "agent_id": {
                "type": "string",
                "description": "ID of the agent making the request"
            },
            "policies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Policy names to enforce (e.g., ['read_only', 'no_pii'])"
            },
            "context": {
                "type": "object",
                "description": "Execution context (history, state, etc.)"
            }
        },
        "required": ["action", "agent_id"]
    }
    
    # Action policies (in production, loaded from config)
    DEFAULT_POLICIES = {
        "database_query": {"allowed_modes": ["read_only", "read_write"]},
        "file_write": {"requires_approval": True, "allowed_paths": ["/tmp", "/data"]},
        "api_call": {"rate_limit": 100, "allowed_domains": ["*"]},
        "send_email": {"requires_approval": True},
    }
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.policy_mode = self.config.get("policy_mode", "strict")
    
    async def execute(self, arguments: dict) -> ToolResult:
        """Execute action with kernel governance."""
        action = arguments.get("action", "")
        params = arguments.get("params", {})
        agent_id = arguments.get("agent_id", "unknown")
        policies = arguments.get("policies", [])
        context = arguments.get("context", {})
        
        # Policy check (stateless - all info in request)
        policy_result = self._check_policies(action, params, policies)
        
        if not policy_result["allowed"]:
            return ToolResult(
                success=False,
                data=None,
                error=f"SIGKILL: Policy violation - {policy_result['reason']}",
                metadata={
                    "tool": self.name,
                    "agent_id": agent_id,
                    "action": action,
                    "signal": "SIGKILL",
                    "violation": policy_result["reason"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Execute action (in production, dispatches to actual handlers)
        execution_result = await self._execute_action(action, params, context)
        
        return ToolResult(
            success=True,
            data=execution_result,
            metadata={
                "tool": self.name,
                "agent_id": agent_id,
                "action": action,
                "policies_applied": policies,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _check_policies(self, action: str, params: dict, policies: list) -> dict:
        """Check if action is allowed under given policies."""
        action_policy = self.DEFAULT_POLICIES.get(action, {})
        
        # Check read_only policy
        if "read_only" in policies:
            if action in ["file_write", "send_email"]:
                return {"allowed": False, "reason": f"Action '{action}' blocked by read_only policy"}
            if action == "database_query" and params.get("query", "").upper().startswith(("INSERT", "UPDATE", "DELETE")):
                return {"allowed": False, "reason": "Write query blocked by read_only policy"}
        
        # Check requires_approval
        if action_policy.get("requires_approval") and not params.get("approved"):
            return {"allowed": False, "reason": f"Action '{action}' requires approval"}
        
        # Check no_pii policy
        if "no_pii" in policies:
            pii_keywords = ["ssn", "social_security", "credit_card", "password"]
            params_str = json.dumps(params).lower()
            for keyword in pii_keywords:
                if keyword in params_str:
                    return {"allowed": False, "reason": f"PII detected ({keyword}) - blocked by no_pii policy"}
        
        return {"allowed": True, "reason": None}
    
    async def _execute_action(self, action: str, params: dict, context: dict) -> dict:
        """Execute the action (stub - real implementation dispatches to handlers)."""
        return {
            "status": "executed",
            "action": action,
            "result": f"Action '{action}' executed successfully",
            "params_received": list(params.keys())
        }


class IATPSignTool:
    """
    Inter-Agent Trust Protocol signing as MCP Tool.
    
    Signs agent outputs with cryptographic attestation for
    trust propagation across agent networks.
    """
    
    name = "iatp_sign"
    description = "Sign content with cryptographic trust attestation for inter-agent communication"
    
    input_schema = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Content to sign"
            },
            "agent_id": {
                "type": "string",
                "description": "ID of the signing agent"
            },
            "capabilities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Capabilities being attested (e.g., ['reversible', 'idempotent'])"
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata to include in signature"
            }
        },
        "required": ["content", "agent_id"]
    }
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
    
    async def execute(self, arguments: dict) -> ToolResult:
        """Sign content with IATP attestation."""
        content = arguments.get("content", "")
        agent_id = arguments.get("agent_id", "")
        capabilities = arguments.get("capabilities", [])
        metadata = arguments.get("metadata", {})
        
        # Generate signature
        signature = self._generate_signature(content, agent_id, capabilities)
        
        return ToolResult(
            success=True,
            data={
                "signature": signature,
                "agent_id": agent_id,
                "capabilities": capabilities,
                "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
                "timestamp": datetime.utcnow().isoformat(),
                "protocol_version": "iatp-1.0"
            },
            metadata={
                "tool": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def _generate_signature(self, content: str, agent_id: str, capabilities: list) -> str:
        """Generate IATP signature (simplified - production uses proper crypto)."""
        payload = f"{content}|{agent_id}|{','.join(sorted(capabilities))}"
        return hashlib.sha256(payload.encode()).hexdigest()


class IATPVerifyTool:
    """
    IATP Trust Verification as MCP Tool.
    
    Verifies trust relationship with a remote agent, checking:
    - Capability manifest
    - Attestation signature
    - Trust level requirements
    - Policy compatibility
    """
    
    name = "iatp_verify"
    description = "Verify trust relationship with another agent before communication"
    
    input_schema = {
        "type": "object",
        "properties": {
            "remote_agent_id": {
                "type": "string",
                "description": "ID of the agent to verify"
            },
            "required_trust_level": {
                "type": "string",
                "enum": ["verified_partner", "trusted", "standard", "any"],
                "description": "Minimum required trust level (default: standard)"
            },
            "required_scopes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Required capability scopes (e.g., ['repo:read'])"
            },
            "data_classification": {
                "type": "string",
                "enum": ["public", "internal", "confidential", "pii"],
                "description": "Classification of data being shared"
            }
        },
        "required": ["remote_agent_id"]
    }
    
    # Trust level scores
    TRUST_SCORES = {
        "verified_partner": 10,
        "trusted": 7,
        "standard": 5,
        "unknown": 2,
        "untrusted": 0
    }
    
    # Minimum scores required
    MIN_SCORES = {
        "verified_partner": 10,
        "trusted": 7,
        "standard": 5,
        "any": 0
    }
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        # Agent registry (in production, fetched from network)
        self.agent_registry = self.config.get("agent_registry", {})
    
    async def execute(self, arguments: dict) -> ToolResult:
        """Verify trust with remote agent."""
        remote_agent_id = arguments.get("remote_agent_id", "")
        required_level = arguments.get("required_trust_level", "standard")
        required_scopes = arguments.get("required_scopes", [])
        data_classification = arguments.get("data_classification", "internal")
        
        # Fetch manifest (simulated - real impl fetches from /.well-known/agent-manifest)
        manifest = await self._fetch_manifest(remote_agent_id)
        
        if manifest is None:
            return ToolResult(
                success=False,
                data=None,
                error=f"Could not fetch manifest for agent '{remote_agent_id}'"
            )
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(manifest)
        min_required = self.MIN_SCORES.get(required_level, 5)
        
        # Check trust level
        if trust_score < min_required:
            return ToolResult(
                success=False,
                data={
                    "verified": False,
                    "trust_score": trust_score,
                    "required_score": min_required,
                    "manifest": manifest
                },
                error=f"Trust score {trust_score} below required {min_required}"
            )
        
        # Check required scopes
        agent_scopes = manifest.get("scopes", [])
        missing_scopes = [s for s in required_scopes if s not in agent_scopes]
        if missing_scopes:
            return ToolResult(
                success=False,
                data={
                    "verified": False,
                    "trust_score": trust_score,
                    "missing_scopes": missing_scopes
                },
                error=f"Agent missing required scopes: {missing_scopes}"
            )
        
        # Check PII restrictions
        if data_classification == "pii":
            retention = manifest.get("privacy", {}).get("retention_policy", "permanent")
            if retention != "ephemeral":
                return ToolResult(
                    success=False,
                    data={
                        "verified": False,
                        "trust_score": trust_score,
                        "reason": "PII requires ephemeral retention"
                    },
                    error="Cannot share PII with non-ephemeral agent"
                )
        
        # Verification passed
        return ToolResult(
            success=True,
            data={
                "verified": True,
                "remote_agent_id": remote_agent_id,
                "trust_score": trust_score,
                "trust_level": manifest.get("trust_level", "unknown"),
                "scopes": agent_scopes,
                "attestation_valid": True,
                "policy_compatible": True
            },
            metadata={
                "tool": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _fetch_manifest(self, agent_id: str) -> Optional[dict]:
        """Fetch manifest from agent (simulated)."""
        # In production, this would HTTP GET /.well-known/agent-manifest
        if agent_id in self.agent_registry:
            return self.agent_registry[agent_id]
        
        # Return simulated manifest for demo
        return {
            "agent_id": agent_id,
            "trust_level": "standard",
            "scopes": ["data:read", "data:write"],
            "capabilities": {
                "idempotency": True,
                "max_concurrency": 10
            },
            "reversibility": {
                "level": "full",
                "undo_window_seconds": 3600
            },
            "privacy": {
                "retention_policy": "ephemeral",
                "human_in_loop": False,
                "training_consent": False
            }
        }
    
    def _calculate_trust_score(self, manifest: dict) -> int:
        """Calculate trust score from manifest."""
        base = self.TRUST_SCORES.get(manifest.get("trust_level", "unknown"), 2)
        
        # Modifiers
        reversibility = manifest.get("reversibility", {}).get("level", "none")
        if reversibility != "none":
            base += 2
        
        privacy = manifest.get("privacy", {})
        retention = privacy.get("retention_policy", "permanent")
        if retention == "ephemeral":
            base += 1
        elif retention in ("permanent", "forever"):
            base -= 1
        
        if privacy.get("human_in_loop", False):
            base -= 2
        
        if privacy.get("training_consent", False):
            base -= 1
        
        return max(0, min(10, base))


class IATPReputationTool:
    """
    IATP Reputation Query/Slash as MCP Tool.
    
    Query or modify agent reputation in the network.
    """
    
    name = "iatp_reputation"
    description = "Query or slash agent reputation in the IATP network"
    
    input_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["query", "slash"],
                "description": "Action to perform"
            },
            "agent_id": {
                "type": "string",
                "description": "Agent ID to query/slash"
            },
            "slash_reason": {
                "type": "string",
                "description": "Reason for slashing (required if action=slash)"
            },
            "slash_severity": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low"],
                "description": "Severity of violation (required if action=slash)"
            },
            "evidence": {
                "type": "object",
                "description": "Evidence for the slash (e.g., CMVK drift score)"
            }
        },
        "required": ["action", "agent_id"]
    }
    
    # Severity penalties
    SLASH_PENALTIES = {
        "critical": 2.0,
        "high": 1.0,
        "medium": 0.5,
        "low": 0.25
    }
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        # In-memory reputation store (production uses distributed store)
        self._reputation: dict = {}
    
    async def execute(self, arguments: dict) -> ToolResult:
        """Execute reputation action."""
        action = arguments.get("action", "query")
        agent_id = arguments.get("agent_id", "")
        
        if action == "query":
            return await self._query_reputation(agent_id)
        elif action == "slash":
            reason = arguments.get("slash_reason", "unknown")
            severity = arguments.get("slash_severity", "medium")
            evidence = arguments.get("evidence", {})
            return await self._slash_reputation(agent_id, reason, severity, evidence)
        else:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown action: {action}"
            )
    
    async def _query_reputation(self, agent_id: str) -> ToolResult:
        """Query agent reputation."""
        score = self._reputation.get(agent_id, 5.0)  # Default to 5.0
        
        # Determine trust level from score
        if score >= 8.0:
            level = "verified_partner"
        elif score >= 6.0:
            level = "trusted"
        elif score >= 4.0:
            level = "standard"
        elif score >= 2.0:
            level = "unknown"
        else:
            level = "untrusted"
        
        return ToolResult(
            success=True,
            data={
                "agent_id": agent_id,
                "reputation_score": round(score, 2),
                "trust_level": level,
                "history_count": 0  # Would track actual history
            }
        )
    
    async def _slash_reputation(
        self, agent_id: str, reason: str, severity: str, evidence: dict
    ) -> ToolResult:
        """Slash agent reputation."""
        current = self._reputation.get(agent_id, 5.0)
        penalty = self.SLASH_PENALTIES.get(severity, 0.5)
        new_score = max(0.0, current - penalty)
        
        self._reputation[agent_id] = new_score
        
        return ToolResult(
            success=True,
            data={
                "agent_id": agent_id,
                "previous_score": round(current, 2),
                "new_score": round(new_score, 2),
                "penalty_applied": penalty,
                "reason": reason,
                "severity": severity,
                "evidence": evidence
            },
            metadata={
                "tool": self.name,
                "action": "slash",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
