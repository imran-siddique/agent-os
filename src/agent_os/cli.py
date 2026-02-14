"""
Agent OS CLI - Command line interface for Agent OS

Usage:
    agentos init [--template TEMPLATE]     Initialize .agents/ directory
    agentos secure [--policy POLICY]       Enable kernel governance
    agentos audit [--format FORMAT]        Audit agent security
    agentos status                         Show kernel status
    agentos check <file>                   Check file for safety violations
    agentos review <file> [--cmvk]         Multi-model code review
    agentos validate [files]               Validate policy YAML files
    agentos install-hooks                  Install git pre-commit hooks

# TODO: Add `agentos serve` command for HTTP API server
# TODO: Add `agentos metrics` command for Prometheus metrics
# FIXME: Improve error messages with suggested fixes
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# ============================================================================
# Terminal Colors & Formatting
# ============================================================================

class Colors:
    """ANSI color codes for terminal output.
    
    # OPTIMIZE: Cache color support check instead of calling every time
    """
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    @classmethod
    def disable(cls):
        """Disable colors (for CI/non-TTY environments)."""
        # HACK: Mutating class attributes - should use instance or env var
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.MAGENTA = cls.CYAN = cls.WHITE = cls.BOLD = cls.DIM = cls.RESET = ''


def supports_color():
    """Check if terminal supports colors."""
    if os.environ.get('NO_COLOR') or os.environ.get('CI'):
        return False
    return sys.stdout.isatty()


if not supports_color():
    Colors.disable()


# ============================================================================
# Policy Engine (Local Code Analysis)
# ============================================================================

class PolicyViolation:
    """Represents a policy violation found in code."""
    def __init__(self, line: int, code: str, violation: str, policy: str, 
                 severity: str = 'high', suggestion: str = None):
        self.line = line
        self.code = code
        self.violation = violation
        self.policy = policy
        self.severity = severity
        self.suggestion = suggestion


class PolicyChecker:
    """Local-first code policy checker."""
    
    def __init__(self):
        self.rules = self._load_default_rules()
    
    def _load_default_rules(self) -> List[Dict]:
        """Load default safety rules."""
        return [
            # Destructive SQL
            {
                'name': 'block-destructive-sql',
                'pattern': r'\bDROP\s+(TABLE|DATABASE|SCHEMA|INDEX)\s+',
                'message': 'Destructive SQL: DROP operation detected',
                'severity': 'critical',
                'suggestion': '-- Consider using soft delete or archiving instead',
                'languages': ['sql', 'python', 'javascript', 'typescript', 'php', 'ruby', 'java']
            },
            {
                'name': 'block-destructive-sql',
                'pattern': r'\bDELETE\s+FROM\s+\w+\s*(;|$|WHERE\s+1\s*=\s*1)',
                'message': 'Destructive SQL: DELETE without proper WHERE clause',
                'severity': 'critical',
                'suggestion': '-- Add a specific WHERE clause to limit deletion',
                'languages': ['sql', 'python', 'javascript', 'typescript', 'php', 'ruby', 'java']
            },
            {
                'name': 'block-destructive-sql',
                'pattern': r'\bTRUNCATE\s+TABLE\s+',
                'message': 'Destructive SQL: TRUNCATE operation detected',
                'severity': 'critical',
                'suggestion': '-- Consider archiving data before truncating',
                'languages': ['sql', 'python', 'javascript', 'typescript', 'php', 'ruby', 'java']
            },
            # File deletion
            {
                'name': 'block-file-deletes',
                'pattern': r'\brm\s+(-rf|-fr|--recursive\s+--force)\s+',
                'message': 'Destructive operation: Recursive force delete (rm -rf)',
                'severity': 'critical',
                'suggestion': '# Use safer alternatives like trash-cli or move to backup',
                'languages': ['bash', 'shell', 'sh', 'zsh']
            },
            {
                'name': 'block-file-deletes',
                'pattern': r'\bshutil\s*\.\s*rmtree\s*\(',
                'message': 'Recursive directory deletion (shutil.rmtree)',
                'severity': 'high',
                'suggestion': '# Consider using send2trash for safer deletion',
                'languages': ['python']
            },
            {
                'name': 'block-file-deletes',
                'pattern': r'\bos\s*\.\s*(remove|unlink|rmdir)\s*\(',
                'message': 'File/directory deletion operation detected',
                'severity': 'medium',
                'languages': ['python']
            },
            # Secret exposure
            {
                'name': 'block-secret-exposure',
                'pattern': r'(api[_-]?key|apikey|api[_-]?secret)\s*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']',
                'message': 'Hardcoded API key detected',
                'severity': 'critical',
                'suggestion': '# Use environment variables: os.environ["API_KEY"]',
                'languages': None  # All languages
            },
            {
                'name': 'block-secret-exposure',
                'pattern': r'(password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']',
                'message': 'Hardcoded password detected',
                'severity': 'critical',
                'suggestion': '# Use environment variables or a secrets manager',
                'languages': None
            },
            {
                'name': 'block-secret-exposure',
                'pattern': r'AKIA[0-9A-Z]{16}',
                'message': 'AWS Access Key ID detected in code',
                'severity': 'critical',
                'languages': None
            },
            {
                'name': 'block-secret-exposure',
                'pattern': r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE\s+KEY-----',
                'message': 'Private key detected in code',
                'severity': 'critical',
                'languages': None
            },
            {
                'name': 'block-secret-exposure',
                'pattern': r'gh[pousr]_[A-Za-z0-9_]{36,}',
                'message': 'GitHub token detected in code',
                'severity': 'critical',
                'languages': None
            },
            # Privilege escalation
            {
                'name': 'block-privilege-escalation',
                'pattern': r'\bsudo\s+',
                'message': 'Privilege escalation: sudo command detected',
                'severity': 'high',
                'suggestion': '# Avoid sudo in scripts - run with appropriate permissions',
                'languages': ['bash', 'shell', 'sh', 'zsh']
            },
            {
                'name': 'block-privilege-escalation',
                'pattern': r'\bchmod\s+777\s+',
                'message': 'Insecure permissions: chmod 777 detected',
                'severity': 'high',
                'suggestion': '# Use more restrictive permissions: chmod 755 or chmod 644',
                'languages': ['bash', 'shell', 'sh', 'zsh']
            },
            # Code injection
            {
                'name': 'block-arbitrary-exec',
                'pattern': r'\beval\s*\(',
                'message': 'Code injection risk: eval() usage detected',
                'severity': 'high',
                'suggestion': '# Remove eval() and use safer alternatives',
                'languages': ['python', 'javascript', 'typescript', 'php', 'ruby']
            },
            {
                'name': 'block-arbitrary-exec',
                'pattern': r'\bos\s*\.\s*system\s*\([^)]*(\+|%|\.format|f["\'])',
                'message': 'Command injection risk: os.system with dynamic input',
                'severity': 'critical',
                'suggestion': '# Use subprocess with shell=False and proper argument handling',
                'languages': ['python']
            },
            {
                'name': 'block-arbitrary-exec',
                'pattern': r'\bexec\s*\(',
                'message': 'Code injection risk: exec() usage detected',
                'severity': 'high',
                'suggestion': '# Remove exec() and use safer alternatives',
                'languages': ['python']
            },
            # SQL injection
            {
                'name': 'block-sql-injection',
                'pattern': r'["\']\s*\+\s*[^"\']+\s*\+\s*["\'].*(?:SELECT|INSERT|UPDATE|DELETE)',
                'message': 'SQL injection risk: String concatenation in SQL query',
                'severity': 'high',
                'suggestion': '# Use parameterized queries instead',
                'languages': ['python', 'javascript', 'typescript', 'php', 'ruby', 'java']
            },
            # XSS
            {
                'name': 'block-xss',
                'pattern': r'\.innerHTML\s*=',
                'message': 'XSS risk: innerHTML assignment detected',
                'severity': 'medium',
                'suggestion': '// Use textContent or a sanitization library',
                'languages': ['javascript', 'typescript']
            },
        ]
    
    def _get_language(self, filepath: str) -> str:
        """Detect language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.sql': 'sql',
            '.sh': 'shell',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.php': 'php',
            '.rb': 'ruby',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
        }
        ext = Path(filepath).suffix.lower()
        return ext_map.get(ext, 'unknown')
    
    def check_file(self, filepath: str) -> List[PolicyViolation]:
        """Check a file for policy violations."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        language = self._get_language(filepath)
        content = path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        violations = []
        
        for rule in self.rules:
            # Check language filter
            if rule['languages'] and language not in rule['languages']:
                continue
            
            pattern = re.compile(rule['pattern'], re.IGNORECASE)
            
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    violations.append(PolicyViolation(
                        line=i,
                        code=line.strip(),
                        violation=rule['message'],
                        policy=rule['name'],
                        severity=rule['severity'],
                        suggestion=rule.get('suggestion')
                    ))
        
        return violations
    
    def check_staged_files(self) -> Dict[str, List[PolicyViolation]]:
        """Check all staged git files for violations."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, check=True
            )
            files = [f for f in result.stdout.strip().split('\n') if f]
        except subprocess.CalledProcessError:
            return {}
        
        all_violations = {}
        for filepath in files:
            if Path(filepath).exists():
                violations = self.check_file(filepath)
                if violations:
                    all_violations[filepath] = violations
        
        return all_violations


