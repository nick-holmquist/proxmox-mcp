"""Smoke-test every public ProxmoxClient method by calling it with plausible
arguments against a ChainMock instead of a real Proxmox server.

This doesn't verify the API paths are *correct* (ChainMock accepts any
chain), but it does catch real Python bugs in the wiring: typos referencing
undefined names, wrong argument counts, kwargs that collide with positional
params, etc. New client methods are picked up automatically via
`inspect.signature` - add a value to ARG_VALUES if a new parameter name
needs a specific synthetic value.
"""

from __future__ import annotations

import inspect

import pytest

from proxmox_mcp.client import ProxmoxClient

# Synthetic values keyed by parameter name. Chosen to satisfy the handful of
# client methods that validate their own arguments before touching the API
# (e.g. download_url_to_storage checks the URL scheme).
ARG_VALUES = {
    "node": "pve",
    "vmid": 100,
    "newid": 200,
    "disk": "scsi0",
    "device": "ide2",
    "iso": "local:iso/test.iso",
    "storage": "local",
    "storage_type": "dir",
    "target_storage": "local-lvm",
    "source_volid": "local:import/test.qcow2",
    "format": "qcow2",
    "idlist": "unused0",
    "size": "+1G",
    "target": "pve2",
    "iface": "vmbr99",
    "iface_type": "bridge",
    "url": "https://example.com/test.qcow2",
    "filename": "test.qcow2",
    "content": "import",
    "checksum": None,
    "checksum_algorithm": None,
    "verify_certificates": True,
    "upid": "UPID:pve:00000000:00000000:00000000:test::root@pam:",
    "vm_type": "qemu",
    "name": "smoke-snap",
    "command": "echo test",
    "pid": 12345,
    "userid": "smoketest@pve",
    "tokenid": "smoketest",
    "groupid": "smoketestgroup",
    "roleid": "SmokeTestRole",
    "privs": "VM.Audit",
    "poolid": "smoketestpool",
    "sid": "vm:100",
    "path": "/vms/100",
    "roles": "PVEVMAdmin",
    "job_id": "100-0",
    "group": "smoketestgroup",
    "nodes": "pve",
    "service": "pveproxy",
    "action": "ACCEPT",
    "pos": 0,
    "resource_type": "vm",
    "comment": "smoke test",
    "restart": False,
    "delete": False,
    "online": False,
    "with_local_disks": False,
    "privsep": True,
    "since": None,
    "until": None,
    "limit": None,
    "vms": None,
    "propagate": True,
    "file_path": None,  # overridden per-test with a real temp file path
}

# Methods that aren't plain API wiring and don't belong in this generic sweep.
SKIP_METHODS = {"__init__"}


def _client_methods():
    for name, member in inspect.getmembers(ProxmoxClient, predicate=inspect.isfunction):
        if name.startswith("_") or name in SKIP_METHODS:
            continue
        yield name, member


def _build_args(method) -> dict:
    sig = inspect.signature(method)
    args = {}
    for pname, param in sig.parameters.items():
        if pname == "self" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.default is not param.empty:
            continue  # optional - let the method's own default apply
        assert pname in ARG_VALUES, (
            f"No synthetic value registered for required parameter '{pname}' "
            f"in {method.__qualname__} - add one to ARG_VALUES in test_client_smoke.py"
        )
        args[pname] = ARG_VALUES[pname]
    return args


@pytest.mark.parametrize("method_name", [name for name, _ in _client_methods()])
def test_client_method_does_not_raise(mock_client, method_name, tmp_path):
    method = getattr(ProxmoxClient, method_name)
    kwargs = _build_args(method)

    if method_name == "upload_to_storage":
        f = tmp_path / "test.qcow2"
        f.write_bytes(b"fake-qcow2-contents")
        kwargs["file_path"] = str(f)

    bound = getattr(mock_client, method_name)
    bound(**kwargs)
