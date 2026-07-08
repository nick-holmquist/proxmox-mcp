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
        Tool(
            name="pve_container_config_update",
            description="Update container configuration (resources, network, mount points, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                    "memory": {"type": "integer", "description": "Memory in MB"},
                    "cores": {"type": "integer", "description": "CPU cores"},
                    "hostname": {"type": "string", "description": "Container hostname"},
                    "net0": {"type": "string", "description": "Network config (e.g., name=eth0,bridge=vmbr1,ip=dhcp)"},
                    "rootfs": {"type": "string", "description": "Root filesystem config"},
                    "nameserver": {"type": "string", "description": "DNS server"},
                    "searchdomain": {"type": "string", "description": "DNS search domain"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_container_clone",
            description="Clone an existing container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Source container ID"},
                    "newid": {"type": "integer", "description": "New container ID"},
                    "hostname": {"type": "string", "description": "New container hostname"},
                    "full": {"type": "boolean", "description": "Full clone (true) or linked clone (false)"},
                    "target": {"type": "string", "description": "Target node (optional)"},
                },
                "required": ["node", "vmid", "newid"],
            },
        ),
        Tool(
            name="pve_container_resize_disk",
            description="Grow a container's mount point or rootfs. Can only grow, never shrink.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                    "disk": {"type": "string", "description": "Mount point to resize, e.g. 'rootfs', 'mp0'"},
                    "size": {"type": "string", "description": "New size: relative '+10G' or absolute '32G'"},
                },
                "required": ["node", "vmid", "disk", "size"],
            },
        ),
        Tool(
            name="pve_container_migrate",
            description="Migrate a container to another node in the cluster (background task)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Source node name"},
                    "vmid": {"type": "integer", "description": "Container ID"},
                    "target": {"type": "string", "description": "Destination node name"},
                    "restart": {"type": "boolean", "description": "Use restart mode (stop/migrate/start) for a running container", "default": False},
                },
                "required": ["node", "vmid", "target"],
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
    elif name == "pve_container_config_update":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        client.update_container_config(node, vmid, **arguments)
        return {"status": "updated", "vmid": vmid}
    elif name == "pve_container_clone":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        newid = arguments.pop("newid")
        return {"task": client.clone_container(node, vmid, newid, **arguments)}
    elif name == "pve_container_resize_disk":
        return {"task": client.resize_container_disk(arguments["node"], arguments["vmid"], arguments["disk"], arguments["size"])}
    elif name == "pve_container_migrate":
        return {"task": client.migrate_container(
            arguments["node"], arguments["vmid"], arguments["target"], restart=arguments.get("restart", False)
        )}
    else:
        raise ValueError(f"Unknown tool: {name}")
