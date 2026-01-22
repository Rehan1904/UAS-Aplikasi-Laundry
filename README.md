# Aplikasi Laundry - Sistem Manajemen Laundry Berbasis Desktop

> Aplikasi desktop untuk manajemen bisnis laundry yang lengkap dengan fitur inventory, pelanggan, order, dan laporan keuangan.

## 📋 Tentang Proyek

Aplikasi Laundry adalah proyek UAS (Ujian Akhir Semester) yang dikembangkan sebagai sistem manajemen bisnis laundry berbasis desktop. Aplikasi ini dibangun menggunakan Python dengan antarmuka PyQt6 dan database SQLite untuk menyediakan solusi lengkap dalam mengelola operasional bisnis laundry.


**Karakteristik Utama:**
- ✅ Sistem autentikasi dengan login (username: `admin`, password: `admin123`)
- ✅ **Executable file siap pakai** di folder `dist/`
- ✅ Manajemen data pelanggan
- ✅ Manajemen inventory produk/jasa
- ✅ Sistem pemesanan (order) lengkap
- ✅ Generasi laporan dalam format PDF
- ✅ Dashboard harian untuk monitoring
- ✅ Database SQLite terintegrasi

## 👤 Informasi Login Default

**Akun Default untuk Login:**
- **Username:** `admin`
- **Password:** `admin123`

**Catatan Keamanan:**
- Disarankan untuk mengganti password default setelah login pertama kali
- Password disimpan dalam database SQLite (`laundry.db`)
- Sistem login terdapat di modul `login_dialog.py`

## 🗂️ Struktur Proyek

```
UAS-Aplikasi-Laundry/
├── main.py                    # Entry point aplikasi
├── main_window.py             # Window utama aplikasi
├── laundry.db                 # Database SQLite (berisi data user, pelanggan, order)
├── build.py                   # Script untuk build aplikasi
├── LaundryApp.spec            # Konfigurasi PyInstaller
├── 
├── ui/                        # File UI PyQt6
│   └── (berbagai file .ui)
├── 
├── inventory_dialog.py        # Dialog manajemen inventory
├── login_dialog.py            # Dialog login (username: admin, password: admin123)
├── order_dialog.py            # Dialog pemesanan
├── pelanggan_dialog.py        # Dialog manajemen pelanggan
├── 
├── __pycache__/               # Cache Python
├── build/                     # Direktori build
│   └── LaundryApp/
├── dist/                      # Direktori distribusi (berisi file .exe)
│   └── LaundryApp.exe         # ✅ FILE EXECUTABLE SIAP PAKAI
├── env/                       # Environment virtual
├── 
└── (berbagai file PDF laporan)
```

📸 Tampilan Aplikasi - Menu Cetak Laporan
Berikut adalah tampilan dashboard aplikasi yang menunjukkan menu cetak laporan PDF:

<img width="1190" height="820" alt="Screenshot 2026-01-22 171509" src="https://github.com/user-attachments/assets/850800c3-a920-4898-a3d4-519ce1f1fc89" />


Keterangan Gambar:
Menu Cetak PDF: Terdapat 7 opsi cetak laporan

📊 Menu Cetak Laporan PDF
Berdasarkan screenshot, aplikasi memiliki 7 jenis laporan PDF yang dapat dicetak:
📋 Daftar Lengkap Fitur Cetak:
📈 Cetak Dashboard Harian - Ringkasan aktivitas harian
👥 Cetak Daftar Pelanggan - Database seluruh pelanggan
🛒 Cetak Daftar Order - Riwayat semua transaksi
📦 Cetak Daftar Inventory - Laporan stok produk
💰 Cetak Laporan Pendapatan - Analisis keuangan
📊 Cetak Laporan Status Order - Tracking progress order
🧾 Cetak Invoice/Struk - Faktur untuk pelanggan
🚀 Cetak Semua Laporan - Generate semua laporan sekaligus

## 🚀 Fitur Utama

