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
        Perform cross-model verification.
        
        In production, this calls multiple LLM APIs and compares responses.
        Here we provide the interface for integration.
        """
        # Hash for deterministic demo results
        claim_hash = int(hashlib.md5(claim.encode()).hexdigest()[:8], 16)
        
        # Simulated multi-model response
        models_checked = ["gpt-4-turbo", "claude-3-sonnet", "gemini-pro"]
        agreement_score = 0.7 + (claim_hash % 30) / 100  # 0.70-0.99
        
        verified = agreement_score >= threshold
        
        return {
            "verified": verified,
            "confidence": round(agreement_score, 3),
            "agreement_score": round(agreement_score, 3),
            "models_checked": models_checked,
            "divergences": [] if verified else [
                {
                    "model": "gemini-pro",
                    "disagreement": "Partial disagreement on technical details",
                    "severity": "low"
                }
            ],
            "claim_hash": claim_hash
        }


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
