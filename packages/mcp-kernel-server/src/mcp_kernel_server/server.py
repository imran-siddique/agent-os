"""
MCP Kernel Server - Main server implementation.

Exposes Agent OS primitives through Model Context Protocol:
- Tools: cmvk_verify, kernel_execute, iatp_sign
- Resources: VFS filesystem
"""

import asyncio
import json
import logging
from typing import Any, Optional
from dataclasses import dataclass, asdict

from mcp_kernel_server.tools import (
    CMVKVerifyTool,
    KernelExecuteTool,
    IATPSignTool,
    ToolResult,
)
from mcp_kernel_server.resources import VFSResource, VFSResourceTemplate

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8080
    policy_mode: str = "strict"
    cmvk_threshold: float = 0.85
    vfs_backend: str = "memory"


class KernelMCPServer:
    """
    MCP Server exposing Agent OS kernel primitives.
    
    Stateless Design (MCP June 2026 Standard):
    - No session state maintained
    - All context passed in each request
    - State externalized to backend storage
    - Horizontally scalable
    
    Tools:
    - cmvk_verify: Cross-model verification
    - kernel_execute: Governed action execution
    - iatp_sign: Trust attestation signing
    
    Resources:
    - vfs://: Agent Virtual File System
    """
    
    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or ServerConfig()
        
        # Initialize tools (stateless)
        self.tools = {
            "cmvk_verify": CMVKVerifyTool({"threshold": self.config.cmvk_threshold}),
            "kernel_execute": KernelExecuteTool({"policy_mode": self.config.policy_mode}),
            "iatp_sign": IATPSignTool(),
        }
        
        # Initialize resources (stateless with external backend)
        self.vfs = VFSResource({"backend": self.config.vfs_backend})
    
    # =========================================================================
    # MCP Protocol Handlers
    # =========================================================================
    
    async def handle_initialize(self, params: dict) -> dict:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
            },
            "serverInfo": {
                "name": "agent-os-kernel",
                "version": "0.1.0"
            }
        }
    
    async def handle_list_tools(self) -> dict:
        """Handle MCP tools/list request."""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema
                }
                for tool in self.tools.values()
            ]
        }
    
    async def handle_call_tool(self, name: str, arguments: dict) -> dict:
        """Handle MCP tools/call request."""
        if name not in self.tools:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}]
            }
        
        tool = self.tools[name]
        
        try:
            result = await tool.execute(arguments)
            
            if result.success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.data, indent=2)
                        }
                    ],
                    "isError": False
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": result.error or "Execution failed"
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            logger.exception(f"Tool execution failed: {name}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": str(e)}]
            }
    
    async def handle_list_resources(self) -> dict:
        """Handle MCP resources/list request."""
        # Return resource templates for discovery
        return {
            "resources": [
                {
                    "uri": "vfs://",
                    "name": "Agent VFS Root",
                    "description": "Virtual File System for agent memory",
                    "mimeType": "application/json"
                }
            ]
        }
    
    async def handle_list_resource_templates(self) -> dict:
        """Handle MCP resources/templates/list request."""
        return {
            "resourceTemplates": VFSResourceTemplate.get_templates()
        }
    
    async def handle_read_resource(self, uri: str) -> dict:
        """Handle MCP resources/read request."""
        try:
            result = await self.vfs.read(uri)
            return {
                "contents": [
                    {
                        "uri": result.uri,
                        "mimeType": result.mime_type,
                        "text": json.dumps(result.content, indent=2)
                    }
                ]
            }
        except Exception as e:
            logger.exception(f"Resource read failed: {uri}")
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": f"Error: {str(e)}"
                    }
                ]
            }
    
    # =========================================================================
    # Server Lifecycle
    # =========================================================================
    
    async def start(self):
        """Start the MCP server."""
        logger.info(f"Starting MCP Kernel Server on {self.config.host}:{self.config.port}")
        # In production, this would start the actual MCP transport
        # (stdio, HTTP, WebSocket based on config)
    
    async def stop(self):
        """Stop the MCP server."""
        logger.info("Stopping MCP Kernel Server")


# =========================================================================
# Stateless Execution Helper (for direct integration)
# =========================================================================

async def stateless_execute(
    action: str,
    params: dict,
    context: dict,
    config: Optional[dict] = None
) -> dict:
    """
    Execute an action through the kernel statelessly.
    
    This is the core stateless API for June 2026 MCP compliance:
    - All context passed in request
    - No session state maintained
    - Can run on any server instance
    
    Args:
        action: Action to execute (e.g., "database_query")
        params: Action parameters
        context: Full execution context including:
            - agent_id: Identifier for the agent
            - policies: List of policy names to enforce
            - history: Previous interactions (optional)
            - state: External state reference (optional)
        config: Optional server configuration
    
    Returns:
        Execution result with success status and data
    """
    server = KernelMCPServer(ServerConfig(**(config or {})))
    
    tool_args = {
        "action": action,
        "params": params,
        "agent_id": context.get("agent_id", "anonymous"),
        "policies": context.get("policies", []),
        "context": context
    }
    
    result = await server.tools["kernel_execute"].execute(tool_args)
    
    return {
        "success": result.success,
        "data": result.data,
        "error": result.error,
        "metadata": result.metadata
    }
