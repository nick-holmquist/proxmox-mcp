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

## Usage with Docker MCP Gateway (Recommended)

The easiest way to use proxmox-mcp is through Docker Desktop's MCP Gateway.

### Prerequisites

1. Docker Desktop with MCP Toolkit enabled (Settings → Features in development → Enable Docker MCP Toolkit)

### Installation

```bash
# Build the Docker image
docker build -t proxmox-mcp:latest .

# Create a custom catalog (if not already created)
docker mcp catalog create custom-servers

# Add the server to the catalog
docker mcp catalog add custom-servers proxmox-mcp ./proxmox-catalog.yaml

# Enable the server
docker mcp server enable proxmox-mcp

# Set your Proxmox credentials
docker mcp secret set PROXMOX_TOKEN_NAME=your-token-name
docker mcp secret set PROXMOX_TOKEN_VALUE=your-token-value
```

### Configure the connection

```bash
# Set Proxmox configuration
docker mcp config set proxmox.host=https://your-proxmox:8006
docker mcp config set proxmox.user=root@pam
docker mcp config set proxmox.verify_ssl=false
```

### Verify the server is enabled

```bash
docker mcp server ls
```

The server will now be available through the Docker MCP Gateway to any connected client (Claude Code, Cursor, etc.).

## Usage with Claude Code (Direct)

