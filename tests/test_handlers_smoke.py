"""End-to-end smoke test of the tool surface: for every registered tool,
synthesize arguments from its own inputSchema (so this stays correct as
schemas evolve) and drive it through the real dispatch path
(server._DISPATCH -> module.handle_tool -> ProxmoxClient) against a
ChainMock. This is the closest thing to "does calling this tool work" we can
do without a live Proxmox server.
"""

from __future__ import annotations

import pytest

# String values keyed by property name, for the couple of tools whose
# handlers validate input shape before touching the (mocked) API.
NAME_STRING = {
    "node": "pve",
    "disk": "scsi0",
    "device": "ide2",
    "iso": "local:iso/test.iso",
    "storage": "local",
    "type": "dir",  # overridden per-tool below where 'type' means something else
    "target_storage": "local-lvm",
    "source_volid": "local:import/test.qcow2",
    "format": "qcow2",
    "idlist": "unused0",
    "size": "+1G",
    "target": "pve2",
    "iface": "vmbr99",
    "url": "https://example.com/test.qcow2",
    "filename": "test.qcow2",
    "content": "import",
    "upid": "UPID:pve:00000000:00000000:00000000:test::root@pam:",
    "name": "smoke-snap",
    "command": "echo test",
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
    "action": "start",  # overridden to 'ACCEPT' for firewall tools below
    "ostemplate": "local:vztmpl/test.tar.zst",
    "url_source": "https://example.com",
}

NAME_INT = {
    "vmid": 100,
    "newid": 200,
    "pid": 12345,
    "pos": 0,
    "since": 0,
    "until": 0,
    "limit": 10,
}

# Per-tool overrides where a generic name-based guess is wrong (e.g. 'action'
# means a service-control verb in one tool and a firewall verdict in another,
# 'type' means a snapshot's guest type in one tool and a storage backend in
# another).
TOOL_OVERRIDES = {
    "pve_node_service_control": {"action": "start"},
    "pve_firewall_rule_create": {"action": "ACCEPT"},
    "pve_firewall_rule_update": {"action": "ACCEPT"},
    "pve_storage_create": {"type": "dir"},
    "pve_network_create": {"type": "bridge"},
}


def synth_value(tool_name: str, prop_name: str, prop_schema: dict):
    override = TOOL_OVERRIDES.get(tool_name, {}).get(prop_name)
    if override is not None:
        return override
    if "enum" in prop_schema:
        return prop_schema["enum"][0]
    prop_type = prop_schema.get("type")
    if prop_type == "boolean":
        return False
    if prop_type == "integer":
        return NAME_INT.get(prop_name, 1)
    return NAME_STRING.get(prop_name, "test-value")


def build_arguments(tool, tmp_path) -> dict:
    schema = tool.inputSchema
    props = schema.get("properties", {})
    arguments = {}
    for field in schema.get("required", []):
        arguments[field] = synth_value(tool.name, field, props[field])
    if tool.name == "pve_storage_upload":
        f = tmp_path / "test.qcow2"
        f.write_bytes(b"fake-qcow2-contents")
        arguments["file_path"] = str(f)
    return arguments


def all_tool_cases():
    from proxmox_mcp import server

    for module in server._MODULES:
        for tool in module.get_tools():
            yield module, tool


@pytest.mark.parametrize(
    "module,tool", all_tool_cases(), ids=lambda x: x.name if hasattr(x, "name") else x.__name__
)
def test_handle_tool_does_not_raise(mock_client, module, tool, tmp_path, monkeypatch):
    if tool.name == "pve_storage_upload":
        monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(tmp_path))
    arguments = build_arguments(tool, tmp_path)
    module.handle_tool(tool.name, arguments)  # smoke test: must not raise


def test_unknown_tool_raises_value_error(mock_client):
    from proxmox_mcp.tools import nodes

    with pytest.raises(ValueError):
        nodes.handle_tool("pve_totally_made_up_tool", {})
