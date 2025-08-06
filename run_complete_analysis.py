#!/usr/bin/env python3
"""
Complete Tokopedia Analysis Workflow
Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman

Script ini mengintegrasikan:
1. Scraping data dari Tokopedia
2. Testing dan validasi data
3. Analisis dan visualisasi data
4. Export laporan lengkap
"""

import os
import sys
import time
from datetime import datetime
from tokopedia_scraper import TokopediaScraper
from data_analyzer import TokopediaDataAnalyzer

def print_banner():
    """Tampilkan banner aplikasi"""
    print("="*70)
    print("🔍 TOKOPEDIA COMPLETE ANALYSIS WORKFLOW")
    print("="*70)
    print("Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman")
    print("Bersertifikasi Internasional - 30 Tahun Pengalaman")
    print("="*70)

def check_dependencies():
    """Cek apakah semua dependencies terinstall"""
    print("🔧 Memeriksa dependencies...")
    
    required_modules = [
        'selenium', 'pandas', 'bs4', 'matplotlib', 
        'seaborn', 'numpy', 'requests'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - TIDAK TERINSTALL")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Dependencies yang hilang: {', '.join(missing_modules)}")
        print("Jalankan: pip install -r requirements.txt")
        return False
    
    print("✅ Semua dependencies terinstall!")
    return True

def get_user_input():
    """Dapatkan input dari user"""
    print("\n📝 KONFIGURASI SCRAPING")
    print("-" * 40)
    
    # Kata kunci pencarian
    search_query = input("Masukkan kata kunci pencarian: ").strip()
    if not search_query:
        print("❌ Kata kunci tidak boleh kosong!")
        return None
    
    # Jumlah scroll
    try:
        max_scrolls = int(input("Jumlah maksimal scroll (default: 5): ").strip() or "5")
        if max_scrolls < 1:
            max_scrolls = 5
    except ValueError:
        max_scrolls = 5
    
    # Mode headless
    headless_choice = input("Gunakan mode headless? (y/n, default: n): ").strip().lower()
    headless = headless_choice in ['y', 'yes']
    
    # Nama file output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = search_query.replace(' ', '_').replace('/', '_')
    base_filename = f"tokopedia_{safe_query}_{timestamp}"
    
    return {
        'search_query': search_query,
        'max_scrolls': max_scrolls,
        'headless': headless,
        'base_filename': base_filename
    }

def run_scraping(config):
    """Jalankan proses scraping"""
    print(f"\n🚀 MEMULAI SCRAPING")
    print(f"Kata kunci: {config['search_query']}")
    print(f"Max scrolls: {config['max_scrolls']}")
    print(f"Headless mode: {'Ya' if config['headless'] else 'Tidak'}")
    print("-" * 50)
    
    # Inisialisasi scraper
    scraper = TokopediaScraper(headless=config['headless'])
    
    try:
        # Lakukan scraping
        start_time = time.time()
        products_data = scraper.scrape_products(
            config['search_query'], 
            max_scrolls=config['max_scrolls']
        )
        end_time = time.time()
        
        if products_data:
            print(f"\n✅ SCRAPING BERHASIL!")
            print(f"Total produk: {len(products_data)}")
            print(f"Waktu eksekusi: {end_time - start_time:.2f} detik")
            
            # Simpan data
            csv_filename = f"{config['base_filename']}.csv"
            json_filename = f"{config['base_filename']}.json"
            
            scraper.save_to_csv(products_data, csv_filename)
            scraper.save_to_json(products_data, json_filename)
            
            return {
                'success': True,
                'data': products_data,
                'csv_file': csv_filename,
                'json_file': json_filename,
                'count': len(products_data)
            }
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
            return {'success': False}
            
    except Exception as e:
        print(f"❌ Error saat scraping: {str(e)}")
        return {'success': False, 'error': str(e)}

def run_analysis(scraping_result):
    """Jalankan analisis data"""
    if not scraping_result['success']:
        print("❌ Tidak dapat melakukan analisis karena scraping gagal")
        return
    
    print(f"\n📊 MEMULAI ANALISIS DATA")
    print("-" * 50)
    
    # Gunakan file JSON untuk analisis
    json_file = scraping_result['json_file']
    
    try:
        # Inisialisasi analyzer
        analyzer = TokopediaDataAnalyzer(json_file)
        
        if analyzer.df is None:
            print("❌ Gagal memuat data untuk analisis")
            return
        
        # Bersihkan data
        analyzer.clean_data()
        
        # Generate ringkasan
        analyzer.generate_summary()
        
        # Buat visualisasi
        print("\n📈 Membuat visualisasi...")
        analyzer.create_visualizations(save_plots=True)
        
        # Cari produk terbaik
        print("\n🏆 Mencari produk terbaik...")
        analyzer.find_best_products('rating', 5)
        
        # Export laporan
        analyzer.export_analysis_report()
        
        print("\n✅ ANALISIS SELESAI!")
        
    except Exception as e:
        print(f"❌ Error saat analisis: {str(e)}")

