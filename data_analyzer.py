#!/usr/bin/env python3
"""
Data Analyzer untuk Hasil Scraping Tokopedia
Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TokopediaDataAnalyzer:
    def __init__(self, data_file):
        """
        Inisialisasi analyzer
        Args:
            data_file (str): Path ke file CSV atau JSON
        """
        self.data_file = data_file
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load data dari file CSV atau JSON"""
        try:
            if self.data_file.endswith('.csv'):
                self.df = pd.read_csv(self.data_file)
            elif self.data_file.endswith('.json'):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.df = pd.DataFrame(data)
            else:
                raise ValueError("File harus berformat CSV atau JSON")
                
            print(f"✅ Data berhasil dimuat: {len(self.df)} produk")
            
        except Exception as e:
            print(f"❌ Error saat memuat data: {str(e)}")
            self.df = None
    
    def clean_data(self):
        """Membersihkan dan memproses data"""
        if self.df is None:
            return
            
        print("🧹 Membersihkan data...")
        
        # Copy dataframe
        df_clean = self.df.copy()
        
        # Bersihkan kolom harga
        if 'harga_produk' in df_clean.columns:
            df_clean['harga_bersih'] = df_clean['harga_produk'].apply(self.extract_price)
        
        # Bersihkan kolom rating
        if 'rating_produk' in df_clean.columns:
            df_clean['rating_bersih'] = df_clean['rating_produk'].apply(self.extract_rating)
        
        # Bersihkan kolom jumlah terjual
        if 'jumlah_terjual' in df_clean.columns:
            df_clean['terjual_bersih'] = df_clean['jumlah_terjual'].apply(self.extract_sold_count)
        
        # Ekstrak lokasi utama
        if 'lokasi_toko' in df_clean.columns:
            df_clean['kota'] = df_clean['lokasi_toko'].apply(self.extract_city)
        
        self.df = df_clean
        print("✅ Data berhasil dibersihkan")
    
    def extract_price(self, price_str):
        """Ekstrak angka harga dari string"""
        if pd.isna(price_str) or price_str == '':
            return np.nan
            
        # Hapus karakter non-digit kecuali titik
        price_clean = re.sub(r'[^\d.]', '', str(price_str))
        
        try:
            return float(price_clean)
        except:
            return np.nan
    
    def extract_rating(self, rating_str):
        """Ekstrak angka rating dari string"""
        if pd.isna(rating_str) or rating_str == '':
            return np.nan
            
        # Cari angka dengan format x.x
        match = re.search(r'(\d+\.?\d*)', str(rating_str))
        if match:
            try:
                return float(match.group(1))
            except:
                return np.nan
        return np.nan
    
    def extract_sold_count(self, sold_str):
        """Ekstrak jumlah terjual dari string"""
        if pd.isna(sold_str) or sold_str == '':
            return np.nan
            
        sold_str = str(sold_str).lower()
        
        # Cari angka
        numbers = re.findall(r'(\d+)', sold_str)
        if numbers:
            try:
                base_num = int(numbers[0])
                
                # Handle multiplier (rb, rb+, etc)
                if 'rb' in sold_str or 'k' in sold_str:
                    if '+' in sold_str:
                        return base_num * 1000  # Minimal value
                    else:
                        return base_num * 1000
                elif 'jt' in sold_str or 'm' in sold_str:
                    if '+' in sold_str:
                        return base_num * 1000000  # Minimal value
                    else:
                        return base_num * 1000000
                else:
                    return base_num
            except:
                return np.nan
        return np.nan
    
    def extract_city(self, location_str):
        """Ekstrak kota dari string lokasi"""
        if pd.isna(location_str) or location_str == '':
            return 'Unknown'
            
        # Split berdasarkan separator
        parts = str(location_str).split('|')
        if parts:
            # Ambil bagian pertama dan bersihkan
            city = parts[0].strip()
            return city
        return 'Unknown'
    
    def generate_summary(self):
        """Generate ringkasan statistik data"""
        if self.df is None:
            return
            
        print("\n" + "="*60)
        print("📊 RINGKASAN STATISTIK DATA")
        print("="*60)
        
        # Basic info
        print(f"Total Produk: {len(self.df)}")
        print(f"Kata Kunci Pencarian: {self.df['search_query'].iloc[0] if 'search_query' in self.df.columns else 'N/A'}")
        
        # Harga analysis
        if 'harga_bersih' in self.df.columns:
            harga_stats = self.df['harga_bersih'].describe()
            print(f"\n💰 ANALISIS HARGA:")
            print(f"  Harga Terendah: Rp {harga_stats['min']:,.0f}")
            print(f"  Harga Tertinggi: Rp {harga_stats['max']:,.0f}")
            print(f"  Harga Rata-rata: Rp {harga_stats['mean']:,.0f}")
            print(f"  Median Harga: Rp {harga_stats['50%']:,.0f}")
        
        # Rating analysis
        if 'rating_bersih' in self.df.columns:
            rating_stats = self.df['rating_bersih'].describe()
            print(f"\n⭐ ANALISIS RATING:")
            print(f"  Rating Terendah: {rating_stats['min']:.1f}")
            print(f"  Rating Tertinggi: {rating_stats['max']:.1f}")
            print(f"  Rating Rata-rata: {rating_stats['mean']:.2f}")
            print(f"  Median Rating: {rating_stats['50%']:.1f}")
        
        # Lokasi analysis
        if 'kota' in self.df.columns:
            print(f"\n📍 ANALISIS LOKASI:")
            city_counts = self.df['kota'].value_counts().head(10)
            for city, count in city_counts.items():
                print(f"  {city}: {count} produk")
    
    def create_visualizations(self, save_plots=True):
        """Membuat visualisasi data"""
        if self.df is None:
            return
            
        print("\n📈 Membuat visualisasi...")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Analisis Data Tokopedia - {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                    fontsize=16, fontweight='bold')
        
        # 1. Distribusi Harga
        if 'harga_bersih' in self.df.columns:
            axes[0, 0].hist(self.df['harga_bersih'].dropna(), bins=20, alpha=0.7, color='skyblue')
            axes[0, 0].set_title('Distribusi Harga Produk')
            axes[0, 0].set_xlabel('Harga (Rp)')
            axes[0, 0].set_ylabel('Frekuensi')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Distribusi Rating
        if 'rating_bersih' in self.df.columns:
            axes[0, 1].hist(self.df['rating_bersih'].dropna(), bins=10, alpha=0.7, color='lightgreen')
            axes[0, 1].set_title('Distribusi Rating Produk')
            axes[0, 1].set_xlabel('Rating')
            axes[0, 1].set_ylabel('Frekuensi')
        
        # 3. Top 10 Kota
        if 'kota' in self.df.columns:
            city_counts = self.df['kota'].value_counts().head(10)
            axes[1, 0].barh(range(len(city_counts)), city_counts.values, color='salmon')
            axes[1, 0].set_yticks(range(len(city_counts)))
            axes[1, 0].set_yticklabels(city_counts.index)
            axes[1, 0].set_title('Top 10 Kota Penjual')
            axes[1, 0].set_xlabel('Jumlah Produk')
        
        # 4. Scatter Plot Harga vs Rating
        if 'harga_bersih' in self.df.columns and 'rating_bersih' in self.df.columns:
            axes[1, 1].scatter(self.df['harga_bersih'], self.df['rating_bersih'], alpha=0.6, color='purple')
            axes[1, 1].set_title('Hubungan Harga vs Rating')
            axes[1, 1].set_xlabel('Harga (Rp)')
            axes[1, 1].set_ylabel('Rating')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_plots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tokopedia_analysis_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✅ Visualisasi disimpan ke: {filename}")
        
        plt.show()
    
    def find_best_products(self, criteria='rating', top_n=10):
        """Mencari produk terbaik berdasarkan kriteria"""
        if self.df is None:
            return
            
        print(f"\n🏆 TOP {top_n} PRODUK BERDASARKAN {criteria.upper()}")
        print("="*60)
        
        if criteria == 'rating' and 'rating_bersih' in self.df.columns:
            best_products = self.df.nlargest(top_n, 'rating_bersih')
        elif criteria == 'price_low' and 'harga_bersih' in self.df.columns:
            best_products = self.df.nsmallest(top_n, 'harga_bersih')
        elif criteria == 'price_high' and 'harga_bersih' in self.df.columns:
            best_products = self.df.nlargest(top_n, 'harga_bersih')
        else:
            print("❌ Kriteria tidak valid atau data tidak tersedia")
            return
        
        for i, (idx, product) in enumerate(best_products.iterrows(), 1):
            print(f"\n{i}. {product['nama_produk'][:50]}...")
            print(f"   Harga: {product['harga_produk']}")
            print(f"   Rating: {product['rating_produk']}")
            print(f"   Lokasi: {product['lokasi_toko']}")
    
    def export_analysis_report(self):
        """Export laporan analisis ke file"""
        if self.df is None:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"analysis_report_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("LAPORAN ANALISIS DATA TOKOPEDIA\n")
            f.write("="*50 + "\n")
            f.write(f"Tanggal Analisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Produk: {len(self.df)}\n")
            f.write(f"Kata Kunci: {self.df['search_query'].iloc[0] if 'search_query' in self.df.columns else 'N/A'}\n\n")
            
            # Statistik harga
            if 'harga_bersih' in self.df.columns:
                harga_stats = self.df['harga_bersih'].describe()
                f.write("STATISTIK HARGA:\n")
                f.write(f"  Min: Rp {harga_stats['min']:,.0f}\n")
                f.write(f"  Max: Rp {harga_stats['max']:,.0f}\n")
                f.write(f"  Mean: Rp {harga_stats['mean']:,.0f}\n")
                f.write(f"  Median: Rp {harga_stats['50%']:,.0f}\n\n")
            
            # Statistik rating
            if 'rating_bersih' in self.df.columns:
                rating_stats = self.df['rating_bersih'].describe()
                f.write("STATISTIK RATING:\n")
                f.write(f"  Min: {rating_stats['min']:.1f}\n")
                f.write(f"  Max: {rating_stats['max']:.1f}\n")
                f.write(f"  Mean: {rating_stats['mean']:.2f}\n")
                f.write(f"  Median: {rating_stats['50%']:.1f}\n\n")
            
            # Top lokasi
            if 'kota' in self.df.columns:
                f.write("TOP 10 LOKASI:\n")
                city_counts = self.df['kota'].value_counts().head(10)
                for city, count in city_counts.items():
                    f.write(f"  {city}: {count} produk\n")
        
        print(f"✅ Laporan analisis disimpan ke: {report_filename}")

