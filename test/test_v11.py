from scanner.discover import os_guess
from scanner.history import annotate


def test_os_guess_windows():
    assert os_guess(128) == "likely Windows"


def test_os_guess_linux():
    assert os_guess(64) == "likely Linux/mac"


def test_os_guess_none():
    assert os_guess(None) == ""


def test_annotate_new_and_changed():
    prev = {
        "hosts": [
            {"ip": "10.0.0.2", "ports": [{"port": 80}], "mac": "AA:AA:AA:AA:AA:AA"},
        ]
    }
    now = [
        {"ip": "10.0.0.2", "ports": [{"port": 80}, {"port": 443}], "mac": "AA:AA:AA:AA:AA:AA"},
        {"ip": "10.0.0.3", "ports": [], "mac": "BB:BB:BB:BB:BB:BB"},
    ]
    out = annotate(now, prev)
    by_ip = {h["ip"]: h for h in out}
    assert by_ip["10.0.0.2"]["flag"] == "changed"
    assert by_ip["10.0.0.3"]["flag"] == "new"


def test_annotate_same_mac():
    hosts = [
        {"ip": "10.0.0.6", "ports": [], "mac": "42:3F:8C:0E:7A:D0"},
        {"ip": "10.0.0.100", "ports": [], "mac": "42:3F:8C:0E:7A:D0"},
    ]
    out = annotate(hosts, {"hosts": []})
    assert out[0]["mac_peers"] == 2
    assert out[1]["mac_peers"] == 2