# Analisis Kompetitor dan Pemetaan Spasial dengan Choropleth Map

## 📋 Deskripsi
Proyek ini merupakan implementasi lengkap analisis kompetitor dan pemetaan spasial untuk data produk sarung tangan dari Tokopedia. Kode ini mencakup visualisasi choropleth map yang sophisticated dengan legenda yang informatif, sesuai dengan permintaan untuk menambahkan visualisasi map spasial seperti pada gambar referensi.

## 🎯 Fitur Utama

### 1. **Choropleth Map Spasial**
- Visualisasi distribusi data per kota dengan gradasi warna
- Legend yang sophisticated dengan informasi detail
- Popup interaktif dengan statistik per wilayah
- Gradasi warna dari lightgreen → yellow → orange → red

### 2. **Heatmap Density dengan Cluster Analysis**
- Analisis density berdasarkan cluster HDBSCAN
- Layer control untuk setiap cluster
- Radius yang dinamis berdasarkan total penjualan

### 3. **Visualisasi Interaktif**
- 3D Scatter Plot dengan Plotly
- Parallel Coordinates Plot
- Competitive Positioning Matrix

### 4. **Analisis Kompetitor**
- Market segment analysis
- Rekomendasi strategi berdasarkan cluster
- Performance scoring

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Analisis Lengkap
```bash
python main_analysis_with_choropleth.py
```

### 3. Generate Data Dummy (Opsional)
```bash
python demo_data_generator.py
```

## 📁 File Output

Setelah menjalankan analisis, Anda akan mendapatkan file-file berikut:

1. **`peta_distribusi_harga_sarung_tangan.html`** - Peta interaktif dengan markers
2. **`choropleth_map_sold_count.html`** - Choropleth map untuk jumlah penjualan
3. **`choropleth_map_price_number.html`** - Choropleth map untuk rata-rata harga
4. **`choropleth_map_performance_score.html`** - Choropleth map untuk performance score
5. **`density_heatmap_clusters.html`** - Heatmap density dengan cluster analysis
6. **`Tokopedia_sarung_tangan_with_clusters.xlsx`** - Dataset dengan hasil clustering

## 🗺️ Fitur Choropleth Map

### Legend yang Sophisticated
- **Posisi**: Bottom-right corner dengan styling modern
- **Informasi**: Range nilai dari rendah hingga sangat tinggi
- **Sumber data**: Tokopedia Digital Service
- **Metrik**: Sesuai dengan data yang divisualisasikan

### Gradasi Warna
- **Light Green**: Nilai rendah
- **Yellow**: Nilai sedang  
- **Orange**: Nilai tinggi
- **Red**: Nilai sangat tinggi

### Popup Interaktif
- Nama kota
- Total metrik per kota
- Rata-rata metrik per kota
- Jumlah produk per kota

## 🔧 Customization

### Mengubah Metrik untuk Choropleth
```python
# Contoh untuk metrik custom
choropleth_custom, filename_custom = create_choropleth_map(
    df_mapping, 
    'Review_Count',  # Ganti dengan kolom yang diinginkan
    "Distribusi Jumlah Review per Kota"
)
```

### Mengubah Warna Gradasi
```python
# Dalam fungsi create_choropleth_map
colormap = cm.LinearColormap(
    colors=['blue', 'cyan', 'yellow', 'red'],  # Ganti warna sesuai kebutuhan
    vmin=min_val,
    vmax=max_val,
    caption=f'Jumlah {metric_column}'
)
```

## 📊 Struktur Data

Dataset harus memiliki kolom-kolom berikut:
- `Product_Name`: Nama produk
- `Shop_Name`: Nama toko
- `Shop_City`: Kota toko
- `Price_Number`: Harga produk
- `Sold_Count`: Jumlah terjual
- `Rating`: Rating produk
- `Review_Count`: Jumlah review
- `Performance_Score`: Skor performa
- `Cluster`: Hasil clustering (opsional)

## 🎨 Visualisasi yang Dihasilkan

### 1. Choropleth Map
- Menampilkan distribusi spasial dengan circles berwarna
- Radius circle berdasarkan nilai metrik
- Legend dengan informasi lengkap

### 2. Heatmap Density
- Intensitas warna berdasarkan density data
- Layer terpisah untuk setiap cluster
- Control panel untuk mengatur visibility

### 3. Interactive Plots
- 3D scatter plot dengan hover information
- Parallel coordinates untuk analisis multi-dimensi
- Competitive positioning matrix

## 🔍 Insight yang Dihasilkan

1. **Distribusi Geografis**: Konsentrasi produk per kota
2. **Segmentasi Pasar**: Analisis cluster berdasarkan karakteristik produk
3. **Competitive Analysis**: Positioning produk dalam market
4. **Performance Metrics**: Skor performa berdasarkan rating, penjualan, dan review
5. **Strategic Recommendations**: Rekomendasi strategi berdasarkan analisis cluster

## 📝 Catatan Penting

- Kode ini menggunakan data dummy untuk demonstrasi
- Untuk data real, pastikan koordinat latitude/longitude tersedia
- Semua visualisasi disimpan dalam format HTML yang dapat dibuka di browser
- Legend dan popup menggunakan styling CSS yang modern dan responsive

## 🤝 Kontribusi

Kode ini dikembangkan sebagai bagian dari analisis sains data dengan fokus pada:
- Visualisasi spasial yang sophisticated
- Analisis kompetitor yang komprehensif
- Rekomendasi strategi yang actionable
- User experience yang optimal dalam eksplorasi data
