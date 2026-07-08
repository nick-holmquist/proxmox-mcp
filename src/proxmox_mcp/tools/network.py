"""Network management tools."""

from typing import Any

from mcp.types import Tool

from . import _annotations
from ..client import client


def get_tools() -> list[Tool]:
    """Return network management tools."""
    return [
        Tool(
            name="pve_network_list",
            annotations=_annotations.READ_ONLY,
            description="List network interfaces and bridges on a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_network_vm",
            annotations=_annotations.READ_ONLY,
            description="Get network configuration for a specific VM",
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
            name="pve_network_create",
            annotations=_annotations.WRITE,
            description=(
                "Create a network interface (bridge, VLAN, bond) on a node. "
                "Changes are staged - call pve_network_apply to activate them."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "iface": {"type": "string", "description": "Interface name, e.g. 'vmbr1'"},
                    "type": {
                        "type": "string",
                        "description": "Interface type",
                        "enum": ["bridge", "bond", "vlan", "eth"],
                    },
                    "bridge_ports": {"type": "string", "description": "Physical ports for a bridge, e.g. 'eth1'"},
                    "cidr": {"type": "string", "description": "IPv4 CIDR, e.g. '10.10.1.1/24'"},
                    "gateway": {"type": "string", "description": "IPv4 gateway"},
                    "autostart": {"type": "boolean", "description": "Start interface at boot", "default": True},
                    "comments": {"type": "string", "description": "Optional comment"},
                },
                "required": ["node", "iface", "type"],
            },
        ),
        Tool(
            name="pve_network_update",
            annotations=_annotations.IDEMPOTENT_WRITE,
            description="Update a network interface's configuration. Staged - call pve_network_apply to activate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "iface": {"type": "string", "description": "Interface name"},
                    "bridge_ports": {"type": "string", "description": "Physical ports for a bridge"},
                    "cidr": {"type": "string", "description": "IPv4 CIDR"},
                    "gateway": {"type": "string", "description": "IPv4 gateway"},
                    "autostart": {"type": "boolean", "description": "Start interface at boot"},
                    "comments": {"type": "string", "description": "Optional comment"},
                },
                "required": ["node", "iface"],
            },
        ),
        Tool(
            name="pve_network_delete",
            annotations=_annotations.DESTRUCTIVE,
            description="Delete a network interface. Staged - call pve_network_apply to activate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "iface": {"type": "string", "description": "Interface name"},
                },
                "required": ["node", "iface"],
            },
        ),
        Tool(
            name="pve_network_apply",
            annotations=_annotations.IDEMPOTENT_WRITE,
            description="Apply pending network changes on a node (reloads networking - can briefly interrupt connectivity)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle network tool calls."""
    if name == "pve_network_list":
        return client.list_networks(arguments["node"])
    elif name == "pve_network_vm":
        return client.get_vm_network(arguments["node"], arguments["vmid"])
    elif name == "pve_network_create":
        node = arguments.pop("node")
        iface = arguments.pop("iface")
        iface_type = arguments.pop("type")
        kwargs = {}
        if "bridge_ports" in arguments:
            kwargs["bridge_ports"] = arguments["bridge_ports"]
        if "cidr" in arguments:
            kwargs["cidr"] = arguments["cidr"]
        if "gateway" in arguments:
            kwargs["gateway"] = arguments["gateway"]
        if "autostart" in arguments:
            kwargs["autostart"] = 1 if arguments["autostart"] else 0
        if "comments" in arguments:
            kwargs["comments"] = arguments["comments"]
        client.create_network(node, iface, iface_type, **kwargs)
        return {"status": "created", "iface": iface, "node": node}
    elif name == "pve_network_update":
        node = arguments.pop("node")
        iface = arguments.pop("iface")
        if "autostart" in arguments:
            arguments["autostart"] = 1 if arguments["autostart"] else 0
        client.update_network(node, iface, **arguments)
        return {"status": "updated", "iface": iface, "node": node}
    elif name == "pve_network_delete":
        client.delete_network(arguments["node"], arguments["iface"])
        return {"status": "deleted", "iface": arguments["iface"], "node": arguments["node"]}
    elif name == "pve_network_apply":
        client.apply_network_config(arguments["node"])
        return {"status": "applied", "node": arguments["node"]}
    else:
        raise ValueError(f"Unknown tool: {name}")
