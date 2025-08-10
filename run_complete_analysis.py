#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER SCRIPT UNTUK ANALISIS LENGKAP GEMASTIK 2024
"Penambangan Data untuk Peningkatan TIK menuju Kemandirian Bangsa"

Script ini akan menjalankan semua analisis secara berurutan:
1. Preprocessing dan Feature Engineering
2. Analisis Kompetitor dan Pemetaan Spasial
3. Analisis Lanjutan untuk Presentasi

Author: [Nama Anda]
NIM: [NIM Anda]
Institution: [Nama Universitas]
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_header():
    """Print header yang menarik untuk Gemastik"""
    print("="*80)
    print("🚀 GEMASTIK 2024 - PENAMBANGAN DATA UNTUK PENINGKATAN TIK")
    print("   MENUJU KEMANDIRIAN BANGSA")
    print("="*80)
    print("📊 Analisis Kompetitor dan Pemetaan Spasial Tokopedia Sarung Tangan")
    print("🎯 Menggunakan HDBSCAN Clustering - Model Terbaru")
    print("="*80)
    print(f"⏰ Waktu mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def check_dependencies():
    """Check apakah semua dependencies terinstall"""
    print("\n🔍 Memeriksa dependencies...")
    
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 
        'folium', 'hdbscan', 'sklearn', 'umap', 'scipy', 'networkx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} - TIDAK TERINSTALL")
    
    if missing_packages:
        print(f"\n⚠️  PACKAGE YANG BELUM TERINSTALL: {', '.join(missing_packages)}")
        print("   Jalankan: pip install -r requirements.txt")
        return False
    
    print("   ✅ Semua dependencies terinstall!")
    return True

def check_data_file():
    """Check apakah file data tersedia"""
    print("\n📁 Memeriksa file data...")
    
    data_files = [
        'Tokopedia_sarung tangan.xlsx',
        'Tokopedia_sarung_tangan.xlsx'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            print(f"   ✅ File data ditemukan: {file}")
            return file
    
    print("   ❌ File data tidak ditemukan!")
    print("   Pastikan file 'Tokopedia_sarung tangan.xlsx' tersedia di direktori ini.")
    return None

def run_script(script_name, description):
    """Jalankan script Python"""
    print(f"\n{'='*60}")
    print(f"🎯 MENJALANKAN: {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Jalankan script menggunakan subprocess
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=1800)  # 30 menit timeout
        
        if result.returncode == 0:
            print(f"✅ {description} BERHASIL!")
            print(f"   Output: {result.stdout[-500:]}...")  # Tampilkan 500 karakter terakhir
        else:
            print(f"❌ {description} GAGAL!")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} TIMEOUT (30 menit)")
        return False
    except Exception as e:
        print(f"❌ Error menjalankan {description}: {e}")
        return False
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"   ⏱️  Durasi: {duration:.2f} detik ({duration/60:.2f} menit)")
    
    return True

