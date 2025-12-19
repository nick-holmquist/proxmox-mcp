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

    # Storage operations
    def list_storage(self, node: str | None = None) -> list[dict[str, Any]]:
        """List storage pools."""
        if node:
            return self.api.nodes(node).storage.get()
        return self.api.storage.get()

    def get_storage_content(self, node: str, storage: str) -> list[dict[str, Any]]:
        """Get content of a storage pool."""
        return self.api.nodes(node).storage(storage).content.get()

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

    # Network operations
    def list_networks(self, node: str) -> list[dict[str, Any]]:
        """List network interfaces/bridges on a node."""
        return self.api.nodes(node).network.get()

    def get_vm_network(self, node: str, vmid: int) -> dict[str, Any]:
        """Get network configuration for a VM."""
        config = self.get_vm_config(node, vmid)
        return {k: v for k, v in config.items() if k.startswith("net")}


# Global client instance
client = ProxmoxClient()
