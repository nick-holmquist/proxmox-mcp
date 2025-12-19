"""Backup and snapshot management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return backup and snapshot management tools."""
    return [
        # Backup tools
        Tool(
            name="pve_backup_list",
            description="List backups in a storage pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "storage": {"type": "string", "description": "Storage pool name"},
                },
                "required": ["node", "storage"],
            },
        ),
        Tool(
            name="pve_backup_create",
            description="Create a backup of a VM or container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM/Container ID"},
                    "storage": {"type": "string", "description": "Target storage pool"},
                    "mode": {
                        "type": "string",
                        "description": "Backup mode: snapshot, suspend, or stop",
                        "enum": ["snapshot", "suspend", "stop"],
                    },
                    "compress": {
                        "type": "string",
                        "description": "Compression: 0 (none), gzip, lzo, zstd",
                    },
                    "notes": {"type": "string", "description": "Backup notes"},
                },
                "required": ["node", "vmid", "storage"],
            },
        ),
        # Snapshot tools
        Tool(
            name="pve_snapshot_list",
            description="List snapshots for a VM or container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM/Container ID"},
                    "type": {
                        "type": "string",
                        "description": "Type: qemu (VM) or lxc (container)",
                        "enum": ["qemu", "lxc"],
                        "default": "qemu",
                    },
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_snapshot_create",
            description="Create a snapshot of a VM or container",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM/Container ID"},
                    "name": {"type": "string", "description": "Snapshot name"},
                    "description": {"type": "string", "description": "Snapshot description"},
                    "type": {
                        "type": "string",
                        "description": "Type: qemu (VM) or lxc (container)",
                        "enum": ["qemu", "lxc"],
                        "default": "qemu",
                    },
                    "vmstate": {
                        "type": "boolean",
                        "description": "Include VM state (RAM) in snapshot",
                    },
                },
                "required": ["node", "vmid", "name"],
            },
        ),
        Tool(
            name="pve_snapshot_rollback",
            description="Rollback to a snapshot. WARNING: This reverts the VM/container to the snapshot state!",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM/Container ID"},
                    "name": {"type": "string", "description": "Snapshot name"},
                    "type": {
                        "type": "string",
                        "description": "Type: qemu (VM) or lxc (container)",
                        "enum": ["qemu", "lxc"],
                        "default": "qemu",
                    },
                },
                "required": ["node", "vmid", "name"],
            },
        ),
        Tool(
            name="pve_snapshot_delete",
            description="Delete a snapshot",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM/Container ID"},
                    "name": {"type": "string", "description": "Snapshot name"},
                    "type": {
                        "type": "string",
                        "description": "Type: qemu (VM) or lxc (container)",
                        "enum": ["qemu", "lxc"],
                        "default": "qemu",
                    },
                },
                "required": ["node", "vmid", "name"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle backup/snapshot tool calls."""
    vm_type = arguments.get("type", "qemu")

    if name == "pve_backup_list":
        return client.list_backups(arguments["node"], arguments["storage"])
    elif name == "pve_backup_create":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        storage = arguments.pop("storage")
        return {"task": client.create_backup(node, vmid, storage, **arguments)}
    elif name == "pve_snapshot_list":
        return client.list_snapshots(arguments["node"], arguments["vmid"], vm_type)
    elif name == "pve_snapshot_create":
        node = arguments["node"]
        vmid = arguments["vmid"]
        snap_name = arguments["name"]
        kwargs = {}
        if "description" in arguments:
            kwargs["description"] = arguments["description"]
        if "vmstate" in arguments:
            kwargs["vmstate"] = arguments["vmstate"]
        return {"task": client.create_snapshot(node, vmid, snap_name, vm_type, **kwargs)}
    elif name == "pve_snapshot_rollback":
        return {"task": client.rollback_snapshot(
            arguments["node"], arguments["vmid"], arguments["name"], vm_type
        )}
    elif name == "pve_snapshot_delete":
        return {"task": client.delete_snapshot(
            arguments["node"], arguments["vmid"], arguments["name"], vm_type
        )}
    else:
        raise ValueError(f"Unknown tool: {name}")
