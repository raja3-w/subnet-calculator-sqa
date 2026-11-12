# SPEC.md: Spesifikasi Teknis Kalkulator Subnet & VLSM

Dokumen spesifikasi teknis untuk pengembangan aplikasi Kalkulator Subnet dan VLSM IPv4 berbasis web menggunakan Python 3.12, FastAPI, dan antarmuka web modern satu halaman.

---

## 1. Tujuan
Menyediakan kalkulator subnetting dan Variable Length Subnet Masking (VLSM) berbasis web yang akurat, deterministik, dan mudah diverifikasi untuk kebutuhan pembelajaran dan pengujian pada kompetensi keahlian Teknik Komputer dan Jaringan (TKJ) SMK.

Aplikasi ini mengedepankan kebenaran matematis pengalamatan IPv4 dengan perhitungan berbasis operasi bitwise (bukan heuristik string) serta penanganan kasus-kasus batas (*edge cases*) sesuai standar Internet Engineering Task Force (IETF).

---

## 2. Aturan Validasi Input

### 2.1 Alamat IPv4
Input alamat IPv4 valid jika memenuhi semua kriteria berikut:
1. Berupa string yang terdiri dari tepat 4 oktet desimal yang dipisahkan oleh karakter titik (`.`).
2. Setiap oktet berupa bilangan bulat dalam rentang `0` sampai `255` (inklusif).
3. **Tanpa angka nol di depan (*no leading zeros*)**: Nilai oktet seperti `01`, `001`, atau `09` ditolak secara tegas guna menghindari ambiguitas penafsiran bilangan oktal (misal: `192.168.01.1` tidak valid). Oktet bernilai `0` tunggal tetap valid (misal: `192.168.0.1`).
4. **Tanpa karakter ilegal**: Tidak boleh mengandung spasi di awal, tengah, atau akhir, serta tidak boleh mengandung karakter alfabet atau simbol selain titik numerik.
5. Input kosong (`""`) atau `None` ditolak.

### 2.2 Panjang Prefix (CIDR)
1. Berupa bilangan bulat (*integer*) dalam rentang `0` sampai `32` (inklusif).
2. Nilai prefix di luar rentang tersebut (misal `-1`, `33`) ditolak.
3. Tipe data selain bilangan bulat valid ditolak.

### 2.3 Blok Jaringan VLSM (`network_cidr`)
1. Berupa string format CIDR `IP/prefix` (contoh: `192.168.1.0/24`).
2. Alamat IP dan prefix harus valid sesuai aturan 2.1 dan 2.2.
3. Alamat IP yang diberikan **wajib merupakan alamat jaringan murni (*network address*)**. Jika alamat IP memiliki bit host bernilai 1 (misal `192.168.1.5/24`), input dianggap tidak valid dan ditolak.

### 2.4 Kebutuhan Host VLSM (`kebutuhan_host`)
1. Berupa daftar/array bilangan bulat positif (`list[int]`).
2. Tidak boleh kosong (`len > 0`).
3. Setiap elemen kebutuhan host harus berupa bilangan bulat $\ge 1$. Nilai $\le 0$ ditolak.
4. Total kebutuhan host (termasuk alokasi subnet mask untuk network & broadcast) tidak boleh melebihi kapasitas blok jaringan induk (`network_cidr`).

---

## 3. Kontrak Fungsi (Domain Logic)

Logika inti perhitungan berada di `main.py` dan independen dari lapisan presentasi web.

### 3.1 Fungsi `hitung_subnet`
```python
def hitung_subnet(ip: str, prefix: int) -> dict:
    ...
```

#### Perilaku & Perhitungan:
1. **Validasi**: Melakukan validasi ketat terhadap `ip` dan `prefix`. Jika tidak valid, lempar `ValueError` dengan pesan deskriptif.
2. **Subnet Mask**: Dihitung dari representasi 32-bit di mana $n$ bit pertama bernilai 1 ($n = \text{prefix}$) dan sisa $(32-n)$ bit bernilai 0.
3. **Network Address**: Dihitung murni dengan **operasi bitwise AND** antara representasi integer 32-bit dari alamat IP dan Subnet Mask:
   $$\text{network\_int} = \text{ip\_int} \ \& \ \text{mask\_int}$$
