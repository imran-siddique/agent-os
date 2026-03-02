"""
End-to-end tests for the MCP Kernel Server stdio mode.
The server is started with `--stdio` and exercised through real JSON-RPC messages over stdin/stdout.

Skipped on Windows due to asyncio pipe limitations.
"""

import json
import os
import selectors
import subprocess
import sys
import time
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

import pytest

if sys.platform.startswith("win"):
    pytest.skip(
        "stdio transport E2E is skipped on Windows (asyncio connect_*_pipe often unsupported).",
        allow_module_level=True,
    )


@dataclass
class StdioServer:
    proc: subprocess.Popen[str]

    def send(self, payload: dict[str, Any]) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def recv(self, timeout_s: float = 5.0) -> dict[str, Any]:
        """
        Read one JSON line from stdout with a real timeout using selectors.
        Also fails fast with stderr if process exits early.
        """
        assert self.proc.stdout is not None
        assert self.proc.stderr is not None

        sel = selectors.DefaultSelector()
        sel.register(self.proc.stdout, selectors.EVENT_READ)

        deadline = time.time() + timeout_s

        while time.time() < deadline:
            rc = self.proc.poll()
            if rc is not None:
                # Process died
                err = self.proc.stderr.read() or ""
                out = self.proc.stdout.read() or ""
                raise RuntimeError(
                    f"Server process exited early with return code {rc}\n"
                    f"--- stderr ---\n{err}\n"
                    f"--- stdout ---\n{out}\n"
                )

            events = sel.select(timeout=0.05)
            if not events:
                continue

            chunk = self.proc.stdout.readline()
            if not chunk:
                continue

            try:
                return json.loads(chunk)
            except json.JSONDecodeError:
                continue

        # timeout
        err = self.proc.stderr.read() or ""
        raise TimeoutError(f"Timed out waiting for server response.\n--- stderr ---\n{err}\n")

    def close(self) -> None:
        try:
            if self.proc.stdin:
                try:
                    self.proc.stdin.close()
                except Exception:
                    pass

            try:
                self.proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=2.0)
        finally:
            try:
                if self.proc.stdout:
                    self.proc.stdout.read()
            except Exception:
                pass
            try:
                if self.proc.stderr:
                    self.proc.stderr.read()
            except Exception:
                pass


@pytest.fixture()
def stdio_server() -> Generator[StdioServer, None, None]:
    """Start mcp-kernel-server in --stdio mode as a subprocess."""
    tests_dir = os.path.dirname(__file__)
    module_dir = os.path.abspath(os.path.join(tests_dir, ".."))
    src_dir = os.path.join(module_dir, "src")

    env = os.environ.copy()
    env["PYTHONPATH"] = src_dir + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    cmd = [sys.executable, "-m", "mcp_kernel_server.cli", "--stdio"]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        bufsize=1,
    )

    server = StdioServer(proc=proc)
    try:
        yield server
    finally:
        server.close()


def assert_jsonrpc_ok(resp: dict[str, Any], expected_id: Any) -> None:
    assert resp.get("jsonrpc") == "2.0"
    assert resp.get("id") == expected_id
    assert ("result" in resp) ^ ("error" in resp), "Response must have exactly one of result/error"


class TestStdioE2E:
    def test_stdio_initialize_tools_list_call_roundtrip(self, stdio_server: StdioServer) -> None:
        # initialize
        stdio_server.send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        init_resp = stdio_server.recv(timeout_s=8.0)
        assert_jsonrpc_ok(init_resp, 1)
        assert init_resp["result"]["serverInfo"]["name"] == "agent-os-kernel"

        # tools/list
        stdio_server.send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools_resp = stdio_server.recv(timeout_s=8.0)
        assert_jsonrpc_ok(tools_resp, 2)
        tools = tools_resp["result"]["tools"]
        names = {t.get("name") for t in tools}
        expected = {
            "verify_code_safety",
            "cmvk_verify",
            "cmvk_review",
            "kernel_execute",
            "iatp_sign",
            "iatp_verify",
            "iatp_reputation",
            "get_audit_log",
        }
        assert set(names) == expected

        # tools/call (success)
        stdio_server.send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "verify_code_safety",
                    "arguments": {"code": "x = 1 + 2", "language": "python"},
                },
            }
        )
        call_resp = stdio_server.recv(timeout_s=8.0)
        assert_jsonrpc_ok(call_resp, expected_id=3)

        result = call_resp["result"]
        assert result.get("isError") is False
        assert isinstance(result.get("content"), list)
        assert result["content"][0]["type"] == "text"
        data = json.loads(result["content"][0]["text"])
        assert data.get("safe") is True

        # tools/call (failure)
        stdio_server.send(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "kernel_execute",
                    "arguments": {
                        "action": "file_write",
                        "params": {"path": "/tmp/x", "content": "nope"},
                        "agent_id": "test-agent",
                        "policies": ["read_only"],
                    },
                },
            }
        )
        blocked_resp = stdio_server.recv(timeout_s=8.0)
        assert_jsonrpc_ok(blocked_resp, expected_id=4)

        blocked = blocked_resp["result"]
        assert blocked.get("isError") is True
        assert isinstance(blocked.get("content"), list)
        assert blocked["content"][0]["type"] == "text"
        assert isinstance(blocked["content"][0]["text"], str)
        assert blocked["content"][0]["text"]

    def test_stdio_unknown_method_returns_32601(self, stdio_server: StdioServer) -> None:
        stdio_server.send({"jsonrpc": "2.0", "id": 10, "method": "does_not_exist", "params": {}})
        resp = stdio_server.recv(timeout_s=8.0)
        assert resp.get("jsonrpc") == "2.0"
        assert resp.get("id") == 10
        assert resp["error"]["code"] == -32601

    def test_stdio_unknown_tool_returns_mcp_error_result(self, stdio_server: StdioServer) -> None:
        stdio_server.send(
            {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {"name": "does_not_exist", "arguments": {}},
            }
        )
        resp = stdio_server.recv(timeout_s=8.0)
        assert_jsonrpc_ok(resp, 11)
        result = resp["result"]
        assert result.get("isError") is True
        assert "Unknown tool" in result["content"][0]["text"]

    def test_stdio_malformed_json_returns_32603(self, stdio_server: StdioServer):
        assert stdio_server.proc.stdin is not None
        stdio_server.proc.stdin.write('{"jsonrpc": "2.0", "method": "initialize"\n')
        stdio_server.proc.stdin.flush()
        resp = stdio_server.recv(timeout_s=5.0)
        assert resp.get("jsonrpc") == "2.0"
        assert resp.get("id") is None
        assert "error" in resp
        assert resp["error"]["code"] == -32603
