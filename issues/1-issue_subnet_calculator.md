# [Feature] Kalkulator Subnet IPv4

## Deskripsi
Implementasi fitur kalkulator subnetting IPv4 berbasis web untuk guru dan siswa SMK jurusan Teknik Komputer dan Jaringan (TKJ). Fitur ini menghitung subnet mask, network address, broadcast address, rentang host yang dapat digunakan (*usable host range*), serta total host yang dapat dialokasikan berdasarkan alamat IPv4 dan prefix (CIDR /0 s.d. /32).

## Tugas
1. Implementasikan fungsi domain `hitung_subnet(ip: str, prefix: int) -> dict` di `main.py` menggunakan operasi bitwise murni (AND/OR).
2. Terapkan validasi ketat terhadap format IPv4 (4 oktet, 0–255, tanpa leading zero, tanpa spasi/karakter non-numerik) dan prefix (0–32).
3. Tangani kasus khusus:
   - `/31`: RFC 3021 (point-to-point, 2 host, broadcast `None`).
   - `/32`: host tunggal (1 host, broadcast `None`).
4. Buat endpoint FastAPI `GET /api/subnet?ip=&prefix=` yang mengembalikan data JSON atau HTTP 400 dengan atribut `detail` saat input tidak valid.
5. Sajikan halaman antarmuka web melalui endpoint `GET /`.
6. Hubungkan antarmuka `index.html` dengan endpoint `GET /api/subnet` untuk menyajikan hasil kalkulasi dan pesan kesalahan yang jelas.

## Kriteria Penerimaan (Acceptance Criteria)
Mengacu pada matriks pengujian di `SPEC.md`:
- [ ] **TC-SUB-01**: Input `172.16.5.130/25` menghasilkan Network `172.16.5.128`, Broadcast `172.16.5.255`, Mask `255.255.255.128`, Host Range `172.16.5.129` - `172.16.5.254`, Usable Hosts `126`.
- [ ] **TC-SUB-02**: Input `10.0.0.0/30` menghasilkan Network `10.0.0.0`, Broadcast `10.0.0.3`, Host Range `10.0.0.1` - `10.0.0.2`, Usable Hosts `2`.
- [ ] **TC-SUB-03**: Input `192.168.1.0/31` menghasilkan Network `192.168.1.0`, Broadcast `None`, Host Range `192.168.1.0` - `192.168.1.1`, Usable Hosts `2`.
- [ ] **TC-SUB-04**: Input `192.168.1.5/32` menghasilkan Network `192.168.1.5`, Broadcast `None`, Host Range `192.168.1.5` - `192.168.1.5`, Usable Hosts `1`.
- [ ] **TC-SUB-05 s.d. TC-SUB-11**: Input tidak valid (`256.1.1.1/24`, `192.168.01.1/24`, `192.168.1`, `abc`, `""`, prefix `33`, prefix `-1`) menghasilkan `ValueError` dan HTTP 400 dengan atribut `detail`.
- [ ] **TC-API-01**: Endpoint `GET /` mengembalikan status HTTP 200 dan menyajikan halaman HTML.
- [ ] **TC-API-02 & TC-API-03**: Endpoint `GET /api/subnet` mengembalikan JSON sesuai kontrak.
- [ ] Seluruh unit test di `test_main.py` lulus 100% dengan `pytest`.

## Alur Kerja (Workflow)
`GitHub Issue` -> `Feature Branch` -> `Tulis Test Dulu (Fase Merah)` -> `Implementasi (Fase Hijau)` -> `Commit` -> `Pull Request` -> `CI Workflow` -> `Merge ke Main`.

