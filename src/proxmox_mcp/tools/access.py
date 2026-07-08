"""Access control tools: users, groups, roles, ACLs, API tokens."""

from typing import Any

from mcp.types import Tool

from . import _annotations
from ..client import client


def get_tools() -> list[Tool]:
    """Return access control tools."""
    return [
        Tool(
            name="pve_access_user_list",
            annotations=_annotations.READ_ONLY,
            description="List all users",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_access_user_get",
            annotations=_annotations.READ_ONLY,
            description="Get a user's configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID, e.g. 'alice@pve'"},
                },
                "required": ["userid"],
            },
        ),
        Tool(
            name="pve_access_user_create",
            annotations=_annotations.WRITE,
            description="Create a new user. WARNING: Grants access to the Proxmox cluster.",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID including realm, e.g. 'alice@pve'"},
                    "password": {"type": "string", "description": "Password (required for realm=pve users)"},
                    "email": {"type": "string", "description": "Email address"},
                    "firstname": {"type": "string", "description": "First name"},
                    "lastname": {"type": "string", "description": "Last name"},
                    "groups": {"type": "string", "description": "Comma-separated group IDs"},
                    "enable": {"type": "boolean", "description": "Enable the account", "default": True},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["userid"],
            },
        ),
        Tool(
            name="pve_access_user_update",
            annotations=_annotations.IDEMPOTENT_WRITE,
            description="Update a user's configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID"},
                    "email": {"type": "string", "description": "Email address"},
                    "groups": {"type": "string", "description": "Comma-separated group IDs"},
                    "enable": {"type": "boolean", "description": "Enable/disable the account"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["userid"],
            },
        ),
        Tool(
            name="pve_access_user_delete",
            annotations=_annotations.DESTRUCTIVE,
            description="Delete a user. WARNING: Revokes all access for this account.",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID"},
                },
                "required": ["userid"],
            },
        ),
        Tool(
            name="pve_access_group_list",
            annotations=_annotations.READ_ONLY,
            description="List all groups",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_access_group_create",
            annotations=_annotations.WRITE,
            description="Create a new group",
            inputSchema={
                "type": "object",
                "properties": {
                    "groupid": {"type": "string", "description": "Group ID"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["groupid"],
            },
        ),
        Tool(
            name="pve_access_group_delete",
            annotations=_annotations.DESTRUCTIVE,
            description="Delete a group",
            inputSchema={
                "type": "object",
                "properties": {
                    "groupid": {"type": "string", "description": "Group ID"},
                },
                "required": ["groupid"],
            },
        ),
        Tool(
            name="pve_access_role_list",
            annotations=_annotations.READ_ONLY,
            description="List all roles (built-in and custom) with their privileges",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_access_role_create",
            annotations=_annotations.WRITE,
            description="Create a custom role with a specific set of privileges",
            inputSchema={
                "type": "object",
                "properties": {
                    "roleid": {"type": "string", "description": "New role ID"},
                    "privs": {"type": "string", "description": "Comma-separated privileges, e.g. 'VM.Audit,VM.Console'"},
                },
                "required": ["roleid", "privs"],
            },
        ),
        Tool(
            name="pve_access_role_delete",
            annotations=_annotations.DESTRUCTIVE,
            description="Delete a custom role",
            inputSchema={
                "type": "object",
                "properties": {
                    "roleid": {"type": "string", "description": "Role ID"},
                },
                "required": ["roleid"],
            },
        ),
        Tool(
            name="pve_access_acl_list",
            annotations=_annotations.READ_ONLY,
            description="List all ACL entries (which users/groups have which roles on which paths)",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="pve_access_acl_update",
            annotations=_annotations.IDEMPOTENT_WRITE,
            description=(
                "Grant (or revoke, with delete=true) roles to users/groups on a resource path, "
                "e.g. path='/vms/100' or path='/storage/local'. WARNING: Changes access permissions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "ACL path, e.g. '/vms/100', '/storage/local', '/'"},
                    "roles": {"type": "string", "description": "Comma-separated role IDs, e.g. 'PVEVMAdmin'"},
                    "users": {"type": "string", "description": "Comma-separated user IDs"},
                    "groups": {"type": "string", "description": "Comma-separated group IDs"},
                    "propagate": {"type": "boolean", "description": "Propagate to sub-paths", "default": True},
                    "delete": {"type": "boolean", "description": "Revoke instead of grant", "default": False},
                },
                "required": ["path", "roles"],
            },
        ),
        Tool(
            name="pve_access_token_list",
            annotations=_annotations.READ_ONLY,
            description="List API tokens belonging to a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID"},
                },
                "required": ["userid"],
            },
        ),
        Tool(
            name="pve_access_token_create",
            annotations=_annotations.WRITE,
            description=(
                "Create a new API token for a user. WARNING: The returned secret is shown "
                "only once and cannot be retrieved again."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID"},
                    "tokenid": {"type": "string", "description": "Token name, e.g. 'mcp'"},
                    "privsep": {
                        "type": "boolean",
                        "description": "Restrict token to explicitly granted ACLs rather than inheriting the full user's permissions",
                        "default": True,
                    },
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["userid", "tokenid"],
            },
        ),
        Tool(
            name="pve_access_token_delete",
            annotations=_annotations.DESTRUCTIVE,
            description="Delete an API token",
            inputSchema={
                "type": "object",
                "properties": {
                    "userid": {"type": "string", "description": "User ID"},
                    "tokenid": {"type": "string", "description": "Token name"},
                },
                "required": ["userid", "tokenid"],
            },
        ),
    ]


