# 🛒 Shopee Login & CAPTCHA Manager

Aplikasi Python untuk mengelola login Shopee dan menangani CAPTCHA secara otomatis dengan GUI yang user-friendly.

## 🚀 Fitur Utama

- ✅ **Login Manual dengan GUI**: Interface yang mudah digunakan untuk proses login
- ✅ **Cookie Management**: Menyimpan dan memuat cookies untuk login otomatis
- ✅ **CAPTCHA Detection**: Deteksi otomatis dan handling CAPTCHA
- ✅ **Anti-Detection**: Menggunakan undetected-chromedriver untuk menghindari deteksi bot
- ✅ **Error Handling**: Penanganan error yang komprehensif
- ✅ **Status Logging**: Log real-time untuk monitoring proses
- ✅ **Threading**: GUI tidak freeze saat proses berjalan

## 📋 Prerequisites

- Python 3.7 atau lebih tinggi
- Google Chrome browser
- Internet connection

## 🔧 Instalasi

1. **Clone atau download repository ini**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Pastikan Google Chrome terinstall di sistem**

## 🎯 Cara Penggunaan

1. **Jalankan aplikasi:**
```bash
python shopee_login_fixed.py
```

2. **Masukkan kata kunci pencarian** (default: "laptop")

3. **Klik "🚀 Mulai Proses Login"**

4. **Ikuti instruksi di popup dialog:**
   - Login manual di browser yang muncul
   - Selesaikan CAPTCHA jika muncul
   - Klik OK setelah selesai

5. **Monitor status di log window**

## 🔧 Konfigurasi

### Chrome Driver Options
Aplikasi menggunakan konfigurasi Chrome yang optimal untuk menghindari deteksi:
- Disabled automation flags
- Realistic user agent
- Disabled extensions dan plugins
- Anti-detection measures

### Cookie Management
- Cookies disimpan di `shopee_cookies.json`
- Gunakan tombol "🗑️ Hapus Cookies" untuk reset login
- Cookies akan otomatis dimuat pada sesi berikutnya

## 🛠️ Troubleshooting

### Error: Chrome Driver tidak bisa diinisialisasi
```bash
# Pastikan Chrome terinstall
# Update Chrome ke versi terbaru
# Install ulang dependencies:
pip uninstall selenium undetected-chromedriver
pip install -r requirements.txt
```

### Error: CAPTCHA tidak terdeteksi
- Pastikan keyword pencarian valid
- Coba keyword yang berbeda
- Periksa koneksi internet

### Error: Login timeout
- Periksa kredensial login
- Pastikan tidak ada masalah jaringan
- Coba hapus cookies dan login ulang

## 📁 Struktur File

```
├── shopee_login_fixed.py    # File utama aplikasi
├── requirements.txt         # Dependencies
├── README.md               # Dokumentasi ini
└── shopee_cookies.json     # File cookies (auto-generated)
```

## 🔍 Komponen Utama

### ShopeeLoginManager
- `setup_chrome_driver()`: Inisialisasi Chrome driver dengan anti-detection
- `save_cookies()`: Simpan cookies dengan error handling
- `load_cookies()`: Muat cookies dengan validasi
- `is_logged_in()`: Cek status login dengan multiple indicators
- `handle_login_and_captcha()`: Proses utama login dan CAPTCHA

### ShopeeLoginGUI
- Interface user-friendly dengan Tkinter
- Real-time status logging
- Threading untuk non-blocking operations
- Cookie management tools

## ⚠️ Disclaimer

Aplikasi ini dibuat untuk tujuan edukasi dan pengembangan. Pastikan penggunaan sesuai dengan Terms of Service Shopee. Penulis tidak bertanggung jawab atas penyalahgunaan aplikasi.

## 🤝 Contributing

Kontribusi sangat diterima! Silakan buat pull request atau report issues.

## 📞 Support

Jika mengalami masalah, silakan buat issue di repository atau hubungi developer.

---

**Dibuat dengan ❤️ untuk komunitas Python dan Data Mining**
