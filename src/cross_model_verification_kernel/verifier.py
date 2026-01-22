"""
Verifier Module

Implements the Verifier component that performs hostile code review.
The Verifier uses a DIFFERENT model than the Generator to reduce shared blind spots.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from .models import ModelProvider, BaseModelInterface, MockModelInterface


class Severity(Enum):
    """Severity levels for verification issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class VerificationIssue:
    """A single issue found during verification"""
    severity: Severity
    category: str
    description: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class VerifierConfig:
    """Configuration for the Verifier"""
    model: ModelProvider
    temperature: float = 0.2  # Lower temperature for more deterministic verification
    max_tokens: int = 3000
    api_key: Optional[str] = None
    adversarial_mode: bool = True  # Enable hostile code review by default


@dataclass
class VerificationReport:
    """Complete verification report"""
    passed: bool
    issues: List[VerificationIssue]
    summary: str
    model_used: str
    code_reviewed: str
    metadata: Optional[Dict[str, Any]] = None


class Verifier:
    """
    Verifier component that performs hostile code review.
    
    This component intentionally uses a DIFFERENT model than the Generator
    to create an adversarial relationship that reduces shared blind spots.
    """
    
    def __init__(self, config: VerifierConfig, model_interface: Optional[BaseModelInterface] = None):
        """
        Initialize the Verifier
        
        Args:
            config: Verifier configuration
            model_interface: Optional custom model interface (uses mock if not provided)
        """
        self.config = config
        self.model_interface = model_interface or MockModelInterface(
            model=config.model,
            api_key=config.api_key
        )
        self.verification_count = 0
    
    def verify_code(
        self,
        code: str,
        description: str,
        language: str = "python",
        **kwargs
    ) -> VerificationReport:
        """
        Verify code with adversarial/hostile code review approach
        
        Args:
            code: The code to verify
            description: What the code is supposed to do
            language: Programming language
            **kwargs: Additional verification parameters
        
        Returns:
            VerificationReport with all found issues
        """
        self.verification_count += 1
        
        # Build adversarial verification prompt
        prompt = self._build_adversarial_prompt(code, description, language)
        
        # Get verification from the model
        response = self.model_interface.generate(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        
        # Parse issues from response
        issues = self._parse_verification_response(response.content)
        
        # Determine if verification passed
        critical_or_high_issues = [
            issue for issue in issues 
            if issue.severity in [Severity.CRITICAL, Severity.HIGH]
        ]
        passed = len(critical_or_high_issues) == 0
        
        return VerificationReport(
            passed=passed,
            issues=issues,
            summary=self._generate_summary(issues, passed),
            model_used=response.model,
            code_reviewed=code,
            metadata={
                "verification_count": self.verification_count,
                "provider": response.provider.value,
                "adversarial_mode": self.config.adversarial_mode,
                "response_metadata": response.metadata
            }
        )
    
    def _build_adversarial_prompt(
        self,
        code: str,
        description: str,
        language: str
    ) -> str:
        """Build adversarial verification prompt"""
        adversarial_instructions = """You are a HOSTILE code reviewer. Your job is to find ALL possible issues, bugs, vulnerabilities, and problems.
Be extremely critical and thorough. Look for:
- Security vulnerabilities
- Logic errors and edge cases
- Performance issues
- Missing error handling
- Type safety issues
- Resource leaks
- Concurrency problems
- Input validation gaps
- Any possible way the code could fail

DO NOT be cooperative or lenient. Find every flaw.""" if self.config.adversarial_mode else ""
        
        return f"""{adversarial_instructions}

Review the following {language} code:

Task Description: {description}

Code:
```{language}
{code}
```

Provide a detailed security and quality review. For each issue found, specify:
- SEVERITY: (CRITICAL/HIGH/MEDIUM/LOW/INFO)
- CATEGORY: (e.g., security, performance, logic, error-handling)
- DESCRIPTION: What is wrong
- SUGGESTION: How to fix it (if applicable)

List ALL issues found:"""
    
    def _parse_verification_response(self, response: str) -> List[VerificationIssue]:
        """Parse verification response into structured issues"""
        issues = []
        
        # Simple parsing logic - in real implementation, this would be more sophisticated
        lines = response.split('\n')
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_issue:
                    issues.append(self._create_issue_from_dict(current_issue))
                    current_issue = {}
                continue
            
            # Parse different fields
            if line.startswith('SEVERITY:') or line.startswith('1.') or line.startswith('CRITICAL') or line.startswith('HIGH'):
                if current_issue:
                    issues.append(self._create_issue_from_dict(current_issue))
                    current_issue = {}
                
                # Extract severity
                severity_text = line.upper()
                if 'CRITICAL' in severity_text:
                    current_issue['severity'] = Severity.CRITICAL
                elif 'HIGH' in severity_text:
                    current_issue['severity'] = Severity.HIGH
                elif 'MEDIUM' in severity_text:
                    current_issue['severity'] = Severity.MEDIUM
                elif 'LOW' in severity_text:
                    current_issue['severity'] = Severity.LOW
                else:
                    current_issue['severity'] = Severity.INFO
                
                # Start capturing description
                current_issue['description'] = line
            elif line.startswith('CATEGORY:'):
                current_issue['category'] = line.replace('CATEGORY:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                current_issue['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('SUGGESTION:'):
                current_issue['suggestion'] = line.replace('SUGGESTION:', '').strip()
            elif current_issue and 'description' in current_issue:
                # Continue multi-line description
                current_issue['description'] += ' ' + line
        
        # Add last issue if exists
        if current_issue:
            issues.append(self._create_issue_from_dict(current_issue))
        
        return issues
    
    def _create_issue_from_dict(self, issue_dict: Dict[str, Any]) -> VerificationIssue:
        """Create a VerificationIssue from parsed dictionary"""
        return VerificationIssue(
            severity=issue_dict.get('severity', Severity.INFO),
            category=issue_dict.get('category', 'general'),
            description=issue_dict.get('description', 'Issue found'),
            suggestion=issue_dict.get('suggestion')
        )
    
    def _generate_summary(self, issues: List[VerificationIssue], passed: bool) -> str:
        """Generate a summary of the verification"""
        if passed:
            return f"Verification PASSED. Found {len(issues)} minor issues (no critical or high severity)."
        
        critical = sum(1 for i in issues if i.severity == Severity.CRITICAL)
        high = sum(1 for i in issues if i.severity == Severity.HIGH)
        medium = sum(1 for i in issues if i.severity == Severity.MEDIUM)
        low = sum(1 for i in issues if i.severity == Severity.LOW)
        
        return (f"Verification FAILED. Found {len(issues)} total issues: "
                f"{critical} critical, {high} high, {medium} medium, {low} low severity.")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get verifier statistics"""
        return {
            "model": self.config.model.value,
            "verification_count": self.verification_count,
            "temperature": self.config.temperature,
            "adversarial_mode": self.config.adversarial_mode
        }
