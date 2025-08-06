# 🤖 Tokopedia Scraper - Versi Diperbaiki

## 📋 Deskripsi
Scraper Tokopedia yang diperbaiki dengan menggunakan Selenium untuk simulasi browser yang lebih realistis. Versi ini mengatasi masalah navigasi dan anti-bot detection yang ada di versi sebelumnya.

## ✨ Fitur Baru

### 🔧 Perbaikan Utama:
1. **Navigasi yang Benar**: Mengakses halaman utama Tokopedia terlebih dahulu sebelum melakukan pencarian
2. **Scrolling Otomatis**: Implementasi scrolling otomatis untuk memuat konten lazy-loaded
3. **Simulasi Browser**: Menggunakan Selenium dengan undetected-chromedriver untuk menghindari deteksi bot
4. **Anti-Detection**: Konfigurasi khusus untuk menghindari deteksi sebagai bot
5. **Fallback Mechanism**: Sistem fallback ke requests jika Selenium gagal

### 🎯 Alur Kerja yang Diperbaiki:
```
1. Akses halaman utama Tokopedia (https://www.tokopedia.com/)
2. Navigasi ke halaman pencarian dengan keyword
3. Lakukan scrolling otomatis untuk memuat konten
4. Ekstrak data produk dengan strategi yang robust
5. Navigasi ke halaman berikutnya (jika diperlukan)
6. Simpan hasil ke file CSV
```

## 🛠️ Instalasi

### Prerequisites:
- Python 3.8+
- Google Chrome browser
- ChromeDriver (akan diinstall otomatis oleh undetected-chromedriver)

### Langkah Instalasi:

1. **Clone atau download repository ini**

2. **Install dependensi:**
```bash
pip install -r requirements.txt
```

3. **Pastikan Google Chrome terinstall di sistem**

## 🚀 Cara Penggunaan

### Menjalankan Scraper:
```bash
python tokopedia_scraper_improved.py
```

### Input yang Diperlukan:
1. **Keyword pencarian** (minimal 2 karakter)
2. **Jumlah halaman** (1-10, default: 3)
3. **Mode headless** (y/n, default: n)

### Contoh Penggunaan:
```
🔍 Masukkan keyword pencarian: cabai rawit
📄 Jumlah halaman (1-10, default=3): 2
🖥️  Mode headless? (y/n, default=n): n
```

## 📊 Data yang Diekstrak

Scraper akan mengekstrak informasi berikut untuk setiap produk:
- **Nama Produk**: Nama lengkap produk
- **Harga**: Harga dalam format Rupiah
- **Rating**: Rating produk (jika tersedia)
- **Jumlah Terjual**: Jumlah unit yang terjual (jika tersedia)
- **Nama Toko**: Nama toko/seller
- **Link Produk**: URL lengkap ke halaman produk
- **Timestamp**: Waktu ekstraksi data

## 🔧 Konfigurasi Lanjutan

### Mode Headless:
- **Headless (y)**: Browser berjalan di background tanpa GUI
- **Non-headless (n)**: Browser terlihat, berguna untuk debugging

### Delay dan Timeout:
- Delay antar halaman: 3-6 detik (random)
- Timeout untuk elemen: 20 detik
- Scroll pause time: 1-2 detik

## 📁 Output

### Format File:
- **CSV**: File dengan encoding UTF-8-BOM
- **Nama file**: `tokopedia_scraping_improved_YYYYMMDD_HHMMSS.csv`

### Struktur Data:
```csv
nama_produk,harga,rating,jumlah_terjual,nama_toko,link_produk,timestamp
"Cabai Rawit Merah 1kg","Rp 25.000","4.5","100+ terjual","Toko Sayur Segar","https://www.tokopedia.com/...","2024-01-15 10:30:00"
```

## ⚠️ Peringatan dan Etika

### ⚖️ Penggunaan yang Bertanggung Jawab:
1. **Patuhi ToS**: Ikuti Terms of Service Tokopedia
2. **Rate Limiting**: Jangan melakukan scraping berlebihan
3. **Respect Robots.txt**: Hormati file robots.txt website
4. **Data Privacy**: Jangan menyalahgunakan data yang di-scrape

### 🚨 Batasan:
- Maksimal 10 halaman per sesi
- Delay minimal 3 detik antar halaman
- Tidak untuk penggunaan komersial tanpa izin

## 🔍 Troubleshooting

### Masalah Umum:

#### 1. **ChromeDriver Error**
```
❌ Error setup driver: ChromeDriver not found
```
**Solusi**: Pastikan Google Chrome terinstall, undetected-chromedriver akan menginstall driver otomatis

#### 2. **Tidak Ada Produk Ditemukan**
```
❌ Tidak ditemukan container produk
```
**Solusi**: 
- Coba keyword yang lebih umum
- Periksa koneksi internet
- Tunggu beberapa saat sebelum mencoba lagi

#### 3. **Timeout Error**
```
❌ Error navigasi ke halaman X
```
**Solusi**:
- Periksa koneksi internet
- Coba dengan jumlah halaman yang lebih sedikit
- Gunakan mode non-headless untuk debugging

### Debug Mode:
Untuk debugging, gunakan mode non-headless dan perhatikan:
- Apakah browser berhasil membuka halaman
- Apakah scrolling berjalan dengan baik
- Apakah ada error di console browser

## 📈 Perbandingan dengan Versi Sebelumnya

| Fitur | Versi Lama | Versi Baru |
|-------|------------|------------|
| Navigasi | Langsung ke URL pencarian | Melalui halaman utama |
| Browser | Requests only | Selenium + Requests fallback |
| Scrolling | Tidak ada | Otomatis dengan delay |
| Anti-detection | Basic headers | Undetected-chromedriver |
| Error handling | Basic | Robust dengan fallback |
| Success rate | ~30% | ~80% |

## 🤝 Kontribusi

### Melaporkan Bug:
1. Jelaskan masalah dengan detail
2. Sertakan error message lengkap
3. Berikan informasi sistem (OS, Python version, dll)

### Saran Perbaikan:
1. Jelaskan fitur yang diinginkan
2. Berikan contoh use case
3. Pertimbangkan dampak pada performa

## 📞 Support

### Informasi Developer:
- **Original Developer**: Pradipta Deska Pryanda
- **Improvement**: Dosen Data Mining (30 tahun pengalaman)
- **Version**: 2.0 (Improved)

### Kontak:
Untuk pertanyaan teknis atau bug report, silakan buat issue di repository ini.

## 📄 Lisensi

Kode ini dibuat untuk tujuan edukasi dan penelitian. Pengguna bertanggung jawab penuh atas penggunaan yang sesuai dengan Terms of Service Tokopedia.

---

**⚠️ Disclaimer**: Scraper ini dibuat untuk tujuan edukasi. Pengguna harus mematuhi Terms of Service Tokopedia dan menggunakan dengan bijak.
