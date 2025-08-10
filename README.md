# Analisis Kompetitor dan Pemetaan Spasial dengan Choropleth Map

## 📋 Deskripsi
Kode ini merupakan implementasi lengkap untuk analisis kompetitor dan pemetaan spasial dengan visualisasi choropleth map yang menampilkan distribusi jumlah kasus per kota. Kode ini dirancang oleh dosen sains data dengan pengalaman 30 tahun untuk memberikan insight yang mendalam tentang distribusi geografis data.

## 🎯 Fitur Utama

### 1. **Pemetaan Spasial dengan Folium**
- Peta interaktif dengan marker untuk setiap produk
- Heatmap layer untuk visualisasi density
- Legend cluster yang informatif
- Popup detail informasi produk

### 2. **Choropleth Map Spasial** ⭐ **BARU**
- Visualisasi distribusi jumlah kasus per kota
- Color gradient dari hijau (rendah) ke merah (tinggi)
- Legend dengan keterangan nilai numerik
- Ukuran marker berdasarkan jumlah kasus
- Popup informasi detail per kota

### 3. **Visualisasi Interaktif dengan Plotly**
- 3D Scatter Plot dengan clustering
- Parallel Coordinates Plot
- Competitive Positioning Matrix
- Choropleth map dengan Plotly

### 4. **Analisis Kompetitor**
- Market segment analysis
- Competitive positioning matrix
- Rekomendasi strategi berdasarkan cluster

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Analisis
```bash
python analisis_kompetitor_spasial.py
```

## 📊 Output yang Dihasilkan

### File HTML Interaktif:
1. `peta_distribusi_harga_sarung_tangan.html` - Peta interaktif dengan marker
2. `choropleth_map_distribusi_kasus.html` - Choropleth map dengan Folium
3. `choropleth_plotly_distribusi_kasus.html` - Choropleth map dengan Plotly
4. `3d_scatter_plot.html` - 3D Scatter Plot
5. `parallel_coordinates_plot.html` - Parallel Coordinates Plot
6. `competitive_positioning_matrix.html` - Competitive Positioning Matrix

### File Data:
- `Tokopedia_sarung_tangan_with_clusters.xlsx` - Dataset dengan hasil clustering

## 🗺️ Fitur Choropleth Map

### Visualisasi Distribusi Kasus:
- **Merah**: Jumlah kasus tertinggi (≥80% dari maksimum)
- **Oranye**: Jumlah kasus tinggi (60-80% dari maksimum)
- **Kuning**: Jumlah kasus sedang (40-60% dari maksimum)
- **Hijau Muda**: Jumlah kasus rendah (20-40% dari maksimum)
- **Hijau**: Jumlah kasus terendah (<20% dari maksimum)

### Legend Informasi:
- Menampilkan range nilai untuk setiap warna
- Format numerik yang mudah dibaca
- Posisi legend yang tidak mengganggu visualisasi

### Popup Detail:
- Nama kota
- Total terjual
- Rata-rata harga
- Rata-rata rating
- Rata-rata performance score
- Jumlah produk

## 📈 Insight yang Dihasilkan

### 1. **Distribusi Geografis**
- Identifikasi kota dengan penjualan tertinggi
- Pola distribusi produk di Indonesia
- Hotspot dan coldspot penjualan

### 2. **Segmentasi Pasar**
- Cluster berdasarkan harga, penjualan, dan rating
- Karakteristik setiap segment pasar
- Positioning kompetitor

### 3. **Rekomendasi Strategi**
- Pricing strategy per cluster
- Performance improvement strategy
- Market penetration opportunity

## 🔧 Customization

### Mengubah Data Input:
```python
# Ganti dengan data Anda sendiri
df = pd.read_excel('your_data.xlsx')
```

### Mengubah Koordinat Kota:
```python
city_coordinates = {
    'Your_City': [latitude, longitude],
    # Tambahkan kota lain
}
```

### Mengubah Color Scheme:
```python
def get_color(sold_count):
    # Customize color logic
    if sold_count >= threshold_high:
        return 'red'
    # ... tambahkan kondisi lain
```

## 📝 Catatan Teknis

### Library yang Digunakan:
- **Folium**: Untuk peta interaktif
- **Plotly**: Untuk visualisasi interaktif
- **Pandas**: Untuk manipulasi data
- **Scikit-learn**: Untuk clustering
- **Geopandas**: Untuk data geografis

### Performance Considerations:
- Kode dioptimalkan untuk dataset hingga 10,000 baris
- Memory efficient dengan filtering data
- Error handling untuk data yang tidak valid

## 🎓 Penggunaan Akademis

Kode ini cocok untuk:
- Skripsi/Tesis sains data
- Analisis pasar dan kompetitor
- Visualisasi data geografis
- Penelitian distribusi spasial

## 📞 Support

Untuk pertanyaan atau masalah teknis, silakan hubungi:
- Email: [your-email@domain.com]
- GitHub Issues: [repository-url]

---

**Dibuat oleh:** Dosen Sains Data dengan 30 tahun pengalaman profesional
**Versi:** 1.0
**Tanggal:** 2024