Alternatively, add to your Claude MCP config:

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "python",
      "args": ["-m", "proxmox_mcp.server"],
      "env": {
        "PROXMOX_HOST": "https://your-proxmox:8006",
        "PROXMOX_USER": "root@pam",
        "PROXMOX_TOKEN_NAME": "your-token",
        "PROXMOX_TOKEN_VALUE": "your-secret",
        "PROXMOX_VERIFY_SSL": "false"
      }
    }
  }
}
```

## MCP Conformance

The server declares its real `version` and `instructions` during the
initialize handshake (not the SDK's own version), and every one of the 114
tools sets explicit [tool annotations](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
(`readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint`) - the
SDK's own defaults for an unset annotation are conservative (destructive and
open-world both default `true`), so clients like Claude Code would otherwise
treat every read-only `pve_*_list`/`pve_*_status` tool as if it were
destructive. Tool-handler exceptions are left to propagate rather than being
caught and returned as a "successful" `{"error": ...}` result, so the SDK can
turn them into a spec-conformant `CallToolResult(isError=True)`; unknown tool
names raise a protocol-level `McpError` (`INVALID_PARAMS`) instead.

## Available Tools

114 tools across 10 modules, covering the day-to-day Proxmox VE API surface.
Endpoints intentionally left out: Ceph management, SDN, and interactive
package upgrades (no clean non-interactive task API for the latter).

### Nodes (`src/proxmox_mcp/tools/nodes.py`)
- `pve_node_list` / `pve_node_status` - List nodes / get node status (CPU, memory, uptime)
- `pve_node_disk_list` / `pve_node_disk_smart` - Physical disk inventory and SMART health
- `pve_node_service_list` / `pve_node_service_state` / `pve_node_service_control` - Inspect and start/stop/restart system services (pveproxy, pvedaemon, etc.)
- `pve_node_apt_list_updates` / `pve_node_apt_refresh` - List/refresh available package updates (no unattended upgrade endpoint exists)
- `pve_node_certificates` - List configured TLS certificates
- `pve_node_journal` - Read node syslog/journal entries
- `pve_task_status` / `pve_task_log` - Poll a background task (UPID) for progress/completion, or read its log

### Virtual Machines (`tools/vms.py`)
- Lifecycle: `pve_vm_list`, `pve_vm_status`, `pve_vm_config`, `pve_vm_config_update`, `pve_vm_start`, `pve_vm_stop`, `pve_vm_force_stop`, `pve_vm_restart`, `pve_vm_reset`, `pve_vm_create`, `pve_vm_delete`, `pve_vm_clone`, `pve_vm_migrate`, `pve_vm_convert_to_template`
- Disks: `pve_vm_mount_iso`, `pve_vm_unmount_iso`, `pve_vm_import_disk` (qcow2/raw/vmdk import), `pve_vm_resize_disk`, `pve_vm_move_disk`, `pve_vm_unlink_disk`
- Guest agent: `pve_vm_exec`, `pve_vm_exec_status`, `pve_vm_get_ip`
- Console access: `pve_vm_vnc_ticket`, `pve_vm_spice_ticket`

### Containers / LXC (`tools/containers.py`)
- `pve_container_list`, `pve_container_status`, `pve_container_config`, `pve_container_config_update`, `pve_container_start`, `pve_container_stop`, `pve_container_force_stop`, `pve_container_create`, `pve_container_delete`, `pve_container_clone`, `pve_container_resize_disk`, `pve_container_migrate`

### Storage (`tools/storage.py`)
- `pve_storage_list`, `pve_storage_content`, `pve_storage_config` - Inspect storage pools and their contents
- `pve_storage_create`, `pve_storage_update`, `pve_storage_delete` - Register/reconfigure/remove a storage pool definition
- `pve_storage_enable_import`, `pve_storage_download_url`, `pve_storage_upload` - qcow2/disk-image import support (see below)

### Network (`tools/network.py`)
- `pve_network_list`, `pve_network_vm` - Inspect node interfaces / a VM's network config
- `pve_network_create`, `pve_network_update`, `pve_network_delete`, `pve_network_apply` - Manage bridges/VLANs/bonds (staged until applied)

### Backups & Snapshots (`tools/backup.py`)
- `pve_backup_list`, `pve_backup_create` - One-off backups
- `pve_snapshot_list`, `pve_snapshot_create`, `pve_snapshot_rollback`, `pve_snapshot_delete` - VM/container snapshots

### Access Control (`tools/access.py`)
- Users: `pve_access_user_list`, `pve_access_user_get`, `pve_access_user_create`, `pve_access_user_update`, `pve_access_user_delete`
- Groups: `pve_access_group_list`, `pve_access_group_create`, `pve_access_group_delete`
- Roles: `pve_access_role_list`, `pve_access_role_create`, `pve_access_role_delete`
- ACLs: `pve_access_acl_list`, `pve_access_acl_update`
- API tokens: `pve_access_token_list`, `pve_access_token_create`, `pve_access_token_delete`

### Resource Pools (`tools/pools.py`)
- `pve_pool_list`, `pve_pool_get`, `pve_pool_create`, `pve_pool_update`, `pve_pool_delete`

### Cluster (`tools/cluster.py`)
- `pve_cluster_status`, `pve_cluster_resources` - Cluster membership/quorum and a flat view of all resources
- HA: `pve_ha_group_list`, `pve_ha_group_create`, `pve_ha_group_delete`, `pve_ha_resource_list`, `pve_ha_resource_create`, `pve_ha_resource_update`, `pve_ha_resource_delete`
- Replication: `pve_replication_list`, `pve_replication_create`, `pve_replication_delete`
- Scheduled backup jobs: `pve_backup_job_list`, `pve_backup_job_create`, `pve_backup_job_update`, `pve_backup_job_delete`

### Firewall (`tools/firewall.py`)
Each tool operates at cluster scope by default, node scope if `node` is given, or a specific VM/container's scope if `node`+`vmid` are given:
- `pve_firewall_rule_list`, `pve_firewall_rule_create`, `pve_firewall_rule_update`, `pve_firewall_rule_delete`
- `pve_firewall_options_get`, `pve_firewall_options_update`

## Importing a qcow2 Disk Image

Proxmox converts external disk images (qcow2/raw/vmdk/ova) into a VM disk as a
background task, driven by the `import-from` config option. There is no
single-shot "import a qcow2" API call — it's three steps:

### 1. Enable `import` content on a storage

Only file-based storages support it (`dir`, `nfs`, `cifs`, `btrfs` — not
LVM/ZFS/Ceph):

```
pve_storage_enable_import storage=local
```

### 2. Get the qcow2 file onto that storage

Prefer `pve_storage_download_url` — the Proxmox node fetches the file
server-side, so multi-gigabyte images never pass through the MCP connection:

```
pve_storage_download_url node=pve storage=local url=https://example.com/debian-12-generic-amd64.qcow2 filename=debian12.qcow2 content=import
```

This returns a task UPID immediately; the download continues in the
background. Only use `pve_storage_upload` for small files or when a volume is
mounted directly into the MCP container (the Docker MCP Gateway does not
support volume mounts for custom servers — see project CLAUDE.md).

Poll the task until it completes:

```
pve_task_status node=pve upid=<UPID>
# status: "stopped", exitstatus: "OK" when done
```

### 3. Import the file as a VM disk

```
pve_vm_import_disk node=pve vmid=2001 disk=scsi0 target_storage=local-lvm source_volid=local:import/debian12.qcow2
```

Proxmox runs `qemu-img convert` in a worker task and attaches the result as
`scsi0`. This also returns a UPID — poll it the same way. On success, set the
VM to boot from it:

```
pve_vm_config_update node=pve vmid=2001 boot=order=scsi0
```

**Notes:**
- Absolute filesystem paths (`import-from=/path/to/file.qcow2`) only work for
  the `root@pam` login, not API tokens — always go through storage `import`
  content as shown above.
- The source image is treated as untrusted and validated by Proxmox before
  conversion; a malformed file or one with an external backing file is
  rejected.
- If the import fails, `pve_task_log` shows the worker's output.

## Project VM Workflow

Complete workflow for creating and provisioning project VMs:

### 1. Clone from Template

```
pve_vm_clone node=pve vmid=101 newid=2001 name=myproject-docker
```

### 2. Configure Cloud-init

```
pve_vm_config_update node=pve vmid=2001 ciuser=admin cipassword=password$1 ipconfig0=ip=dhcp
```

### 3. Start VM

```
pve_vm_start node=pve vmid=2001
```

### 4. Get IP Address

```
pve_vm_get_ip node=pve vmid=2001
# Returns: {"interfaces": [{"interface": "eth0", "ip": "10.10.51.125", "prefix": 22}]}
```

### 5. Execute Commands (Install Software)

```
# Run a command
pve_vm_exec node=pve vmid=2001 command="bash -c 'apt-get update'"
# Returns: {"pid": 12345}

