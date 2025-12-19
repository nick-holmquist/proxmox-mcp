"""Storage management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return storage management tools."""
    return [
        Tool(
            name="pve_storage_list",
            description="List all storage pools in the cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Optional: filter by node name",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="pve_storage_content",
            description="List contents of a storage pool (ISOs, templates, backups, disk images)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "storage": {"type": "string", "description": "Storage pool name"},
                },
                "required": ["node", "storage"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle storage tool calls."""
    if name == "pve_storage_list":
        return client.list_storage(arguments.get("node"))
    elif name == "pve_storage_content":
        return client.get_storage_content(arguments["node"], arguments["storage"])
    else:
        raise ValueError(f"Unknown tool: {name}")
