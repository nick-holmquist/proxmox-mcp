"""Proxmox API client wrapper."""

from __future__ import annotations

import os
from typing import Any

from proxmoxer import ProxmoxAPI


class ProxmoxClient:
    """Wrapper around proxmoxer for Proxmox VE API access."""

    def __init__(self):
        self._api: ProxmoxAPI | None = None

    @property
    def api(self) -> ProxmoxAPI:
        """Lazy-load the Proxmox API connection."""
        if self._api is None:
            host = os.environ.get("PROXMOX_HOST", "https://localhost:8006")
            # Remove https:// prefix if present
            host = host.replace("https://", "").replace("http://", "")
            # Remove port if present in host
            if ":" in host:
                host, port = host.rsplit(":", 1)
                port = int(port)
            else:
                port = 8006

            user = os.environ.get("PROXMOX_USER", "root@pam")
            token_name = os.environ.get("PROXMOX_TOKEN_NAME")
            token_value = os.environ.get("PROXMOX_TOKEN_VALUE")
            verify_ssl = os.environ.get("PROXMOX_VERIFY_SSL", "false").lower() == "true"

            if token_name and token_value:
                self._api = ProxmoxAPI(
                    host,
                    port=port,
                    user=user,
                    token_name=token_name,
                    token_value=token_value,
                    verify_ssl=verify_ssl,
                )
            else:
                raise ValueError(
                    "PROXMOX_TOKEN_NAME and PROXMOX_TOKEN_VALUE environment variables required"
                )

        return self._api

    # Node operations
    def list_nodes(self) -> list[dict[str, Any]]:
        """List all nodes in the cluster."""
        return self.api.nodes.get()

    def get_node_status(self, node: str) -> dict[str, Any]:
        """Get detailed status for a node."""
        return self.api.nodes(node).status.get()

    def list_disks(self, node: str) -> list[dict[str, Any]]:
        """List physical disks attached to a node."""
        return self.api.nodes(node).disks.list.get()

    def get_disk_smart(self, node: str, disk: str) -> dict[str, Any]:
        """Get SMART health data for a physical disk (disk is the device path, e.g. '/dev/sda')."""
        return self.api.nodes(node).disks.smart.get(disk=disk)

    def list_services(self, node: str) -> list[dict[str, Any]]:
        """List system services on a node (pveproxy, pvedaemon, etc.)."""
        return self.api.nodes(node).services.get()

    def get_service_state(self, node: str, service: str) -> dict[str, Any]:
        """Get a system service's current state."""
        return self.api.nodes(node).services(service).state.get()

    def start_service(self, node: str, service: str) -> str:
        """Start a system service."""
        return self.api.nodes(node).services(service).start.post()

    def stop_service(self, node: str, service: str) -> str:
        """Stop a system service."""
        return self.api.nodes(node).services(service).stop.post()

    def restart_service(self, node: str, service: str) -> str:
        """Restart a system service."""
        return self.api.nodes(node).services(service).restart.post()

    def list_apt_updates(self, node: str) -> list[dict[str, Any]]:
        """List available package updates (from the last refreshed index)."""
        return self.api.nodes(node).apt.update.get()

    def refresh_apt_index(self, node: str) -> str:
        """Refresh the node's package index (like 'apt-get update'). Runs as
        a background task; does not install anything."""
        return self.api.nodes(node).apt.update.post()

    def list_certificates(self, node: str) -> list[dict[str, Any]]:
        """List TLS certificates configured on a node."""
        return self.api.nodes(node).certificates.info.get()

    def get_node_journal(
        self, node: str, since: int | None = None, until: int | None = None, limit: int | None = None
    ) -> list[str]:
        """Get syslog/journal entries from a node. since/until are unix
        timestamps; limit caps the number of lines returned."""
        kwargs: dict[str, Any] = {}
        if since is not None:
            kwargs["since"] = since
        if until is not None:
            kwargs["until"] = until
        if limit is not None:
            kwargs["limit"] = limit
        return self.api.nodes(node).journal.get(**kwargs)

    # VM operations
    def list_vms(self, node: str | None = None) -> list[dict[str, Any]]:
        """List all VMs, optionally filtered by node."""
        vms = []
        nodes = [node] if node else [n["node"] for n in self.list_nodes()]
        for n in nodes:
            for vm in self.api.nodes(n).qemu.get():
                vm["node"] = n
                vms.append(vm)
        return vms

    def get_vm_status(self, node: str, vmid: int) -> dict[str, Any]:
        """Get detailed status for a VM."""
        return self.api.nodes(node).qemu(vmid).status.current.get()

    def get_vm_config(self, node: str, vmid: int) -> dict[str, Any]:
        """Get VM configuration."""
        return self.api.nodes(node).qemu(vmid).config.get()

    def update_vm_config(self, node: str, vmid: int, **kwargs) -> None:
        """Update VM configuration."""
        return self.api.nodes(node).qemu(vmid).config.put(**kwargs)

    def start_vm(self, node: str, vmid: int) -> str:
        """Start a VM."""
        return self.api.nodes(node).qemu(vmid).status.start.post()

    def stop_vm(self, node: str, vmid: int) -> str:
        """Stop a VM (graceful shutdown)."""
        return self.api.nodes(node).qemu(vmid).status.shutdown.post()

    def force_stop_vm(self, node: str, vmid: int) -> str:
        """Force stop a VM."""
        return self.api.nodes(node).qemu(vmid).status.stop.post()

    def restart_vm(self, node: str, vmid: int) -> str:
        """Restart a VM."""
        return self.api.nodes(node).qemu(vmid).status.reboot.post()

    def create_vm(self, node: str, vmid: int, **kwargs) -> str:
        """Create a new VM."""
        return self.api.nodes(node).qemu.post(vmid=vmid, **kwargs)

    def delete_vm(self, node: str, vmid: int) -> str:
        """Delete a VM."""
        return self.api.nodes(node).qemu(vmid).delete()

    def clone_vm(self, node: str, vmid: int, newid: int, **kwargs) -> str:
        """Clone a VM."""
        return self.api.nodes(node).qemu(vmid).clone.post(newid=newid, **kwargs)

    def mount_iso(self, node: str, vmid: int, device: str, iso: str) -> dict[str, Any]:
        """Mount an ISO image to a VM's CD-ROM drive.

        Args:
            node: Node name (e.g., 'pve')
            vmid: VM ID
            device: CD-ROM device (e.g., 'ide2', 'scsi1')
            iso: ISO volume ID (e.g., 'local:iso/ubuntu.iso')

        Returns:
            Status dict with device and mounted ISO info
        """
        # Format: device=iso,media=cdrom
        config_value = f"{iso},media=cdrom"
        self.api.nodes(node).qemu(vmid).config.put(**{device: config_value})
        return {"status": "mounted", "vmid": vmid, "device": device, "iso": iso}

    def unmount_iso(self, node: str, vmid: int, device: str) -> dict[str, Any]:
        """Unmount/eject the ISO from a VM's CD-ROM drive.

        Args:
            node: Node name (e.g., 'pve')
            vmid: VM ID
            device: CD-ROM device (e.g., 'ide2', 'scsi1')

        Returns:
            Status dict with device info
        """
        # Format: device=none,media=cdrom (empty CD-ROM)
        config_value = "none,media=cdrom"
        self.api.nodes(node).qemu(vmid).config.put(**{device: config_value})
        return {"status": "unmounted", "vmid": vmid, "device": device}

    def import_vm_disk(
        self,
        node: str,
        vmid: int,
        disk: str,
        target_storage: str,
        source_volid: str,
        format: str | None = None,
    ) -> str:
        """Import an external disk image (qcow2/raw/vmdk) as a new VM disk.

        The source must already be reachable on the node: either a volume in a
        storage's 'import' content (e.g. 'local:import/debian.qcow2', see
        enable_storage_import/download_url_to_storage/upload_to_storage) or an
        OVA member path. Conversion runs asynchronously in a Proxmox worker
        task, so this uses the async config endpoint (POST, not PUT) and
        returns a UPID - poll it with get_task_status.

        Args:
            node: Node name
            vmid: VM ID to attach the imported disk to
            disk: Disk slot to create, e.g. 'scsi0', 'virtio0'
            target_storage: Storage to place the converted disk on
            source_volid: Source volume ID, e.g. 'local:import/disk.qcow2'
            format: Optional target format override (qcow2, raw, vmdk)
        """
        value = f"{target_storage}:0,import-from={source_volid}"
        if format:
            value += f",format={format}"
        return self.api.nodes(node).qemu(vmid).config.post(**{disk: value})

    def resize_vm_disk(self, node: str, vmid: int, disk: str, size: str) -> None:
        """Grow a VM disk. size uses Proxmox's relative/absolute syntax, e.g.
        '+10G' to grow by 10GB or '32G' for an absolute size. Disks can only
        be grown, never shrunk, via this API."""
        return self.api.nodes(node).qemu(vmid).resize.put(disk=disk, size=size)

    def move_vm_disk(
        self, node: str, vmid: int, disk: str, storage: str, delete: bool = False
    ) -> str:
        """Move a VM disk to a different storage. Runs as a background task."""
        return self.api.nodes(node).qemu(vmid).move_disk.post(
            disk=disk, storage=storage, delete=1 if delete else 0
        )

    def unlink_vm_disk(self, node: str, vmid: int, idlist: str, force: bool = False) -> None:
        """Detach one or more unused/orphaned disks from a VM config.
        idlist is a comma-separated list of disk keys, e.g. 'unused0,unused1'."""
        return self.api.nodes(node).qemu(vmid).unlink.put(idlist=idlist, force=1 if force else 0)

    def migrate_vm(
        self,
        node: str,
        vmid: int,
        target: str,
        online: bool = False,
        with_local_disks: bool = True,
    ) -> str:
        """Migrate a VM to another node. Runs as a background task."""
        return self.api.nodes(node).qemu(vmid).migrate.post(
            target=target,
            online=1 if online else 0,
            **{"with-local-disks": 1 if with_local_disks else 0},
        )

    def convert_vm_to_template(self, node: str, vmid: int) -> None:
        """Convert a VM into a template. This is irreversible."""
        return self.api.nodes(node).qemu(vmid).template.post()

    def reset_vm(self, node: str, vmid: int) -> str:
        """Hard reset a VM (like pressing the reset button)."""
        return self.api.nodes(node).qemu(vmid).status.reset.post()

    def get_vm_vnc_ticket(self, node: str, vmid: int) -> dict[str, Any]:
        """Create a VNC console ticket for a VM (short-lived credentials for
        the noVNC web console)."""
        return self.api.nodes(node).qemu(vmid).vncproxy.post()

    def get_vm_spice_ticket(self, node: str, vmid: int) -> dict[str, Any]:
        """Create a SPICE console ticket for a VM."""
        return self.api.nodes(node).qemu(vmid).spiceproxy.post()

    # Container operations
    def list_containers(self, node: str | None = None) -> list[dict[str, Any]]:
        """List all LXC containers, optionally filtered by node."""
        containers = []
        nodes = [node] if node else [n["node"] for n in self.list_nodes()]
        for n in nodes:
            for ct in self.api.nodes(n).lxc.get():
                ct["node"] = n
                containers.append(ct)
        return containers

    def get_container_status(self, node: str, vmid: int) -> dict[str, Any]:
        """Get detailed status for a container."""
        return self.api.nodes(node).lxc(vmid).status.current.get()

    def get_container_config(self, node: str, vmid: int) -> dict[str, Any]:
        """Get container configuration."""
        return self.api.nodes(node).lxc(vmid).config.get()

    def start_container(self, node: str, vmid: int) -> str:
        """Start a container."""
        return self.api.nodes(node).lxc(vmid).status.start.post()

    def stop_container(self, node: str, vmid: int) -> str:
        """Stop a container."""
        return self.api.nodes(node).lxc(vmid).status.shutdown.post()

    def force_stop_container(self, node: str, vmid: int) -> str:
        """Force stop a container."""
        return self.api.nodes(node).lxc(vmid).status.stop.post()

    def create_container(self, node: str, vmid: int, **kwargs) -> str:
        """Create a new container."""
        return self.api.nodes(node).lxc.post(vmid=vmid, **kwargs)

    def delete_container(self, node: str, vmid: int) -> str:
        """Delete a container."""
        return self.api.nodes(node).lxc(vmid).delete()

    def update_container_config(self, node: str, vmid: int, **kwargs) -> None:
        """Update container configuration."""
        return self.api.nodes(node).lxc(vmid).config.put(**kwargs)

    def clone_container(self, node: str, vmid: int, newid: int, **kwargs) -> str:
        """Clone an existing container."""
        return self.api.nodes(node).lxc(vmid).clone.post(newid=newid, **kwargs)

    def resize_container_disk(self, node: str, vmid: int, disk: str, size: str) -> str:
        """Grow a container's mount point/rootfs. size uses relative ('+10G')
        or absolute ('32G') syntax; can only grow, never shrink."""
        return self.api.nodes(node).lxc(vmid).resize.put(disk=disk, size=size)

    def migrate_container(
        self, node: str, vmid: int, target: str, restart: bool = False
    ) -> str:
        """Migrate a container to another node. Runs as a background task."""
        return self.api.nodes(node).lxc(vmid).migrate.post(
            target=target, restart=1 if restart else 0
        )

    # Storage operations
    def list_storage(self, node: str | None = None) -> list[dict[str, Any]]:
        """List storage pools."""
        if node:
            return self.api.nodes(node).storage.get()
        return self.api.storage.get()

    def get_storage_content(
        self, node: str, storage: str, content: str | None = None
    ) -> list[dict[str, Any]]:
        """Get content of a storage pool, optionally filtered by content type
        (e.g. 'iso', 'vztmpl', 'backup', 'images', 'import')."""
        if content:
            return self.api.nodes(node).storage(storage).content.get(content=content)
        return self.api.nodes(node).storage(storage).content.get()

    def get_storage_config(self, storage: str) -> dict[str, Any]:
        """Get the cluster-wide configuration for a storage pool."""
        return self.api.storage(storage).get()

    def create_storage(self, storage: str, storage_type: str, **kwargs) -> None:
        """Register a new storage pool at the cluster level, e.g. type='dir'
        with path=, or type='nfs' with server=/export=."""
        return self.api.storage.post(storage=storage, type=storage_type, **kwargs)

    def update_storage(self, storage: str, **kwargs) -> None:
        """Update an existing storage pool's configuration."""
        return self.api.storage(storage).put(**kwargs)

    def delete_storage(self, storage: str) -> None:
        """Remove a storage pool definition from the cluster. Does not delete
        the underlying data, only the Proxmox storage registration."""
        return self.api.storage(storage).delete()

    def enable_storage_import(self, storage: str) -> None:
        """Enable the 'import' content type on a storage so qcow2/raw/vmdk/ova
        disk images can be uploaded or downloaded onto it for VM disk import.

        Only file-based storage types (dir, nfs, cifs, btrfs) support 'import'
        content; this call fails on block storage (lvm, zfs, ceph, etc.).
        """
        config = self.get_storage_config(storage)
        existing = {c for c in config.get("content", "").split(",") if c}
        existing.add("import")
        self.api.storage(storage).put(content=",".join(sorted(existing)))

    def download_url_to_storage(
        self,
        node: str,
        storage: str,
        url: str,
        filename: str,
        content: str = "import",
        checksum: str | None = None,
        checksum_algorithm: str | None = None,
        verify_certificates: bool = True,
    ) -> str:
        """Have the Proxmox node fetch a file (ISO, template, or disk image)
        directly from a URL into storage. Runs server-side; bytes never pass
        through the MCP client. Returns a task UPID to poll for completion."""
        if not url.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        kwargs: dict[str, Any] = {
            "content": content,
            "filename": filename,
            "url": url,
            "verify-certificates": 1 if verify_certificates else 0,
        }
        if checksum:
            kwargs["checksum"] = checksum
            kwargs["checksum-algorithm"] = checksum_algorithm or "sha256"
        return self.api.nodes(node).storage(storage)("download-url").post(**kwargs)

    def _resolve_upload_path(self, file_path: str) -> str:
        """Resolve file_path and confine it to the PROXMOX_MCP_UPLOAD_DIR
        allowlisted directory. Fails closed: if that env var isn't set,
        local-file upload is disabled entirely rather than defaulting to
        something permissive (e.g. the whole host filesystem). This exists
        because file_path is caller-controlled - without confinement, an MCP
        tool caller could read arbitrary files the server process can access
        (SSH keys, this server's own .env, etc.) and exfiltrate them into
        Proxmox storage."""
        upload_dir = os.environ.get("PROXMOX_MCP_UPLOAD_DIR")
        if not upload_dir:
            raise PermissionError(
                "Local file upload is disabled: set PROXMOX_MCP_UPLOAD_DIR to an "
                "allowlisted directory to enable pve_storage_upload, or use "
                "pve_storage_download_url instead."
            )
        base = os.path.realpath(upload_dir)
        resolved = os.path.realpath(os.path.join(base, file_path) if not os.path.isabs(file_path) else file_path)
        if os.path.commonpath([base, resolved]) != base:
            raise PermissionError(
                f"file_path must be inside the allowlisted upload directory ({base})"
            )
        return resolved

    def upload_to_storage(
        self,
        node: str,
        storage: str,
        file_path: str,
        content: str = "import",
        checksum: str | None = None,
        checksum_algorithm: str | None = None,
    ) -> str:
        """Upload a local file to node storage via multipart upload. Only use
        for small files or when the MCP process has direct filesystem access
        to the source (e.g. a mounted volume) - the whole file streams through
        this connection before the node moves it into place. For anything
        multi-gigabyte or remote, prefer download_url_to_storage instead.

        file_path must resolve inside PROXMOX_MCP_UPLOAD_DIR (see
        _resolve_upload_path) - this tool is disabled unless that directory
        is configured. Returns a task UPID to poll for completion."""
        resolved_path = self._resolve_upload_path(file_path)
        if not os.path.isfile(resolved_path):
            raise FileNotFoundError(f"No such file: {file_path}")
        kwargs: dict[str, Any] = {"content": content}
        if checksum:
            kwargs["checksum"] = checksum
            kwargs["checksum-algorithm"] = checksum_algorithm or "sha256"
        with open(resolved_path, "rb") as fh:
            return self.api.nodes(node).storage(storage).upload.post(
                filename=fh, **kwargs
            )

    # Task operations
    def get_task_status(self, node: str, upid: str) -> dict[str, Any]:
        """Get the status of a running or completed task by its UPID."""
        return self.api.nodes(node).tasks(upid).status.get()

    def get_task_log(self, node: str, upid: str) -> list[dict[str, Any]]:
        """Get the log output of a task by its UPID."""
        return self.api.nodes(node).tasks(upid).log.get()

    # Backup operations
    def list_backups(self, node: str, storage: str) -> list[dict[str, Any]]:
        """List backups in a storage pool."""
        content = self.get_storage_content(node, storage)
        return [item for item in content if item.get("content") == "backup"]

    def create_backup(self, node: str, vmid: int, storage: str, **kwargs) -> str:
        """Create a backup of a VM or container."""
        return self.api.nodes(node).vzdump.post(vmid=vmid, storage=storage, **kwargs)

    # Snapshot operations
    def list_snapshots(self, node: str, vmid: int, vm_type: str = "qemu") -> list[dict[str, Any]]:
        """List snapshots for a VM or container."""
        if vm_type == "qemu":
            return self.api.nodes(node).qemu(vmid).snapshot.get()
        return self.api.nodes(node).lxc(vmid).snapshot.get()

    def create_snapshot(self, node: str, vmid: int, name: str, vm_type: str = "qemu", **kwargs) -> str:
        """Create a snapshot."""
        if vm_type == "qemu":
            return self.api.nodes(node).qemu(vmid).snapshot.post(snapname=name, **kwargs)
        return self.api.nodes(node).lxc(vmid).snapshot.post(snapname=name, **kwargs)

    def rollback_snapshot(self, node: str, vmid: int, name: str, vm_type: str = "qemu") -> str:
        """Rollback to a snapshot."""
        if vm_type == "qemu":
            return self.api.nodes(node).qemu(vmid).snapshot(name).rollback.post()
        return self.api.nodes(node).lxc(vmid).snapshot(name).rollback.post()

    def delete_snapshot(self, node: str, vmid: int, name: str, vm_type: str = "qemu") -> str:
        """Delete a snapshot."""
        if vm_type == "qemu":
            return self.api.nodes(node).qemu(vmid).snapshot(name).delete()
        return self.api.nodes(node).lxc(vmid).snapshot(name).delete()

    # Guest agent operations
    def agent_exec(self, node: str, vmid: int, command: str) -> dict[str, Any]:
        """Execute a command via QEMU guest agent."""
        return self.api.nodes(node).qemu(vmid).agent.exec.post(command=command)

    def agent_exec_status(self, node: str, vmid: int, pid: int) -> dict[str, Any]:
        """Get status of a guest agent command execution."""
        return self.api.nodes(node).qemu(vmid).agent("exec-status").get(pid=pid)

    def agent_network_get_interfaces(self, node: str, vmid: int) -> dict[str, Any]:
        """Get network interfaces from guest agent."""
        return self.api.nodes(node).qemu(vmid).agent("network-get-interfaces").get()

    # Network operations
    def list_networks(self, node: str) -> list[dict[str, Any]]:
        """List network interfaces/bridges on a node."""
        return self.api.nodes(node).network.get()

    def get_vm_network(self, node: str, vmid: int) -> dict[str, Any]:
        """Get network configuration for a VM."""
        config = self.get_vm_config(node, vmid)
        return {k: v for k, v in config.items() if k.startswith("net")}

    # Access control operations
    def list_users(self) -> list[dict[str, Any]]:
        """List all users."""
        return self.api.access.users.get()

    def get_user(self, userid: str) -> dict[str, Any]:
        """Get a user's configuration."""
        return self.api.access.users(userid).get()

    def create_user(self, userid: str, **kwargs) -> None:
        """Create a new user, e.g. userid='alice@pve', password=, email=, groups=."""
        return self.api.access.users.post(userid=userid, **kwargs)

    def update_user(self, userid: str, **kwargs) -> None:
        """Update a user's configuration."""
        return self.api.access.users(userid).put(**kwargs)

    def delete_user(self, userid: str) -> None:
        """Delete a user."""
        return self.api.access.users(userid).delete()

    def list_groups(self) -> list[dict[str, Any]]:
        """List all groups."""
        return self.api.access.groups.get()

    def create_group(self, groupid: str, **kwargs) -> None:
        """Create a new group."""
        return self.api.access.groups.post(groupid=groupid, **kwargs)

    def delete_group(self, groupid: str) -> None:
        """Delete a group."""
        return self.api.access.groups(groupid).delete()

    def list_roles(self) -> list[dict[str, Any]]:
        """List all roles (built-in and custom)."""
        return self.api.access.roles.get()

    def create_role(self, roleid: str, privs: str) -> None:
        """Create a custom role with a comma-separated list of privileges."""
        return self.api.access.roles.post(roleid=roleid, privs=privs)

    def delete_role(self, roleid: str) -> None:
        """Delete a custom role."""
        return self.api.access.roles(roleid).delete()

    def list_acl(self) -> list[dict[str, Any]]:
        """List all ACL entries (permission grants)."""
        return self.api.access.acl.get()

    def update_acl(
        self,
        path: str,
        roles: str,
        users: str | None = None,
        groups: str | None = None,
        propagate: bool = True,
        delete: bool = False,
    ) -> None:
        """Grant (or with delete=True, revoke) roles to users/groups on a path.
        At least one of users or groups is required."""
        kwargs: dict[str, Any] = {
            "path": path,
            "roles": roles,
            "propagate": 1 if propagate else 0,
        }
        if users:
            kwargs["users"] = users
        if groups:
            kwargs["groups"] = groups
        if delete:
            kwargs["delete"] = 1
        return self.api.access.acl.put(**kwargs)

    def list_api_tokens(self, userid: str) -> list[dict[str, Any]]:
        """List API tokens belonging to a user."""
        return self.api.access.users(userid).token.get()

    def create_api_token(
        self, userid: str, tokenid: str, privsep: bool = True, comment: str | None = None
    ) -> dict[str, Any]:
        """Create a new API token for a user. The returned secret value is
        shown only once. privsep=True (default) restricts the token to the
        intersection of the user's and any explicitly-granted ACL entries."""
        kwargs: dict[str, Any] = {"privsep": 1 if privsep else 0}
        if comment:
            kwargs["comment"] = comment
        return self.api.access.users(userid).token(tokenid).post(**kwargs)

    def delete_api_token(self, userid: str, tokenid: str) -> None:
        """Delete an API token."""
        return self.api.access.users(userid).token(tokenid).delete()

    # Resource pool operations
    def list_pools(self) -> list[dict[str, Any]]:
        """List all resource pools."""
        return self.api.pools.get()

    def get_pool(self, poolid: str) -> dict[str, Any]:
        """Get a resource pool's members and configuration."""
        return self.api.pools(poolid).get()

    def create_pool(self, poolid: str, comment: str | None = None) -> None:
        """Create a new resource pool."""
        kwargs: dict[str, Any] = {"poolid": poolid}
        if comment:
            kwargs["comment"] = comment
        return self.api.pools.post(**kwargs)

    def update_pool(
        self,
        poolid: str,
        comment: str | None = None,
        vms: str | None = None,
        storage: str | None = None,
        delete: bool = False,
    ) -> None:
        """Update a resource pool: change its comment or add/remove members.
        vms/storage are comma-separated IDs; delete=True removes the listed
        members instead of adding them."""
        kwargs: dict[str, Any] = {}
        if comment is not None:
            kwargs["comment"] = comment
        if vms:
            kwargs["vms"] = vms
        if storage:
            kwargs["storage"] = storage
        if delete:
            kwargs["delete"] = 1
        return self.api.pools(poolid).put(**kwargs)

    def delete_pool(self, poolid: str) -> None:
        """Delete a resource pool."""
        return self.api.pools(poolid).delete()

    # Cluster operations
    def get_cluster_status(self) -> list[dict[str, Any]]:
        """Get cluster status (nodes, quorum, and cluster membership info)."""
        return self.api.cluster.status.get()

    def get_cluster_resources(self, resource_type: str | None = None) -> list[dict[str, Any]]:
        """Get a flat list of all cluster resources (VMs, storage, nodes),
        optionally filtered by type ('vm', 'storage', 'node', 'sdn')."""
        if resource_type:
            return self.api.cluster.resources.get(type=resource_type)
        return self.api.cluster.resources.get()

    def list_ha_groups(self) -> list[dict[str, Any]]:
        """List HA groups."""
        return self.api.cluster.ha.groups.get()

    def create_ha_group(self, group: str, nodes: str, **kwargs) -> None:
        """Create an HA group. nodes is a comma-separated list, e.g. 'pve1,pve2'."""
        return self.api.cluster.ha.groups.post(group=group, nodes=nodes, **kwargs)

    def delete_ha_group(self, group: str) -> None:
        """Delete an HA group."""
        return self.api.cluster.ha.groups(group).delete()

    def list_ha_resources(self) -> list[dict[str, Any]]:
        """List HA-managed resources (VMs/containers)."""
        return self.api.cluster.ha.resources.get()

    def create_ha_resource(self, sid: str, **kwargs) -> None:
        """Add a VM/container to HA management. sid is e.g. 'vm:100'."""
        return self.api.cluster.ha.resources.post(sid=sid, **kwargs)

    def update_ha_resource(self, sid: str, **kwargs) -> None:
        """Update an HA-managed resource's configuration (group, state, etc.)."""
        return self.api.cluster.ha.resources(sid).put(**kwargs)

    def delete_ha_resource(self, sid: str) -> None:
        """Remove a VM/container from HA management."""
        return self.api.cluster.ha.resources(sid).delete()

    def list_replication_jobs(self) -> list[dict[str, Any]]:
        """List storage replication jobs."""
        return self.api.cluster.replication.get()

    def create_replication_job(self, job_id: str, target: str, **kwargs) -> None:
        """Create a replication job. job_id is '<vmid>-<n>', e.g. '100-0'."""
        return self.api.cluster.replication.post(id=job_id, target=target, **kwargs)

    def delete_replication_job(self, job_id: str) -> None:
        """Delete a replication job."""
        return self.api.cluster.replication(job_id).delete()

    def list_backup_jobs(self) -> list[dict[str, Any]]:
        """List scheduled backup jobs (vzdump jobs)."""
        return self.api.cluster.backup.get()

    def create_backup_job(self, **kwargs) -> str:
        """Create a scheduled backup job, e.g. schedule='sat 22:00', storage=,
        vmid= (comma-separated), mode='snapshot'."""
        return self.api.cluster.backup.post(**kwargs)

    def update_backup_job(self, job_id: str, **kwargs) -> None:
        """Update a scheduled backup job."""
        return self.api.cluster.backup(job_id).put(**kwargs)

    def delete_backup_job(self, job_id: str) -> None:
        """Delete a scheduled backup job."""
        return self.api.cluster.backup(job_id).delete()

    # Firewall operations
    def _firewall_endpoint(
        self, node: str | None = None, vmid: int | None = None, vm_type: str = "qemu"
    ):
        """Resolve the firewall rules endpoint for cluster, node, or VM/container scope."""
        if vmid is not None:
            if node is None:
                raise ValueError("node is required when vmid is given")
            guest = self.api.nodes(node).qemu(vmid) if vm_type == "qemu" else self.api.nodes(node).lxc(vmid)
            return guest.firewall
        if node is not None:
            return self.api.nodes(node).firewall
        return self.api.cluster.firewall

    def list_firewall_rules(
        self, node: str | None = None, vmid: int | None = None, vm_type: str = "qemu"
    ) -> list[dict[str, Any]]:
        """List firewall rules at cluster, node, or VM/container scope."""
        return self._firewall_endpoint(node, vmid, vm_type).rules.get()

    def create_firewall_rule(
        self,
        action: str,
        node: str | None = None,
        vmid: int | None = None,
        vm_type: str = "qemu",
        **kwargs,
    ) -> None:
        """Create a firewall rule. kwargs commonly include type ('in'/'out'),
        source, dest, proto, dport, enable, comment."""
        return self._firewall_endpoint(node, vmid, vm_type).rules.post(action=action, **kwargs)

    def update_firewall_rule(
        self,
        pos: int,
        node: str | None = None,
        vmid: int | None = None,
        vm_type: str = "qemu",
        **kwargs,
    ) -> None:
        """Update a firewall rule by its position index."""
        return self._firewall_endpoint(node, vmid, vm_type).rules(pos).put(**kwargs)

    def delete_firewall_rule(
        self, pos: int, node: str | None = None, vmid: int | None = None, vm_type: str = "qemu"
    ) -> None:
        """Delete a firewall rule by its position index."""
        return self._firewall_endpoint(node, vmid, vm_type).rules(pos).delete()

    def get_firewall_options(
        self, node: str | None = None, vmid: int | None = None, vm_type: str = "qemu"
    ) -> dict[str, Any]:
        """Get firewall options (enable/disable, default policy) at cluster,
        node, or VM/container scope."""
        return self._firewall_endpoint(node, vmid, vm_type).options.get()

    def update_firewall_options(
        self, node: str | None = None, vmid: int | None = None, vm_type: str = "qemu", **kwargs
    ) -> None:
        """Update firewall options, e.g. enable=1, policy_in='DROP'."""
        return self._firewall_endpoint(node, vmid, vm_type).options.put(**kwargs)

    def create_network(self, node: str, iface: str, iface_type: str, **kwargs) -> None:
        """Create a network interface (e.g. a bridge or VLAN) on a node.
        Changes are staged until apply_network_config is called."""
        return self.api.nodes(node).network.post(iface=iface, type=iface_type, **kwargs)

    def update_network(self, node: str, iface: str, **kwargs) -> None:
        """Update a network interface's configuration. Staged until applied."""
        return self.api.nodes(node).network(iface).put(**kwargs)

    def delete_network(self, node: str, iface: str) -> None:
        """Delete a network interface. Staged until applied."""
        return self.api.nodes(node).network(iface).delete()

    def apply_network_config(self, node: str) -> str:
        """Apply pending network changes on a node (reloads networking)."""
        return self.api.nodes(node).network.put()


# Global client instance
client = ProxmoxClient()
