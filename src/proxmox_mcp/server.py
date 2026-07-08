"""MCP Server for Proxmox VE management."""

import asyncio
import json
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, TextContent, Tool

from .tools import nodes, vms, containers, storage, network, backup, access, pools, cluster, firewall

# Load environment variables
load_dotenv()

try:
    _SERVER_VERSION = _pkg_version("proxmox-mcp")
except PackageNotFoundError:
    _SERVER_VERSION = "0.0.0-dev"

_INSTRUCTIONS = (
    "Manages a Proxmox VE cluster: nodes, VMs, containers, storage, networking, "
    "backups/snapshots, access control, resource pools, HA/cluster, and firewall rules. "
    "Long-running operations (clone, migrate, disk import, scheduled backups) return a "
    "task UPID - poll pve_task_status until status='stopped' and exitstatus=='OK'; use "
    "pve_task_log to see failure detail. Commands run via pve_vm_exec go through the "
    "QEMU guest agent and do not support shell chaining (&&) - run one command at a time "
    "and check pve_vm_exec_status for output."
)

# Create MCP server
server = Server("proxmox-mcp", version=_SERVER_VERSION, instructions=_INSTRUCTIONS)

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
    """Execute a Proxmox tool.

    Unknown tool names are a protocol-level error (JSON-RPC INVALID_PARAMS).
    Exceptions raised by a tool handler are left to propagate: the SDK's
    call_tool decorator catches them and returns a CallToolResult with
    isError=True, which is the spec-conformant way for clients to
    distinguish a failed tool call from a successful one.
    """
    module = _DISPATCH.get(name)
    if module is None:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}"))

    result = module.handle_tool(name, arguments)
    return [TextContent(type="text", text=format_result(result))]


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
