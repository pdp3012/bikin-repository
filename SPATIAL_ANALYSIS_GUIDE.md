# 🗺️ Panduan Analisis Spasial Lanjutan untuk Gemastik 2024

## 📋 Daftar Isi
1. [Overview](#overview)
2. [Fitur Utama](#fitur-utama)
3. [Instalasi](#instalasi)
4. [Penggunaan](#penggunaan)
5. [Interpretasi Hasil](#interpretasi-hasil)
6. [Kontribusi untuk Gemastik](#kontribusi-untuk-gemastik)

## 🎯 Overview

Script `analisis_spasial_lanjutan.py` merupakan implementasi analisis spasial tingkat lanjut yang mengintegrasikan:

- **Geocoding** dengan Google Maps API
- **Hotspot Detection** menggunakan Global Moran's I dan Getis-Ord Gi*
- **Spatial Cross-Validation** untuk HDBSCAN
- **Geographically Weighted Regression (GWR)**
- **Visualisasi spasial interaktif**

## 🚀 Fitur Utama

### 1. 🌍 Geocoding & Standarisasi Lokasi
```python
# Menggunakan Google Maps API untuk konversi nama kota ke koordinat
GOOGLE_MAPS_API_KEY = "AIzaSyA8vber5Sovu6ufeQjyW4W1F0_APLsYtpE"
```

**Fungsi:**
- Konversi `Shop_City` → koordinat (lat, lng)
- Batch processing dengan rate limiting
- Error handling untuk kota yang tidak ditemukan

### 2. 🔥 Hotspot Detection yang Kredibel

#### Global Moran's I
```python
def global_morans_i(values, distances, weights=None):
    """
    Menghitung autokorelasi spasial global
    """
```

**Interpretasi:**
- **> 0.3**: Kuat autokorelasi positif (cluster)
- **0.1 - 0.3**: Autokorelasi moderat
- **-0.1 - 0.1**: Autokorelasi lemah
- **< -0.1**: Autokorelasi negatif (dispersi)

#### Getis-Ord Gi*
```python
def getis_ord_gi_star(values, distances, weights=None):
    """
    Mendeteksi hotspot/coldspot lokal
    """
```

**Interpretasi:**
- **> 1.96**: Hotspot (95% confidence)
- **< -1.96**: Coldspot (95% confidence)
- **-1.96 - 1.96**: Tidak signifikan

### 3. 🎯 Spatial Cross-Validation untuk HDBSCAN

```python
def spatial_block_cv(X, y, coordinates, n_splits=5):
    """
    Spatial block cross-validation untuk mencegah kebocoran spasial
    """
```

**Keunggulan:**
- Mencegah overfitting spasial
- Optimasi parameter HDBSCAN yang robust
- Validasi yang "benar secara spasial"

### 4. 📊 Spatial Modeling (GWR)

```python
def simple_gwr(X, y, coordinates, bandwidth=None):
    """
    Geographically Weighted Regression
    """
```

**Fitur:**
- Koefisien berbeda per lokasi
- Bandwidth optimization
- R² lokal untuk setiap titik

### 5. 🎨 Visualisasi Spasial Interaktif

- **Hotspot Map**: Peta dengan hotspot/coldspot
- **GWR Coefficient Maps**: Peta koefisien lokal
- **Spatial Autocorrelation**: Analisis autokorelasi
- **Cross-Validation Comparison**: Perbandingan CV

## 📦 Instalasi

### 1. Install Dependencies
```bash
pip install -r requirements_spatial.txt
```

### 2. Setup Google Maps API
```python
# Masukkan API key Anda
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"
```

### 3. Jalankan Script
```bash
python analisis_spasial_lanjutan.py
```

## 🔧 Penggunaan

### 1. Persiapan Data
```python
# Load data yang sudah diproses
df = pd.read_excel("Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx")
```

### 2. Geocoding
```python
# Proses geocoding otomatis
city_coordinates = batch_geocode_cities(df, GOOGLE_MAPS_API_KEY)
```

### 3. Hotspot Detection
```python
# Analisis autokorelasi dan hotspot
moran_i_price = global_morans_i(price_values, distances)
gi_star_price = getis_ord_gi_star(price_values, distances)
```

### 4. Spatial Modeling
```python
# GWR untuk modeling spasial
coefs_gwr, intercepts_gwr, r2_gwr = simple_gwr(X_model_scaled, y_model, coordinates_list)
```

## 📊 Interpretasi Hasil

### 1. Spatial Autocorrelation
```python
# Contoh output
Global Moran's I untuk harga: 0.2345
→ Autokorelasi spasial moderat
```

**Interpretasi:**
- **Kuat (>0.3)**: Ada cluster harga yang jelas
- **Moderat (0.1-0.3)**: Ada pola spasial
- **Lemah (-0.1-0.1)**: Harga tersebar acak
- **Negatif (<-0.1)**: Harga terdispersi

### 2. Hotspot Analysis
```python
Price Hotspots: 15 (12.5%)
Price Coldspots: 8 (6.7%)
```

**Interpretasi:**
- **Hotspots**: Area dengan harga tinggi yang signifikan
- **Coldspots**: Area dengan harga rendah yang signifikan
- **Regular**: Area dengan harga normal

### 3. GWR Results
```python
Rata-rata R²: 0.7234
Koefisien Sold_Count:
   Rata-rata: 0.1234
   Std Dev: 0.0567
   Range: 0.2345
```

**Interpretasi:**
- **R² tinggi**: Model menjelaskan variasi harga dengan baik
- **Koefisien bervariasi**: Pengaruh faktor berbeda antar lokasi
- **Range besar**: Variasi spasial yang signifikan

### 4. Cross-Validation
```python
Traditional CV mean R²: 0.8234
Spatial CV mean R²: 0.7123
Perbedaan: 0.1111
→ Ada kebocoran spasial yang signifikan
```

**Interpretasi:**
- **Perbedaan besar (>0.1)**: Ada kebocoran spasial
- **Perbedaan kecil (<0.05)**: Validasi robust

## 🏆 Kontribusi untuk Gemastik

### 1. 🎯 Inovasi Teknologi
- **HDBSCAN**: Model clustering terbaru yang robust
- **Spatial Analysis**: Analisis spasial tingkat lanjut
- **GWR**: Modeling spasial yang sophisticated

### 2. 📊 Metodologi yang Kredibel
- **Hotspot Detection**: Menggunakan metode statistik yang valid
- **Spatial Cross-Validation**: Mencegah overfitting
- **Geocoding**: Akurasi lokasi yang tinggi

### 3. 🔍 Insight yang Mendalam
- **Spatial Patterns**: Pola spasial yang tersembunyi
- **Local Variations**: Variasi lokal yang unik
- **Strategic Recommendations**: Rekomendasi berbasis spasial

### 4. 🎨 Visualisasi yang Menarik
- **Interactive Maps**: Peta interaktif dengan Plotly
- **Hotspot Visualization**: Visualisasi hotspot yang jelas
- **Coefficient Maps**: Peta koefisien yang informatif

### 5. 💼 Aplikasi Bisnis
- **Market Entry**: Strategi masuk pasar berbasis spasial
- **Pricing Strategy**: Pricing dinamis berdasarkan lokasi
- **Operational Optimization**: Optimasi operasional spasial

## 📁 Output Files

### 1. Data Files
- `spatial_analysis_results.xlsx`: Hasil analisis spasial
- `Tokopedia_sarung_tangan_spatial_analysis.xlsx`: Dataset dengan analisis spasial
- `hotspot_analysis.xlsx`: Data hotspot

### 2. Visualizations
- **Hotspot Map**: Peta dengan hotspot/coldspot
- **GWR Coefficient Maps**: Peta koefisien lokal
- **Spatial Autocorrelation**: Analisis autokorelasi
- **Cross-Validation Comparison**: Perbandingan CV

## 🚀 Tips untuk Presentasi

### 1. Highlight Inovasi
- "Implementasi analisis spasial tingkat lanjut"
- "Penggunaan HDBSCAN yang masih jarang"
- "Spatial cross-validation untuk validasi robust"

### 2. Demonstrasi Visual
- Tampilkan peta hotspot interaktif
- Jelaskan variasi koefisien GWR
- Bandingkan traditional vs spatial CV

### 3. Insight Bisnis
- "Hotspot menunjukkan area premium"
- "Coldspot untuk penetrasi harga rendah"
- "Dynamic pricing berdasarkan lokasi"

### 4. Kontribusi Teknologi
- "Geocoding dengan akurasi tinggi"
- "Hotspot detection yang kredibel"
- "Spatial modeling yang sophisticated"

## 🎉 Kesimpulan

Script analisis spasial lanjutan ini memberikan:

1. **🔬 Metodologi yang Kredibel**: Menggunakan metode statistik yang valid
2. **🎯 Insight yang Mendalam**: Pola spasial yang tersembunyi
3. **💼 Aplikasi Bisnis**: Rekomendasi strategis yang actionable
4. **🎨 Visualisasi Menarik**: Peta interaktif yang informatif
5. **🏆 Kontribusi Teknologi**: Implementasi analisis spasial tingkat lanjut

**Siap untuk memenangkan Gemastik 2024!** 🚀🏆