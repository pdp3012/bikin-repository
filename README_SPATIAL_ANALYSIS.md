# Analisis Spasial Lanjutan dengan Koordinat Dummy

## 📋 Deskripsi
Script Python untuk analisis spasial lanjutan yang menggantikan Google Maps API dengan koordinat dummy untuk demo/fallback purposes. Dikembangkan oleh dosen sains data dengan 30 tahun pengalaman profesional dan sertifikasi internasional.

## 🚀 Fitur Utama

### 🔧 Geocoding dengan Koordinat Dummy
- **Pengganti Google Maps API**: Menggunakan dictionary koordinat dummy untuk 100+ kota di Indonesia
- **Fallback System**: Jika kota tidak ditemukan, menggunakan koordinat default Jakarta
- **Partial Matching**: Mencari kota dengan partial string matching

### 🔍 HDBSCAN Clustering
- **Spatial Features**: Menggabungkan data numerik dengan koordinat spasial
- **Parameter Optimization**: Grid search untuk parameter optimal
- **Evaluation Metrics**: Silhouette Score dan Calinski-Harabasz Score
- **Noise Handling**: Deteksi dan analisis noise points

### 🌍 Analisis Spasial
- **Global Moran's I**: Mengukur spatial autocorrelation
- **Getis-Ord Gi***: Deteksi hotspot dan coldspot
- **Interpretasi Otomatis**: Klasifikasi tingkat spatial clustering

### 📈 Geographically Weighted Regression (GWR)
- **Distance-Weighted Regression**: Implementasi GWR custom
- **Performance Metrics**: MAE, MSE, R² Score
- **Spatial Cross-Validation**: Traditional K-fold vs Spatial Block CV
- **OLS Comparison**: Bandingkan dengan Ordinary Least Squares

### 🎨 Visualisasi Interaktif
- **Interactive Maps**: Peta clustering dan hotspot dengan Plotly
- **Box Plots**: Analisis distribusi per cluster
- **Spatial Autocorrelation**: Bar chart Moran's I
- **GWR Results**: Scatter plot actual vs predicted

### 💾 Export Data
- **Multiple Excel Files**: 3 file output terpisah
- **Summary Statistics**: Ringkasan semua analisis
- **Enhanced Dataset**: Dataset lengkap dengan hasil analisis
- **Hotspot Analysis**: Detail hotspot dan coldspot

## 📦 Instalasi

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- pandas >= 1.5.0
- numpy >= 1.21.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0
- plotly >= 5.0.0
- hdbscan >= 0.8.29
- scikit-learn >= 1.1.0
- scipy >= 1.9.0
- networkx >= 2.8.0
- umap-learn >= 0.5.3
- openpyxl >= 3.0.0

## 🎯 Penggunaan

### 1. Jalankan Script
```bash
python3 spatial_analysis_fixed.py
```

### 2. Input Data
Script akan mencoba load file Excel berikut (dalam urutan prioritas):
- `Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx`
- `Tokopedia_sarung tangan.xlsx`

Jika file tidak ditemukan, script akan membuat data dummy untuk demo.

### 3. Output Files
Setelah selesai, akan dihasilkan 3 file Excel:

#### a. `spatial_analysis_results.xlsx`
- **Sheet 1**: Summary_Statistics - Ringkasan semua metrics
- **Sheet 2**: Enhanced_Dataset - Dataset lengkap dengan hasil analisis
- **Sheet 3**: Spatial_Analysis - Hasil analisis spasial per variabel

#### b. `Tokopedia_sarung_tangan_spatial_analysis.xlsx`
Dataset lengkap dengan kolom tambahan:
- `latitude`, `longitude`: Koordinat geografis
- `cluster`: Label cluster HDBSCAN
- `{variable}_hotspot`: Indikator hotspot per variabel
- `{variable}_coldspot`: Indikator coldspot per variabel
- `{variable}_gi_star`: Nilai Getis-Ord Gi* per variabel
- `gwr_prediction`: Prediksi GWR
- `gwr_residual`: Residual GWR
- `analysis_date`: Tanggal analisis
- `data_source`: Sumber data
- `analysis_type`: Jenis analisis

