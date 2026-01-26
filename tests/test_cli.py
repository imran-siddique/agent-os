"""
Test Agent OS CLI.
"""

import pytest
import tempfile
from pathlib import Path
import sys


class TestCLIInit:
    """Test agentos init command."""
    
    def test_init_creates_agents_dir(self):
        """Test init creates .agents/ directory."""
        from agent_os.cli import cmd_init
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Args:
                path = tmpdir
                template = "strict"
                force = False
            
            result = cmd_init(Args())
            
            assert result == 0
            assert (Path(tmpdir) / ".agents").exists()
            assert (Path(tmpdir) / ".agents" / "agents.md").exists()
            assert (Path(tmpdir) / ".agents" / "security.md").exists()
    
    def test_init_strict_template(self):
        """Test init with strict template."""
        from agent_os.cli import cmd_init
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Args:
                path = tmpdir
                template = "strict"
                force = False
            
            cmd_init(Args())
            
            security_md = (Path(tmpdir) / ".agents" / "security.md").read_text()
            assert "mode: strict" in security_md
            assert "SIGKILL" in security_md
    
    def test_init_permissive_template(self):
        """Test init with permissive template."""
        from agent_os.cli import cmd_init
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Args:
                path = tmpdir
                template = "permissive"
                force = False
            
            cmd_init(Args())
            
            security_md = (Path(tmpdir) / ".agents" / "security.md").read_text()
            assert "mode: permissive" in security_md
    
    def test_init_audit_template(self):
        """Test init with audit template."""
        from agent_os.cli import cmd_init
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Args:
                path = tmpdir
                template = "audit"
                force = False
            
            cmd_init(Args())
            
            security_md = (Path(tmpdir) / ".agents" / "security.md").read_text()
            assert "mode: audit" in security_md
    
    def test_init_fails_if_exists(self):
        """Test init fails if .agents/ already exists."""
        from agent_os.cli import cmd_init
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".agents").mkdir()
            
            class Args:
                path = tmpdir
                template = "strict"
                force = False
            
            result = cmd_init(Args())
            assert result == 1
    
    def test_init_force_overwrites(self):
        """Test init --force overwrites existing."""
        from agent_os.cli import cmd_init
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".agents").mkdir()
            (Path(tmpdir) / ".agents" / "old.txt").write_text("old")
            
            class Args:
                path = tmpdir
                template = "strict"
                force = True
            
            result = cmd_init(Args())
            assert result == 0
            assert (Path(tmpdir) / ".agents" / "agents.md").exists()


class TestCLISecure:
    """Test agentos secure command."""
    
    def test_secure_validates_config(self):
        """Test secure validates security config."""
        from agent_os.cli import cmd_init, cmd_secure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # First init
            class InitArgs:
                path = tmpdir
                template = "strict"
                force = False
            cmd_init(InitArgs())
            
            # Then secure
            class SecureArgs:
                path = tmpdir
                verify = False
            
            result = cmd_secure(SecureArgs())
            assert result == 0
    
    def test_secure_fails_without_agents_dir(self):
        """Test secure fails if no .agents/ directory."""
        from agent_os.cli import cmd_secure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class Args:
                path = tmpdir
                verify = False
            
            result = cmd_secure(Args())
            assert result == 1
    
    def test_secure_fails_without_security_md(self):
        """Test secure fails if no security.md."""
        from agent_os.cli import cmd_secure
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".agents").mkdir()
            
            class Args:
                path = tmpdir
                verify = False
            
            result = cmd_secure(Args())
            assert result == 1


class TestCLIAudit:
    """Test agentos audit command."""
    
    def test_audit_reports_missing_files(self):
        """Test audit reports missing files."""
        from agent_os.cli import cmd_audit
        
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".agents").mkdir()
            (Path(tmpdir) / ".agents" / "agents.md").write_text("# Agent")
            # No security.md
            
            class Args:
                path = tmpdir
                format = "text"
            
            result = cmd_audit(Args())
            assert result == 1  # Fails due to missing security.md
    
    def test_audit_passes_with_valid_config(self):
        """Test audit passes with valid configuration."""
        from agent_os.cli import cmd_init, cmd_audit
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # First init
            class InitArgs:
                path = tmpdir
                template = "strict"
                force = False
            cmd_init(InitArgs())
            
            # Then audit
            class AuditArgs:
                path = tmpdir
                format = "text"
            
            result = cmd_audit(AuditArgs())
            assert result == 0
    
    def test_audit_json_format(self):
        """Test audit JSON output format."""
        from agent_os.cli import cmd_init, cmd_audit
        import json
        from io import StringIO
        
        with tempfile.TemporaryDirectory() as tmpdir:
            class InitArgs:
                path = tmpdir
                template = "strict"
                force = False
            cmd_init(InitArgs())
            
            class AuditArgs:
                path = tmpdir
                format = "json"
            
            # Capture output would need more setup
            # Just verify it doesn't crash
            result = cmd_audit(AuditArgs())
            assert result == 0


class TestCLIStatus:
    """Test agentos status command."""
    
    def test_status_shows_version(self):
        """Test status shows version information."""
        from agent_os.cli import cmd_status
        
        class Args:
            pass
        
        # Should not crash
        result = cmd_status(Args())
        assert result == 0


class TestCLIMain:
    """Test main CLI entry point."""
    
    def test_main_no_args(self):
        """Test main with no arguments."""
        from agent_os.cli import main
        import sys
        
        # Save original argv
        original_argv = sys.argv
        
        try:
            sys.argv = ["agentos"]
            result = main()
            assert result == 0
        finally:
            sys.argv = original_argv
    
    def test_main_version(self):
        """Test main --version."""
        from agent_os.cli import main
        import sys
        
        original_argv = sys.argv
        
        try:
            sys.argv = ["agentos", "--version"]
            result = main()
            assert result == 0
        finally:
            sys.argv = original_argv
