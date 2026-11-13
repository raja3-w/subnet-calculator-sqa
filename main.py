from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Kalkulator Subnet & VLSM")



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


def int_to_ip(n: int) -> str:
    return f"{(n >> 24) & 0xFF}.{(n >> 16) & 0xFF}.{(n >> 8) & 0xFF}.{n & 0xFF}"


def hitung_subnet(ip: str, prefix: int) -> dict:
    if not isinstance(ip, str) or not ip:
        raise ValueError("Alamat IP tidak boleh kosong")

    if " " in ip:
        raise ValueError("Alamat IP tidak boleh mengandung spasi")

    oktets = ip.split(".")
    if len(oktets) != 4:
        raise ValueError("Alamat IP harus terdiri dari tepat 4 oktet")

    int_oktets = []
    for oktet in oktets:
        if not oktet.isdigit():
            raise ValueError(f"Oktet '{oktet}' bukan angka desimal valid")
        if len(oktet) > 1 and oktet.startswith("0"):
            raise ValueError(f"Oktet '{oktet}' tidak boleh diawali angka nol (leading zero)")
        val = int(oktet)
        if val < 0 or val > 255:
            raise ValueError(f"Nilai oktet '{val}' harus berada dalam rentang 0-255")
        int_oktets.append(val)

    if not isinstance(prefix, int) or prefix < 0 or prefix > 32:
        raise ValueError(f"Prefix '{prefix}' tidak valid (harus bilangan bulat 0-32)")

    # Bitwise calculations
    ip_int = (int_oktets[0] << 24) | (int_oktets[1] << 16) | (int_oktets[2] << 8) | int_oktets[3]
    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix > 0 else 0
    network_int = ip_int & mask_int

    if prefix == 31:
        # RFC 3021
        broadcast = None
        usable_hosts = 2
        first_host = int_to_ip(network_int)
        last_host = int_to_ip(network_int + 1)
    elif prefix == 32:
        # Host route
        broadcast = None
        usable_hosts = 1
        first_host = ip
        last_host = ip
    else:
        broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)
        broadcast = int_to_ip(broadcast_int)
        usable_hosts = (1 << (32 - prefix)) - 2
        first_host = int_to_ip(network_int + 1)
        last_host = int_to_ip(broadcast_int - 1)

    return {
        "mask": int_to_ip(mask_int),
        "network": int_to_ip(network_int),
        "broadcast": broadcast,
        "first_host": first_host,
        "last_host": last_host,
        "usable_hosts": usable_hosts,
    }


@app.get("/", response_class=HTMLResponse)
def read_root():
    html_file = Path(__file__).parent / "index.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="index.html tidak ditemukan")
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


@app.get("/api/subnet")
@app.get("/subnet")
def api_subnet(ip: str, prefix: int):

    try:
        return hitung_subnet(ip, prefix)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]:
    if not isinstance(network_cidr, str) or "/" not in network_cidr:
        raise ValueError("Format network CIDR tidak valid, harus 'IP/prefix'")

    parts = network_cidr.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Format network CIDR tidak valid, harus 'IP/prefix'")

    ip_str, prefix_str = parts[0], parts[1]
    if not prefix_str.isdigit():
        raise ValueError(f"Prefix '{prefix_str}' tidak valid (harus bilangan bulat 0-32)")

    base_prefix = int(prefix_str)
    if base_prefix < 0 or base_prefix > 32:
        raise ValueError(f"Prefix '{base_prefix}' tidak valid (harus bilangan bulat 0-32)")

    # Validasi alamat IP dan memastikan merupakan network address murni
    base_subnet = hitung_subnet(ip_str, base_prefix)
    if base_subnet["network"] != ip_str:
        raise ValueError(f"Alamat IP '{ip_str}' bukan merupakan alamat jaringan yang valid untuk prefix /{base_prefix}")

    if not isinstance(kebutuhan_host, list) or len(kebutuhan_host) == 0:
        raise ValueError("Daftar kebutuhan host tidak boleh kosong")

    for h in kebutuhan_host:
        if not isinstance(h, int) or isinstance(h, bool) or h < 1:
            raise ValueError(f"Setiap kebutuhan host harus bernilai >= 1 (ditemukan: '{h}')")

    # Urutkan secara descending
    sorted_kebutuhan = sorted(kebutuhan_host, reverse=True)

    # Hitung batasan alamat integer induk
    oktets = [int(x) for x in ip_str.split(".")]
    base_network_int = (oktets[0] << 24) | (oktets[1] << 16) | (oktets[2] << 8) | oktets[3]
    base_size = (1 << (32 - base_prefix)) if base_prefix < 32 else 1
    base_end_int = base_network_int + base_size

    curr_network_int = base_network_int
    alokasi = []

    for h in sorted_kebutuhan:
        # Cari prefix p sedemikian rupa sehingga 2^(32-p) - 2 >= h, batas maksimal prefix /30
        p = None
        for candidate_p in range(30, -1, -1):
            usable = (1 << (32 - candidate_p)) - 2
            if usable >= h:
                p = candidate_p
                break

        if p is None:
            raise ValueError("Kapasitas subnet induk tidak mencukupi untuk seluruh kebutuhan host")

        block_size = 1 << (32 - p)
        if curr_network_int + block_size > base_end_int:
            raise ValueError("Kapasitas subnet induk tidak mencukupi untuk seluruh kebutuhan host")

        sub = hitung_subnet(int_to_ip(curr_network_int), p)
        alokasi.append(
            {
                "kebutuhan": h,
                "network_cidr": f"{sub['network']}/{p}",
                "mask": sub["mask"],
                "network": sub["network"],
                "broadcast": sub["broadcast"],
                "first_host": sub["first_host"],
                "last_host": sub["last_host"],
                "usable_hosts": sub["usable_hosts"],
            }
        )
        curr_network_int += block_size

    return alokasi



class VLSMRequest(BaseModel):
    network: str
    kebutuhan_host: list[int]


@app.post("/api/vlsm")
@app.post("/vlsm")
def api_vlsm(req: VLSMRequest):

    try:
        return alokasi_vlsm(req.network, req.kebutuhan_host)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

