"""Resource pool management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return resource pool management tools."""
    return [
        Tool(
            name="pve_pool_list",
            description="List all resource pools",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_pool_get",
            description="Get a resource pool's members (VMs, containers, storage) and configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "poolid": {"type": "string", "description": "Pool ID"},
                },
                "required": ["poolid"],
            },
        ),
        Tool(
            name="pve_pool_create",
            description="Create a new resource pool, used to group VMs/containers/storage for organization or delegated access",
            inputSchema={
                "type": "object",
                "properties": {
                    "poolid": {"type": "string", "description": "New pool ID"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["poolid"],
            },
        ),
        Tool(
            name="pve_pool_update",
            description="Update a resource pool's comment, or add/remove VM and storage members",
            inputSchema={
                "type": "object",
                "properties": {
                    "poolid": {"type": "string", "description": "Pool ID"},
                    "comment": {"type": "string", "description": "New comment"},
                    "vms": {"type": "string", "description": "Comma-separated VM/container IDs to add or remove"},
                    "storage": {"type": "string", "description": "Comma-separated storage IDs to add or remove"},
                    "delete": {"type": "boolean", "description": "Remove the listed members instead of adding them", "default": False},
                },
                "required": ["poolid"],
            },
        ),
        Tool(
            name="pve_pool_delete",
            description="Delete a resource pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "poolid": {"type": "string", "description": "Pool ID"},
                },
                "required": ["poolid"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle resource pool tool calls."""
    if name == "pve_pool_list":
        return client.list_pools()
    elif name == "pve_pool_get":
        return client.get_pool(arguments["poolid"])
    elif name == "pve_pool_create":
        client.create_pool(arguments["poolid"], comment=arguments.get("comment"))
        return {"status": "created", "poolid": arguments["poolid"]}
    elif name == "pve_pool_update":
        client.update_pool(
            arguments["poolid"],
            comment=arguments.get("comment"),
            vms=arguments.get("vms"),
            storage=arguments.get("storage"),
            delete=arguments.get("delete", False),
        )
        return {"status": "updated", "poolid": arguments["poolid"]}
    elif name == "pve_pool_delete":
        client.delete_pool(arguments["poolid"])
        return {"status": "deleted", "poolid": arguments["poolid"]}
    else:
        raise ValueError(f"Unknown tool: {name}")