### 🔐 **Sistem Autentikasi**
- Login dengan username dan password
- Default credentials: `admin` / `admin123`
- Keamanan akses untuk mencegah penggunaan tanpa izin

### 👥 **Manajemen Pelanggan**
- Tambah, edit, dan hapus data pelanggan
- Riwayat transaksi pelanggan
- Data kontak dan informasi lengkap

### 📦 **Manajemen Inventory**
- Kelola stok produk laundry (detergen, pelembut, dll)
- Kelola jenis layanan (cuci, setrika, dry cleaning)
- Monitoring stok dan harga

### 🛒 **Sistem Pemesanan**
- Buat order baru dengan detail lengkap
- Pilih layanan dan produk
- Hitung total biaya otomatis
- Lacak status order (baru, proses, selesai, diambil)

### 📊 **Laporan dan Analytics**
- **Invoice Order** - Cetak invoice untuk pelanggan
- **Daftar Inventory** - Laporan stok produk
- **Daftar Order** - Riwayat semua transaksi
- **Daftar Pelanggan** - Database pelanggan
- **Dashboard Harian** - Ringkasan aktivitas harian
- **Laporan Pendapatan** - Analisis keuangan
- **Laporan Status Order** - Monitoring progress

## 💻 Instalasi dan Menjalankan

### 🎯 **Cara Termudah: Gunakan File Executable (Tanpa Install Python)**

1. **Download atau clone repository**
2. **Masuk ke folder `dist/`**
3. **Jalankan `LaundryApp.exe`**
4. **Login dengan:**
   - **Username:** `admin`
   - **Password:** `admin123`

**Keuntungan menggunakan executable:**
- Tidak perlu install Python atau dependencies
- Aplikasi sudah standalone
- Langsung jalan dengan double-click

### 🛠️ **Cara Alternatif: Jalankan dari Source Code**

#### Prasyarat
1. Python 3.x terinstal
2. pip (Python package manager)

#### Langkah-langkah Instalasi

1. **Clone repository**
```bash
git clone https://github.com/Rehan1904/UAS-Aplikasi-Laundry.git
cd UAS-Aplikasi-Laundry
```

2. **Buat virtual environment (opsional tapi disarankan)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install PyQt6
# Tambahkan library lain jika diperlukan
```

4. **Jalankan aplikasi**
```bash
python main.py
```

5. **Login dengan kredensial default:**
   - **Username:** `admin`
   - **Password:** `admin123`

### 📦 **Membuild Executable Sendiri (Optional)**

Jika ingin membuat executable versi sendiri:

```bash
# Menggunakan PyInstaller (jika sudah terinstall)
pyinstaller --onefile --windowed --name "LaundryApp" main.py

# Atau gunakan script build yang sudah ada
python build.py

