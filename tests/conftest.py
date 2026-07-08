"""Shared fixtures for smoke tests.

These tests never talk to a real Proxmox server. ChainMock stands in for
proxmoxer's ProxmoxAPI: every attribute access and call returns another
ChainMock (so arbitrary chains like `.nodes(node).qemu(vmid).config` work),
except the four HTTP-verb methods (get/post/put/delete), which return a
plain empty dict so code that does `result.get(...)` or iterates the result
behaves like it would against a real (empty) API response.
"""

from __future__ import annotations

import pytest

from proxmox_mcp.client import client as _client


class ChainMock:
    """Stand-in for proxmoxer's fluent resource chain."""

    def __getattr__(self, name: str):
        if name in ("get", "post", "put", "delete"):
            return lambda *args, **kwargs: {}
        return self

    def __call__(self, *args, **kwargs):
        return self


@pytest.fixture
def mock_client():
    """Patch the global ProxmoxClient's underlying API with a ChainMock so
    every client method can be exercised without network access or
    credentials. Restores the original state after the test."""
    original = _client._api
    _client._api = ChainMock()
    try:
        yield _client
    finally:
        _client._api = original