def generate_final_report(scraping_result, config):
    """Generate laporan akhir"""
    if not scraping_result['success']:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_filename = f"final_report_{config['base_filename']}.txt"
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("LAPORAN LENGKAP ANALISIS TOKOPEDIA\n")
            f.write("="*60 + "\n")
            f.write(f"Tanggal: {timestamp}\n")
            f.write(f"Dibuat oleh: Dosen Data Mining (30 tahun pengalaman)\n")
            f.write("="*60 + "\n\n")
            
            f.write("KONFIGURASI SCRAPING:\n")
            f.write("-"*30 + "\n")
            f.write(f"Kata kunci: {config['search_query']}\n")
            f.write(f"Max scrolls: {config['max_scrolls']}\n")
            f.write(f"Headless mode: {'Ya' if config['headless'] else 'Tidak'}\n\n")
            
            f.write("HASIL SCRAPING:\n")
            f.write("-"*20 + "\n")
            f.write(f"Total produk: {scraping_result['count']}\n")
            f.write(f"File CSV: {scraping_result['csv_file']}\n")
            f.write(f"File JSON: {scraping_result['json_file']}\n\n")
            
            f.write("FILE OUTPUT:\n")
            f.write("-"*15 + "\n")
            f.write(f"1. Data mentah: {scraping_result['csv_file']}\n")
            f.write(f"2. Data JSON: {scraping_result['json_file']}\n")
            f.write(f"3. Visualisasi: tokopedia_analysis_*.png\n")
            f.write(f"4. Laporan analisis: analysis_report_*.txt\n")
            f.write(f"5. Laporan lengkap: {report_filename}\n\n")
            
            f.write("CARA MENGGUNAKAN HASIL:\n")
            f.write("-"*25 + "\n")
            f.write("1. Buka file CSV untuk analisis di Excel/Google Sheets\n")
            f.write("2. Gunakan file JSON untuk analisis lanjutan dengan Python\n")
            f.write("3. Lihat visualisasi untuk insight grafis\n")
            f.write("4. Baca laporan analisis untuk ringkasan statistik\n\n")
            
            f.write("TIPS ANALISIS LANJUTAN:\n")
            f.write("-"*25 + "\n")
            f.write("1. Analisis tren harga berdasarkan lokasi\n")
            f.write("2. Identifikasi produk dengan rating tinggi tapi harga rendah\n")
            f.write("3. Bandingkan performa penjual berdasarkan lokasi\n")
            f.write("4. Analisis seasonal pattern jika data dikumpulkan berkala\n")
            
        print(f"✅ Laporan lengkap disimpan ke: {report_filename}")
        
    except Exception as e:
        print(f"❌ Error saat membuat laporan: {str(e)}")

def main():
    """Fungsi utama"""
    print_banner()
    
    # Cek dependencies
    if not check_dependencies():
        print("\n❌ Silakan install dependencies terlebih dahulu!")
        return
    
    # Dapatkan input user
    config = get_user_input()
    if config is None:
        return
    
    # Jalankan scraping
    scraping_result = run_scraping(config)
    
    # Jalankan analisis jika scraping berhasil
    if scraping_result['success']:
        run_analysis(scraping_result)
        
        # Generate laporan akhir
        generate_final_report(scraping_result, config)
        
        print("\n" + "="*70)
        print("🎉 WORKFLOW SELESAI!")
        print("="*70)
        print("File yang dihasilkan:")
        print(f"  📄 Data CSV: {scraping_result['csv_file']}")
        print(f"  📄 Data JSON: {scraping_result['json_file']}")
        print(f"  📊 Visualisasi: tokopedia_analysis_*.png")
        print(f"  📋 Laporan: analysis_report_*.txt")
        print(f"  📋 Laporan Lengkap: final_report_{config['base_filename']}.txt")
        print("\nTerima kasih telah menggunakan Tokopedia Complete Analysis Workflow!")
        print("Dibuat dengan ❤️ oleh Dosen Data Mining dengan 30 tahun pengalaman")
    else:
        print("\n❌ Workflow gagal. Silakan coba lagi!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Workflow dihentikan oleh user")
        print("Terima kasih telah menggunakan aplikasi ini!")
    except Exception as e:
        print(f"\n❌ Error tidak terduga: {str(e)}")
        print("Silakan coba lagi atau hubungi support!")