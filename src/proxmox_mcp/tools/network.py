"""Network management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return network management tools."""
    return [
        Tool(
            name="pve_network_list",
            description="List network interfaces and bridges on a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_network_vm",
            description="Get network configuration for a specific VM",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle network tool calls."""
    if name == "pve_network_list":
        return client.list_networks(arguments["node"])
    elif name == "pve_network_vm":
        return client.get_vm_network(arguments["node"], arguments["vmid"])
    else:
        raise ValueError(f"Unknown tool: {name}")
