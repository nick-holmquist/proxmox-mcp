"""LXC container management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return container management tools."""
    return [
        Tool(
            name="pve_container_list",
            description="List all LXC containers across all nodes",
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
            name="pve_container_status",
            description="Get detailed status for a specific container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_container_config",
            description="Get configuration for a specific container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_container_start",
            description="Start a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_container_stop",
            description="Gracefully shutdown a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_container_force_stop",
            description="Force stop a container (immediate)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_container_create",
            description="Create a new LXC container. WARNING: This creates a new container.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                    "ostemplate": {"type": "string", "description": "Template (e.g., local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst)"},
                    "hostname": {"type": "string", "description": "Container hostname"},
                    "memory": {"type": "integer", "description": "Memory in MB"},
                    "cores": {"type": "integer", "description": "Number of CPU cores"},
                    "rootfs": {"type": "string", "description": "Root filesystem config (e.g., local-lvm:8)"},
                    "net0": {"type": "string", "description": "Network config"},
                    "password": {"type": "string", "description": "Root password"},
                    "ssh_public_keys": {"type": "string", "description": "SSH public keys"},
                    "unprivileged": {"type": "boolean", "description": "Unprivileged container"},
                },
                "required": ["node", "vmid", "ostemplate"],
            },
        ),
        Tool(
            name="pve_container_delete",
            description="Delete a container. WARNING: This permanently deletes the container!",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle container tool calls."""
    if name == "pve_container_list":
        return client.list_containers(arguments.get("node"))
    elif name == "pve_container_status":
        return client.get_container_status(arguments["node"], arguments["vmid"])
    elif name == "pve_container_config":
        return client.get_container_config(arguments["node"], arguments["vmid"])
    elif name == "pve_container_start":
        return {"task": client.start_container(arguments["node"], arguments["vmid"])}
    elif name == "pve_container_stop":
        return {"task": client.stop_container(arguments["node"], arguments["vmid"])}
    elif name == "pve_container_force_stop":
        return {"task": client.force_stop_container(arguments["node"], arguments["vmid"])}
    elif name == "pve_container_create":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        return {"task": client.create_container(node, vmid, **arguments)}
    elif name == "pve_container_delete":
        return {"task": client.delete_container(arguments["node"], arguments["vmid"])}
    else:
        raise ValueError(f"Unknown tool: {name}")
