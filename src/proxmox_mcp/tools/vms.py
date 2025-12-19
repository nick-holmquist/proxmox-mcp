"""Virtual machine management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return VM management tools."""
    return [
        Tool(
            name="pve_vm_list",
            description="List all virtual machines across all nodes",
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
            name="pve_vm_status",
            description="Get detailed status for a specific VM",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_config",
            description="Get configuration for a specific VM",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_start",
            description="Start a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_stop",
            description="Gracefully shutdown a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_force_stop",
            description="Force stop a virtual machine (immediate power off)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_restart",
            description="Restart a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_create",
            description="Create a new virtual machine. WARNING: This creates a new VM.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "name": {"type": "string", "description": "VM name"},
                    "memory": {"type": "integer", "description": "Memory in MB"},
                    "cores": {"type": "integer", "description": "Number of CPU cores"},
                    "sockets": {"type": "integer", "description": "Number of CPU sockets", "default": 1},
                    "ostype": {"type": "string", "description": "OS type (l26, win10, etc.)"},
                    "iso": {"type": "string", "description": "ISO image path (e.g., local:iso/ubuntu.iso)"},
                    "scsi0": {"type": "string", "description": "SCSI disk config"},
                    "net0": {"type": "string", "description": "Network config (e.g., virtio,bridge=vmbr0)"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_delete",
            description="Delete a virtual machine. WARNING: This permanently deletes the VM!",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_clone",
            description="Clone an existing virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "Source VM ID"},
                    "newid": {"type": "integer", "description": "New VM ID"},
                    "name": {"type": "string", "description": "New VM name"},
                    "full": {"type": "boolean", "description": "Full clone (true) or linked clone (false)"},
                    "target": {"type": "string", "description": "Target node (optional)"},
                },
                "required": ["node", "vmid", "newid"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle VM tool calls."""
    if name == "pve_vm_list":
        return client.list_vms(arguments.get("node"))
    elif name == "pve_vm_status":
        return client.get_vm_status(arguments["node"], arguments["vmid"])
    elif name == "pve_vm_config":
        return client.get_vm_config(arguments["node"], arguments["vmid"])
    elif name == "pve_vm_start":
        return {"task": client.start_vm(arguments["node"], arguments["vmid"])}
    elif name == "pve_vm_stop":
        return {"task": client.stop_vm(arguments["node"], arguments["vmid"])}
    elif name == "pve_vm_force_stop":
        return {"task": client.force_stop_vm(arguments["node"], arguments["vmid"])}
    elif name == "pve_vm_restart":
        return {"task": client.restart_vm(arguments["node"], arguments["vmid"])}
    elif name == "pve_vm_create":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        return {"task": client.create_vm(node, vmid, **arguments)}
    elif name == "pve_vm_delete":
        return {"task": client.delete_vm(arguments["node"], arguments["vmid"])}
    elif name == "pve_vm_clone":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        newid = arguments.pop("newid")
        return {"task": client.clone_vm(node, vmid, newid, **arguments)}
    else:
        raise ValueError(f"Unknown tool: {name}")
