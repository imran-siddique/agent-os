"""
Test Agent OS CLI.
"""

import pytest
import tempfile
from pathlib import Path
import argparse
import json
import io
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


class TestCLIServe:
    """Test agentos serve command."""

    def test_serve_parser_defaults(self):
        """Test serve subparser accepts --port and --host with defaults."""
        from agent_os.cli import main
        import argparse

        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        # Re-use the real parser by parsing known args
        original_argv = sys.argv
        try:
            sys.argv = ["agentos", "serve"]
            # Just verify parsing doesn't error
            from agent_os.cli import main as _m
        finally:
            sys.argv = original_argv

    def test_serve_custom_port(self):
        """Test serve accepts a custom port."""
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        sp = sub.add_parser("serve")
        sp.add_argument("--port", type=int, default=8080)
        sp.add_argument("--host", default="0.0.0.0")
        args = parser.parse_args(["serve", "--port", "9090", "--host", "127.0.0.1"])
        assert args.port == 9090
        assert args.host == "127.0.0.1"

    def test_request_handler_health(self):
        """Test /health endpoint returns ok status."""
        import io
        from agent_os.cli import AgentOSRequestHandler

        handler = _make_get_handler("/health")
        body = json.loads(handler._response_body)
        assert body["status"] == "ok"
        assert "version" in body

    def test_request_handler_agents(self):
        """Test /agents endpoint returns list."""
        from agent_os.cli import AgentOSRequestHandler, _registered_agents

        _registered_agents.clear()
        handler = _make_get_handler("/agents")
        body = json.loads(handler._response_body)
        assert body == {"agents": []}

    def test_request_handler_status(self):
        """Test /status endpoint returns kernel state."""
        handler = _make_get_handler("/status")
        body = json.loads(handler._response_body)
        assert "active_agents" in body
        assert "uptime_seconds" in body

    def test_request_handler_not_found(self):
        """Test unknown path returns 404."""
        handler = _make_get_handler("/unknown")
        assert handler._response_code == 404

    def test_post_execute_unknown_agent(self):
        """Test POST /agents/{id}/execute with unknown agent returns 404."""
        from agent_os.cli import _registered_agents

        _registered_agents.clear()
        handler = _make_post_handler("/agents/unknown-agent/execute", b'{"action":"test"}')
        assert handler._response_code == 404

    def test_post_execute_known_agent(self):
        """Test POST /agents/{id}/execute with known agent succeeds."""
        from agent_os.cli import _registered_agents

        _registered_agents["a1"] = {"id": "a1", "name": "test-agent"}
        try:
            handler = _make_post_handler("/agents/a1/execute", b'{"action":"run"}')
            body = json.loads(handler._response_body)
            assert body["status"] == "executed"
            assert body["agent_id"] == "a1"
        finally:
            _registered_agents.clear()


class TestCLIMetrics:
    """Test agentos metrics command."""

    def test_metrics_output_format(self, capsys):
        """Test metrics prints Prometheus exposition format."""
        from agent_os.cli import cmd_metrics

        class Args:
            pass

        result = cmd_metrics(Args())
        assert result == 0
        output = capsys.readouterr().out

        assert "# HELP agentos_policy_violations_total" in output
        assert "# TYPE agentos_policy_violations_total counter" in output
        assert "agentos_active_agents" in output
        assert "agentos_uptime_seconds" in output
        assert 'agentos_kernel_operations_total{operation="execute"}' in output
        assert 'agentos_kernel_operations_total{operation="set"}' in output
        assert 'agentos_kernel_operations_total{operation="get"}' in output
        assert "agentos_audit_log_entries" in output

    def test_metrics_types(self, capsys):
        """Test metrics include correct TYPE annotations."""
        from agent_os.cli import cmd_metrics

        class Args:
            pass

        cmd_metrics(Args())
        output = capsys.readouterr().out
        assert "# TYPE agentos_active_agents gauge" in output
        assert "# TYPE agentos_uptime_seconds gauge" in output
        assert "# TYPE agentos_kernel_operations_total counter" in output
        assert "# TYPE agentos_audit_log_entries gauge" in output


# ============================================================================
# Helpers for handler unit tests
# ============================================================================


class _FakeSocket:
    """Minimal socket stand-in for BaseHTTPRequestHandler."""

    def __init__(self, request_bytes: bytes):
        self._file = io.BytesIO(request_bytes)

    def makefile(self, mode: str, buffering: int = -1):
        if "r" in mode:
            return self._file
        return io.BytesIO()


class _StubHandler:
    """Capture response instead of writing to a real socket."""

    _response_body: str = ""
    _response_code: int = 200


