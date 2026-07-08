"""Static validation of every tool's declared schema - no network, no mocking.

Catches: duplicate tool names across modules, malformed inputSchema shapes,
and `required` fields that don't correspond to a declared property (a classic
copy-paste bug when adding tools).
"""

from __future__ import annotations

from proxmox_mcp.tools import access, backup, cluster, containers, firewall, network, nodes, pools, storage, vms

MODULES = [nodes, vms, containers, storage, network, backup, access, pools, cluster, firewall]


def all_tools():
    for module in MODULES:
        for tool in module.get_tools():
            yield module, tool


def test_no_duplicate_tool_names():
    seen: dict[str, str] = {}
    for module, tool in all_tools():
        assert tool.name not in seen, (
            f"Tool '{tool.name}' is registered by both {seen.get(tool.name)} and {module.__name__}"
        )
        seen[tool.name] = module.__name__
    assert len(seen) > 100, "Expected the full tool surface to be registered"


def test_tool_names_follow_convention():
    for _module, tool in all_tools():
        assert tool.name.startswith("pve_"), f"{tool.name} should start with 'pve_'"
        assert tool.name == tool.name.lower(), f"{tool.name} should be lowercase"
        assert " " not in tool.name


def test_tool_has_description():
    for _module, tool in all_tools():
        assert tool.description and len(tool.description) > 5, f"{tool.name} needs a real description"


def test_schema_shape_is_valid():
    for _module, tool in all_tools():
        schema = tool.inputSchema
        assert schema.get("type") == "object", f"{tool.name}: inputSchema.type must be 'object'"
        assert isinstance(schema.get("properties"), dict), f"{tool.name}: inputSchema.properties must be a dict"
        assert isinstance(schema.get("required", []), list), f"{tool.name}: inputSchema.required must be a list"


def test_required_fields_are_declared_properties():
    for _module, tool in all_tools():
        schema = tool.inputSchema
        props = schema.get("properties", {})
        for field in schema.get("required", []):
            assert field in props, f"{tool.name}: required field '{field}' has no matching property"


def test_every_property_has_type_or_enum():
    for _module, tool in all_tools():
        for prop_name, prop in tool.inputSchema.get("properties", {}).items():
            assert "type" in prop or "enum" in prop, (
                f"{tool.name}.{prop_name}: property must declare a 'type' or 'enum'"
            )


def test_server_dispatch_table_matches_tool_registry():
    # Import here (not at module scope) so a broken server.py surfaces as a
    # clear test failure rather than a collection-time import error.
    from proxmox_mcp import server

    all_names = {tool.name for _module, tool in all_tools()}
    assert set(server._DISPATCH.keys()) == all_names