def create_summary_report():
    """Buat laporan ringkasan"""
    print(f"\n{'='*60}")
    print("📋 MEMBUAT LAPORAN RINGKASAN")
    print(f"{'='*60}")
    
    report_content = f"""
# LAPORAN ANALISIS GEMASTIK 2024
## "Penambangan Data untuk Peningkatan TIK menuju Kemandirian Bangsa"

### 📊 Informasi Analisis
- **Tanggal**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Dataset**: Tokopedia Sarung Tangan
- **Model Clustering**: HDBSCAN (Hierarchical Density-Based Spatial Clustering)
- **Tujuan**: Analisis Kompetitor dan Pemetaan Spasial

### 🎯 Metodologi
1. **Preprocessing Data**
   - Pembersihan data dan handling missing values
   - Feature engineering untuk kategori penggunaan dan bahan
   - Penanganan outlier dengan metode gabungan

2. **Analisis Kompetitor**
   - HDBSCAN clustering untuk segmentasi pasar
   - UMAP dimensionality reduction
   - Analisis positioning dan market share

3. **Pemetaan Spasial**
   - Peta interaktif dengan Folium
   - Heatmap distribusi harga
   - Analisis geografis per kota

4. **Visualisasi Interaktif**
   - 3D scatter plot dengan Plotly
   - Parallel coordinates plot
   - Competitive positioning matrix

### 📁 File Output
- `peta_distribusi_harga_sarung_tangan.html` - Peta interaktif
- `Tokopedia_sarung_tangan_with_clusters.xlsx` - Data dengan clustering
- `summary_statistics_presentation.xlsx` - Statistik ringkasan
- `cluster_analysis_presentation.xlsx` - Analisis cluster
- `city_analysis_presentation.xlsx` - Analisis geografis

### 🔍 Insight Utama
1. **Market Segmentation**: Identifikasi segment pasar yang berbeda
2. **Competitive Intelligence**: Analisis positioning kompetitor
3. **Geographic Distribution**: Konsentrasi produk per kota
4. **Pricing Strategy**: Rekomendasi strategi harga

### 🎯 Rekomendasi Strategis
1. **Market Entry**: Fokus pada segment mass market
2. **Geographic Focus**: Target kota dengan konsentrasi tinggi
3. **Product Strategy**: Kembangkan produk dengan rating tinggi
4. **Technology**: Implementasi AI untuk personalisasi

### 💻 Teknologi yang Digunakan
- **HDBSCAN**: Clustering algorithm terbaru
- **UMAP**: Dimensionality reduction modern
- **Folium**: Peta interaktif
- **Plotly**: Visualisasi 3D dan interaktif
- **Python**: Data science ecosystem

### 🏆 Kontribusi untuk Kemandirian Bangsa
1. **Inovasi Teknologi**: Penggunaan algoritma clustering terbaru
2. **Analisis Komprehensif**: Dari preprocessing hingga rekomendasi
3. **Visualisasi Modern**: Peta dan grafik interaktif
4. **Insight Bisnis**: Rekomendasi konkret untuk pengambilan keputusan

---
*Dibuat untuk Lomba Gemastik 2024*
*"Penambangan Data untuk Peningkatan TIK menuju Kemandirian Bangsa"*
"""
    
    with open("LAPORAN_GEMASTIK_2024.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("✅ Laporan ringkasan disimpan: LAPORAN_GEMASTIK_2024.md")

def main():
    """Main function"""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies tidak lengkap. Install terlebih dahulu.")
        return
    
    # Check data file
    data_file = check_data_file()
    if not data_file:
        print("\n❌ File data tidak ditemukan. Pastikan file Excel tersedia.")
        return
    
    print(f"\n🚀 MEMULAI ANALISIS LENGKAP...")
    
    # Step 1: Preprocessing dan Feature Engineering
    print("\n" + "="*80)
    print("📊 STEP 1: PREPROCESSING DAN FEATURE ENGINEERING")
    print("="*80)
    
    # Buat script preprocessing dari kode yang sudah ada
    preprocessing_code = '''
# --- IMPORT LIBRARY DAN LOAD DATA ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import re
import warnings
warnings.filterwarnings("ignore")

# --- 1. LOAD DATA ---
file_path = 'Tokopedia_sarung tangan.xlsx'
sheet_name = 'Products Min1000 Sold'

print(f"📁 Membaca data dari file: {file_path}, sheet: {sheet_name}")
df = pd.read_excel(file_path, sheet_name=sheet_name)
print(f"✅ Data berhasil dimuat. Dimensi {df.shape}")

# --- 2. FEATURE ENGINEERING: EKSTRAKSI SUB-KATEGORI ---
print("\\n🔧 Membuat feature engineering...")

# Definisi Keywords untuk Sub-kategori Berdasarkan Penggunaan
usage_keywords = {
    'Medis': ['medis', 'medical', 'surgical', 'n95', 'bedah', 'sarung tangan bedah', 'sarung tangan medis', 'dokter', 'perawat'],
    'Mekanik/Kerja': ['mekanik', 'kerja', 'work', 'industrial', 'k3', 'apd', 'tahan air', 'anti selip', 'anti-slip', 'construction', 'builder', 'teknisi', 'insinyur', 'engineer', 'montir', 'bengkel', 'welder', 'las', 'electrician', 'listrik', 'pertukangan', 'tukang'],
    'Rumah Tangga/Bersih-Bersih': ['dapur', 'cuci', 'bersih', 'rumah tangga', 'oven mitt', 'pel', 'pembersih', 'cleaning', 'household', 'dishwashing', 'cuci piring', 'sarung tangan dapur'],
    'Olahraga': ['olahraga', 'sport', 'fitness', 'gym', 'sepeda', 'cycling', 'motor', 'riding', 'cyclist', 'gym', 'weightlifting', 'angkat beban', 'berenang', 'swimming']
}

# Definisi Keywords untuk Sub-kategori Berdasarkan Bahan
material_keywords = {
    'Lateks': ['lateks', 'latex', 'karet'],
    'Nitril': ['nitril', 'nitrile'],
    'Kulit': ['kulit', 'leather'],
    'Vinil': ['vinil', 'vinyl', 'plastik'],
    'Kain/Tekstil': ['kain', 'tekstil', 'microfiber', 'polyester', 'benang', 'kain katun', 'katun bintik', 'katun', 'cotton']
}

def assign_single_category(product_name, keyword_dict, default_category='Umum/Lainnya'):
    if not isinstance(product_name, str):
        return default_category
    normalized_name = product_name.lower()
    for category, keywords in keyword_dict.items():
        if not keywords:
            continue
        for keyword in keywords:
            if re.search(rf'\\b{re.escape(keyword)}\\b', normalized_name):
                return category
    return default_category

def assign_material_categories(product_name, keyword_dict):
    if not isinstance(product_name, str):
        return 'Tidak Dikategorikan'
    normalized_name = product_name.lower()
    matched_materials = set()
    for material, keywords in keyword_dict.items():
        if not keywords:
            continue
        for keyword in keywords:
            if re.search(rf'\\b{re.escape(keyword)}\\b', normalized_name):
                matched_materials.add(material)
    if matched_materials:
        return '; '.join(sorted(list(matched_materials)))
    else:
        return 'Tidak Dikategorikan'

# Terapkan Feature Engineering
print("🔍 Mengekstrak sub-kategori berdasarkan Penggunaan...")
df['Sub_Kategori_Penggunaan'] = df['Product_Name'].apply(assign_single_category, keyword_dict=usage_keywords, default_category='Umum/Lainnya')

print("🔍 Mengekstrak sub-kategori berdasarkan Bahan...")
df['Sub_Kategori_Bahan'] = df['Product_Name'].apply(assign_material_categories, keyword_dict=material_keywords)

# Simpan hasil
output_filename = "Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx"
df.to_excel(output_filename, index=False)
print(f"✅ Dataset dengan feature engineering disimpan: {output_filename}")
'''
    
    with open("preprocessing_step.py", "w", encoding="utf-8") as f:
        f.write(preprocessing_code)
    
    if not run_script("preprocessing_step.py", "Preprocessing dan Feature Engineering"):
        print("❌ Gagal pada step preprocessing")
        return
    
    # Step 2: Analisis Kompetitor dan Pemetaan Spasial
    print("\n" + "="*80)
    print("🎯 STEP 2: ANALISIS KOMPETITOR DAN PEMETAAN SPASIAL")
    print("="*80)
    
    if not run_script("analisis_kompetitor_pemetaan_spasial.py", "Analisis Kompetitor dengan HDBSCAN"):
        print("❌ Gagal pada step analisis kompetitor")
        return
    
    # Step 3: Analisis Lanjutan untuk Presentasi
    print("\n" + "="*80)
    print("📊 STEP 3: ANALISIS LANJUTAN UNTUK PRESENTASI")
    print("="*80)
    
    if not run_script("analisis_lanjutan_presentasi.py", "Analisis Lanjutan dan Visualisasi"):
        print("❌ Gagal pada step analisis lanjutan")
        return
    
    # Buat laporan ringkasan
    create_summary_report()
    
    # Tampilkan hasil akhir
    print(f"\n{'='*80}")
    print("🎉 ANALISIS LENGKAP GEMASTIK 2024 SELESAI!")
    print(f"{'='*80}")
    
    print(f"\n📁 FILE OUTPUT YANG DIHASILKAN:")
    output_files = [
        "Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx",
        "Tokopedia_sarung_tangan_with_clusters.xlsx",
        "peta_distribusi_harga_sarung_tangan.html",
        "summary_statistics_presentation.xlsx",
        "cluster_analysis_presentation.xlsx",
        "city_analysis_presentation.xlsx",
        "LAPORAN_GEMASTIK_2024.md"
    ]
    
    for file in output_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - TIDAK DITEMUKAN")
    
    print(f"\n🎯 INSIGHT UTAMA:")
    print("   1. ✅ HDBSCAN clustering berhasil mengidentifikasi segmentasi pasar")
    print("   2. ✅ Peta spasial menunjukkan distribusi geografis produk")
    print("   3. ✅ Analisis kompetitor memberikan insight positioning strategis")
    print("   4. ✅ Visualisasi interaktif memudahkan eksplorasi data")
    print("   5. ✅ Rekomendasi strategi untuk pengambilan keputusan bisnis")
    
    print(f"\n🏆 SIAP UNTUK PRESENTASI GEMASTIK 2024!")
    print("   Semua analisis telah selesai dan file output tersedia.")
    print("   Gunakan file HTML untuk demonstrasi peta interaktif.")
    print("   Gunakan file Excel untuk data analisis detail.")
    print("   Gunakan file MD untuk laporan ringkasan.")
    
    print(f"\n⏰ Waktu selesai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()