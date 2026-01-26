"""
AGENTS.md Compatibility for Agent OS.

Parses OpenAI/Anthropic standard .agents/ directory structure
and maps to Agent OS kernel policies.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import yaml


@dataclass
class AgentSkill:
    """Parsed agent skill/capability."""
    name: str
    description: str
    allowed: bool = True
    requires_approval: bool = False
    read_only: bool = False
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Parsed agent configuration from AGENTS.md."""
    name: str
    description: str
    skills: List[AgentSkill]
    policies: List[str]
    instructions: str
    security_config: Dict[str, Any] = field(default_factory=dict)


class AgentsParser:
    """
    Parse .agents/ directory structure.
    
    Supports:
    - agents.md (OpenAI/Anthropic standard)
    - security.md (Agent OS extension)
    - YAML front matter
    
    Usage:
        parser = AgentsParser()
        config = parser.parse_directory("./my-project/.agents")
        
        # Convert to kernel policies
        policies = parser.to_kernel_policies(config)
    """
    
    def __init__(self):
        self.skill_patterns = [
            r"^[-*]\s+(.+)$",  # - skill or * skill
            r"^(\d+)\.\s+(.+)$",  # 1. skill
        ]
    
    def parse_directory(self, path: str) -> AgentConfig:
        """Parse .agents/ directory."""
        agents_dir = Path(path)
        
        if not agents_dir.exists():
            raise FileNotFoundError(f"Agents directory not found: {path}")
        
        # Parse main agents.md
        agents_md = agents_dir / "agents.md"
        if not agents_md.exists():
            agents_md = agents_dir / "AGENTS.md"
        
        config = self._parse_agents_md(agents_md) if agents_md.exists() else AgentConfig(
            name="default",
            description="",
            skills=[],
            policies=[],
            instructions=""
        )
        
        # Parse security.md (Agent OS extension)
        security_md = agents_dir / "security.md"
        if security_md.exists():
            config.security_config = self._parse_security_md(security_md)
        
        return config
    
    def _parse_agents_md(self, path: Path) -> AgentConfig:
        """Parse agents.md file."""
        content = path.read_text(encoding="utf-8")
        
        # Extract YAML front matter if present
        front_matter = {}
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                yaml_content = content[3:end]
                front_matter = yaml.safe_load(yaml_content) or {}
                content = content[end + 3:].strip()
        
        # Parse sections
        name = front_matter.get("name", "agent")
        description = ""
        skills = []
        instructions = content
        
        # Find "You can:" or "Capabilities:" section
        can_match = re.search(r"(?:You can|Capabilities|Skills):\s*\n((?:[-*\d].*\n?)+)", content, re.IGNORECASE)
        if can_match:
            skills_text = can_match.group(1)
            skills = self._parse_skills(skills_text)
        
        # Find description (first paragraph)
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith(("#", "-", "*", "You can", "Capabilities")):
                description = line
                break
        
        return AgentConfig(
            name=name,
            description=description,
            skills=skills,
            policies=front_matter.get("policies", []),
            instructions=instructions,
            security_config=front_matter.get("security", {})
        )
    
    def _parse_skills(self, text: str) -> List[AgentSkill]:
        """Parse skills from bullet list."""
        skills = []
        
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Extract skill text
            skill_text = re.sub(r"^[-*\d.]+\s*", "", line)
            
            # Parse constraints from parentheses
            constraints = {}
            read_only = False
            requires_approval = False
            
            # Check for (read-only), (requires approval), etc.
            if "(read-only)" in skill_text.lower() or "(read only)" in skill_text.lower():
                read_only = True
                skill_text = re.sub(r"\s*\(read[- ]?only\)", "", skill_text, flags=re.IGNORECASE)
            
            if "(requires approval)" in skill_text.lower():
                requires_approval = True
                skill_text = re.sub(r"\s*\(requires approval\)", "", skill_text, flags=re.IGNORECASE)
            
            skills.append(AgentSkill(
                name=self._skill_to_action(skill_text),
                description=skill_text.strip(),
                read_only=read_only,
                requires_approval=requires_approval,
                constraints=constraints
            ))
        
        return skills
    
    def _skill_to_action(self, skill: str) -> str:
        """Convert skill description to action name."""
        skill_lower = skill.lower()
        
        # Map common patterns
        mappings = {
            "query database": "database_query",
            "read database": "database_query",
            "write to database": "database_write",
            "send email": "send_email",
            "write file": "file_write",
            "read file": "file_read",
            "call api": "api_call",
            "execute code": "code_execution",
            "search": "search",
            "browse": "web_browse",
        }
        
        for pattern, action in mappings.items():
            if pattern in skill_lower:
                return action
        
        # Default: snake_case the skill
        return re.sub(r"[^a-z0-9]+", "_", skill_lower).strip("_")
    
    def _parse_security_md(self, path: Path) -> Dict[str, Any]:
        """Parse security.md (Agent OS extension)."""
        content = path.read_text(encoding="utf-8")
        
        # Try YAML front matter first
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                yaml_content = content[3:end]
                return yaml.safe_load(yaml_content) or {}
        
        # Try full YAML
        try:
            return yaml.safe_load(content) or {}
        except yaml.YAMLError:
            pass
        
        return {}
    
    def to_kernel_policies(self, config: AgentConfig) -> Dict[str, Any]:
        """
        Convert AgentConfig to Agent OS kernel policies.
        
        Returns policy configuration for Control Plane.
        """
        policies = {
            "name": config.name,
            "version": "1.0",
            "rules": []
        }
        
        # Convert skills to rules
        for skill in config.skills:
            rule = {
                "action": skill.name,
                "effect": "allow" if skill.allowed else "deny",
            }
            
            if skill.read_only:
                rule["mode"] = "read_only"
            
            if skill.requires_approval:
                rule["requires_approval"] = True
            
            if skill.constraints:
                rule["constraints"] = skill.constraints
            
            policies["rules"].append(rule)
        
        # Add security config
        if config.security_config:
            sec = config.security_config
            
            if "signals" in sec:
                policies["allowed_signals"] = sec["signals"]
            
            if "max_tokens" in sec:
                policies["limits"] = {"max_tokens": sec["max_tokens"]}
        
        return policies


def discover_agents(root_dir: str = ".") -> List[AgentConfig]:
    """
    Discover all agent configurations in a repository.
    
    Looks for:
    - .agents/agents.md
    - .agents/AGENTS.md
    - agents.md (root)
    - AGENTS.md (root)
    
    Returns list of parsed configurations.
    """
    parser = AgentsParser()
    configs = []
    root = Path(root_dir)
    
    # Check .agents/ directory
    agents_dir = root / ".agents"
    if agents_dir.exists():
        try:
            configs.append(parser.parse_directory(str(agents_dir)))
        except Exception:
            pass
    
    # Check root agents.md
    for name in ["agents.md", "AGENTS.md"]:
        agents_md = root / name
        if agents_md.exists():
            try:
                config = parser._parse_agents_md(agents_md)
                configs.append(config)
            except Exception:
                pass
    
    return configs
