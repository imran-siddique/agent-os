"""
Test AGENTS.md compatibility module.
"""

import pytest
import tempfile
from pathlib import Path


class TestAgentsParser:
    """Test AgentsParser class."""
    
    def test_import_agents_compat(self):
        """Test importing agents_compat module."""
        from agent_os.agents_compat import (
            AgentsParser,
            AgentConfig,
            AgentSkill,
            discover_agents,
        )
        assert AgentsParser is not None
        assert AgentConfig is not None
    
    def test_create_parser(self):
        """Test creating a parser."""
        from agent_os.agents_compat import AgentsParser
        
        parser = AgentsParser()
        assert parser is not None
    
    def test_parse_skill_bullet_list(self):
        """Test parsing skill bullet lists."""
        from agent_os.agents_compat import AgentsParser
        
        parser = AgentsParser()
        skills = parser._parse_skills("""
- Query databases
- Generate reports
- Send emails
""")
        
        assert len(skills) == 3
        assert skills[0].description == "Query databases"
        assert skills[1].description == "Generate reports"
        assert skills[2].description == "Send emails"
    
    def test_parse_skill_with_read_only(self):
        """Test parsing skills with (read-only) modifier."""
        from agent_os.agents_compat import AgentsParser
        
        parser = AgentsParser()
        skills = parser._parse_skills("""
- Query databases (read-only)
- Read files (read only)
""")
        
        assert skills[0].read_only is True
        assert skills[1].read_only is True
    
    def test_parse_skill_with_approval(self):
        """Test parsing skills with (requires approval) modifier."""
        from agent_os.agents_compat import AgentsParser
        
        parser = AgentsParser()
        skills = parser._parse_skills("""
- Send emails (requires approval)
- Delete files (requires approval)
""")
        
        assert skills[0].requires_approval is True
        assert skills[1].requires_approval is True
    
    def test_skill_to_action(self):
        """Test converting skill descriptions to action names."""
        from agent_os.agents_compat import AgentsParser
        
        parser = AgentsParser()
        
        assert parser._skill_to_action("Query databases") == "database_query"
        assert parser._skill_to_action("Send email") == "send_email"
        assert parser._skill_to_action("Write file") == "file_write"
        assert parser._skill_to_action("Call API") == "api_call"
    
    def test_parse_agents_md_file(self):
        """Test parsing actual agents.md file."""
        from agent_os.agents_compat import AgentsParser
        
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".agents"
            agents_dir.mkdir()
            
            agents_md = agents_dir / "agents.md"
            agents_md.write_text("""# Data Analyst Agent

You are a data analyst agent.

## Capabilities

You can:
- Query databases (read-only)
- Generate visualizations
- Export to PDF
""")
            
            parser = AgentsParser()
            config = parser.parse_directory(str(agents_dir))
            
            assert config is not None
            assert len(config.skills) == 3
            assert config.skills[0].read_only is True
    
    def test_parse_security_md_file(self):
        """Test parsing security.md extension."""
        from agent_os.agents_compat import AgentsParser
        
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".agents"
            agents_dir.mkdir()
            
            (agents_dir / "agents.md").write_text("# Agent")
            
            security_md = agents_dir / "security.md"
            security_md.write_text("""
kernel:
  version: "1.0"
  mode: strict

signals:
  - SIGSTOP
  - SIGKILL
""")
            
            parser = AgentsParser()
            config = parser.parse_directory(str(agents_dir))
            
            assert "kernel" in config.security_config
            assert config.security_config["kernel"]["mode"] == "strict"
    
    def test_to_kernel_policies(self):
        """Test converting AgentConfig to kernel policies."""
        from agent_os.agents_compat import AgentsParser, AgentConfig, AgentSkill
        
        config = AgentConfig(
            name="test-agent",
            description="Test agent",
            skills=[
                AgentSkill(name="database_query", description="Query DB", read_only=True),
                AgentSkill(name="file_write", description="Write files", requires_approval=True),
            ],
            policies=[],
            instructions=""
        )
        
        parser = AgentsParser()
        policies = parser.to_kernel_policies(config)
        
        assert policies["name"] == "test-agent"
        assert len(policies["rules"]) == 2
        assert policies["rules"][0]["mode"] == "read_only"
        assert policies["rules"][1]["requires_approval"] is True


class TestDiscoverAgents:
    """Test agent discovery function."""
    
    def test_discover_agents_empty_dir(self):
        """Test discovering agents in empty directory."""
        from agent_os.agents_compat import discover_agents
        
        with tempfile.TemporaryDirectory() as tmpdir:
            configs = discover_agents(tmpdir)
            assert configs == []
    
    def test_discover_agents_with_dotdir(self):
        """Test discovering agents with .agents/ directory."""
        from agent_os.agents_compat import discover_agents
        
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / ".agents"
            agents_dir.mkdir()
            (agents_dir / "agents.md").write_text("# Test Agent\n\nYou can:\n- Do things")
            
            configs = discover_agents(tmpdir)
            assert len(configs) == 1
    
    def test_discover_agents_root_file(self):
        """Test discovering agents.md in root."""
        from agent_os.agents_compat import discover_agents
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "AGENTS.md").write_text("# Root Agent\n\nYou can:\n- Do stuff")
            
            configs = discover_agents(tmpdir)
            # On case-insensitive filesystems (Windows), may find both AGENTS.md patterns
            assert len(configs) >= 1


class TestAgentSkill:
    """Test AgentSkill dataclass."""
    
    def test_skill_defaults(self):
        """Test skill default values."""
        from agent_os.agents_compat import AgentSkill
        
        skill = AgentSkill(name="test", description="Test skill")
        
        assert skill.allowed is True
        assert skill.requires_approval is False
        assert skill.read_only is False
        assert skill.constraints == {}
    
    def test_skill_with_options(self):
        """Test skill with all options."""
        from agent_os.agents_compat import AgentSkill
        
        skill = AgentSkill(
            name="dangerous",
            description="Dangerous action",
            allowed=False,
            requires_approval=True,
            read_only=False,
            constraints={"max_calls": 10}
        )
        
        assert skill.allowed is False
        assert skill.requires_approval is True
        assert skill.constraints["max_calls"] == 10


class TestAgentConfig:
    """Test AgentConfig dataclass."""
    
    def test_config_creation(self):
        """Test creating an agent config."""
        from agent_os.agents_compat import AgentConfig, AgentSkill
        
        config = AgentConfig(
            name="my-agent",
            description="My agent",
            skills=[AgentSkill(name="test", description="Test")],
            policies=["strict"],
            instructions="Do things safely"
        )
        
        assert config.name == "my-agent"
        assert len(config.skills) == 1
        assert config.policies == ["strict"]
