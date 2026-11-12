import pytest
from fastapi.testclient import TestClient

from main import app, hitung_subnet

client = TestClient(app)


@pytest.mark.parametrize(
    "ip,prefix,expected",
    [
        (
            "172.16.5.130",
            25,
            {
                "mask": "255.255.255.128",
                "network": "172.16.5.128",
                "broadcast": "172.16.5.255",
                "first_host": "172.16.5.129",
                "last_host": "172.16.5.254",
                "usable_hosts": 126,
            },
        ),
        (
            "10.0.0.0",
            30,
            {
                "mask": "255.255.255.252",
                "network": "10.0.0.0",
                "broadcast": "10.0.0.3",
                "first_host": "10.0.0.1",
                "last_host": "10.0.0.2",
                "usable_hosts": 2,
            },
        ),
        (
            "192.168.1.0",
            31,
            {
                "mask": "255.255.255.254",
                "network": "192.168.1.0",
                "broadcast": None,
                "first_host": "192.168.1.0",
                "last_host": "192.168.1.1",
                "usable_hosts": 2,
            },
        ),
        (
            "192.168.1.5",
            32,
            {
                "mask": "255.255.255.255",
                "network": "192.168.1.5",
                "broadcast": None,
                "first_host": "192.168.1.5",
                "last_host": "192.168.1.5",
                "usable_hosts": 1,
            },
        ),
    ],
)
def test_hitung_subnet_valid(ip, prefix, expected):
    hasil = hitung_subnet(ip, prefix)
    assert hasil == expected


@pytest.mark.parametrize(
    "ip,prefix",
    [
        ("256.1.1.1", 24),
        ("192.168.01.1", 24),
        ("192.168.1", 24),
        ("abc", 24),
        ("", 24),
        ("10.0.0.1", 33),
        ("10.0.0.1", -1),
    ],
)
def test_hitung_subnet_invalid(ip, prefix):
    with pytest.raises(ValueError):
        hitung_subnet(ip, prefix)


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_api_subnet_valid():
    response = client.get("/api/subnet?ip=172.16.5.130&prefix=25")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == "172.16.5.128"
    assert data["broadcast"] == "172.16.5.255"
    assert data["usable_hosts"] == 126


@pytest.mark.parametrize(
    "ip,prefix",
    [
        ("256.1.1.1", 24),
        ("192.168.01.1", 24),
        ("192.168.1", 24),
        ("abc", 24),
        ("", 24),
        ("10.0.0.1", 33),
        ("10.0.0.1", -1),
    ],
)
def test_api_subnet_invalid(ip, prefix):
    response = client.get(f"/api/subnet?ip={ip}&prefix={prefix}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

