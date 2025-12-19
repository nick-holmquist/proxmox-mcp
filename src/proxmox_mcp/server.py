"""MCP Server for Proxmox VE management."""

import asyncio
import json
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import client
from .tools import nodes, vms, containers, storage, network, backup

# Load environment variables
load_dotenv()

# Create MCP server
server = Server("proxmox-mcp")


def format_result(data: Any) -> str:
    """Format API result as JSON string."""
    return json.dumps(data, indent=2, default=str)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Proxmox tools."""
    tools = []
    tools.extend(nodes.get_tools())
    tools.extend(vms.get_tools())
    tools.extend(containers.get_tools())
    tools.extend(storage.get_tools())
    tools.extend(network.get_tools())
    tools.extend(backup.get_tools())
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Proxmox tool."""
    try:
        # Route to appropriate handler
        if name.startswith("pve_node"):
            result = nodes.handle_tool(name, arguments)
        elif name.startswith("pve_vm"):
            result = vms.handle_tool(name, arguments)
        elif name.startswith("pve_container"):
            result = containers.handle_tool(name, arguments)
        elif name.startswith("pve_storage"):
            result = storage.handle_tool(name, arguments)
        elif name.startswith("pve_network"):
            result = network.handle_tool(name, arguments)
        elif name.startswith("pve_backup") or name.startswith("pve_snapshot"):
            result = backup.handle_tool(name, arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=format_result(result))]

    except Exception as e:
        return [TextContent(type="text", text=format_result({"error": str(e)}))]


def main():
    """Run the MCP server."""
    asyncio.run(run_server())


async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    main()
