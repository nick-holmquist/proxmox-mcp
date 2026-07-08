"""Firewall management tools at cluster, node, and VM/container scope."""

from typing import Any

from mcp.types import Tool

from ..client import client

_SCOPE_PROPS = {
    "node": {"type": "string", "description": "Optional: node name (node/VM scope). Omit for cluster-wide rules."},
    "vmid": {"type": "integer", "description": "Optional: VM/container ID (requires node). Omit for cluster or node scope."},
    "vm_type": {
        "type": "string",
        "description": "When vmid is given, whether it's a VM or container",
        "enum": ["qemu", "lxc"],
        "default": "qemu",
    },
}


def get_tools() -> list[Tool]:
    """Return firewall management tools."""
    return [
        Tool(
            name="pve_firewall_rule_list",
            description=(
                "List firewall rules at cluster, node, or VM/container scope. "
                "Omit node+vmid for cluster-wide rules, give node only for node rules, "
                "give node+vmid for a specific VM/container's rules."
            ),
            inputSchema={"type": "object", "properties": dict(_SCOPE_PROPS), "required": []},
        ),
        Tool(
            name="pve_firewall_rule_create",
            description="Create a firewall rule at cluster, node, or VM/container scope. WARNING: Can block network access if misconfigured.",
            inputSchema={
                "type": "object",
                "properties": {
                    **_SCOPE_PROPS,
                    "action": {"type": "string", "description": "Rule action", "enum": ["ACCEPT", "DROP", "REJECT"]},
                    "type": {"type": "string", "description": "Direction", "enum": ["in", "out"]},
                    "source": {"type": "string", "description": "Source address/CIDR/alias"},
                    "dest": {"type": "string", "description": "Destination address/CIDR/alias"},
                    "proto": {"type": "string", "description": "Protocol, e.g. 'tcp', 'udp', 'icmp'"},
                    "dport": {"type": "string", "description": "Destination port(s), e.g. '22' or '8000:9000'"},
                    "enable": {"type": "boolean", "description": "Enable the rule", "default": True},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="pve_firewall_rule_update",
            description="Update a firewall rule by its position index",
            inputSchema={
                "type": "object",
                "properties": {
                    **_SCOPE_PROPS,
                    "pos": {"type": "integer", "description": "Rule position index (from pve_firewall_rule_list)"},
                    "action": {"type": "string", "description": "Rule action", "enum": ["ACCEPT", "DROP", "REJECT"]},
                    "source": {"type": "string", "description": "Source address/CIDR/alias"},
                    "dest": {"type": "string", "description": "Destination address/CIDR/alias"},
                    "dport": {"type": "string", "description": "Destination port(s)"},
                    "enable": {"type": "boolean", "description": "Enable/disable the rule"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["pos"],
            },
        ),
        Tool(
            name="pve_firewall_rule_delete",
            description="Delete a firewall rule by its position index",
            inputSchema={
                "type": "object",
                "properties": {
                    **_SCOPE_PROPS,
                    "pos": {"type": "integer", "description": "Rule position index"},
                },
                "required": ["pos"],
            },
        ),
        Tool(
            name="pve_firewall_options_get",
            description="Get firewall options (enabled state, default input/output policy) at cluster, node, or VM/container scope",
            inputSchema={"type": "object", "properties": dict(_SCOPE_PROPS), "required": []},
        ),
        Tool(
            name="pve_firewall_options_update",
            description="Update firewall options at cluster, node, or VM/container scope. WARNING: Can block network access if misconfigured.",
            inputSchema={
                "type": "object",
                "properties": {
                    **_SCOPE_PROPS,
                    "enable": {"type": "boolean", "description": "Enable/disable the firewall at this scope"},
                    "policy_in": {"type": "string", "description": "Default input policy", "enum": ["ACCEPT", "DROP", "REJECT"]},
                    "policy_out": {"type": "string", "description": "Default output policy", "enum": ["ACCEPT", "DROP", "REJECT"]},
                },
                "required": [],
            },
        ),
    ]


def _scope(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "node": arguments.pop("node", None),
        "vmid": arguments.pop("vmid", None),
        "vm_type": arguments.pop("vm_type", "qemu"),
    }


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle firewall tool calls."""
    arguments = dict(arguments)
    scope = _scope(arguments)

    if name == "pve_firewall_rule_list":
        return client.list_firewall_rules(**scope)
    elif name == "pve_firewall_rule_create":
        action = arguments.pop("action")
        if "enable" in arguments:
            arguments["enable"] = 1 if arguments.pop("enable") else 0
        client.create_firewall_rule(action, **scope, **arguments)
        return {"status": "created"}
    elif name == "pve_firewall_rule_update":
        pos = arguments.pop("pos")
        if "enable" in arguments:
            arguments["enable"] = 1 if arguments.pop("enable") else 0
        client.update_firewall_rule(pos, **scope, **arguments)
        return {"status": "updated", "pos": pos}
    elif name == "pve_firewall_rule_delete":
        pos = arguments.pop("pos")
        client.delete_firewall_rule(pos, **scope)
        return {"status": "deleted", "pos": pos}
    elif name == "pve_firewall_options_get":
        return client.get_firewall_options(**scope)
    elif name == "pve_firewall_options_update":
        if "enable" in arguments:
            arguments["enable"] = 1 if arguments.pop("enable") else 0
        client.update_firewall_options(**scope, **arguments)
        return {"status": "updated"}
    else:
        raise ValueError(f"Unknown tool: {name}")
