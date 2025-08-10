# 🚀 Analisis Kompetitor dan Pemetaan Spasial - Tokopedia Sarung Tangan

## 📋 Deskripsi
Kode ini merupakan lanjutan dari preprocessing data untuk melakukan analisis kompetitor dan pemetaan spasial distribusi harga produk sarung tangan di Tokopedia menggunakan model clustering **HDBSCAN** yang merupakan algoritma terbaru dan masih jarang digunakan.

## 🎯 Tujuan Analisis
1. **Analisis Kompetitor**: Mengidentifikasi segmentasi pasar dan positioning kompetitor
2. **Pemetaan Spasial**: Visualisasi distribusi geografis produk dengan peta interaktif
3. **Clustering HDBSCAN**: Pengelompokan produk menggunakan algoritma clustering terbaru
4. **Rekomendasi Strategi**: Memberikan insight untuk pengambilan keputusan bisnis

## 📦 Library yang Digunakan

### Core Libraries
- `pandas` - Manipulasi data
- `numpy` - Komputasi numerik
- `matplotlib` & `seaborn` - Visualisasi statis

### Advanced Clustering
- `hdbscan` - **HDBSCAN clustering (model terbaru)**
- `umap-learn` - Dimensionality reduction modern
- `scikit-learn` - Preprocessing dan metrics

### Interactive Visualization
- `plotly` - Visualisasi interaktif 3D dan parallel coordinates
- `folium` - Peta interaktif dengan heatmap

### Data Processing
- `scipy` - Analisis statistik
- `networkx` - Analisis jaringan (opsional)
- `openpyxl` & `xlrd` - Reading Excel files

## 🛠️ Instalasi

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install HDBSCAN (Jika ada masalah)
```bash
# Untuk Windows
conda install -c conda-forge hdbscan

# Untuk Linux/Mac
pip install hdbscan
```

## 📁 Struktur File

```
├── analisis_kompetitor_pemetaan_spasial.py  # Kode utama
├── requirements.txt                          # Dependencies
├── README.md                                # Dokumentasi ini
├── Tokopedia_sarung tangan.xlsx             # Data original
└── Output Files (akan dibuat otomatis):
    ├── peta_distribusi_harga_sarung_tangan.html
    ├── Tokopedia_sarung_tangan_with_clusters.xlsx
    └── Visualisasi interaktif (Plotly)
```

## 🚀 Cara Penggunaan

### 1. Persiapan Data
Pastikan file Excel `Tokopedia_sarung tangan.xlsx` dengan sheet `Products Min1000 Sold` tersedia di direktori yang sama.

### 2. Jalankan Kode
```python
# Di Google Colab atau Jupyter Notebook
!python analisis_kompetitor_pemetaan_spasial.py

# Atau jalankan cell by cell di notebook
```

### 3. Output yang Dihasilkan

#### 📊 Analisis Clustering
- **HDBSCAN Clustering**: Pengelompokan produk berdasarkan 8 features
- **UMAP Visualization**: Dimensionality reduction untuk visualisasi cluster
- **Cluster Analysis**: Statistik detail setiap cluster

#### 🗺️ Peta Interaktif
- **Folium Map**: Peta Indonesia dengan marker produk
- **Heatmap**: Density distribution berdasarkan harga
- **Cluster Legend**: Legenda warna untuk setiap cluster
- **Popup Info**: Detail produk saat marker diklik

#### 📈 Visualisasi Interaktif
- **3D Scatter Plot**: Price vs Sold Count vs Rating
- **Parallel Coordinates**: Relationship antar features
- **Competitive Matrix**: Price vs Performance positioning

#### 📋 Analisis Kompetitor
- **Top Performers**: Produk terbaik di setiap cluster
- **Market Share**: Analisis revenue dan volume share
- **Segment Analysis**: Karakteristik setiap segment pasar

## 🔍 Fitur Utama

### 1. HDBSCAN Clustering
```python
hdbscan_clusterer = hdbscan.HDBSCAN(
    min_cluster_size=5,           # Minimal 5 produk per cluster
    min_samples=3,                # Minimal 3 sampel untuk core point
    cluster_selection_epsilon=0.1, # Epsilon untuk cluster selection
    cluster_selection_method='eom' # Excess of Mass method
)
```

**Keunggulan HDBSCAN:**
- Tidak memerlukan jumlah cluster yang ditentukan sebelumnya
- Robust terhadap noise dan outliers
- Dapat mendeteksi cluster dengan bentuk irregular
- Lebih modern dari K-means atau DBSCAN