4. **Broadcast Address**:
   - Untuk prefix `0` sampai `30`: Dihitung dengan operasi bitwise OR antara Network Address dan negasi bitwise (NOT 32-bit) dari Subnet Mask:
     $$\text{broadcast\_int} = \text{network\_int} \ | \ (\sim\text{mask\_int} \ \& \ \text{0xFFFFFFFF})$$
   - Untuk prefix `31` (RFC 3021) dan `32` (Host route): bernilai `None`.
5. **Host Range & Usable Hosts**:
   - **Prefix 0 s.d. 30**:
     - `usable_hosts` = $2^{(32 - \text{prefix})} - 2$
     - `first_host` = $\text{network\_int} + 1$ (dikonversi ke format dotted-decimal)
     - `last_host` = $\text{broadcast\_int} - 1$ (dikonversi ke format dotted-decimal)
   - **Prefix 31 (RFC 3021 - Point-to-Point Links)**:
     - Digunakan khusus interkoneksi router point-to-point.
     - `usable_hosts` = `2`
     - `first_host` = IP pada network address ($\text{network\_int}$)
     - `last_host` = IP pada alamat kedua ($\text{network\_int} + 1$)
     - `broadcast` = `None`
   - **Prefix 32 (Single Host / Loopback)**:
     - `usable_hosts` = `1`
     - `first_host` = `last_host` = IP input itu sendiri
     - `broadcast` = `None`

#### Return Value:
Dictionary Python dengan skema kunci:
```python
{
    "mask": str,           # contoh: "255.255.255.128"
    "network": str,        # contoh: "172.16.5.128"
    "broadcast": str | None, # contoh: "172.16.5.255" atau None untuk /31, /32
    "first_host": str,     # contoh: "172.16.5.129"
    "last_host": str,      # contoh: "172.16.5.254"
    "usable_hosts": int    # contoh: 126
}
```

---

### 3.2 Fungsi `alokasi_vlsm`
```python
def alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]:
    ...
```

#### Perilaku & Algoritma Alokasi:
1. **Validasi**:
   - Pisahkan `network_cidr` menjadi IP dan prefix.
   - Pastikan IP merupakan alamat jaringan sah untuk prefix tersebut. Jika bukan, lempar `ValueError`.
   - Pastikan `kebutuhan_host` tidak kosong dan setiap nilai $\ge 1$. Jika tidak, lempar `ValueError`.
2. **Pengurutan Descending**:
   - Kebutuhan host wajib diurutkan dari yang terbesar ke terkecil guna meminimalkan fragmentasi ruang alamat IPv4.
3. **Penentuan Ukuran Blok Subnet**:
   - Untuk setiap kebutuhan host $H$:
     - Cari bilangan bulat $p$ (prefix) sedemikian rupa sehingga kapasitas host memenuhi $2^{(32-p)} - 2 \ge H$.
     - Batas alokasi minimal adalah prefix `/30` (kapasitas 2 usable host), kecuali untuk kebutuhan point-to-point RFC 3021 jika ditentukan. Secara standar VLSM konvensional: ukuran blok adalah pangkat 2 terkecil $\ge H + 2$, dengan prefix maksimum `/30`.
4. **Alokasi Berurutan**:
   - Mulai alokasi dari network address awal `network_cidr`.
   - Setiap subnet dialokasikan sebesar ukuran bloknya, lalu alamat awal subnet berikutnya digeser sebesar $2^{(32-p)}$.
5. **Pemeriksaan Kapasitas (Overflow)**:
   - Jika alamat subnet berikutnya melampaui batas broadcast dari blok induk `network_cidr`, lempar `ValueError` ("Kapasitas subnet induk tidak mencukupi untuk seluruh kebutuhan host").

#### Return Value:
List of dictionary di mana setiap elemen memuat:
```python
{
    "kebutuhan": int,      # jumlah host yang diminta, misal: 100
    "network_cidr": str,   # blok subnet hasil alokasi, misal: "192.168.1.0/25"
    "mask": str,
    "network": str,
    "broadcast": str | None,
    "first_host": str,
    "last_host": str,
    "usable_hosts": int
}
```

---