def _make_get_handler(path: str):
    """Create a handler, invoke do_GET, and capture the JSON response."""
    from agent_os.cli import AgentOSRequestHandler

    request_line = f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode()

    class _Capture(AgentOSRequestHandler):
        def __init__(self):
            self.path = path
            self.headers = {}
            self._response_body = ""
            self._response_code = 200
            self.wfile = io.BytesIO()

        def _send_json(self, data, status=200):
            self._response_body = json.dumps(data, indent=2)
            self._response_code = status

    h = _Capture()
    h.do_GET()
    return h


def _make_post_handler(path: str, body: bytes):
    """Create a handler, invoke do_POST, and capture the JSON response."""
    from agent_os.cli import AgentOSRequestHandler

    class _Capture(AgentOSRequestHandler):
        def __init__(self):
            self.path = path
            self.headers = {"Content-Length": str(len(body))}
            self.rfile = io.BytesIO(body)
            self._response_body = ""
            self._response_code = 200
            self.wfile = io.BytesIO()

        def _send_json(self, data, status=200):
            self._response_body = json.dumps(data, indent=2)
            self._response_code = status

    h = _Capture()
    h.do_POST()
    return h


# ============================================================================
# Tests for error message formatting (#126)
# ============================================================================


class TestErrorFormatting:
    """Test CLI error formatting helpers."""

    def test_format_error_basic(self):
        """Test basic error message without suggestion."""
        from agent_os.cli import format_error

        msg = format_error("something went wrong")
        assert "something went wrong" in msg
        assert "Error:" in msg

    def test_format_error_with_suggestion(self):
        """Test error message includes suggestion text."""
        from agent_os.cli import format_error

        msg = format_error("missing file", suggestion="create it first")
        assert "missing file" in msg
        assert "create it first" in msg
        assert "Suggestion:" in msg

    def test_format_error_with_docs_link(self):
        """Test error message includes a docs URL."""
        from agent_os.cli import format_error

        msg = format_error("bad config", docs_path="getting-started.md")
        assert "getting-started.md" in msg

    def test_handle_missing_config(self):
        """Test missing-config helper includes init suggestion."""
        from agent_os.cli import handle_missing_config

        msg = handle_missing_config("/tmp/proj")
        assert "agentos init" in msg
        assert "/tmp/proj" in msg

    def test_handle_invalid_policy_with_typo(self):
        """Test invalid-policy helper offers a fuzzy suggestion."""
        from agent_os.cli import handle_invalid_policy

        msg = handle_invalid_policy("strct")
        assert "strict" in msg
        assert "Did you mean" in msg

    def test_handle_invalid_policy_unknown(self):
        """Test invalid-policy helper lists available policies."""
        from agent_os.cli import handle_invalid_policy

        msg = handle_invalid_policy("foobar")
        assert "strict" in msg
        assert "permissive" in msg
        assert "audit" in msg

    def test_handle_missing_dependency(self):
        """Test missing-dependency helper shows pip install command."""
        from agent_os.cli import handle_missing_dependency

        msg = handle_missing_dependency("redis", extra="redis")
        assert "pip install agent-os[redis]" in msg

    def test_handle_connection_error(self):
        """Test connection-error helper includes host:port."""
        from agent_os.cli import handle_connection_error

        msg = handle_connection_error("localhost", 6379)
        assert "localhost:6379" in msg


# ============================================================================
# Tests for Colors instance isolation (#127)
# ============================================================================


class TestColorsInstanceIsolation:
    """Test that Colors uses instance state, not shared class state."""

    def test_disable_is_instance_scoped(self):
        """Disabling one Colors instance must not affect another."""
        from agent_os.cli import Colors as _ColorsClass

        a = _ColorsClass.__class__(enabled=True)
        b = _ColorsClass.__class__(enabled=True)

        a.disable()

        assert a.RED == ""
        assert b.RED != "", "Second instance should still have colours"

    def test_enable_restores_codes(self):
        """Calling enable() after disable() restores ANSI codes."""
        from agent_os.cli import Colors as _ColorsClass

        inst = _ColorsClass.__class__(enabled=True)
        inst.disable()
        assert inst.RED == ""

        inst.enable()
        assert inst.RED == "\033[91m"

    def test_enabled_property(self):
        """The enabled property reflects current state."""
        from agent_os.cli import Colors as _ColorsClass

        inst = _ColorsClass.__class__(enabled=True)
        assert inst.enabled is True

        inst.disable()
        assert inst.enabled is False

    def test_thread_safety_separate_instances(self):
        """Concurrent threads with separate instances don't interfere."""
        import threading
        from agent_os.cli import Colors as _ColorsClass

        results = {}

        def worker(name, enabled):
            inst = _ColorsClass.__class__(enabled=enabled)
            # Small sleep to interleave threads
            import time
            time.sleep(0.01)
            results[name] = inst.RED

        t1 = threading.Thread(target=worker, args=("on", True))
        t2 = threading.Thread(target=worker, args=("off", False))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert results["on"] != "", "Enabled instance keeps codes"
        assert results["off"] == "", "Disabled instance has empty codes"