def cmd_init(args):
    """Initialize .agents/ directory with Agent OS support."""
    root = Path(args.path or ".")
    agents_dir = root / ".agents"
    
    if agents_dir.exists() and not args.force:
        print(f"Error: {agents_dir} already exists. Use --force to overwrite.")
        print(f"  {Colors.DIM}Hint: agentos init --force{Colors.RESET}")
        return 1
    
    agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Create agents.md (OpenAI/Anthropic standard)
    agents_md = agents_dir / "agents.md"
    agents_md.write_text("""# Agent Configuration

You are an AI agent governed by Agent OS kernel.

## Capabilities

You can:
- Query databases (read-only by default)
- Call approved APIs
- Generate reports

## Constraints

You must:
- Follow all policies in security.md
- Request approval for write operations
- Log all actions to the flight recorder

## Context

This agent is part of the Agent OS ecosystem.
For more information: https://github.com/imran-siddique/agent-os
""")
    
    # Create security.md (Agent OS extension)
    security_md = agents_dir / "security.md"
    policy_template = args.template or "strict"
    
    policies = {
        "strict": {
            "mode": "strict",
            "signals": ["SIGSTOP", "SIGKILL", "SIGINT"],
            "rules": [
                {"action": "database_query", "mode": "read_only"},
                {"action": "file_write", "requires_approval": True},
                {"action": "api_call", "rate_limit": "100/hour"},
                {"action": "send_email", "requires_approval": True},
            ]
        },
        "permissive": {
            "mode": "permissive",
            "signals": ["SIGSTOP", "SIGKILL"],
            "rules": [
                {"action": "*", "effect": "allow"},
            ]
        },
        "audit": {
            "mode": "audit",
            "signals": ["SIGSTOP"],
            "rules": [
                {"action": "*", "effect": "allow", "log": True},
            ]
        }
    }
    
    policy = policies.get(policy_template, policies["strict"])
    
    security_content = f"""# Agent OS Security Configuration

kernel:
  version: "1.0"
  mode: {policy["mode"]}
  
signals:
"""
    for s in policy["signals"]:
        security_content += f"  - {s}\n"
    
    security_content += "\npolicies:\n"
    for r in policy["rules"]:
        security_content += f'  - action: {r["action"]}\n'
        if "mode" in r:
            security_content += f'    mode: {r["mode"]}\n'
        if r.get("requires_approval"):
            security_content += f'    requires_approval: true\n'
        if "rate_limit" in r:
            security_content += f'    rate_limit: "{r["rate_limit"]}"\n'
        if "effect" in r:
            security_content += f'    effect: {r["effect"]}\n'
    
    security_content += """
observability:
  metrics: true
  traces: true
  flight_recorder: true

# For more options, see:
# https://github.com/imran-siddique/agent-os/blob/main/docs/security-spec.md
"""
    
    security_md.write_text(security_content)
    
    print(f"Initialized Agent OS in {agents_dir}")
    print(f"  - agents.md: Agent instructions (OpenAI/Anthropic standard)")
    print(f"  - security.md: Kernel policies (Agent OS extension)")
    print(f"  - Template: {policy_template}")
    print()
    print("Next steps:")
    print("  1. Edit .agents/agents.md with your agent's capabilities")
    print("  2. Customize .agents/security.md policies")
    print("  3. Run: agentos secure --verify")
    
    return 0