## 4. Kontrak API (HTTP REST)

Backend diimplementasikan dengan FastAPI dan mengekspos endpoint berikut:

### 4.1 `GET /api/subnet`
Menghitung informasi subnet berdasarkan IP dan prefix query parameters.

* **Query Parameters**:
  - `ip` (string, required): Alamat IPv4 (contoh: `172.16.5.130`).
  - `prefix` (integer, required): Panjang prefix (contoh: `25`).
* **Respons Sukses (HTTP 200 OK)**:
  ```json
  {
    "mask": "255.255.255.128",
    "network": "172.16.5.128",
    "broadcast": "172.16.5.255",
    "first_host": "172.16.5.129",
    "last_host": "172.16.5.254",
    "usable_hosts": 126
  }
  ```
* **Respons Error (HTTP 400 Bad Request)**:
  ```json
  {
    "detail": "Pesan deskripsi kesalahan validasi"
  }
  ```

### 4.2 `POST /api/vlsm`
Menghitung alokasi VLSM untuk blok subnet induk.

* **Request Headers**: `Content-Type: application/json`
* **Request Body (JSON)**:
  ```json
  {
    "network": "192.168.1.0/24",
    "kebutuhan_host": [100, 50, 20, 2]
  }
  ```
* **Respons Sukses (HTTP 200 OK)**:
  ```json
  [
    {
      "kebutuhan": 100,
      "network_cidr": "192.168.1.0/25",
      "mask": "255.255.255.128",
      "network": "192.168.1.0",
      "broadcast": "192.168.1.127",
      "first_host": "192.168.1.1",
      "last_host": "192.168.1.126",
      "usable_hosts": 126
    },
    {
      "kebutuhan": 50,
      "network_cidr": "192.168.1.128/26",
      "mask": "255.255.255.192",
      "network": "192.168.1.128",
      "broadcast": "192.168.1.191",
      "first_host": "192.168.1.129",
      "last_host": "192.168.1.190",
      "usable_hosts": 62
    },
    {
      "kebutuhan": 20,
      "network_cidr": "192.168.1.192/27",
      "mask": "255.255.255.224",
      "network": "192.168.1.192",
      "broadcast": "192.168.1.223",
      "first_host": "192.168.1.193",
      "last_host": "192.168.1.222",
      "usable_hosts": 30
    },
    {
      "kebutuhan": 2,
      "network_cidr": "192.168.1.224/30",
      "mask": "255.255.255.252",
      "network": "192.168.1.224",
      "broadcast": "192.168.1.227",
      "first_host": "192.168.1.225",
      "last_host": "192.168.1.226",
      "usable_hosts": 2
    }
  ]
  ```
* **Respons Error (HTTP 400 Bad Request)**:
  ```json
  {
    "detail": "Kapasitas subnet induk tidak mencukupi untuk seluruh kebutuhan host"
  }
  ```

### 4.3 `GET /`
Menyajikan halaman antarmuka pengguna (`index.html`) dengan `Content-Type: text/html`.

---

## 5. Halaman Web (Frontend)

Antarmuka web menggunakan satu file `index.html` yang mandiri (*self-contained*):
1. **Dua Mode (Tab Navigation)**:
   - **Tab Subnet**: Input IP Address dan Prefix (0–32), tombol "Hitung Subnet", dan kartu hasil (*result card*) yang menampilkan: Mask, Network, Broadcast, First Host, Last Host, Usable Hosts.
   - **Tab VLSM**: Input Base Network CIDR, daftar kebutuhan host dinamis (dapat menambah dan menghapus baris kebutuhan host), tombol "Alokasikan VLSM", dan tabel hasil alokasi berurutan.
2. **State Handling yang Jelas**:
   - **Empty State**: Area hasil menampilkan panduan singkat sebelum tombol hitung ditekan.
   - **Success State**: Menampilkan hasil perhitungan dalam format kartu atau tabel yang rapi.
   - **Error State**: Menampilkan kotak pesan error merah yang jelas tepat di bawah field input berdasarkan properti `detail` dari respons API (HTTP 400).

---

## 6. Tabel Test Case Lengkap (SQA Matrix)

Tabel ini menjadi acuan mutlak untuk penyusunan pengujian otomatis (`test_main.py`):

