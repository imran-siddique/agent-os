"""
Policy Engine - Governance and compliance rules for agent execution

The Policy Engine enforces rules and constraints on agent behavior,
including resource quotas, access controls, and risk management.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from .agent_kernel import ExecutionRequest, ActionType, PolicyRule
import uuid
import os
import re


@dataclass
class ResourceQuota:
    """Resource quota for an agent or tenant"""
    agent_id: str
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_execution_time_seconds: float = 300.0
    max_concurrent_executions: int = 5
    allowed_action_types: List[ActionType] = field(default_factory=list)
    
    # Usage tracking
    requests_this_minute: int = 0
    requests_this_hour: int = 0
    current_executions: int = 0
    last_reset_minute: datetime = field(default_factory=datetime.now)
    last_reset_hour: datetime = field(default_factory=datetime.now)


@dataclass
class RiskPolicy:
    """Risk-based policy for agent actions"""
    max_risk_score: float = 0.5
    require_approval_above: float = 0.7
    deny_above: float = 0.9
    
    # Risk factors
    high_risk_patterns: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)


class PolicyEngine:
    """
    Policy Engine - Enforces governance rules for agent execution
    
    Provides:
    - Rate limiting and quotas
    - Risk assessment
    - Access control policies
    - Compliance rules
    """
    
    def __init__(self):
        self.quotas: Dict[str, ResourceQuota] = {}
        self.risk_policies: Dict[str, RiskPolicy] = {}
        self.custom_rules: List[PolicyRule] = []
        self.blocked_patterns: List[str] = []
        
        # Graph-based allow-list approach (Scale by Subtraction)
        # By default, EVERYTHING is blocked unless explicitly allowed
        self.allowed_transitions: set = set()
        self.state_permissions: Dict[str, set] = {}
        
        # Configurable dangerous patterns for code/command execution
        # Uses regex patterns for better detection
        self.dangerous_code_patterns: List[re.Pattern] = [
            re.compile(r'\brm\s+-rf\b', re.IGNORECASE),
            re.compile(r'\bdel\s+/f\b', re.IGNORECASE),
            re.compile(r'\bformat\s+', re.IGNORECASE),
            re.compile(r'\bdrop\s+table\b', re.IGNORECASE),
            re.compile(r'\bdrop\s+database\b', re.IGNORECASE),
            re.compile(r'\btruncate\s+table\b', re.IGNORECASE),
            re.compile(r'\bdelete\s+from\b', re.IGNORECASE),
        ]
        
        # Configurable system paths to protect
        self.protected_paths: List[str] = ['/etc/', '/sys/', '/proc/', '/dev/', 'C:\\Windows\\System32']
        
    def set_quota(self, agent_id: str, quota: ResourceQuota):
        """Set resource quota for an agent"""
        self.quotas[agent_id] = quota
    
    def set_risk_policy(self, policy_id: str, policy: RiskPolicy):
        """Set a risk policy"""
        self.risk_policies[policy_id] = policy
    
    def add_custom_rule(self, rule: PolicyRule):
        """Add a custom policy rule"""
        self.custom_rules.append(rule)
        self.custom_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def add_constraint(self, role: str, allowed_tools: List[str]):
        """
        Define the 'Physics' of the agent using allow-list approach.
        
        This implements "Scale by Subtraction" - by defining what IS allowed,
        everything else is implicitly blocked.
        
        Args:
            role: The agent role/ID
            allowed_tools: List of tool names this role can use
        """
        self.state_permissions[role] = set(allowed_tools)
    
    def check_violation(self, agent_role: str, tool_name: str, args: Dict[str, Any]) -> Optional[str]:
        """
        Check if an action violates the constraint graph.
        
        Uses a two-level check:
        1. Role-Based Check: Is this tool allowed for this role?
        2. Argument-Based Check: Are the arguments safe?
        
        Returns:
            None if no violation, or a string describing the violation
        """
        # 1. Role-Based Check (Allow-list approach)
        allowed = self.state_permissions.get(agent_role, set())
        if tool_name not in allowed:
            return f"Role {agent_role} cannot use tool {tool_name}"

        # 2. Argument-Based Check
        
        # 2a. Path validation with normalization to prevent traversal attacks
        if tool_name in ["write_file", "read_file", "delete_file"] and "path" in args:
            path = args.get("path", "")
            
            # Normalize path to resolve '..' and symbolic links
            try:
                normalized_path = os.path.normpath(os.path.abspath(path))
            except (ValueError, OSError):
                return "Path Validation Error: Invalid path format"
            
            # Check against protected paths
            for protected in self.protected_paths:
                if normalized_path.startswith(os.path.normpath(protected)):
                    return f"Path Violation: Cannot access protected directory {protected}"
        
        # 2b. Code execution validation using regex patterns
        if tool_name in ["execute_code", "run_command"]:
            code_or_cmd = args.get("code", args.get("command", ""))
            
            # Check against dangerous patterns using regex
            for pattern in self.dangerous_code_patterns:
                if pattern.search(code_or_cmd):
                    return f"Dangerous pattern detected: {pattern.pattern}"
            
        return None
    
    def check_rate_limit(self, request: ExecutionRequest) -> bool:
        """Check if request is within rate limits"""
        agent_id = request.agent_context.agent_id
        
        if agent_id not in self.quotas:
            # No quota set, allow by default (or could deny by default)
            return True
        
        quota = self.quotas[agent_id]
        now = datetime.now()
        
        # Reset counters if needed
        if (now - quota.last_reset_minute).total_seconds() >= 60:
            quota.requests_this_minute = 0
            quota.last_reset_minute = now
        
        if (now - quota.last_reset_hour).total_seconds() >= 3600:
            quota.requests_this_hour = 0
            quota.last_reset_hour = now
        
        # Check limits
        if quota.requests_this_minute >= quota.max_requests_per_minute:
            return False
        
        if quota.requests_this_hour >= quota.max_requests_per_hour:
            return False
        
        if quota.current_executions >= quota.max_concurrent_executions:
            return False
        
        # Check action type allowed
        if quota.allowed_action_types and request.action_type not in quota.allowed_action_types:
            return False
        
        # Update counters
        quota.requests_this_minute += 1
        quota.requests_this_hour += 1
        
        return True
    
    def validate_risk(self, request: ExecutionRequest, risk_score: float) -> bool:
        """Validate request against risk policies"""
        # Check against all risk policies
        for policy_id, policy in self.risk_policies.items():
            # Check if risk score exceeds limits
            if risk_score >= policy.deny_above:
                return False
            
            # Check parameters for high-risk patterns
            params_str = str(request.parameters)
            for pattern in policy.high_risk_patterns:
                if pattern.lower() in params_str.lower():
                    return False
            
            # Check domain restrictions if applicable
            if 'url' in request.parameters or 'domain' in request.parameters:
                url = request.parameters.get('url', request.parameters.get('domain', ''))
                
                # Check blocked domains
                for blocked in policy.blocked_domains:
                    if blocked in url:
                        return False
                
                # Check allowed domains (if list is not empty, only allow listed domains)
                if policy.allowed_domains:
                    allowed = False
                    for allowed_domain in policy.allowed_domains:
                        if allowed_domain in url:
                            allowed = True
                            break
                    if not allowed:
                        return False
        
        return True
    
    def validate_request(self, request: ExecutionRequest) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive validation of a request
        Returns (is_valid, reason_if_invalid)
        """
        # Check rate limits
        if not self.check_rate_limit(request):
            return False, "rate_limit_exceeded"
        
        # Check custom rules
        for rule in self.custom_rules:
            if request.action_type in rule.action_types:
                if not rule.validator(request):
                    return False, f"policy_violation: {rule.name}"
        
        return True, None
    
    def get_quota_status(self, agent_id: str) -> Dict[str, Any]:
        """Get current quota usage for an agent"""
        if agent_id not in self.quotas:
            return {"error": "No quota set for agent"}
        
        quota = self.quotas[agent_id]
        return {
            "agent_id": agent_id,
            "requests_this_minute": quota.requests_this_minute,
            "max_requests_per_minute": quota.max_requests_per_minute,
            "requests_this_hour": quota.requests_this_hour,
            "max_requests_per_hour": quota.max_requests_per_hour,
            "current_executions": quota.current_executions,
            "max_concurrent_executions": quota.max_concurrent_executions,
        }


