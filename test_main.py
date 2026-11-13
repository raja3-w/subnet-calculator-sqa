import pytest
from fastapi.testclient import TestClient

from main import alokasi_vlsm, app, hitung_subnet

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


def test_alokasi_vlsm_valid():
    hasil = alokasi_vlsm("192.168.1.0/24", [100, 50, 20, 2])
    assert hasil == [
        {
            "kebutuhan": 100,
            "network_cidr": "192.168.1.0/25",
            "mask": "255.255.255.128",
            "network": "192.168.1.0",
            "broadcast": "192.168.1.127",
            "first_host": "192.168.1.1",
            "last_host": "192.168.1.126",
            "usable_hosts": 126,
        },
        {
            "kebutuhan": 50,
            "network_cidr": "192.168.1.128/26",
            "mask": "255.255.255.192",
            "network": "192.168.1.128",
            "broadcast": "192.168.1.191",
            "first_host": "192.168.1.129",
            "last_host": "192.168.1.190",
            "usable_hosts": 62,
        },
        {
            "kebutuhan": 20,
            "network_cidr": "192.168.1.192/27",
            "mask": "255.255.255.224",
            "network": "192.168.1.192",
            "broadcast": "192.168.1.223",
            "first_host": "192.168.1.193",
            "last_host": "192.168.1.222",
            "usable_hosts": 30,
        },
        {
            "kebutuhan": 2,
            "network_cidr": "192.168.1.224/30",
            "mask": "255.255.255.252",
            "network": "192.168.1.224",
            "broadcast": "192.168.1.227",
            "first_host": "192.168.1.225",
            "last_host": "192.168.1.226",
            "usable_hosts": 2,
        },
    ]


@pytest.mark.parametrize(
    "network_cidr,kebutuhan_host",
    [
        ("192.168.1.0/24", [200, 100]),
        ("192.168.1.5/24", [50, 20]),
        ("192.168.1.0/24", [50, 0]),
        ("192.168.1.0/24", []),
        ("192.168.1.0/24", [-5]),
        ("192.168.1.0", [10]),
        ("192.168.1.0/33", [10]),
    ],
)
def test_alokasi_vlsm_invalid(network_cidr, kebutuhan_host):
    with pytest.raises(ValueError):
        alokasi_vlsm(network_cidr, kebutuhan_host)


def test_api_vlsm_valid():
    response = client.post(
        "/api/vlsm",
        json={"network": "192.168.1.0/24", "kebutuhan_host": [100, 50, 20, 2]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert data[0]["network_cidr"] == "192.168.1.0/25"
    assert data[0]["usable_hosts"] == 126


@pytest.mark.parametrize(
    "payload",
    [
        {"network": "192.168.1.0/24", "kebutuhan_host": [200, 100]},
        {"network": "192.168.1.5/24", "kebutuhan_host": [50]},
        {"network": "192.168.1.0/24", "kebutuhan_host": [0]},
        {"network": "192.168.1.0/24", "kebutuhan_host": []},
    ],
)
def test_api_vlsm_invalid(payload):
    response = client.post("/api/vlsm", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


