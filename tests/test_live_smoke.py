"""Opt-in smoke tests against a real Proxmox server.

These make actual read-only API calls and are skipped by default - they are
not run as part of the normal test suite, CI, or `pytest` with no flags.
To run them against your homelab cluster:

    RUN_LIVE_PROXMOX_TESTS=1 pytest tests/test_live_smoke.py -v

Requires PROXMOX_HOST/PROXMOX_USER/PROXMOX_TOKEN_NAME/PROXMOX_TOKEN_VALUE to
be set (e.g. via a .env file - see .env.example). Every call here is
read-only (list/get); nothing here creates, modifies, or deletes anything.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_PROXMOX_TESTS") != "1",
    reason="Set RUN_LIVE_PROXMOX_TESTS=1 to run tests against a real Proxmox server (see module docstring)",
)


@pytest.fixture(scope="module")
def live_client():
    if not os.environ.get("PROXMOX_TOKEN_NAME") or not os.environ.get("PROXMOX_TOKEN_VALUE"):
        pytest.skip("PROXMOX_TOKEN_NAME/PROXMOX_TOKEN_VALUE not set")
    from proxmox_mcp.client import ProxmoxClient

    return ProxmoxClient()


@pytest.fixture(scope="module")
def first_node(live_client):
    nodes = live_client.list_nodes()
    if not nodes:
        pytest.skip("Cluster reported zero nodes")
    return nodes[0]["node"]


def test_list_nodes(live_client):
    nodes = live_client.list_nodes()
    assert isinstance(nodes, list)
    assert nodes, "expected at least one node"
    assert "node" in nodes[0]


def test_get_node_status(live_client, first_node):
    status = live_client.get_node_status(first_node)
    assert "uptime" in status or "cpu" in status


def test_list_vms(live_client):
    vms = live_client.list_vms()
    assert isinstance(vms, list)
    for vm in vms:
        assert "vmid" in vm
        assert "node" in vm


def test_list_containers(live_client):
    containers = live_client.list_containers()
    assert isinstance(containers, list)
    for ct in containers:
        assert "vmid" in ct


def test_list_storage(live_client):
    storage = live_client.list_storage()
    assert isinstance(storage, list)
    for s in storage:
        assert "storage" in s


def test_get_cluster_status(live_client):
    status = live_client.get_cluster_status()
    assert isinstance(status, list)


def test_get_cluster_resources(live_client):
    resources = live_client.get_cluster_resources()
    assert isinstance(resources, list)


def test_list_pools(live_client):
    pools = live_client.list_pools()
    assert isinstance(pools, list)


def test_list_disks(live_client, first_node):
    disks = live_client.list_disks(first_node)
    assert isinstance(disks, list)


def test_list_services(live_client, first_node):
    services = live_client.list_services(first_node)
    assert isinstance(services, list)