#### c. `hotspot_analysis.xlsx`
Detail hotspot dan coldspot:
- `Variable`: Nama variabel
- `City`: Nama kota
- `Latitude`, `Longitude`: Koordinat
- `Value`: Nilai variabel
- `Gi_Star`: Nilai Getis-Ord Gi*
- `Type`: Hotspot/Coldspot

## 🔧 Konfigurasi

### Koordinat Dummy
Dictionary `city_coordinates_dummy` berisi koordinat untuk 100+ kota di Indonesia. Format:
```python
'Kota': [latitude, longitude]
```

### Parameter HDBSCAN
```python
min_cluster_sizes = [5, 10, 15, 20]
min_samples_list = [3, 5, 7, 10]
```

### Hotspot Threshold
```python
hotspot_threshold = 1.96  # 95% confidence level
coldspot_threshold = -1.96
```

## 📊 Interpretasi Hasil

### Global Moran's I
- **> 0.3**: Spatial clustering yang kuat (positive autocorrelation)
- **0.1 - 0.3**: Spatial clustering sedang (positive autocorrelation)
- **-0.1 - 0.1**: Spatial randomness
- **-0.3 - -0.1**: Spatial dispersion sedang (negative autocorrelation)
- **< -0.3**: Spatial dispersion yang kuat (negative autocorrelation)

### Getis-Ord Gi*
- **> 1.96**: Hotspot (signifikan pada level 95%)
- **< -1.96**: Coldspot (signifikan pada level 95%)
- **-1.96 - 1.96**: Normal area

### HDBSCAN Clustering
- **Silhouette Score**: Semakin tinggi semakin baik (range -1 sampai 1)
- **Calinski-Harabasz Score**: Semakin tinggi semakin baik
- **Noise Points**: Data yang tidak masuk ke cluster manapun

## 🎨 Visualisasi

### Interactive Maps
- **Clustering Map**: Distribusi cluster secara spasial
- **Hotspot Maps**: Lokasi hotspot dan coldspot per variabel
- **Hover Information**: Detail data saat hover

### Statistical Plots
- **Box Plots**: Distribusi variabel per cluster
- **Moran's I Bar Chart**: Spatial autocorrelation per variabel
- **GWR Scatter Plot**: Actual vs predicted values

## 🔍 Troubleshooting

### Error: ModuleNotFoundError
```bash
pip3 install --break-system-packages -r requirements.txt
```

### Error: ImportError plotly
Script sudah di-fix untuk environment non-notebook.

### File Not Found
Script akan otomatis membuat data dummy jika file Excel tidak ditemukan.

## 📈 Contoh Output

```
🚀 MEMULAI ANALISIS SPASIAL LANJUTAN DENGAN KOORDINAT DUMMY
======================================================================
📊 Total data points: 50
🔍 Jumlah cluster: 2
🌍 Jumlah kota: 50
📈 Variabel target: 4
🗺️  Visualisasi dibuat: 5 peta
💾 File yang di-export: 3 file Excel
```

## 🎯 Keunggulan

1. **Tanpa API**: Tidak memerlukan Google Maps API key
2. **Robust**: Fallback system untuk data yang tidak ditemukan
3. **Comprehensive**: Analisis spasial lengkap dalam satu script
4. **Interactive**: Visualisasi interaktif dengan Plotly
5. **Export Ready**: Output dalam format Excel yang siap digunakan
6. **Professional**: Dikembangkan dengan standar akademis tinggi

## 📞 Support

Script ini dikembangkan oleh dosen sains data dengan 30 tahun pengalaman profesional dan sertifikasi internasional sebagai dosen penguji skripsi.

---

**🎉 Analisis Spasial Berhasil Dilakukan dengan Koordinat Dummy!**