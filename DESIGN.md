# DESIGN.md: Desain Antarmuka Pengguna (UI/UX)

Dokumen perancangan desain antarmuka web untuk **Kalkulator Subnet & VLSM** yang ditujukan bagi pengajar dan siswa SMK Teknik Komputer dan Jaringan (TKJ).

---

## 1. Konsep & Filosofi Desain

* **Aesthetic**: *Clean, Modern, Minimalist, Google-like*.
* **Color Palette**:
  - Background Utama: `#F8F9FA` (Soft warm-gray)
  - Card & Container: `#FFFFFF` (Pure white) dengan bayangan halus (*subtle elevation* `0 1px 3px rgba(0,0,0,0.08)`)
  - Accent / Primary Color: `#1A73E8` (Google Material Blue)
  - Primary Hover: `#1557B0`
  - Text Utama: `#202124` (High contrast dark gray)
  - Text Sekunder / Label: `#5F6368` (Medium gray)
  - Border: `#DADCE0` (Hairline crisp border)
  - Error Background: `#FCE8E6`, Error Text: `#C5221F`, Error Border: `#F5C2C7`
  - Success Badge: `#E6F4EA`, Text: `#137333`
* **Tipografi**:
  - Font System Native: `Google Sans`, `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, sans-serif.
  - Angka / Hasil Alamat IP: Monospace font (`ui-monospace`, `SFMono-Regular`, `Consolas`, `monospace`) untuk keterbacaan digit IP.

---

## 2. Struktur Tata Letak (Layout)

Halaman dirancang responsif untuk desktop ($\ge 768\text{px}$) maupun perangkat mobile ($< 768\text{px}$):
1. **Header / App Bar**:
   - Judul aplikasi: **Subnet & VLSM Calculator**
   - Subjudul singkat: *Alat bantu kalkulasi pengalamatan IPv4 & VLSM untuk Guru & Siswa TKJ*.
2. **Navigasi Tab**:
   - Tab 1: **Subnet Calculator**
   - Tab 2: **VLSM Allocator**
   - Indikator aktif berupa garis bawah tebal (*bottom active bar*) warna biru `#1A73E8`.
3. **Panel Konten**:
   - **Tab Subnet**:
     - Form Input: Baris grid responsif berisi input Alamat IP dan input Prefix CIDR (`/0` - `/32`).
     - Tombol Aksi: *"Hitung Subnet"* (Primary button).
     - Area Hasil: Kartu ringkasan dengan indikator visual dan 6 metrik (Subnet Mask, Network Address, Broadcast Address, Host Pertama, Host Terakhir, Usable Hosts).
   - **Tab VLSM**:
     - Form Input: Input Base Network (contoh: `192.168.1.0/24`).
     - Daftar Kebutuhan Host: List dinamis di mana pengguna bisa menambah baris kebutuhan host (`+ Tambah Subnet/Host`) atau menghapus baris individual.
     - Tombol Aksi: *"Alokasikan VLSM"*.
     - Area Hasil: Tabel interaktif hasil alokasi berurutan dengan kolom Kebutuhan, Blok CIDR, Mask, Network, Broadcast, Range Usable Host, dan Kapasitas.

---

## 3. Tiga Status Antarmuka (*UI States*)

1. **Empty State**:
   - Sebelum kalkulasi dijalankan, area hasil menampilkan ilustrasi teks lembut dan petunjuk sederhana untuk membimbing pengguna.
2. **Success State**:
   - Nilai hasil kalkulasi dimuat seketika dengan transisi halus (*fade-in*).
   - Label metrik dan angka alamat IP diformat dengan jelas dan kontras tinggi.
3. **Error State**:
   - Input field yang bermasalah diberi border merah `#C5221F`.
   - Kotak alert pesan kesalahan muncul tepat di bawah form dengan ikon peringatan dan deskripsi kesalahan dari backend API.