| ID | Kategori | Input | Ekspektasi Hasil |
| :--- | :--- | :--- | :--- |
| **TC-SUB-01** | Subnet Normal | `172.16.5.130`, Prefix `25` | `network`: `"172.16.5.128"`, `broadcast`: `"172.16.5.255"`, `mask`: `"255.255.255.128"`, `first_host`: `"172.16.5.129"`, `last_host`: `"172.16.5.254"`, `usable_hosts`: `126` |
| **TC-SUB-02** | Subnet /30 | `10.0.0.0`, Prefix `30` | `network`: `"10.0.0.0"`, `broadcast`: `"10.0.0.3"`, `first_host`: `"10.0.0.1"`, `last_host`: `"10.0.0.2"`, `usable_hosts`: `2` |
| **TC-SUB-03** | RFC 3021 /31 | `192.168.1.0`, Prefix `31` | `network`: `"192.168.1.0"`, `broadcast`: `None`, `first_host`: `"192.168.1.0"`, `last_host`: `"192.168.1.1"`, `usable_hosts`: `2` |
| **TC-SUB-04** | Host Route /32 | `192.168.1.5`, Prefix `32` | `network`: `"192.168.1.5"`, `broadcast`: `None`, `first_host`: `"192.168.1.5"`, `last_host`: `"192.168.1.5"`, `usable_hosts`: `1` |
| **TC-SUB-05** | Oktet > 255 | `256.1.1.1`, Prefix `24` | `ValueError` / HTTP 400 |
| **TC-SUB-06** | Leading Zero | `192.168.01.1`, Prefix `24` | `ValueError` / HTTP 400 |
| **TC-SUB-07** | Format Oktet Kurang | `192.168.1`, Prefix `24` | `ValueError` / HTTP 400 |
| **TC-SUB-08** | Karakter Huruf | `abc`, Prefix `24` | `ValueError` / HTTP 400 |
| **TC-SUB-09** | Input Kosong | `""`, Prefix `24` | `ValueError` / HTTP 400 |
| **TC-SUB-10** | Prefix > 32 | `10.0.0.1`, Prefix `33` | `ValueError` / HTTP 400 |
| **TC-SUB-11** | Prefix Negatif | `10.0.0.1`, Prefix `-1` | `ValueError` / HTTP 400 |
| **TC-VLSM-01** | VLSM Normal | Network: `192.168.1.0/24`<br>Kebutuhan: `[100, 50, 20, 2]` | 4 blok subnet:<br>1. `192.168.1.0/25`<br>2. `192.168.1.128/26`<br>3. `192.168.1.192/27`<br>4. `192.168.1.224/30` |
| **TC-VLSM-02** | VLSM Overflow | Network: `192.168.1.0/24`<br>Kebutuhan: `[200, 100]` | `ValueError` / HTTP 400 (Kapasitas tidak cukup) |
| **TC-VLSM-03** | VLSM Invalid Network | Network: `192.168.1.5/24`<br>Kebutuhan: `[50, 20]` | `ValueError` / HTTP 400 (Bukan alamat jaringan sah) |
| **TC-VLSM-04** | VLSM Kebutuhan $\le 0$ | Network: `192.168.1.0/24`<br>Kebutuhan: `[50, 0]` | `ValueError` / HTTP 400 |
| **TC-API-01** | API GET / | Path: `/` | HTTP 200, HTML Content |
| **TC-API-02** | API Subnet Valid | GET `/api/subnet?ip=172.16.5.130&prefix=25` | HTTP 200, JSON skema valid |
| **TC-API-03** | API Subnet Invalid | GET `/api/subnet?ip=256.1.1.1&prefix=24` | HTTP 400, body memuat field `detail` |

---

## 7. Di Luar Cakupan (*Out of Scope*)
1. Dukungan pengalamatan IPv6.
2. Otentikasi pengguna, manajemen hak akses, atau basis data.
3. Fitur routing table calculation, supernetting/CIDR aggregation di luar VLSM standar.
4. Framework frontend berbasis kompilasi kompleks (seperti React/Vue/Angular build step); frontend cukup vanila HTML/CSS/JS agar ringan dan ramah deployment.
