"""MCP Server for Proxmox VE management."""

import asyncio
import json
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import nodes, vms, containers, storage, network, backup, access, pools, cluster, firewall

# Load environment variables
load_dotenv()

# Create MCP server
server = Server("proxmox-mcp")

# All tool-providing modules. Dispatch is built from each module's own
# get_tools() output rather than name-prefix guessing, so there's a single
# source of truth for which module owns which tool name.
_MODULES = [nodes, vms, containers, storage, network, backup, access, pools, cluster, firewall]


def _build_dispatch_table() -> dict[str, Any]:
    table: dict[str, Any] = {}
    for module in _MODULES:
        for tool in module.get_tools():
            if tool.name in table:
                raise RuntimeError(f"Duplicate tool name registered: {tool.name}")
            table[tool.name] = module
    return table


_DISPATCH = _build_dispatch_table()


def format_result(data: Any) -> str:
    """Format API result as JSON string."""
    return json.dumps(data, indent=2, default=str)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Proxmox tools."""
    tools = []
    for module in _MODULES:
        tools.extend(module.get_tools())
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Proxmox tool."""
    try:
        module = _DISPATCH.get(name)
        if module is None:
            result = {"error": f"Unknown tool: {name}"}
        else:
            result = module.handle_tool(name, arguments)

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
