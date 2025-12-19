"""Node management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return node management tools."""
    return [
        Tool(
            name="pve_node_list",
            description="List all nodes in the Proxmox cluster with their status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="pve_node_status",
            description="Get detailed status for a specific node (CPU, memory, uptime)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Node name",
                    },
                },
                "required": ["node"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle node tool calls."""
    if name == "pve_node_list":
        return client.list_nodes()
    elif name == "pve_node_status":
        return client.get_node_status(arguments["node"])
    else:
        raise ValueError(f"Unknown tool: {name}")
