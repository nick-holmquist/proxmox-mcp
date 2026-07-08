"""Cluster-wide tools: status, resources, HA, replication, scheduled backups."""

from typing import Any

from mcp.types import Tool

from ..client import client


def get_tools() -> list[Tool]:
    """Return cluster management tools."""
    return [
        Tool(
            name="pve_cluster_status",
            description="Get cluster status: member nodes, quorum, and cluster membership info",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_cluster_resources",
            description="Get a flat list of all cluster resources (VMs, containers, storage, nodes) in one call",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Optional: filter by resource type",
                        "enum": ["vm", "storage", "node", "sdn"],
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="pve_ha_group_list",
            description="List High Availability groups",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_ha_group_create",
            description="Create a High Availability group (a set of nodes a resource can run on, with priorities)",
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {"type": "string", "description": "New HA group ID"},
                    "nodes": {"type": "string", "description": "Comma-separated node list, optionally with priority e.g. 'pve1:2,pve2:1'"},
                    "restricted": {"type": "boolean", "description": "Only allow the resource on listed nodes"},
                    "nofailback": {"type": "boolean", "description": "Don't automatically fail back to a higher-priority node"},
                },
                "required": ["group", "nodes"],
            },
        ),
        Tool(
            name="pve_ha_group_delete",
            description="Delete a High Availability group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {"type": "string", "description": "HA group ID"},
                },
                "required": ["group"],
            },
        ),
        Tool(
            name="pve_ha_resource_list",
            description="List VMs/containers currently managed by High Availability",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_ha_resource_create",
            description="Add a VM or container to High Availability management",
            inputSchema={
                "type": "object",
                "properties": {
                    "sid": {"type": "string", "description": "Resource ID, e.g. 'vm:100' or 'ct:200'"},
                    "group": {"type": "string", "description": "HA group to constrain this resource to"},
                    "state": {
                        "type": "string",
                        "description": "Desired HA state",
                        "enum": ["started", "stopped", "enabled", "disabled", "ignored"],
                    },
                    "max_restart": {"type": "integer", "description": "Max restart attempts on failure"},
                },
                "required": ["sid"],
            },
        ),
        Tool(
            name="pve_ha_resource_update",
            description="Update an HA-managed resource's group, state, or restart policy",
            inputSchema={
                "type": "object",
                "properties": {
                    "sid": {"type": "string", "description": "Resource ID, e.g. 'vm:100'"},
                    "group": {"type": "string", "description": "HA group"},
                    "state": {
                        "type": "string",
                        "description": "Desired HA state",
                        "enum": ["started", "stopped", "enabled", "disabled", "ignored"],
                    },
                },
                "required": ["sid"],
            },
        ),
        Tool(
            name="pve_ha_resource_delete",
            description="Remove a VM/container from High Availability management",
            inputSchema={
                "type": "object",
                "properties": {
                    "sid": {"type": "string", "description": "Resource ID, e.g. 'vm:100'"},
                },
                "required": ["sid"],
            },
        ),
        Tool(
            name="pve_replication_list",
            description="List storage replication jobs",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_replication_create",
            description="Create a storage replication job to periodically replicate a VM/container's disks to another node",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Job ID in the form '<vmid>-<n>', e.g. '100-0'"},
                    "target": {"type": "string", "description": "Target node name"},
                    "schedule": {"type": "string", "description": "Schedule, e.g. '*/15'"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["job_id", "target"],
            },
        ),
        Tool(
            name="pve_replication_delete",
            description="Delete a storage replication job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Replication job ID"},
                },
                "required": ["job_id"],
            },
        ),
        Tool(
            name="pve_backup_job_list",
            description="List scheduled backup jobs (vzdump schedules)",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_backup_job_create",
            description="Create a scheduled backup job",
            inputSchema={
                "type": "object",
                "properties": {
                    "schedule": {"type": "string", "description": "Cron-like schedule, e.g. 'sat 22:00'"},
                    "storage": {"type": "string", "description": "Target storage"},
                    "vmid": {"type": "string", "description": "Comma-separated VM/container IDs to include"},
                    "all": {"type": "boolean", "description": "Back up all guests instead of a specific vmid list"},
                    "mode": {
                        "type": "string",
                        "description": "Backup mode",
                        "enum": ["snapshot", "suspend", "stop"],
                        "default": "snapshot",
                    },
                    "compress": {"type": "string", "description": "Compression: 0, gzip, lzo, zstd"},
                    "enabled": {"type": "boolean", "description": "Enable the job", "default": True},
                },
                "required": ["schedule", "storage"],
            },
        ),
        Tool(
            name="pve_backup_job_update",
            description="Update a scheduled backup job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Backup job ID"},
                    "schedule": {"type": "string", "description": "Cron-like schedule"},
                    "storage": {"type": "string", "description": "Target storage"},
                    "enabled": {"type": "boolean", "description": "Enable/disable the job"},
                },
                "required": ["job_id"],
            },
        ),
        Tool(
            name="pve_backup_job_delete",
            description="Delete a scheduled backup job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Backup job ID"},
                },
                "required": ["job_id"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle cluster tool calls."""
    if name == "pve_cluster_status":
        return client.get_cluster_status()
    elif name == "pve_cluster_resources":
        return client.get_cluster_resources(arguments.get("type"))
    elif name == "pve_ha_group_list":
        return client.list_ha_groups()
    elif name == "pve_ha_group_create":
        group = arguments.pop("group")
        nodes = arguments.pop("nodes")
        if "restricted" in arguments:
            arguments["restricted"] = 1 if arguments.pop("restricted") else 0
        if "nofailback" in arguments:
            arguments["nofailback"] = 1 if arguments.pop("nofailback") else 0
        client.create_ha_group(group, nodes, **arguments)
        return {"status": "created", "group": group}
    elif name == "pve_ha_group_delete":
        client.delete_ha_group(arguments["group"])
        return {"status": "deleted", "group": arguments["group"]}
    elif name == "pve_ha_resource_list":
        return client.list_ha_resources()
    elif name == "pve_ha_resource_create":
        sid = arguments.pop("sid")
        client.create_ha_resource(sid, **arguments)
        return {"status": "created", "sid": sid}
    elif name == "pve_ha_resource_update":
        sid = arguments.pop("sid")
        client.update_ha_resource(sid, **arguments)
        return {"status": "updated", "sid": sid}
    elif name == "pve_ha_resource_delete":
        client.delete_ha_resource(arguments["sid"])
        return {"status": "deleted", "sid": arguments["sid"]}
    elif name == "pve_replication_list":
        return client.list_replication_jobs()
    elif name == "pve_replication_create":
        job_id = arguments.pop("job_id")
        target = arguments.pop("target")
        client.create_replication_job(job_id, target, **arguments)
        return {"status": "created", "job_id": job_id}
    elif name == "pve_replication_delete":
        client.delete_replication_job(arguments["job_id"])
        return {"status": "deleted", "job_id": arguments["job_id"]}
    elif name == "pve_backup_job_list":
        return client.list_backup_jobs()
    elif name == "pve_backup_job_create":
        if "all" in arguments:
            arguments["all"] = 1 if arguments.pop("all") else 0
        if "enabled" in arguments:
            arguments["enabled"] = 1 if arguments.pop("enabled") else 0
        return {"task": client.create_backup_job(**arguments)}
    elif name == "pve_backup_job_update":
        job_id = arguments.pop("job_id")
        if "enabled" in arguments:
            arguments["enabled"] = 1 if arguments.pop("enabled") else 0
        client.update_backup_job(job_id, **arguments)
        return {"status": "updated", "job_id": job_id}
    elif name == "pve_backup_job_delete":
        client.delete_backup_job(arguments["job_id"])
        return {"status": "deleted", "job_id": arguments["job_id"]}
    else:
        raise ValueError(f"Unknown tool: {name}")
