"""Storage management tools."""

from typing import Any

from mcp.types import Tool

from . import _annotations
from ..client import client


def get_tools() -> list[Tool]:
    """Return storage management tools."""
    return [
        Tool(
            name="pve_storage_list",
            annotations=_annotations.READ_ONLY,
            description="List all storage pools in the cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Optional: filter by node name",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="pve_storage_content",
            annotations=_annotations.READ_ONLY,
            description="List contents of a storage pool (ISOs, templates, backups, disk images)",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "storage": {"type": "string", "description": "Storage pool name"},
                    "content": {
                        "type": "string",
                        "description": "Optional: filter by content type",
                        "enum": ["iso", "vztmpl", "backup", "images", "import", "rootdir", "snippets"],
                    },
                },
                "required": ["node", "storage"],
            },
        ),
        Tool(
            name="pve_storage_config",
            annotations=_annotations.READ_ONLY,
            description="Get the cluster-wide configuration for a storage pool, including enabled content types",
            inputSchema={
                "type": "object",
                "properties": {
                    "storage": {"type": "string", "description": "Storage pool name"},
                },
                "required": ["storage"],
            },
        ),
        Tool(
            name="pve_storage_create",
            annotations=_annotations.WRITE,
            description="Register a new storage pool at the cluster level (e.g. dir, nfs, cifs, lvm, zfspool)",
            inputSchema={
                "type": "object",
                "properties": {
                    "storage": {"type": "string", "description": "New storage pool ID/name"},
                    "type": {
                        "type": "string",
                        "description": "Storage backend type",
                        "enum": ["dir", "nfs", "cifs", "lvm", "lvmthin", "zfspool", "btrfs", "cephfs", "rbd"],
                    },
                    "path": {"type": "string", "description": "Filesystem path (for type=dir/btrfs)"},
                    "server": {"type": "string", "description": "Server address (for type=nfs/cifs)"},
                    "export": {"type": "string", "description": "NFS export path (for type=nfs)"},
                    "share": {"type": "string", "description": "CIFS share name (for type=cifs)"},
                    "content": {"type": "string", "description": "Comma-separated content types, e.g. 'iso,vztmpl,images,import'"},
                    "nodes": {"type": "string", "description": "Comma-separated list of nodes this storage is available on (default: all)"},
                },
                "required": ["storage", "type"],
            },
        ),
        Tool(
            name="pve_storage_update",
            annotations=_annotations.IDEMPOTENT_WRITE,
            description="Update an existing storage pool's configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "storage": {"type": "string", "description": "Storage pool ID"},
                    "content": {"type": "string", "description": "Comma-separated content types"},
                    "nodes": {"type": "string", "description": "Comma-separated list of nodes"},
                    "disable": {"type": "boolean", "description": "Disable this storage"},
                },
                "required": ["storage"],
            },
        ),
        Tool(
            name="pve_storage_delete",
            annotations=_annotations.DESTRUCTIVE,
            description="Remove a storage pool's registration from the cluster. Does not delete the underlying data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "storage": {"type": "string", "description": "Storage pool ID"},
                },
                "required": ["storage"],
            },
        ),
        Tool(
            name="pve_storage_enable_import",
            annotations=_annotations.IDEMPOTENT_WRITE,
            description=(
                "Enable the 'import' content type on a storage so external disk images "
                "(qcow2/raw/vmdk/ova) can be uploaded or downloaded onto it for VM disk "
                "import. Only works on file-based storages (dir, nfs, cifs, btrfs)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "storage": {"type": "string", "description": "Storage pool name"},
                },
                "required": ["storage"],
            },
        ),
        Tool(
            name="pve_storage_download_url",
            annotations=_annotations.WRITE,
            description=(
                "Have the Proxmox node download a file directly from a URL into storage "
                "(server-side fetch - no bytes pass through this MCP connection). This is "
                "the recommended way to import a qcow2 disk image: host it at an "
                "http(s) URL, then call this with content='import'. Returns a task UPID; "
                "poll it with pve_task_status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "storage": {"type": "string", "description": "Target storage (must have the target content type enabled)"},
                    "url": {"type": "string", "description": "Source http(s) URL of the file"},
                    "filename": {"type": "string", "description": "Destination filename, e.g. 'debian12.qcow2'"},
                    "content": {
                        "type": "string",
                        "description": "Content type of the downloaded file",
                        "enum": ["iso", "vztmpl", "import"],
                        "default": "import",
                    },
                    "checksum": {"type": "string", "description": "Optional expected checksum to verify after download"},
                    "checksum_algorithm": {
                        "type": "string",
                        "description": "Algorithm for the checksum (default sha256)",
                        "enum": ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"],
                    },
                    "verify_certificates": {
                        "type": "boolean",
                        "description": "Verify TLS certificates on the source URL (default true)",
                        "default": True,
                    },
                },
                "required": ["node", "storage", "url", "filename"],
            },
        ),
        Tool(
            name="pve_storage_upload",
            annotations=_annotations.WRITE,
            description=(
                "Upload a local file from the MCP host's filesystem to node storage. "
                "The whole file streams through this connection - only practical for "
                "small files or when a volume is mounted into the MCP container. For "
                "large qcow2 images, host them at a URL and use pve_storage_download_url "
                "instead. Returns a task UPID; poll it with pve_task_status. Disabled "
                "unless the server has PROXMOX_MCP_UPLOAD_DIR configured; file_path must "
                "resolve inside that directory."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "storage": {"type": "string", "description": "Target storage (must have the target content type enabled)"},
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file, resolved relative to and confined within PROXMOX_MCP_UPLOAD_DIR",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content type of the uploaded file",
                        "enum": ["iso", "vztmpl", "import"],
                        "default": "import",
                    },
                    "checksum": {"type": "string", "description": "Optional expected checksum to verify after upload"},
                    "checksum_algorithm": {
                        "type": "string",
                        "description": "Algorithm for the checksum (default sha256)",
                        "enum": ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"],
                    },
                },
                "required": ["node", "storage", "file_path"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle storage tool calls."""
    if name == "pve_storage_list":
        return client.list_storage(arguments.get("node"))
    elif name == "pve_storage_content":
        return client.get_storage_content(
            arguments["node"], arguments["storage"], arguments.get("content")
        )
    elif name == "pve_storage_config":
        return client.get_storage_config(arguments["storage"])
    elif name == "pve_storage_create":
        storage = arguments.pop("storage")
        storage_type = arguments.pop("type")
        client.create_storage(storage, storage_type, **arguments)
        return {"status": "created", "storage": storage}
    elif name == "pve_storage_update":
        storage = arguments.pop("storage")
        if "disable" in arguments:
            arguments["disable"] = 1 if arguments.pop("disable") else 0
        client.update_storage(storage, **arguments)
        return {"status": "updated", "storage": storage}
    elif name == "pve_storage_delete":
        client.delete_storage(arguments["storage"])
        return {"status": "deleted", "storage": arguments["storage"]}
    elif name == "pve_storage_enable_import":
        client.enable_storage_import(arguments["storage"])
        return {"status": "enabled", "storage": arguments["storage"], "content": "import"}
    elif name == "pve_storage_download_url":
        upid = client.download_url_to_storage(
            arguments["node"],
            arguments["storage"],
            arguments["url"],
            arguments["filename"],
            content=arguments.get("content", "import"),
            checksum=arguments.get("checksum"),
            checksum_algorithm=arguments.get("checksum_algorithm"),
            verify_certificates=arguments.get("verify_certificates", True),
        )
        return {"task": upid}
    elif name == "pve_storage_upload":
        upid = client.upload_to_storage(
            arguments["node"],
            arguments["storage"],
            arguments["file_path"],
            content=arguments.get("content", "import"),
            checksum=arguments.get("checksum"),
            checksum_algorithm=arguments.get("checksum_algorithm"),
        )
        return {"task": upid}
    else:
        raise ValueError(f"Unknown tool: {name}")
