# Tokopedia Scraper

**Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman**

Scraper Tokopedia yang canggih untuk mengekstrak data produk dari halaman pencarian dengan fitur scrolling otomatis dan anti-deteksi bot.

## Fitur Utama

- ✅ **Scrolling Otomatis**: Memuat lebih banyak produk secara otomatis
- ✅ **Anti-Deteksi Bot**: Konfigurasi optimal untuk menghindari deteksi
- ✅ **Ekstraksi Data Lengkap**: Nama produk, harga, jumlah terjual, rating, lokasi toko
- ✅ **Export Multiple Format**: CSV dan JSON
- ✅ **Error Handling**: Penanganan error yang robust
- ✅ **User-Friendly**: Interface yang mudah digunakan

## Data yang Diekstrak

- **Nama Produk**: Nama lengkap produk
- **Harga Produk**: Harga dalam format Rupiah
- **Jumlah Terjual**: Informasi penjualan produk
- **Rating Produk**: Rating dan ulasan produk
- **Lokasi Toko**: Lokasi penjual/toko

## Instalasi

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Chrome WebDriver

Pastikan Anda sudah menginstall Google Chrome browser. WebDriver akan di-download otomatis oleh Selenium.

### 3. Verifikasi Instalasi

```bash
python -c "import selenium; import pandas; import bs4; print('Semua dependencies berhasil diinstall!')"
```

## Cara Penggunaan

### 🚀 Cara Cepat (Recommended)

Jalankan workflow lengkap yang mengintegrasikan scraping, testing, dan analisis:

```bash
python run_complete_analysis.py
```

### 📊 Analisis Data Terpisah

Jika Anda sudah memiliki data hasil scraping:

```bash
python data_analyzer.py
```

### 🧪 Testing Scraper

Untuk testing dan validasi scraper:

```bash
python test_scraper.py
```

### 🔧 Scraper Manual

Untuk scraping manual:

```bash
python tokopedia_scraper.py
```

### Input Kata Kunci

Ketika diminta, masukkan kata kunci pencarian:
- Contoh: `cabai`
- Contoh: `cabai rawit`
- Contoh: `laptop gaming`

### Hasil Output

Workflow lengkap akan menghasilkan:
- 📄 File CSV: `tokopedia_[kata_kunci]_[timestamp].csv`
- 📄 File JSON: `tokopedia_[kata_kunci]_[timestamp].json`
- 📊 Visualisasi: `tokopedia_analysis_[timestamp].png`
- 📋 Laporan Analisis: `analysis_report_[timestamp].txt`
- 📋 Laporan Lengkap: `final_report_[kata_kunci]_[timestamp].txt`

## Contoh Penggunaan Programatik

```python
from tokopedia_scraper import TokopediaScraper

# Inisialisasi scraper
scraper = TokopediaScraper(headless=True)  # True untuk mode headless

# Lakukan scraping
products = scraper.scrape_products("cabai rawit", max_scrolls=10)

# Simpan hasil
scraper.save_to_csv(products, "hasil_scraping.csv")
scraper.save_to_json(products, "hasil_scraping.json")
```

## Konfigurasi

### Parameter Scraping

- `max_scrolls`: Jumlah maksimal scroll (default: 10)
- `scroll_pause_time`: Waktu jeda antar scroll dalam detik (default: 2)
- `headless`: Mode browser tanpa GUI (default: False)

### Contoh Konfigurasi Lanjutan

```python
# Scraping dengan konfigurasi custom
scraper = TokopediaScraper(headless=True)
products = scraper.scrape_products(
    search_query="laptop",
    max_scrolls=15,  # Scroll lebih banyak
    scroll_pause_time=3  # Jeda lebih lama
)
```

## Fitur Analisis Data

### 📊 Statistik Deskriptif
- Analisis distribusi harga produk
- Statistik rating dan ulasan
- Analisis lokasi penjual
- Identifikasi produk terbaik

### 📈 Visualisasi Data
- Histogram distribusi harga
- Distribusi rating produk
- Top 10 kota penjual
- Scatter plot harga vs rating

### 🏆 Produk Terbaik
- Top produk berdasarkan rating
- Produk termurah
- Produk termahal
- Analisis value for money

### 📋 Laporan Otomatis
- Laporan statistik lengkap
- Export ke file teks
- Visualisasi dalam format PNG
- Rekomendasi produk

## Struktur Data Output

### Format CSV
```csv
nama_produk,harga_produk,jumlah_terjual,rating_produk,lokasi_toko,search_query
"Cabai Rawit Merah 1kg","Rp 25.000","Terjual 1rb+","4.8","Jakarta Selatan","cabai rawit"
```

### Format JSON
```json
[
  {
    "nama_produk": "Cabai Rawit Merah 1kg",
    "harga_produk": "Rp 25.000",
    "jumlah_terjual": "Terjual 1rb+",
    "rating_produk": "4.8",
    "lokasi_toko": "Jakarta Selatan",
    "search_query": "cabai rawit"
  }
]
```

## Troubleshooting

### 1. Error ChromeDriver
```
Message: unknown error: cannot find Chrome binary
```
**Solusi**: Pastikan Google Chrome sudah terinstall dan path-nya benar.

### 2. Timeout Error
```
TimeoutException: Message: timeout
```
**Solusi**: 
- Periksa koneksi internet
- Coba kurangi `max_scrolls`
- Tambah `scroll_pause_time`

### 3. Tidak Ada Data Ter-scrape
**Solusi**:
- Periksa selector CSS masih valid
- Coba kata kunci pencarian yang berbeda
- Pastikan halaman Tokopedia tidak berubah struktur

### 4. Deteksi Bot
**Solusi**:
- Gunakan `headless=False` untuk debugging
- Tambah delay antara request
- Gunakan proxy jika diperlukan

## Tips Penggunaan

1. **Kata Kunci Spesifik**: Gunakan kata kunci yang spesifik untuk hasil yang lebih akurat
2. **Mode Headless**: Gunakan `headless=True` untuk performa lebih baik
3. **Jumlah Scroll**: Sesuaikan `max_scrolls` dengan kebutuhan data
4. **Backup Data**: Selalu backup hasil scraping secara berkala

## Batasan dan Etika

- **Rate Limiting**: Jangan melakukan scraping terlalu agresif
- **Terms of Service**: Patuhi Terms of Service Tokopedia
- **Data Usage**: Gunakan data hanya untuk tujuan yang etis
- **Respect Robots.txt**: Hormati file robots.txt website

## Dukungan

Untuk pertanyaan atau masalah teknis, silakan buat issue di repository ini.

## Lisensi

Kode ini dibuat untuk tujuan edukasi dan penelitian. Pengguna bertanggung jawab penuh atas penggunaan yang sesuai dengan hukum yang berlaku.

---

**Dibuat dengan ❤️ oleh Dosen Data Mining dengan 30 tahun pengalaman**
