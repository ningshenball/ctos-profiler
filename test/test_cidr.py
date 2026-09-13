"""Safety tests for require_small_private."""

import pytest

from scanner.discover import require_small_private


def test_accepts_private_24():
    net = require_small_private("192.168.1.0/24")
    assert str(net) == "192.168.1.0/24"


def test_rejects_too_large():
    with pytest.raises(ValueError, match="max range"):
        require_small_private("192.168.0.0/16")


def test_rejects_public():
    with pytest.raises(ValueError, match="private"):
        require_small_private("8.8.8.0/24")


def test_rejects_junk():
    with pytest.raises(ValueError):
        require_small_private("not-a-cidr")