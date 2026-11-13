# Kalkulator Subnet & VLSM (subnet-calculator-sqa)

Aplikasi Kalkulator Subnetting dan Variable Length Subnet Masking (VLSM) IPv4 berbasis web yang akurat, deterministik, dan teruji secara ketat menggunakan prinsip Software Quality Assurance (SQA) dan Test-Driven Development (TDD).

## Fitur Utama
- **Kalkulator Subnet**: Menghitung subnet mask, network address, broadcast address, rentang host, dan usable host untuk prefix `/0` sampai `/32` (termasuk RFC 3021 `/31` dan host route `/32`).
- **Alokasi VLSM**: Alokasi subnet dinamis berdasarkan kebutuhan host yang diurutkan secara efisien guna meminimalkan pemborosan ruang alamat IPv4.
- **REST API**: Endpoint `/api/subnet` dan `/api/vlsm` berbasis FastAPI.
- **Single Page Interface**: Antarmuka web responsif dan interaktif (`index.html`).

## Pengujian Lokal (Local Testing)
Jalankan pengujian unit dan cakupan kode (*coverage*) menggunakan `uv`:
```bash
uv run pytest test_main.py -v --cov=main --cov-report=term-missing
```

## Docker

Aplikasi ini telah dikemas dalam container Docker berbasis image ramping `python:3.12-slim` dengan manajemen dependency menggunakan `uv`.

### 1. Build Image Docker
Untuk membangun image Docker:
```bash
docker build -t subnet-calculator .
```

### 2. Menjalankan Container
Jalankan container di latar belakang (*detached mode*) dan ekspos ke port `8000`:
```bash
docker run -d --name subnet-app -p 8000:8000 subnet-calculator
```

Aplikasi dapat diakses melalui browser pada `http://localhost:8000`.

### 3. Smoke Test Container Lokal
Untuk memverifikasi kesehatan dan kebenaran seluruh endpoint aplikasi di dalam container lokal:
```bash
uv run python scripts/smoke_test.py http://127.0.0.1:8000
```
*(Atau gunakan `python3 scripts/smoke_test.py http://127.0.0.1:8000`)*.

### 4. Menghentikan Container
Setelah pengujian selesai, hentikan dan hapus container dengan:
```bash
docker rm -f subnet-app
```

