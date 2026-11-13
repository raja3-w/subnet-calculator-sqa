# [Feature] Alokasi Subnet VLSM (Variable Length Subnet Masking)

## Deskripsi
Implementasi fitur alokasi VLSM (Variable Length Subnet Masking) IPv4 berbasis web untuk membagi blok jaringan induk menjadi beberapa subnet dengan ukuran bervariasi sesuai kebutuhan host tiap subnet secara efisien guna meminimalkan pemborosan alamat IP.

## Tugas
1. Implementasikan fungsi domain `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]` di `main.py`.
2. Validasi input:
   - `network_cidr` harus berformat `IP/prefix` yang valid dan IP wajib merupakan alamat jaringan murni (*network address*).
   - `kebutuhan_host` berupa list bilangan bulat positif ($\ge 1$) dan tidak boleh kosong.
3. Algoritma alokasi:
   - Urutkan kebutuhan host secara menurun (*descending*).
   - Tentukan prefix terkecil yang menampung kebutuhan host ($2^{(32-p)} - 2 \ge H$, batas maksimal prefix `/30`).
   - Alokasikan blok subnet secara berurutan mulai dari alamat awal jaringan induk.
   - Deteksi kapasitas subnet induk; lempar `ValueError` jika total kebutuhan melebihi kapasitas (*overflow*).
4. Buat endpoint FastAPI `POST /api/vlsm` menerima body JSON `{"network": "...", "kebutuhan_host": [...]}` dan mengembalikan list objek alokasi subnet atau HTTP 400 dengan atribut `detail` saat input tidak valid / overflow.
5. Pastikan antarmuka `index.html` terhubung dengan endpoint `POST /api/vlsm` untuk menampilkan tabel hasil alokasi dan penanganan pesan error.

## Kriteria Penerimaan (Acceptance Criteria)
Mengacu pada matriks pengujian di `SPEC.md`:
- [ ] **TC-VLSM-01**: Input Network `192.168.1.0/24` dengan kebutuhan `[100, 50, 20, 2]` menghasilkan 4 subnet:
  1. `192.168.1.0/25`
  2. `192.168.1.128/26`
  3. `192.168.1.192/27`
  4. `192.168.1.224/30`
- [ ] **TC-VLSM-02**: Kapasitas tidak cukup (misal `192.168.1.0/24` dengan kebutuhan `[200, 100]`) menghasilkan `ValueError` / HTTP 400 ("Kapasitas subnet induk tidak mencukupi untuk seluruh kebutuhan host").
- [ ] **TC-VLSM-03**: Network bukan alamat jaringan sah (misal `192.168.1.5/24`) menghasilkan `ValueError` / HTTP 400.
- [ ] **TC-VLSM-04**: Kebutuhan host tidak valid ($\le 0$ atau kosong) menghasilkan `ValueError` / HTTP 400.
- [ ] **TC-API-VLSM**: Endpoint `POST /api/vlsm` mengembalikan respons JSON valid status 200 untuk input valid, dan status 400 dengan atribut `detail` untuk input tidak valid.
- [ ] Seluruh unit test VLSM di `test_main.py` lulus 100% dengan `pytest`.

## Alur Kerja (Workflow)
`GitHub Issue` -> `Feature Branch` -> `Tulis Test Dulu (Fase Merah)` -> `Implementasi (Fase Hijau)` -> `Commit` -> `Pull Request` -> `CI Workflow` -> `Merge ke Main`.