### 2. Feature Engineering
```python
# Performance Score (composite metric)
df['Performance_Score'] = (df['Rating_Score'] * 0.4 + 
                          df['Popularity_Score'] * 0.3 + 
                          (1 / (1 + df['Price_Number']/100000)) * 0.3)
```

### 3. Spatial Mapping
```python
# Koordinat kota-kota utama Indonesia
city_coordinates = {
    'Jakarta': [-6.2088, 106.8456],
    'Surabaya': [-7.2575, 112.7521],
    'Bandung': [-6.9175, 107.6191],
    # ... dan seterusnya
}
```

## 📊 Interpretasi Hasil

### Cluster Analysis
- **Cluster 0**: Segment premium dengan harga tinggi
- **Cluster 1**: Segment mass market dengan volume tinggi
- **Cluster 2**: Segment mid-range dengan performance seimbang
- **Noise Points**: Produk unik yang tidak masuk kategori tertentu

### Competitive Positioning
- **Low-Cost Leadership**: Fokus pada harga murah
- **Premium Pricing**: Fokus pada kualitas dan harga tinggi
- **Competitive Pricing**: Harga menengah dengan value proposition
- **High-Performance Focus**: Fokus pada rating dan review tinggi

## 🎯 Insight Bisnis

### 1. Market Segmentation
- Identifikasi segment pasar yang berbeda
- Karakteristik unik setiap segment
- Peluang positioning yang belum terisi

### 2. Competitive Intelligence
- Analisis kompetitor berdasarkan cluster
- Benchmark performance antar segment
- Identifikasi gap pasar

### 3. Geographic Distribution
- Konsentrasi produk berdasarkan kota
- Hotspot penjualan sarung tangan
- Peluang ekspansi geografis

### 4. Pricing Strategy
- Analisis distribusi harga per segment
- Benchmark harga kompetitor
- Rekomendasi pricing strategy

## 🔧 Customization

### 1. Mengubah Parameter Clustering
```python
hdbscan_clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,  # Ubah ukuran minimal cluster
    min_samples=5,        # Ubah jumlah minimal sampel
    cluster_selection_epsilon=0.2  # Ubah epsilon
)
```

### 2. Menambah Kota untuk Mapping
```python
city_coordinates.update({
    'Malang': [-7.9839, 112.6214],
    'Solo': [-7.5755, 110.8243],
    # Tambahkan kota lain
})
```

### 3. Mengubah Features Clustering
```python
clustering_features = [
    'Price_Number', 'Sold_Count', 'Rating', 'Review_Count',
    'Revenue_Estimate', 'Rating_Score', 'Popularity_Score', 'Performance_Score'
    # Tambah atau kurangi features sesuai kebutuhan
]
```

## ⚠️ Troubleshooting

### 1. Error HDBSCAN Installation
```bash
# Coba install dengan conda
conda install -c conda-forge hdbscan

# Atau compile dari source
pip install --no-binary :all: hdbscan
```

### 2. Memory Issues
```python
# Kurangi jumlah data untuk clustering
df_clustering = df[clustering_features].dropna().sample(n=1000)
```

### 3. Folium Map Not Displaying
```python
# Pastikan file HTML tersimpan dan buka di browser
import webbrowser
webbrowser.open('peta_distribusi_harga_sarung_tangan.html')
```

## 📚 Referensi

### Papers & Documentation
- [HDBSCAN Paper](https://arxiv.org/abs/1705.07321)
- [UMAP Documentation](https://umap-learn.readthedocs.io/)
- [Folium Documentation](https://python-visualization.github.io/folium/)

### Related Work
- Market Basket Analysis
- Customer Segmentation
- Geographic Information Systems (GIS)
- Competitive Intelligence

## 🤝 Kontribusi

Untuk lomba Gemastik dengan tema "Penambangan Data untuk Peningkatan TIK menuju Kemandirian Bangsa", kode ini memberikan:

1. **Inovasi Teknologi**: Penggunaan HDBSCAN yang masih jarang
2. **Analisis Komprehensif**: Dari preprocessing hingga rekomendasi strategi
3. **Visualisasi Modern**: Peta interaktif dan 3D visualization
4. **Insight Bisnis**: Rekomendasi konkret untuk pengambilan keputusan

## 📞 Support

Jika ada pertanyaan atau masalah, silakan hubungi:
- Email: [your-email@domain.com]
- GitHub Issues: [repository-url]

---

**Dibuat untuk Lomba Gemastik 2024** 🏆
*"Penambangan Data untuk Peningkatan TIK menuju Kemandirian Bangsa"*
