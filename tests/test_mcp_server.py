"""
Test MCP Kernel Server.
"""

import pytest
from typing import Dict, Any


class TestMCPTools:
    """Test MCP tool implementations."""
    
    def test_import_tools(self):
        """Test importing MCP tools."""
        try:
            from mcp_kernel_server.tools import (
                CMVKVerifyTool,
                KernelExecuteTool,
                IATPSignTool,
            )
            assert CMVKVerifyTool is not None
            assert KernelExecuteTool is not None
            assert IATPSignTool is not None
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    def test_cmvk_tool_schema(self):
        """Test CMVK verify tool schema."""
        try:
            from mcp_kernel_server.tools import CMVKVerifyTool
            
            tool = CMVKVerifyTool()
            
            assert tool.name == "cmvk_verify"
            assert "claim" in tool.input_schema["properties"]
            assert "models" in tool.input_schema["properties"]
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    def test_kernel_execute_tool_schema(self):
        """Test kernel execute tool schema."""
        try:
            from mcp_kernel_server.tools import KernelExecuteTool
            
            tool = KernelExecuteTool()
            
            assert tool.name == "kernel_execute"
            assert "agent_id" in tool.input_schema["properties"]
            assert "action" in tool.input_schema["properties"]
            assert "context" in tool.input_schema["properties"]
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    def test_iatp_sign_tool_schema(self):
        """Test IATP sign tool schema."""
        try:
            from mcp_kernel_server.tools import IATPSignTool
            
            tool = IATPSignTool()
            
            assert tool.name == "iatp_sign"
            assert "message" in tool.input_schema["properties"]
            assert "agent_id" in tool.input_schema["properties"]
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    @pytest.mark.asyncio
    async def test_cmvk_verify_execution(self):
        """Test CMVK verify tool execution."""
        try:
            from mcp_kernel_server.tools import CMVKVerifyTool
            
            tool = CMVKVerifyTool()
            
            result = await tool.execute({
                "claim": "2 + 2 = 4",
                "models": ["mock-model-1", "mock-model-2"]
            })
            
            assert "verified" in result
            assert "confidence" in result
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    @pytest.mark.asyncio
    async def test_kernel_execute_allowed(self):
        """Test kernel execute for allowed action."""
        try:
            from mcp_kernel_server.tools import KernelExecuteTool
            
            tool = KernelExecuteTool()
            
            result = await tool.execute({
                "agent_id": "test-agent",
                "action": "database_query",
                "params": {"query": "SELECT 1"},
                "context": {"policies": []}
            })
            
            assert result["success"] is True
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    @pytest.mark.asyncio
    async def test_kernel_execute_blocked(self):
        """Test kernel execute for blocked action."""
        try:
            from mcp_kernel_server.tools import KernelExecuteTool
            
            tool = KernelExecuteTool()
            
            result = await tool.execute({
                "agent_id": "test-agent",
                "action": "file_write",
                "params": {"path": "/data/file.txt"},
                "context": {"policies": ["read_only"]}
            })
            
            assert result["success"] is False
            assert result["signal"] == "SIGKILL"
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    @pytest.mark.asyncio
    async def test_iatp_sign_execution(self):
        """Test IATP sign tool execution."""
        try:
            from mcp_kernel_server.tools import IATPSignTool
            
            tool = IATPSignTool()
            
            result = await tool.execute({
                "message": "Hello, World!",
                "agent_id": "test-agent"
            })
            
            assert "signature" in result
            assert "timestamp" in result
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")


class TestMCPServer:
    """Test MCP server implementation."""
    
    def test_import_server(self):
        """Test importing MCP server."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            assert KernelMCPServer is not None
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    def test_create_server(self):
        """Test creating MCP server."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            assert server is not None
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    def test_server_has_tools(self):
        """Test server has registered tools."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            
            assert len(server.tools) == 3
            tool_names = [t.name for t in server.tools]
            assert "cmvk_verify" in tool_names
            assert "kernel_execute" in tool_names
            assert "iatp_sign" in tool_names
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    def test_server_tools_list(self):
        """Test server tools/list response."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            tools = server.list_tools()
            
            assert len(tools) == 3
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    @pytest.mark.asyncio
    async def test_server_handle_tool_call(self):
        """Test server handles tool call."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            
            result = await server.call_tool(
                name="cmvk_verify",
                arguments={"claim": "1 + 1 = 2", "models": ["m1", "m2"]}
            )
            
            assert result is not None
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")


class TestMCPResources:
    """Test MCP resource handling."""
    
    def test_server_has_vfs_resources(self):
        """Test server exposes VFS resources."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            resources = server.list_resources()
            
            # Should have VFS resource templates
            assert any("vfs" in str(r.get("uri", "")) for r in resources)
        except (ImportError, AttributeError):
            pytest.skip("mcp_kernel_server not installed or resources not implemented")
    
    @pytest.mark.asyncio
    async def test_read_vfs_resource(self):
        """Test reading VFS resource."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            
            # Read memory resource
            content = await server.read_resource("vfs://test-agent/mem/working/data")
            
            # May be empty but shouldn't crash
            assert content is not None or content == ""
        except (ImportError, AttributeError):
            pytest.skip("mcp_kernel_server not installed or resources not implemented")


class TestMCPProtocol:
    """Test MCP protocol handling."""
    
    @pytest.mark.asyncio
    async def test_initialize_response(self):
        """Test initialize protocol response."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            
            response = await server.handle_message({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            })
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert "capabilities" in response["result"]
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
    
    @pytest.mark.asyncio
    async def test_tools_list_response(self):
        """Test tools/list protocol response."""
        try:
            from mcp_kernel_server.server import KernelMCPServer
            
            server = KernelMCPServer()
            
            # Initialize first
            await server.handle_message({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            })
            
            response = await server.handle_message({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            })
            
            assert response["id"] == 2
            assert "tools" in response["result"]
        except ImportError:
            pytest.skip("mcp_kernel_server not installed")