# Get output
pve_vm_exec_status node=pve vmid=2001 pid=12345
# Returns: {"exited": 1, "exitcode": 0, "out-data": "..."}
```

### 6. Install Docker Example

```
pve_vm_exec node=pve vmid=2001 command="bash -c 'curl -fsSL https://get.docker.com | sh'"
```

### 7. Mount ISO Image

```
# Mount an ISO to a CD-ROM device
pve_vm_mount_iso node=pve vmid=2001 device=ide2 iso=local:iso/ubuntu-22.04.iso
# Returns: {"status": "mounted", "vmid": 2001, "device": "ide2", "iso": "local:iso/ubuntu-22.04.iso"}

# Mount from NAS storage
pve_vm_mount_iso node=pve vmid=2001 device=scsi1 iso=NAS_ISO:iso/Citrix_CVAD_7.iso

# Eject/unmount the ISO
pve_vm_unmount_iso node=pve vmid=2001 device=ide2
# Returns: {"status": "unmounted", "vmid": 2001, "device": "ide2"}
```

### 8. Cleanup

```
pve_vm_stop node=pve vmid=2001
pve_vm_delete node=pve vmid=2001
```

## Docker MCP Gateway Setup (Detailed)

Since the default `docker-mcp` catalog is managed by Docker, fork it first:

```bash
# Fork the default catalog
docker mcp catalog fork docker-mcp my-catalog

# Add proxmox-mcp to forked catalog
docker mcp catalog add my-catalog proxmox-mcp ./proxmox-catalog.yaml

# Enable the server
docker mcp server enable proxmox-mcp

# Set all required secrets
docker mcp secret set PROXMOX_HOST=https://10.10.1.10:8006
docker mcp secret set PROXMOX_USER=root@pam
docker mcp secret set PROXMOX_TOKEN_NAME=claude
docker mcp secret set PROXMOX_TOKEN_VALUE=your-token-uuid
docker mcp secret set PROXMOX_VERIFY_SSL=false
```

Update Claude Code MCP config to use the forked catalog:

```json
{
  "mcpServers": {
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "stdio", "--catalog", "my-catalog"]
    }
  }
}
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

The default suite (`tests/test_schema.py`, `test_client_smoke.py`,
`test_handlers_smoke.py`, `test_client_construction.py`) never touches a real
Proxmox server - it validates every tool's schema, drives all 114 tools and
all `ProxmoxClient` methods through a fake API object to catch wiring bugs
(typos, bad argument names, dispatch collisions), and checks host/port/env
parsing. It runs in under a second and is safe to run anywhere.

`tests/test_live_smoke.py` makes real, read-only calls (list nodes/VMs/
containers/storage, cluster status) against an actual cluster. It's skipped
unless you opt in:

```bash
RUN_LIVE_PROXMOX_TESTS=1 pytest tests/test_live_smoke.py -v
```

This requires `PROXMOX_HOST`/`PROXMOX_USER`/`PROXMOX_TOKEN_NAME`/
`PROXMOX_TOKEN_VALUE` to be set (`.env` is picked up automatically). Nothing
in it creates, modifies, or deletes anything.

## Security Notes

**Authentication model:** This server authenticates to Proxmox with a single
API token (`PROXMOX_TOKEN_NAME`/`PROXMOX_TOKEN_VALUE`) and passes every tool
call through with whatever privileges that token has - there is no per-tool
authorization inside the MCP server itself.

**Trust boundary:** Anyone who can invoke this MCP's tools (any client
connected to it) can do anything the configured token can do against your
Proxmox cluster, including user/ACL management, firewall rule changes, and
VM/container/storage lifecycle operations. Treat access to this MCP server as
equivalent to holding that Proxmox token directly.

**Least privilege:** Do not point this at a `root@pam` token unless you
specifically need node-level operations `root@pam` alone can grant (e.g. some
absolute-path imports are `root@pam`-only). For most use, create a dedicated
user, assign only the roles/paths it needs via `pve_access_acl_update` (or the
Proxmox UI) and issue an API token from that user instead. The access-control
tools in this MCP (`pve_access_*`) can themselves change permissions - be
deliberate about who can reach them.

**Known non-goals:** No SSO/MFA, no audit logging beyond what Proxmox itself
logs, no rate limiting, and no confirmation prompts before destructive calls
(delete/force-stop/firewall changes) - the calling client is responsible for
confirming intent before invoking a destructive tool.

## License

MIT
