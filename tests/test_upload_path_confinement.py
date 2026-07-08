"""Security regression tests for pve_storage_upload's file_path confinement.

file_path is a caller-controlled argument naming a file on the MCP host's
filesystem. Without confinement it's an arbitrary-file-read primitive (an
MCP tool caller could read this server's own .env, SSH keys, etc. and
exfiltrate them via Proxmox storage). ProxmoxClient.upload_to_storage fails
closed - disabled unless PROXMOX_MCP_UPLOAD_DIR is set - and rejects any
file_path that resolves outside that directory.
"""

from __future__ import annotations

import pytest


def test_upload_disabled_when_upload_dir_unset(mock_client, monkeypatch, tmp_path):
    monkeypatch.delenv("PROXMOX_MCP_UPLOAD_DIR", raising=False)
    f = tmp_path / "test.qcow2"
    f.write_bytes(b"data")
    with pytest.raises(PermissionError):
        mock_client.upload_to_storage("pve", "local", str(f))


def test_upload_allows_file_inside_allowlisted_dir(mock_client, monkeypatch, tmp_path):
    monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(tmp_path))
    f = tmp_path / "test.qcow2"
    f.write_bytes(b"data")
    # Should not raise.
    mock_client.upload_to_storage("pve", "local", str(f))


def test_upload_allows_relative_path_inside_allowlisted_dir(mock_client, monkeypatch, tmp_path):
    monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(tmp_path))
    (tmp_path / "sub").mkdir()
    f = tmp_path / "sub" / "test.qcow2"
    f.write_bytes(b"data")
    mock_client.upload_to_storage("pve", "local", "sub/test.qcow2")


def test_upload_rejects_absolute_path_outside_allowlisted_dir(mock_client, monkeypatch, tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.qcow2"
    outside.write_bytes(b"secret-data")
    monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(allowed))
    with pytest.raises(PermissionError):
        mock_client.upload_to_storage("pve", "local", str(outside))


def test_upload_rejects_traversal_out_of_allowlisted_dir(mock_client, monkeypatch, tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    secret = tmp_path / "secret.env"
    secret.write_bytes(b"PROXMOX_TOKEN_VALUE=leaked")
    monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(allowed))
    with pytest.raises(PermissionError):
        mock_client.upload_to_storage("pve", "local", "../secret.env")


def test_upload_rejects_sibling_directory_with_shared_prefix(mock_client, monkeypatch, tmp_path):
    # A naive `startswith` check (instead of os.path.commonpath) would let
    # "/allowed-evil" pass a check against base "/allowed" since it shares a
    # string prefix. Guard against that regression explicitly.
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    evil = tmp_path / "allowed-evil"
    evil.mkdir()
    f = evil / "test.qcow2"
    f.write_bytes(b"data")
    monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(allowed))
    with pytest.raises(PermissionError):
        mock_client.upload_to_storage("pve", "local", str(f))


def test_upload_missing_file_inside_allowed_dir_raises_file_not_found(mock_client, monkeypatch, tmp_path):
    monkeypatch.setenv("PROXMOX_MCP_UPLOAD_DIR", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        mock_client.upload_to_storage("pve", "local", str(tmp_path / "does-not-exist.qcow2"))
