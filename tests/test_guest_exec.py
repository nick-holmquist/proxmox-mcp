"""Regression tests for QEMU guest command argument handling."""

from unittest.mock import Mock

import pytest

from proxmox_mcp.client import ProxmoxClient


@pytest.mark.parametrize(
    ("command", "arguments"),
    [
        ("hostname", ["hostname"]),
        ("df -h", ["df", "-h"]),
        ("""printf '%s' 'two words' "" """, ["printf", "%s", "two words", ""]),
    ],
)
def test_agent_exec_sends_an_argument_list(command, arguments):
    client = ProxmoxClient()
    client._api = api = Mock()
    post = api.nodes.return_value.qemu.return_value.agent.exec.post
    post.return_value = {"pid": 42}

    assert client.agent_exec("pve", 100, command) == {"pid": 42}

    api.nodes.assert_called_once_with("pve")
    api.nodes.return_value.qemu.assert_called_once_with(100)
    post.assert_called_once_with(command=arguments)


@pytest.mark.parametrize("command", ["", "   ", "''", "printf '"])
def test_agent_exec_rejects_invalid_commands_before_contacting_proxmox(command):
    client = ProxmoxClient()
    client._api = api = Mock()

    with pytest.raises(ValueError):
        client.agent_exec("pve", 100, command)

    api.nodes.assert_not_called()