def main():
    """Fungsi utama"""
    print("=== TOKOPEDIA DATA ANALYZER ===")
    print("Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman")
    print("="*50)
    
    # Input file
    data_file = input("Masukkan path file data (CSV/JSON): ").strip()
    
    if not data_file:
        print("❌ Path file tidak boleh kosong!")
        return
    
    # Inisialisasi analyzer
    analyzer = TokopediaDataAnalyzer(data_file)
    
    if analyzer.df is None:
        print("❌ Gagal memuat data!")
        return
    
    # Menu analisis
    while True:
        print("\n" + "="*50)
        print("MENU ANALISIS:")
        print("1. Ringkasan Statistik")
        print("2. Visualisasi Data")
        print("3. Produk Terbaik (Berdasarkan Rating)")
        print("4. Produk Termurah")
        print("5. Produk Termahal")
        print("6. Export Laporan")
        print("7. Keluar")
        
        choice = input("\nPilihan Anda (1-7): ").strip()
        
        if choice == "1":
            analyzer.clean_data()
            analyzer.generate_summary()
        elif choice == "2":
            analyzer.clean_data()
            analyzer.create_visualizations()
        elif choice == "3":
            analyzer.clean_data()
            analyzer.find_best_products('rating', 10)
        elif choice == "4":
            analyzer.clean_data()
            analyzer.find_best_products('price_low', 10)
        elif choice == "5":
            analyzer.clean_data()
            analyzer.find_best_products('price_high', 10)
        elif choice == "6":
            analyzer.clean_data()
            analyzer.export_analysis_report()
        elif choice == "7":
            print("Terima kasih!")
            break
        else:
            print("❌ Pilihan tidak valid!")

if __name__ == "__main__":
    main()