def create_default_policies() -> List[PolicyRule]:
    """Create a set of default security policies"""
    
    def no_system_file_access(request: ExecutionRequest) -> bool:
        """Prevent access to system files"""
        if request.action_type in [ActionType.FILE_READ, ActionType.FILE_WRITE]:
            path = request.parameters.get('path', '')
            dangerous_paths = ['/etc/', '/sys/', '/proc/', '/dev/', 'C:\\Windows\\System32']
            return not any(dp in path for dp in dangerous_paths)
        return True
    
    def no_credential_exposure(request: ExecutionRequest) -> bool:
        """Prevent exposure of credentials"""
        params_str = str(request.parameters).lower()
        sensitive_keywords = ['password', 'secret', 'api_key', 'token', 'credential']
        # This is a simple check; real implementation would be more sophisticated
        return not any(keyword in params_str for keyword in sensitive_keywords)
    
    def no_destructive_sql(request: ExecutionRequest) -> bool:
        """Prevent destructive SQL operations"""
        if request.action_type == ActionType.DATABASE_QUERY:
            query = request.parameters.get('query', '').upper()
            destructive_ops = ['DROP', 'TRUNCATE', 'DELETE FROM', 'ALTER']
            return not any(op in query for op in destructive_ops)
        return True
    
    return [
        PolicyRule(
            rule_id=str(uuid.uuid4()),
            name="no_system_file_access",
            description="Prevent access to system files",
            action_types=[ActionType.FILE_READ, ActionType.FILE_WRITE],
            validator=no_system_file_access,
            priority=10
        ),
        PolicyRule(
            rule_id=str(uuid.uuid4()),
            name="no_credential_exposure",
            description="Prevent exposure of credentials",
            action_types=[ActionType.CODE_EXECUTION, ActionType.FILE_READ, ActionType.API_CALL],
            validator=no_credential_exposure,
            priority=10
        ),
        PolicyRule(
            rule_id=str(uuid.uuid4()),
            name="no_destructive_sql",
            description="Prevent destructive SQL operations",
            action_types=[ActionType.DATABASE_QUERY, ActionType.DATABASE_WRITE],
            validator=no_destructive_sql,
            priority=9
        ),
    ]
