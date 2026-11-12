from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

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
def api_subnet(ip: str, prefix: int):
    try:
        return hitung_subnet(ip, prefix)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