def handle_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Handle access control tool calls."""
    if name == "pve_access_user_list":
        return client.list_users()
    elif name == "pve_access_user_get":
        return client.get_user(arguments["userid"])
    elif name == "pve_access_user_create":
        userid = arguments.pop("userid")
        if "enable" in arguments:
            arguments["enable"] = 1 if arguments.pop("enable") else 0
        client.create_user(userid, **arguments)
        return {"status": "created", "userid": userid}
    elif name == "pve_access_user_update":
        userid = arguments.pop("userid")
        if "enable" in arguments:
            arguments["enable"] = 1 if arguments.pop("enable") else 0
        client.update_user(userid, **arguments)
        return {"status": "updated", "userid": userid}
    elif name == "pve_access_user_delete":
        client.delete_user(arguments["userid"])
        return {"status": "deleted", "userid": arguments["userid"]}
    elif name == "pve_access_group_list":
        return client.list_groups()
    elif name == "pve_access_group_create":
        groupid = arguments.pop("groupid")
        client.create_group(groupid, **arguments)
        return {"status": "created", "groupid": groupid}
    elif name == "pve_access_group_delete":
        client.delete_group(arguments["groupid"])
        return {"status": "deleted", "groupid": arguments["groupid"]}
    elif name == "pve_access_role_list":
        return client.list_roles()
    elif name == "pve_access_role_create":
        client.create_role(arguments["roleid"], arguments["privs"])
        return {"status": "created", "roleid": arguments["roleid"]}
    elif name == "pve_access_role_delete":
        client.delete_role(arguments["roleid"])
        return {"status": "deleted", "roleid": arguments["roleid"]}
    elif name == "pve_access_acl_list":
        return client.list_acl()
    elif name == "pve_access_acl_update":
        client.update_acl(
            arguments["path"],
            arguments["roles"],
            users=arguments.get("users"),
            groups=arguments.get("groups"),
            propagate=arguments.get("propagate", True),
            delete=arguments.get("delete", False),
        )
        return {"status": "updated", "path": arguments["path"]}
    elif name == "pve_access_token_list":
        return client.list_api_tokens(arguments["userid"])
    elif name == "pve_access_token_create":
        return client.create_api_token(
            arguments["userid"],
            arguments["tokenid"],
            privsep=arguments.get("privsep", True),
            comment=arguments.get("comment"),
        )
    elif name == "pve_access_token_delete":
        client.delete_api_token(arguments["userid"], arguments["tokenid"])
        return {"status": "deleted", "userid": arguments["userid"], "tokenid": arguments["tokenid"]}
    else:
        raise ValueError(f"Unknown tool: {name}")
