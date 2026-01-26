"""
CLI for MCP Kernel Server.

Usage:
    mcp-kernel-server [--port PORT] [--config CONFIG]
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from mcp_kernel_server.server import KernelMCPServer, ServerConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP Kernel Server - Agent OS primitives via Model Context Protocol"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (YAML)"
    )
    parser.add_argument(
        "--policy-mode",
        choices=["strict", "permissive", "audit"],
        default="strict",
        help="Policy enforcement mode (default: strict)"
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Use stdio transport instead of HTTP"
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit"
    )
    
    return parser.parse_args()


async def run_stdio_server(server: KernelMCPServer):
    """Run server with stdio transport (for Claude Desktop integration)."""
    import json
    
    logger.info("Starting MCP Kernel Server with stdio transport")
    
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())
    
    async def read_message():
        """Read JSON-RPC message from stdin."""
        line = await reader.readline()
        if not line:
            return None
        return json.loads(line.decode())
    
    def write_message(msg: dict):
        """Write JSON-RPC message to stdout."""
        writer.write((json.dumps(msg) + "\n").encode())
    
    while True:
        try:
            message = await read_message()
            if message is None:
                break
            
            method = message.get("method", "")
            params = message.get("params", {})
            msg_id = message.get("id")
            
            # Route to handler
            if method == "initialize":
                result = await server.handle_initialize(params)
            elif method == "tools/list":
                result = await server.handle_list_tools()
            elif method == "tools/call":
                result = await server.handle_call_tool(
                    params.get("name", ""),
                    params.get("arguments", {})
                )
            elif method == "resources/list":
                result = await server.handle_list_resources()
            elif method == "resources/templates/list":
                result = await server.handle_list_resource_templates()
            elif method == "resources/read":
                result = await server.handle_read_resource(params.get("uri", ""))
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Send response
            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
            write_message(response)
            await writer.drain()
            
        except Exception as e:
            logger.exception("Error processing message")
            if msg_id:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32000, "message": str(e)}
                }
                write_message(error_response)
                await writer.drain()


def main():
    """Main entry point."""
    args = parse_args()
    
    if args.version:
        from mcp_kernel_server import __version__
        print(f"mcp-kernel-server {__version__}")
        return
    
    # Build config
    config = ServerConfig(
        host=args.host,
        port=args.port,
        policy_mode=args.policy_mode
    )
    
    # Create server
    server = KernelMCPServer(config)
    
    # Run
    if args.stdio:
        asyncio.run(run_stdio_server(server))
    else:
        # HTTP transport (simplified - production would use proper ASGI)
        logger.info(f"MCP Kernel Server ready on http://{args.host}:{args.port}")
        logger.info("Tools: cmvk_verify, kernel_execute, iatp_sign")
        logger.info("Resources: vfs://")
        logger.info("Press Ctrl+C to stop")
        
        try:
            asyncio.run(server.start())
            # Keep running
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    main()
