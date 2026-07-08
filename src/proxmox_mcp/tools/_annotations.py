"""Shared MCP tool-annotation presets (readOnlyHint/destructiveHint/
idempotentHint/openWorldHint). Clients like Claude Code use these hints to
decide things like auto-approval and confirmation UX - see the MCP spec's
Tool Annotations section. All are optional per spec; the SDK's own defaults
for an unset ToolAnnotations are conservative (destructiveHint and
openWorldHint both default to true), so tools that don't set these are
presumed destructive by clients that honor the hints.
"""

from mcp.types import ToolAnnotations

# Pure reads: listing/getting state, never changes anything.
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

# Changes state, but calling it again with the same arguments converges to
# the same end state (start an already-started VM, re-apply the same config).
IDEMPOTENT_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)

# Changes state and creates/consumes something new each call (clone, create,
# issue a ticket) - calling it twice is not equivalent to calling it once.
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)

# Destroys or irreversibly discards something (delete, rollback, convert to
# template, unlink a disk).
DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=False)

# Like WRITE, but the tool's effect isn't confined to the closed Proxmox
# domain - pve_vm_exec runs arbitrary guest commands, so its outcome depends
# on unpredictable guest-OS state.
OPEN_WORLD_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True)