# File executable akan muncul di folder dist/
# Untuk Windows: LaundryApp.exe
# Untuk Linux/Mac: LaundryApp
```

## 📁 File Executable yang Tersedia

Di repository ini sudah tersedia **file executable siap pakai**:

### **📍 Lokasi:** `dist/LaundryApp.exe`

### **Spesifikasi Executable:**
- **Nama file:** `LaundryApp.exe`
- **Lokasi:** `UAS-Aplikasi-Laundry/dist/`
- **Ukuran:** (tergantung build)
- **Sistem Operasi:** Windows
- **Dependencies:** Sudah termasuk semua library yang diperlukan

### **Cara Menggunakan:**
1. Download seluruh folder repository
2. Buka folder `dist/`
3. Double-click `LaundryApp.exe`
4. **Login dengan:**
   - **Username:** `admin`
   - **Password:** `admin123`

## 🖥️ Tampilan Aplikasi

*(Catatan: Screenshot dapat ditambahkan di sini)*

### 1. **Login Screen**
   - Halaman pertama yang muncul
   - Masukkan username: `admin` dan password: `admin123`
   - Akses ke semua fitur setelah login berhasil

### 2. **Dashboard** 
   - Overview bisnis setelah login

### 3. **Manajemen Pelanggan**
   - CRUD data pelanggan

### 4. **Manajemen Inventory**
   - Kelola produk/layanan

### 5. **Form Order**
   - Input transaksi baru

### 6. **Laporan**
   - Berbagai jenis report PDF

## 📄 Generasi Laporan

Aplikasi mampu menghasilkan 7 jenis laporan PDF:
1. **Invoice Order** - Faktur untuk pelanggan
2. **Daftar Inventory** - Laporan stok
3. **Daftar Order** - Riwayat transaksi
4. **Daftar Pelanggan** - Database pelanggan
5. **Dashboard Harian** - Aktivitas harian
6. **Laporan Pendapatan** - Analisis keuangan
7. **Laporan Status Order** - Tracking order

## 🔧 Troubleshooting

### **Masalah dengan Executable (`LaundryApp.exe`):**

1. **"File tidak dapat dijalankan" atau "Access denied"**
   - Pastikan file tidak sedang digunakan oleh program lain
   - Coba run sebagai Administrator (right-click → Run as administrator)
   - Periksa antivirus yang mungkin memblok file .exe

2. **"Missing DLL" atau error runtime**
   - Instal Microsoft Visual C++ Redistributable
   - Download: https://aka.ms/vs/16/release/vc_redist.x64.exe

3. **Aplikasi terbuka tapi cepat tertutup**
   - Buka Command Prompt di folder `dist/`
   - Jalankan: `LaundryApp.exe`
   - Lihat error message di console

### **Masalah Login:**
1. **"Username atau password salah"**: Pastikan menggunakan `admin` / `admin123`
2. **Database tidak ditemukan**: Pastikan file `laundry.db` ada di folder yang sama dengan executable

### **Solusi Umum:**
```bash
# Jika executable tidak bekerja, coba jalankan dari source:
python main.py

# Atau build ulang executable:
python build.py
```

## ⚠️ Catatan Penting

### **Untuk Pengguna Executable:**
1. **Jangan pindahkan `LaundryApp.exe` sendiri** - butuh file `laundry.db` dan folder `ui/`(ui harusnya optional)
2. **Simpan seluruh folder** `dist/` jika ingin membagikan aplikasi
3. **File executable hanya untuk Windows** - Linux/Mac butuh build terpisah

### **Keamanan:**
1. **Ganti Password Default**: Sangat disarankan untuk mengganti password `admin123` setelah login pertama
2. **Hanya untuk Pengembangan**: Kredensial default hanya untuk keperluan pengembangan/demo
3. **Environment Produksi**: Untuk penggunaan produksi, buat user baru dengan password yang kuat

## 🤝 Kontribusi

Kontribusi dipersilakan! Untuk kontribusi:

1. Fork repository
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -m 'Menambah fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

**Area untuk Improvement:**
- Enkripsi password (saat ini plaintext di database)
- Multi-user dengan role yang berbeda
- Fitur reset password
- Audit log untuk aktivitas user
- Build executable untuk Linux/Mac

## 📝 Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 👨‍💻 Pengembang

- **Muhammad-Rizqan** - [GitHub](https://github.com/Muhammad-Rizqan)
- **Rehan1904** - [GitHub](https://github.com/Rehan1904)
- Dikembangkan sebagai proyek Ujian Akhir Semester

## 📞 Kontak

Untuk pertanyaan atau feedback mengenai proyek ini, silakan buka [issue](https://github.com/Rehan1904/UAS-Aplikasi-Laundry/issues) di repository GitHub.

---

⭐ Jika proyek ini bermanfaat, jangan lupa beri bintang di repository!

**🚀 Coba Sekarang:** 
1. Download repository
2. Buka folder `dist/`
3. Jalankan `LaundryApp.exe`
4. Login dengan `admin` / `admin123`

**Peringatan**: Jangan gunakan kredensial `admin`/`admin123` di environment produksi!
