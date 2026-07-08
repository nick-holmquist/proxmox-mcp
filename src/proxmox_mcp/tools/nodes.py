"""Node management tools."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return node management tools."""
    return [
        Tool(
            name="pve_node_list",
            description="List all nodes in the Proxmox cluster with their status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="pve_node_status",
            description="Get detailed status for a specific node (CPU, memory, uptime)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Node name",
                    },
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_task_status",
            description=(
                "Get the status of a background task by its UPID (returned by long-running "
                "operations like disk import, backup, or clone). Check 'status' for "
                "'running'/'stopped' and 'exitstatus' for 'OK' on completion."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "upid": {"type": "string", "description": "Task UPID"},
                },
                "required": ["node", "upid"],
            },
        ),
        Tool(
            name="pve_task_log",
            description="Get the log output of a background task by its UPID (useful for diagnosing a failed disk import)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "upid": {"type": "string", "description": "Task UPID"},
                },
                "required": ["node", "upid"],
            },
        ),
        Tool(
            name="pve_node_disk_list",
            description="List physical disks attached to a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_node_disk_smart",
            description="Get SMART health data for a physical disk",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "disk": {"type": "string", "description": "Device path, e.g. '/dev/sda'"},
                },
                "required": ["node", "disk"],
            },
        ),
        Tool(
            name="pve_node_service_list",
            description="List system services on a node (pveproxy, pvedaemon, pvestatd, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_node_service_state",
            description="Get a system service's current state",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "service": {"type": "string", "description": "Service name, e.g. 'pveproxy'"},
                },
                "required": ["node", "service"],
            },
        ),
        Tool(
            name="pve_node_service_control",
            description="Start, stop, or restart a system service on a node. WARNING: Stopping/restarting core services (pveproxy, pvedaemon) can disrupt cluster management.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "service": {"type": "string", "description": "Service name, e.g. 'pveproxy'"},
                    "action": {"type": "string", "description": "Action to perform", "enum": ["start", "stop", "restart"]},
                },
                "required": ["node", "service", "action"],
            },
        ),
        Tool(
            name="pve_node_apt_list_updates",
            description="List available package updates on a node (from the last refreshed index)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_node_apt_refresh",
            description="Refresh a node's package index (equivalent to 'apt-get update'). Does not install anything.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_node_certificates",
            description="List TLS certificates configured on a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                },
                "required": ["node"],
            },
        ),
        Tool(
            name="pve_node_journal",
            description="Get syslog/journal entries from a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "since": {"type": "integer", "description": "Unix timestamp: only entries after this time"},
                    "until": {"type": "integer", "description": "Unix timestamp: only entries before this time"},
                    "limit": {"type": "integer", "description": "Max number of lines to return"},
                },
                "required": ["node"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle node tool calls."""
    if name == "pve_node_list":
        return client.list_nodes()
    elif name == "pve_node_status":
        return client.get_node_status(arguments["node"])
    elif name == "pve_task_status":
        return client.get_task_status(arguments["node"], arguments["upid"])
    elif name == "pve_task_log":
        return client.get_task_log(arguments["node"], arguments["upid"])
    elif name == "pve_node_disk_list":
        return client.list_disks(arguments["node"])
    elif name == "pve_node_disk_smart":
        return client.get_disk_smart(arguments["node"], arguments["disk"])
    elif name == "pve_node_service_list":
        return client.list_services(arguments["node"])
    elif name == "pve_node_service_state":
        return client.get_service_state(arguments["node"], arguments["service"])
    elif name == "pve_node_service_control":
        node = arguments["node"]
        service = arguments["service"]
        action = arguments["action"]
        if action == "start":
            task = client.start_service(node, service)
        elif action == "stop":
            task = client.stop_service(node, service)
        else:
            task = client.restart_service(node, service)
        return {"task": task}
    elif name == "pve_node_apt_list_updates":
        return client.list_apt_updates(arguments["node"])
    elif name == "pve_node_apt_refresh":
        return {"task": client.refresh_apt_index(arguments["node"])}
    elif name == "pve_node_certificates":
        return client.list_certificates(arguments["node"])
    elif name == "pve_node_journal":
        return client.get_node_journal(
            arguments["node"],
            since=arguments.get("since"),
            until=arguments.get("until"),
            limit=arguments.get("limit"),
        )
    else:
        raise ValueError(f"Unknown tool: {name}")
