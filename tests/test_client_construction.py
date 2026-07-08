"""Tests for ProxmoxClient's lazy API construction: host/port parsing from
PROXMOX_HOST, verify_ssl parsing, and the fail-closed behavior when
credentials are missing (per project security requirements: missing config
must halt startup, not silently proceed with degraded security)."""

from __future__ import annotations

import pytest

import proxmox_mcp.client as client_module
from proxmox_mcp.client import ProxmoxClient


class RecordingProxmoxAPI:
    """Stands in for proxmoxer.ProxmoxAPI and records how it was constructed."""

    last_kwargs: dict | None = None
    last_host: str | None = None

    def __init__(self, host, **kwargs):
        RecordingProxmoxAPI.last_host = host
        RecordingProxmoxAPI.last_kwargs = kwargs


@pytest.fixture
def recording_api(monkeypatch):
    RecordingProxmoxAPI.last_kwargs = None
    RecordingProxmoxAPI.last_host = None
    monkeypatch.setattr(client_module, "ProxmoxAPI", RecordingProxmoxAPI)
    return RecordingProxmoxAPI


def _clear_proxmox_env(monkeypatch):
    for var in ("PROXMOX_HOST", "PROXMOX_USER", "PROXMOX_TOKEN_NAME", "PROXMOX_TOKEN_VALUE", "PROXMOX_VERIFY_SSL"):
        monkeypatch.delenv(var, raising=False)


def test_missing_token_raises_value_error(monkeypatch, recording_api):
    _clear_proxmox_env(monkeypatch)
    c = ProxmoxClient()
    with pytest.raises(ValueError):
        _ = c.api


def test_host_with_scheme_and_no_port(monkeypatch, recording_api):
    _clear_proxmox_env(monkeypatch)
    monkeypatch.setenv("PROXMOX_HOST", "https://10.10.1.10")
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "mcp")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    c = ProxmoxClient()
    _ = c.api
    assert recording_api.last_host == "10.10.1.10"
    assert recording_api.last_kwargs["port"] == 8006


def test_host_with_explicit_port(monkeypatch, recording_api):
    _clear_proxmox_env(monkeypatch)
    monkeypatch.setenv("PROXMOX_HOST", "https://10.10.1.10:8007")
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "mcp")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    c = ProxmoxClient()
    _ = c.api
    assert recording_api.last_host == "10.10.1.10"
    assert recording_api.last_kwargs["port"] == 8007
    assert isinstance(recording_api.last_kwargs["port"], int)


def test_host_defaults_when_unset(monkeypatch, recording_api):
    _clear_proxmox_env(monkeypatch)
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "mcp")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    c = ProxmoxClient()
    _ = c.api
    assert recording_api.last_host == "localhost"
    assert recording_api.last_kwargs["port"] == 8006


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, False),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("true", True),
        ("True", True),
        ("TRUE", True),
    ],
)
def test_verify_ssl_parsing(monkeypatch, recording_api, raw, expected):
    _clear_proxmox_env(monkeypatch)
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "mcp")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    if raw is not None:
        monkeypatch.setenv("PROXMOX_VERIFY_SSL", raw)
    c = ProxmoxClient()
    _ = c.api
    assert recording_api.last_kwargs["verify_ssl"] is expected


def test_default_user_is_root_at_pam(monkeypatch, recording_api):
    _clear_proxmox_env(monkeypatch)
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "mcp")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    c = ProxmoxClient()
    _ = c.api
    assert recording_api.last_kwargs["user"] == "root@pam"


def test_api_is_cached_across_accesses(monkeypatch, recording_api):
    _clear_proxmox_env(monkeypatch)
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "mcp")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    c = ProxmoxClient()
    first = c.api
    second = c.api
    assert first is second
