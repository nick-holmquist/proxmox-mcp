"""Tests for server.call_tool's MCP-conformance fixes:

- Unknown tool names raise a protocol-level McpError (INVALID_PARAMS) rather
  than being swallowed into a "successful" {"error": ...} result.
- Tool-handler exceptions propagate out of call_tool instead of being caught
  here - the SDK's own @server.call_tool() wrapper is what turns them into a
  CallToolResult(isError=True), per spec. If we caught them ourselves first,
  that mechanism would never fire.
"""

from __future__ import annotations

import pytest
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS

from proxmox_mcp import server


async def test_unknown_tool_raises_mcp_error():
    with pytest.raises(McpError) as exc_info:
        await server.call_tool("pve_totally_made_up_tool", {})
    assert exc_info.value.error.code == INVALID_PARAMS


async def test_known_tool_success_returns_text_content(mock_client):
    result = await server.call_tool("pve_node_list", {})
    assert len(result) == 1
    assert result[0].type == "text"


async def test_handler_exception_propagates(mock_client, monkeypatch):
    def boom(name, arguments):
        raise RuntimeError("simulated Proxmox API failure")

    monkeypatch.setattr(server.nodes, "handle_tool", boom)

    with pytest.raises(RuntimeError, match="simulated Proxmox API failure"):
        await server.call_tool("pve_node_list", {})
