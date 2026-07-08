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
        Tool(
            name="pve_vm_config_update",
            description="Update VM configuration including cloud-init settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "ciuser": {"type": "string", "description": "Cloud-init: username"},
                    "cipassword": {"type": "string", "description": "Cloud-init: password"},
                    "ipconfig0": {"type": "string", "description": "Cloud-init: IP config (e.g., ip=dhcp or ip=10.0.0.5/24,gw=10.0.0.1)"},
                    "nameserver": {"type": "string", "description": "Cloud-init: DNS server"},
                    "searchdomain": {"type": "string", "description": "Cloud-init: DNS search domain"},
                    "sshkeys": {"type": "string", "description": "Cloud-init: SSH public keys (URL-encoded)"},
                    "net0": {"type": "string", "description": "Network config (e.g., virtio,bridge=vmbr1,tag=50)"},
                    "memory": {"type": "integer", "description": "Memory in MB"},
                    "cores": {"type": "integer", "description": "CPU cores"},
                },
                "required": ["node", "vmid"],
            },
        ),
        Tool(
            name="pve_vm_exec",
            description="Execute a command on a VM via QEMU guest agent. Returns a PID to check status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "command": {"type": "string", "description": "Command to execute (e.g., 'apt-get update')"},
                },
                "required": ["node", "vmid", "command"],
            },
        ),
        Tool(
            name="pve_vm_exec_status",
            description="Get the status and output of a command executed via guest agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "pid": {"type": "integer", "description": "Process ID from pve_vm_exec"},
                },
                "required": ["node", "vmid", "pid"],
            },
        ),
        Tool(
            name="pve_vm_get_ip",
            description="Get IP addresses of a VM via QEMU guest agent",
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
            name="pve_vm_mount_iso",
            description="Mount an ISO image to a VM's CD-ROM drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "device": {
                        "type": "string",
                        "description": "CD-ROM device (e.g., 'ide2', 'scsi1')",
                    },
                    "iso": {
                        "type": "string",
                        "description": "ISO volume ID (e.g., 'local:iso/ubuntu.iso' or 'NAS_ISO:iso/windows.iso')",
                    },
                },
                "required": ["node", "vmid", "device", "iso"],
            },
        ),
        Tool(
            name="pve_vm_unmount_iso",
            description="Unmount/eject the ISO from a VM's CD-ROM drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "device": {
                        "type": "string",
                        "description": "CD-ROM device to eject (e.g., 'ide2', 'scsi1')",
                    },
                },
                "required": ["node", "vmid", "device"],
            },
        ),
        Tool(
            name="pve_vm_import_disk",
            description=(
                "Import an external disk image (qcow2/raw/vmdk) as a new disk on a VM. "
                "The source must already be on the node, referenced as a storage volume "
                "id such as 'local:import/debian.qcow2' (see pve_storage_download_url / "
                "pve_storage_upload to get a file there first, and "
                "pve_storage_enable_import to enable import content on a storage). "
                "Proxmox converts the image into the target storage's native format in "
                "a background task - this returns a UPID; poll it with pve_task_status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID to attach the disk to"},
                    "disk": {
                        "type": "string",
                        "description": "Disk slot to create, e.g. 'scsi0', 'virtio0', 'sata0'",
                    },
                    "target_storage": {"type": "string", "description": "Storage to place the converted disk on"},
                    "source_volid": {
                        "type": "string",
                        "description": "Source volume id, e.g. 'local:import/disk.qcow2'",
                    },
                    "format": {
                        "type": "string",
                        "description": "Optional target disk format override",
                        "enum": ["qcow2", "raw", "vmdk"],
                    },
                },
                "required": ["node", "vmid", "disk", "target_storage", "source_volid"],
            },
        ),
        Tool(
            name="pve_vm_resize_disk",
            description="Grow a VM disk. Disks can only be grown, never shrunk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "disk": {"type": "string", "description": "Disk to resize, e.g. 'scsi0'"},
                    "size": {
                        "type": "string",
                        "description": "New size: relative '+10G' to grow by 10GB, or absolute '32G'",
                    },
                },
                "required": ["node", "vmid", "disk", "size"],
            },
        ),
        Tool(
            name="pve_vm_move_disk",
            description="Move a VM disk to a different storage (background task)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "disk": {"type": "string", "description": "Disk to move, e.g. 'scsi0'"},
                    "storage": {"type": "string", "description": "Destination storage"},
                    "delete": {"type": "boolean", "description": "Delete the source disk after the move", "default": False},
                },
                "required": ["node", "vmid", "disk", "storage"],
            },
        ),
        Tool(
            name="pve_vm_unlink_disk",
            description="Detach one or more unused/orphaned disks from a VM's configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "idlist": {"type": "string", "description": "Comma-separated disk keys, e.g. 'unused0,unused1'"},
                    "force": {"type": "boolean", "description": "Force removal even if referenced", "default": False},
                },
                "required": ["node", "vmid", "idlist"],
            },
        ),
        Tool(
            name="pve_vm_migrate",
            description="Migrate a VM to another node in the cluster (background task)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Source node name"},
                    "vmid": {"type": "integer", "description": "VM ID"},
                    "target": {"type": "string", "description": "Destination node name"},
                    "online": {"type": "boolean", "description": "Live-migrate a running VM", "default": False},
                    "with_local_disks": {"type": "boolean", "description": "Migrate local disks along with the VM", "default": True},
                },
                "required": ["node", "vmid", "target"],
            },
        ),
        Tool(
            name="pve_vm_convert_to_template",
            description="Convert a VM into a template. WARNING: This is irreversible.",
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
            name="pve_vm_reset",
            description="Hard reset a VM (equivalent to pressing the physical reset button)",
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
            name="pve_vm_vnc_ticket",
            description="Create a short-lived VNC console ticket for a VM (for the noVNC web console)",
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
            name="pve_vm_spice_ticket",
            description="Create a short-lived SPICE console ticket for a VM",
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
    elif name == "pve_vm_config_update":
        node = arguments.pop("node")
        vmid = arguments.pop("vmid")
        client.update_vm_config(node, vmid, **arguments)
        return {"status": "updated", "vmid": vmid}
    elif name == "pve_vm_exec":
        return client.agent_exec(arguments["node"], arguments["vmid"], arguments["command"])
    elif name == "pve_vm_exec_status":
        return client.agent_exec_status(arguments["node"], arguments["vmid"], arguments["pid"])
    elif name == "pve_vm_get_ip":
        result = client.agent_network_get_interfaces(arguments["node"], arguments["vmid"])
        # Extract IP addresses from the result
        ips = []
        for iface in result.get("result", []):
            name = iface.get("name", "")
            for addr in iface.get("ip-addresses", []):
                if addr.get("ip-address-type") == "ipv4" and not addr.get("ip-address", "").startswith("127."):
                    ips.append({"interface": name, "ip": addr.get("ip-address"), "prefix": addr.get("prefix")})
        return {"interfaces": ips}
    elif name == "pve_vm_mount_iso":
        return client.mount_iso(
            arguments["node"],
            arguments["vmid"],
            arguments["device"],
            arguments["iso"],
        )
    elif name == "pve_vm_unmount_iso":
        return client.unmount_iso(
            arguments["node"],
            arguments["vmid"],
            arguments["device"],
        )
    elif name == "pve_vm_import_disk":
        upid = client.import_vm_disk(
            arguments["node"],
            arguments["vmid"],
            arguments["disk"],
            arguments["target_storage"],
            arguments["source_volid"],
            format=arguments.get("format"),
        )
        return {"task": upid}
    elif name == "pve_vm_resize_disk":
        client.resize_vm_disk(arguments["node"], arguments["vmid"], arguments["disk"], arguments["size"])
        return {"status": "resized", "vmid": arguments["vmid"], "disk": arguments["disk"], "size": arguments["size"]}
    elif name == "pve_vm_move_disk":
        upid = client.move_vm_disk(
            arguments["node"], arguments["vmid"], arguments["disk"], arguments["storage"],
            delete=arguments.get("delete", False),
        )
        return {"task": upid}
    elif name == "pve_vm_unlink_disk":
        client.unlink_vm_disk(
            arguments["node"], arguments["vmid"], arguments["idlist"], force=arguments.get("force", False)
        )
        return {"status": "unlinked", "vmid": arguments["vmid"], "idlist": arguments["idlist"]}
    elif name == "pve_vm_migrate":
        upid = client.migrate_vm(
            arguments["node"], arguments["vmid"], arguments["target"],
            online=arguments.get("online", False),
            with_local_disks=arguments.get("with_local_disks", True),
        )
        return {"task": upid}
    elif name == "pve_vm_convert_to_template":
        client.convert_vm_to_template(arguments["node"], arguments["vmid"])
        return {"status": "converted", "vmid": arguments["vmid"]}
    elif name == "pve_vm_reset":
        return {"task": client.reset_vm(arguments["node"], arguments["vmid"])}
    elif name == "pve_vm_vnc_ticket":
        return client.get_vm_vnc_ticket(arguments["node"], arguments["vmid"])
    elif name == "pve_vm_spice_ticket":
        return client.get_vm_spice_ticket(arguments["node"], arguments["vmid"])
    else:
        raise ValueError(f"Unknown tool: {name}")
