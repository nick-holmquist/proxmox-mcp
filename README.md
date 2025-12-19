# proxmox-mcp

MCP server for full Proxmox VE management - VMs, containers, storage, backups, networking.

## Installation

```bash
pip install proxmox-mcp
```

## Configuration

Set environment variables:

```bash
export PROXMOX_HOST=https://192.168.1.100:8006
export PROXMOX_USER=root@pam
export PROXMOX_TOKEN_NAME=mcp-token
export PROXMOX_TOKEN_VALUE=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export PROXMOX_VERIFY_SSL=false
```

## Usage with Claude Code

Add to your Claude MCP config:

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "python",
      "args": ["-m", "proxmox_mcp.server"],
      "env": {
        "PROXMOX_HOST": "https://your-proxmox:8006",
        "PROXMOX_TOKEN_NAME": "your-token",
        "PROXMOX_TOKEN_VALUE": "your-secret"
      }
    }
  }
}
```

## Available Tools

### Nodes
- `pve_node_list` - List all cluster nodes
- `pve_node_status` - Get node status (CPU, memory, uptime)

### Virtual Machines
- `pve_vm_list` - List all VMs
- `pve_vm_status` - Get VM status
- `pve_vm_config` - Get VM configuration
- `pve_vm_start` - Start a VM
- `pve_vm_stop` - Graceful shutdown
- `pve_vm_force_stop` - Force power off
- `pve_vm_restart` - Restart VM
- `pve_vm_create` - Create new VM
- `pve_vm_delete` - Delete VM
- `pve_vm_clone` - Clone VM

### Containers (LXC)
- `pve_container_list` - List all containers
- `pve_container_status` - Get container status
- `pve_container_config` - Get container configuration
- `pve_container_start` - Start container
- `pve_container_stop` - Graceful shutdown
- `pve_container_force_stop` - Force stop
- `pve_container_create` - Create new container
- `pve_container_delete` - Delete container

### Storage
- `pve_storage_list` - List storage pools
- `pve_storage_content` - List storage contents

### Network
- `pve_network_list` - List network interfaces
- `pve_network_vm` - Get VM network config

### Backups & Snapshots
- `pve_backup_list` - List backups
- `pve_backup_create` - Create backup
- `pve_snapshot_list` - List snapshots
- `pve_snapshot_create` - Create snapshot
- `pve_snapshot_rollback` - Rollback to snapshot
- `pve_snapshot_delete` - Delete snapshot

## License

MIT
