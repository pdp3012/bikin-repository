# 🔥 TOKOPEDIA SCRAPER ENHANCED

## 🎓 Enhanced Version dengan Sold Count & Detail Scraping

Versi enhanced dari Tokopedia Scraper yang dirancang khusus untuk mendapatkan data yang lebih lengkap, termasuk **jumlah terjual** dari halaman listing dan **detail produk** dari halaman individual.

### ✨ Fitur Baru Enhanced

1. **🛒 Sold Count dari Listing**: Mengambil jumlah terjual langsung dari halaman pencarian
2. **🔍 Detail Product Scraping**: Scraping halaman detail untuk data tambahan
3. **📊 Enhanced Excel Output**: Excel file dengan statistik lengkap dan summary sheet
4. **📈 Smart Sorting**: Hasil diurutkan berdasarkan performa penjualan

### 🆚 Perbedaan dengan Versi Original

| Fitur | Original | Enhanced |
|-------|----------|----------|
| Jumlah Terjual | ❌ | ✅ (dari listing) |
| Detail Scraping | ❌ | ✅ (opsional) |
| Summary Sheet | ❌ | ✅ |
| Smart Sorting | Rating + Review | **Sold Count** + Rating + Review |
| Progress Display | Per 50 halaman | Per 10 halaman (lebih sering) |
| Data Tambahan | - | Deskripsi, Stok, Berat, Kondisi |

### 📊 Data yang Dikumpulkan

#### Basic Data (dari listing):
- Product ID, Name, URL
- Price (Text, Number, Original, Discount %)
- Shop (ID, Name, City, Tier)
- Rating & Review Count
- **🆕 Sold Count** (jumlah terjual)
- Category Name
- Timestamp

#### Enhanced Data (opsional, dari detail page):
- **🆕 Description** (500 chars)
- **🆕 Sold Count Detail** (lebih akurat)
- **🆕 Stock Info**
- **🆕 Weight**
- **🆕 Condition** (Baru/Bekas)
- **🆕 Minimum Order**

### 🚀 Cara Penggunaan

```bash
python3 tokopedia_scraper_enhanced.py
```

#### Input yang Diminta:
1. **Keyword**: Kata kunci pencarian (e.g., 'telur', 'samsung')
2. **Target Produk**: Jumlah produk yang ingin diambil (kosong = semua)
3. **Detail Scraping**: Y/N untuk mengaktifkan scraping detail

### 📁 Output

File Excel dengan 2 sheet:
1. **Products**: Data lengkap semua produk
2. **Summary**: Statistik ringkasan

Contoh output: `tokopedia_telur_20241210_143025_enhanced.xlsx`

### 🎯 Contoh Use Case

```
Keyword: telur
Target: 1000 produk
Detail Scraping: Ya

Hasil:
✅ 1000 produk dengan sold count
✅ Detail deskripsi, stok, berat
✅ Top 5 produk terlaris
✅ Summary statistik lengkap
```

### 📈 Enhanced Stats yang Ditampilkan

- Total produk unik
- Range harga (min-max)
- Average rating
- Unique shops & cities
- **🆕 Total sold count**
- **🆕 Products with sales data (%)**
- **🆕 Highest sold count**
- **🆕 Top 5 produk terlaris**

### ⚡ Performance

- **Flow Optimal**: Listing → Sold Count → Detail (jika diminta)
- **Smart Rate Limiting**: Delay otomatis untuk mencegah blocking
- **Error Handling**: Fallback untuk request yang gagal
- **Progress Monitoring**: Update real-time setiap 10 halaman

### 🛠️ Dependencies

```
requests==2.32.3
pandas==2.2.3
beautifulsoup4==4.13.3
openpyxl==3.1.5
```

### 🔧 Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-requests python3-pandas python3-bs4 python3-openpyxl

# Atau menggunakan pip
pip install -r requirements.txt
```

### 💡 Tips Penggunaan

1. **Untuk Analisis Cepat**: Gunakan tanpa detail scraping
2. **Untuk Riset Mendalam**: Aktifkan detail scraping
3. **Target Optimal**: 500-2000 produk untuk balance speed vs completeness
4. **Keyword Spesifik**: Gunakan keyword yang tepat untuk hasil relevan

### 🎓 Dari Perspektif Data Mining Expert

Sebagai dosen data mining dengan 30 tahun pengalaman, scraper ini dirancang dengan:

- **Data Quality**: Duplikasi otomatis dihapus
- **Data Completeness**: Sold count melengkapi analisis performa
- **Data Timeliness**: Timestamp untuk tracking temporal
- **Data Consistency**: Normalisasi format numerik
- **Scalability**: Handling target dinamis dan rate limiting

### 🔍 Data Mining Use Cases

1. **Market Analysis**: Produk terlaris per kategori
2. **Price Intelligence**: Korelasi harga vs penjualan
3. **Competitor Research**: Performa shop berdasarkan kota
4. **Trend Analysis**: Pattern rating vs sold count
5. **Supply Chain**: Analisis stok vs demand

---

**💎 Enhanced Features Summary**:
- ✅ Sold count dari listing
- ✅ Optional detail scraping  
- ✅ Enhanced Excel dengan summary
- ✅ Smart sorting by performance
- ✅ Real-time top products preview
- ✅ Comprehensive error handling