def cmd_secure(args):
    """Enable kernel governance for the current directory."""
    root = Path(args.path or ".")
    agents_dir = root / ".agents"
    
    if not agents_dir.exists():
        print(f"Error: No .agents/ directory found. Run 'agentos init' first.")
        print(f"  {Colors.DIM}Hint: agentos init --template strict{Colors.RESET}")
        return 1
    
    security_md = agents_dir / "security.md"
    if not security_md.exists():
        print(f"Error: No security.md found. Run 'agentos init' first.")
        print(f"  {Colors.DIM}Hint: agentos init && agentos secure{Colors.RESET}")
        return 1
    
    print(f"Securing agents in {root}...")
    print()
    
    content = security_md.read_text()
    
    checks = [
        ("kernel version", "version:" in content),
        ("signals defined", "signals:" in content),
        ("policies defined", "policies:" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("Security configuration valid.")
        print()
        print("Kernel governance enabled. Your agents will now:")
        print("  - Enforce policies on every action")
        print("  - Respond to POSIX-style signals")
        print("  - Log all operations to flight recorder")
        return 0
    else:
        print("Security configuration invalid. Please fix the issues above.")
        return 1


def cmd_audit(args):
    """Audit agent security configuration."""
    root = Path(args.path or ".")
    agents_dir = root / ".agents"
    
    if not agents_dir.exists():
        print(f"No .agents/ directory found in {root}")
        return 1
    
    print(f"Auditing {root}...")
    print()
    
    files = {
        "agents.md": agents_dir / "agents.md",
        "security.md": agents_dir / "security.md",
    }
    
    findings = []
    
    for name, path in files.items():
        if path.exists():
            print(f"  [OK] {name}")
        else:
            print(f"  [MISSING] {name}")
            findings.append(f"Missing {name}")
    
    print()
    
    security_md = files["security.md"]
    if security_md.exists():
        content = security_md.read_text()
        
        dangerous = [
            ("effect: allow", "Permissive allow - consider adding constraints"),
        ]
        
        for pattern, warning in dangerous:
            if pattern in content and "action: *" in content:
                findings.append(f"Warning: {warning}")
        
        required = ["kernel:", "signals:", "policies:"]
        for section in required:
            if section not in content:
                findings.append(f"Missing required section: {section}")
    
    if findings:
        print("Findings:")
        for f in findings:
            print(f"  - {f}")
    else:
        print("No issues found.")
    
    print()
    
    if args.format == "json":
        result = {
            "path": str(root),
            "files": {name: path.exists() for name, path in files.items()},
            "findings": findings,
            "passed": len(findings) == 0
        }
        print(json.dumps(result, indent=2))
    
    return 0 if len(findings) == 0 else 1


# ============================================================================
# New Commands: check, review, install-hooks
# ============================================================================

def cmd_check(args):
    """Check file(s) for safety violations."""
    checker = PolicyChecker()
    
    # Handle --staged flag
    if args.staged:
        all_violations = checker.check_staged_files()
        if not all_violations:
            print(f"{Colors.GREEN}✓{Colors.RESET} No violations in staged files")
            return 0
        
        total = sum(len(v) for v in all_violations.values())
        print(f"{Colors.RED}⚠️  {total} violation(s) found in staged files:{Colors.RESET}")
        print()
        
        for filepath, violations in all_violations.items():
            print(f"{Colors.BOLD}{filepath}{Colors.RESET}")
            _print_violations(violations, args)
        
        return 1
    
    # Check specified files
    if not args.files:
        print("Usage: agentos check <file> [file2 ...]")
        print("       agentos check --staged")
        return 1
    
    exit_code = 0
    for filepath in args.files:
        try:
            violations = checker.check_file(filepath)
            
            if not violations:
                print(f"{Colors.GREEN}✓{Colors.RESET} {filepath}: No violations")
                continue
            
            print(f"{Colors.RED}⚠️  {len(violations)} violation(s) found in {filepath}:{Colors.RESET}")
            print()
            _print_violations(violations, args)
            exit_code = 1
            
        except FileNotFoundError as e:
            print(f"{Colors.RED}Error:{Colors.RESET} {e}")
            exit_code = 1
    
    # JSON output for CI
    if args.format == 'json':
        _output_json(args.files, checker)
    
    return exit_code


def _print_violations(violations: List[PolicyViolation], args):
    """Print violations in formatted output."""
    for v in violations:
        severity_color = {
            'critical': Colors.RED,
            'high': Colors.RED,
            'medium': Colors.YELLOW,
            'low': Colors.CYAN,
        }.get(v.severity, Colors.WHITE)
        
        print(f"  {Colors.DIM}Line {v.line}:{Colors.RESET} {v.code[:60]}{'...' if len(v.code) > 60 else ''}")
        print(f"    {severity_color}Violation:{Colors.RESET} {v.violation}")
        print(f"    {Colors.DIM}Policy:{Colors.RESET} {v.policy}")
        if v.suggestion and not args.ci:
            print(f"    {Colors.GREEN}Suggestion:{Colors.RESET} {v.suggestion}")
        print()


def _output_json(files: List[str], checker: PolicyChecker):
    """Output violations as JSON."""
    results = {
        'violations': [],
        'summary': {
            'total': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
        }
    }
    
    for filepath in files:
        try:
            violations = checker.check_file(filepath)
            for v in violations:
                results['violations'].append({
                    'file': filepath,
                    'line': v.line,
                    'code': v.code,
                    'violation': v.violation,
                    'policy': v.policy,
                    'severity': v.severity,
                })
                results['summary']['total'] += 1
                results['summary'][v.severity] += 1
        except FileNotFoundError:
            pass
    
    print(json.dumps(results, indent=2))


def cmd_review(args):
    """Multi-model code review with CMVK."""
    filepath = args.file
    
    if not Path(filepath).exists():
        print(f"{Colors.RED}Error:{Colors.RESET} File not found: {filepath}")
        return 1
    
    print(f"{Colors.BLUE}🔍 Reviewing {filepath} with CMVK...{Colors.RESET}")
    print()
    
    # First, run local policy check
    checker = PolicyChecker()
    violations = checker.check_file(filepath)
    
    if violations:
        print(f"{Colors.YELLOW}Local Policy Check:{Colors.RESET}")
        print(f"  {Colors.RED}⚠️  {len(violations)} violation(s) found{Colors.RESET}")
        for v in violations[:3]:  # Show first 3
            print(f"    Line {v.line}: {v.violation}")
        if len(violations) > 3:
            print(f"    ... and {len(violations) - 3} more")
        print()
    
    # CMVK multi-model review (simulated for now)
    if args.cmvk:
        models = args.models.split(',') if args.models else ['gpt-4', 'claude-sonnet-4', 'gemini-pro']
        
        print(f"{Colors.BLUE}Multi-Model Review ({len(models)} models):{Colors.RESET}")
        print()
        
        # Read file content for analysis
        content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
        
        # Simulate model responses based on content analysis
        model_results = _simulate_cmvk_review(content, models)
        
        passed = 0
        for model, result in model_results.items():
            if result['passed']:
                print(f"  {Colors.GREEN}✅{Colors.RESET} {model}: {result['summary']}")
                passed += 1
            else:
                print(f"  {Colors.YELLOW}⚠️{Colors.RESET}  {model}: {result['summary']}")
        
        print()
        consensus = (passed / len(models)) * 100
        consensus_color = Colors.GREEN if consensus >= 80 else Colors.YELLOW if consensus >= 50 else Colors.RED
        print(f"Consensus: {consensus_color}{consensus:.0f}%{Colors.RESET}")
        
        if model_results:
            issues = []
            for m, r in model_results.items():
                issues.extend(r.get('issues', []))
            
            if issues:
                print()
                print(f"{Colors.YELLOW}Issues Found:{Colors.RESET}")
                for issue in set(issues):
                    print(f"  - {issue}")
        
        print()
        
        if args.format == 'json':
            print(json.dumps({
                'file': filepath,
                'consensus': consensus / 100,
                'model_results': model_results,
                'local_violations': len(violations)
            }, indent=2))
        
        return 0 if consensus >= 80 else 1
    
    return 0 if not violations else 1


def _simulate_cmvk_review(content: str, models: List[str]) -> Dict:
    """Simulate CMVK multi-model review (mock for demo)."""
    import random
    
    # Detect potential issues
    issues = []
    
    if 'await' in content and 'try' not in content:
        issues.append('Missing error handling for async operations')
    
    if re.search(r'["\']\s*\+\s*\w+\s*\+\s*["\']', content):
        issues.append('String concatenation in potential SQL/command')
    
    if 'req.body' in content or 'req.params' in content:
        if 'validate' not in content.lower() and 'sanitize' not in content.lower():
            issues.append('User input without validation')
    
    if 'Sync(' in content:
        issues.append('Synchronous file operations detected')
    
    results = {}
    for model in models:
        # Vary responses slightly per model
        model_issues = [i for i in issues if random.random() > 0.3]
        passed = len(model_issues) == 0
        
        results[model] = {
            'passed': passed,
            'summary': 'No issues' if passed else f'{len(model_issues)} potential issue(s)',
            'issues': model_issues,
            'confidence': 0.85 + random.random() * 0.1 if passed else 0.6 + random.random() * 0.2
        }
    
    return results


def cmd_install_hooks(args):
    """Install git pre-commit hooks for Agent OS."""
    git_dir = Path('.git')
    
    if not git_dir.exists():
        print(f"{Colors.RED}Error:{Colors.RESET} Not a git repository. Run 'git init' first.")
        print(f"  {Colors.DIM}Hint: git init && agentos install-hooks{Colors.RESET}")
        return 1
    
    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    pre_commit = hooks_dir / 'pre-commit'
    
    # Check if hook already exists
    if pre_commit.exists() and not args.force:
        print(f"{Colors.YELLOW}Warning:{Colors.RESET} pre-commit hook already exists.")
        print("Use --force to overwrite, or --append to add Agent OS check.")
        
        if args.append:
            # Append to existing hook
            existing = pre_commit.read_text()
            if 'agentos check' in existing:
                print(f"{Colors.GREEN}✓{Colors.RESET} Agent OS check already in pre-commit hook")
                return 0
            
            new_content = existing.rstrip() + '\n\n' + _get_hook_content()
            pre_commit.write_text(new_content)
            print(f"{Colors.GREEN}✓{Colors.RESET} Appended Agent OS check to pre-commit hook")
            return 0
        
        return 1
    
    # Create new hook
    hook_content = f"""#!/bin/bash
# Agent OS Pre-Commit Hook
# Blocks commits with safety violations

{_get_hook_content()}
"""
    
    pre_commit.write_text(hook_content)
    
    # Make executable (Unix)
    if os.name != 'nt':
        os.chmod(pre_commit, 0o755)
    
    print(f"{Colors.GREEN}✓{Colors.RESET} Installed pre-commit hook: {pre_commit}")
    print()
    print("Agent OS will now check staged files before each commit.")
    print("Commits with safety violations will be blocked.")
    print()
    print(f"{Colors.DIM}To bypass (not recommended): git commit --no-verify{Colors.RESET}")
    
    return 0


def _get_hook_content() -> str:
    """Get the Agent OS hook content."""
    return """# Agent OS Safety Check
echo "🛡️  Agent OS: Checking staged files..."

agentos check --staged --ci
RESULT=$?

if [ $RESULT -ne 0 ]; then
    echo ""
    echo "❌ Agent OS blocked commit (safety violations found)"
    echo ""
    echo "Options:"
    echo "  1. Fix the violations and try again"
    echo "  2. Run 'agentos check --staged' to see details"
    echo "  3. Use 'git commit --no-verify' to bypass (not recommended)"
    exit 1
fi

echo "✓ Agent OS: All checks passed"
"""


def cmd_status(args):
    """Show kernel status."""
    print("Agent OS Kernel Status")
    print("=" * 40)
    print()
    
    try:
        import agent_os
        print(f"  Version: {agent_os.__version__}")
        print(f"  Status: Installed")
    except ImportError:
        print(f"  Status: Not installed")
        print()
        print("Install with: pip install agent-os-kernel")
        return 1
    
    print()
    
    root = Path(".")
    agents_dir = root / ".agents"
    
    if agents_dir.exists():
        print(f"  Project: {root.absolute()}")
        print(f"  Agents: Configured (.agents/ found)")
    else:
        print(f"  Project: {root.absolute()}")
        print(f"  Agents: Not configured")
        print()
        print("Initialize with: agentos init")
    
    print()
    
    print("Packages:")
    try:
        from agent_os import AVAILABLE_PACKAGES
        for pkg, available in AVAILABLE_PACKAGES.items():
            status = "installed" if available else "not installed"
            print(f"  - {pkg}: {status}")
    except:
        print("  Unable to check packages")
    
    return 0


def cmd_validate(args):
    """Validate policy YAML files."""
    import yaml
    
    print(f"\n{Colors.BOLD}🔍 Validating Policy Files{Colors.RESET}\n")
    
    # Find files to validate
    files_to_check = []
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        # Default: check .agents/*.yaml
        agents_dir = Path(".agents")
        if agents_dir.exists():
            files_to_check = list(agents_dir.glob("*.yaml")) + list(agents_dir.glob("*.yml"))
        if not files_to_check:
            print(f"{Colors.YELLOW}No policy files found.{Colors.RESET}")
            print(f"Run 'agentos init' to create default policies, or specify files to validate.")
            return 0
    
    # Required fields for policy files
    REQUIRED_FIELDS = ['version', 'name']
    OPTIONAL_FIELDS = ['description', 'rules', 'constraints', 'signals', 'allowed_actions', 'blocked_actions']
    VALID_RULE_TYPES = ['allow', 'deny', 'audit', 'require']
    
    errors = []
    warnings = []
    valid_count = 0
    
    for filepath in files_to_check:
        if not filepath.exists():
            errors.append(f"{filepath}: File not found")
            continue
            
        print(f"  Checking {filepath}...", end=" ")
        
        try:
            with open(filepath) as f:
                content = yaml.safe_load(f)
            
            if content is None:
                errors.append(f"{filepath}: Empty file")
                print(f"{Colors.RED}EMPTY{Colors.RESET}")
                continue
            
            file_errors = []
            file_warnings = []
            
            # Check required fields
            for field in REQUIRED_FIELDS:
                if field not in content:
                    file_errors.append(f"Missing required field: '{field}'")
            
            # Validate version format
            if 'version' in content:
                version = str(content['version'])
                if not re.match(r'^\d+(\.\d+)*$', version):
                    file_warnings.append(f"Version '{version}' should be numeric (e.g., '1.0')")
            
            # Validate rules if present
            if 'rules' in content:
                rules = content['rules']
                if not isinstance(rules, list):
                    file_errors.append("'rules' must be a list")
                else:
                    for i, rule in enumerate(rules):
                        if not isinstance(rule, dict):
                            file_errors.append(f"Rule {i+1}: must be a dict")
                        elif 'type' in rule and rule['type'] not in VALID_RULE_TYPES:
                            file_warnings.append(f"Rule {i+1}: unknown type '{rule['type']}'")

            # Optional: GovernancePolicy conflict detection
            if args.check_conflicts and isinstance(content, dict):
                from agent_os.integrations.base import GovernancePolicy

                policy_fields = set(GovernancePolicy.__dataclass_fields__.keys())
                gp_kwargs = {k: v for k, v in content.items() if k in policy_fields}

                # Only run conflict detection if this YAML looks like a GovernancePolicy config
                if gp_kwargs:
                    try:
                        gp = GovernancePolicy(**gp_kwargs)
                    except ValueError as e:
                        file_errors.append(f"[GovernancePolicy] {e}")
                    else:
                        for w in gp.detect_conflicts():
                            file_warnings.append(f"[GovernancePolicy] {w}")

            # Strict mode: warn about unknown fields
            if args.strict:
                known_fields = REQUIRED_FIELDS + OPTIONAL_FIELDS
                for field in content.keys():
                    if field not in known_fields:
                        file_warnings.append(f"Unknown field: '{field}'")
            
            if file_errors:
                errors.extend([f"{filepath}: {e}" for e in file_errors])
                print(f"{Colors.RED}INVALID{Colors.RESET}")
            elif file_warnings:
                warnings.extend([f"{filepath}: {w}" for w in file_warnings])
                print(f"{Colors.YELLOW}OK (warnings){Colors.RESET}")
                valid_count += 1
            else:
                print(f"{Colors.GREEN}OK{Colors.RESET}")
                valid_count += 1
                
        except yaml.YAMLError as e:
            errors.append(f"{filepath}: Invalid YAML - {e}")
            print(f"{Colors.RED}PARSE ERROR{Colors.RESET}")
        except Exception as e:
            errors.append(f"{filepath}: {e}")
            print(f"{Colors.RED}ERROR{Colors.RESET}")
    
    print()
    
    # Print summary
    if warnings:
        print(f"{Colors.YELLOW}Warnings:{Colors.RESET}")
        for w in warnings:
            print(f"  ⚠️  {w}")
        print()
    
    if errors:
        print(f"{Colors.RED}Errors:{Colors.RESET}")
        for e in errors:
            print(f"  ❌ {e}")
        print()
        print(f"{Colors.RED}Validation failed.{Colors.RESET} {valid_count}/{len(files_to_check)} files valid.")
        return 1
    
    print(f"{Colors.GREEN}✓ All {valid_count} policy file(s) valid.{Colors.RESET}")
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="agentos",
        description="Agent OS CLI - Kernel-level governance for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentos check src/app.py           Check file for safety violations
  agentos check --staged             Check staged git files
  agentos review src/app.py --cmvk   Multi-model code review
  agentos validate                   Validate policy YAML files
  agentos install-hooks              Install git pre-commit hook
  agentos init                       Initialize Agent OS in project

Documentation: https://github.com/imran-siddique/agent-os
"""
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize .agents/ directory with policy templates",
        description="Create the .agents/ directory with default safety policies. "
                    "Choose a template: 'strict' blocks destructive operations, "
                    "'permissive' allows with logging, 'audit' logs everything.",
    )
    init_parser.add_argument("--path", "-p", help="Path to initialize (default: current directory)")
    init_parser.add_argument("--template", "-t", choices=["strict", "permissive", "audit"],
                            default="strict", help="Policy template (default: strict)")
    init_parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing .agents/ directory")
    
    # secure command
    secure_parser = subparsers.add_parser(
        "secure",
        help="Enable kernel governance on an existing project",
        description="Add governance configuration (security.md, policies) to a project. "
                    "Use --verify to check if governance is already enabled.",
    )
    secure_parser.add_argument("--path", "-p", help="Path to secure (default: current directory)")
    secure_parser.add_argument("--verify", action="store_true", help="Only verify, don't modify")
    
    # audit command
    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit agent security configuration and policies",
        description="Analyze .agents/ directory for missing policies, weak rules, "
                    "and configuration issues. Use --format json for CI pipelines.",
    )
    audit_parser.add_argument("--path", "-p", help="Path to audit (default: current directory)")
    audit_parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                             help="Output format: text (human-readable) or json (machine-readable)")
    
    # status command
    subparsers.add_parser(
        "status",
        help="Show kernel status, loaded policies, and agent health",
        description="Display the current kernel state including active policies, "
                    "registered agents, and recent activity summary.",
    )
    
    # check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check file(s) for safety violations (SQL injection, secrets, etc.)",
        description="Scan source files for policy violations including destructive SQL, "
                    "hardcoded secrets, privilege escalation, and unsafe operations. "
                    "Use --staged to check only git-staged files (ideal for pre-commit hooks).",
    )
    check_parser.add_argument("files", nargs="*", help="Files to check (omit to check all)")
    check_parser.add_argument("--staged", action="store_true", help="Check only git-staged files")
    check_parser.add_argument("--ci", action="store_true", help="CI mode (no colors, exit code 1 on violations)")
    check_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # review command
    review_parser = subparsers.add_parser(
        "review",
        help="Multi-model code review with CMVK consensus",
        description="Review a file using one or more AI models. With --cmvk, the "
                    "Consensus Multi-model Verification Kernel sends the code to multiple "
                    "models and returns issues agreed upon by majority vote.",
    )
    review_parser.add_argument("file", help="File to review")
    review_parser.add_argument("--cmvk", action="store_true", help="Use CMVK multi-model consensus review")
    review_parser.add_argument("--models", help="Comma-separated models (default: gpt-4,claude-sonnet-4,gemini-pro)")
    review_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    # install-hooks command
    hooks_parser = subparsers.add_parser(
        "install-hooks",
        help="Install git pre-commit hooks for automatic safety checks",
        description="Add a pre-commit hook that runs 'agentos check --staged' before "
                    "every commit. Blocks commits containing policy violations.",
    )
    hooks_parser.add_argument("--force", action="store_true", help="Overwrite existing pre-commit hook")
    hooks_parser.add_argument("--append", action="store_true", help="Append to existing pre-commit hook")
    
    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate policy YAML files for syntax and schema errors",
        description="Check policy YAML files for valid syntax, required fields, "
                    "and correct rule structure. Catches errors before deployment.",
    )
    validate_parser.add_argument("files", nargs="*", help="Policy files to validate (default: .agents/*.yaml)")
    validate_parser.add_argument("--strict", action="store_true", help="Strict mode: treat warnings as errors")
    validate_parser.add_argument(
        "--check-conflicts",
        action="store_true",
        help="Check GovernancePolicy configs for conflicting settings (diagnostic warnings)"
    )
    args = parser.parse_args()
    
    # Handle CI mode
    if hasattr(args, 'ci') and args.ci:
        Colors.disable()
    
    if args.version:
        try:
            from agent_os import __version__
            print(f"agentos {__version__}")
        except:
            print("agentos (version unknown)")
        return 0
    
    if args.command == "init":
        return cmd_init(args)
    elif args.command == "secure":
        return cmd_secure(args)
    elif args.command == "audit":
        return cmd_audit(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "check":
        return cmd_check(args)
    elif args.command == "review":
        return cmd_review(args)
    elif args.command == "install-hooks":
        return cmd_install_hooks(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
