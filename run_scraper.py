#!/usr/bin/env python3
"""
Script untuk menjalankan Tokopedia Scraper dengan konfigurasi yang mudah
"""

import sys
import os
from datetime import datetime

def check_dependencies():
    """Check apakah semua dependensi terinstall"""
    try:
        import requests
        import pandas
        import bs4
        import selenium
        import undetected_chromedriver
        print("✅ Semua dependensi terinstall")
        return True
    except ImportError as e:
        print(f"❌ Dependensi tidak lengkap: {e}")
        print("💡 Jalankan: pip install -r requirements.txt")
        return False

def run_scraper():
    """Jalankan scraper dengan konfigurasi default"""
    
    print("🤖 TOKOPEDIA SCRAPER - QUICK START")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    try:
        from tokopedia_scraper_improved import TokopediaScraperImproved
        
        # Konfigurasi default
        keyword = "cabai rawit"
        max_pages = 2
        headless = True
        
        print(f"\n📋 KONFIGURASI DEFAULT:")
        print(f"   🔍 Keyword: '{keyword}'")
        print(f"   📄 Halaman: {max_pages}")
        print(f"   🖥️  Headless: {headless}")
        
        # Konfirmasi
        confirm = input("\n🚀 Jalankan dengan konfigurasi ini? (y/n): ").lower()
        if confirm not in ['y', 'yes', 'ya']:
            print("❌ Dibatalkan")
            return False
        
        # Inisialisasi scraper
        print(f"\n🔧 Inisialisasi scraper...")
        scraper = TokopediaScraperImproved(headless=headless)
        
        # Jalankan scraping
        print(f"\n🎬 MEMULAI SCRAPING...")
        start_time = datetime.now()
        
        products = scraper.search_products_with_scrolling(keyword, max_pages)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Tampilkan hasil
        if products:
            print(f"\n🎉 SCRAPING BERHASIL!")
            print(f"⏱️  Waktu eksekusi: {duration}")
            print(f"📊 Total produk: {len(products)}")
            
            # Tampilkan sample
            print(f"\n📋 SAMPLE DATA:")
            for i, product in enumerate(products[:3]):
                print(f"   {i+1}. {product['nama_produk'][:50]}... | {product['harga']}")
            
            # Simpan otomatis
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tokopedia_scraping_{timestamp}.csv'
            
            if scraper.save_to_csv(products, filename):
                print(f"\n💾 Data disimpan ke: {filename}")
            
        else:
            print(f"\n❌ TIDAK ADA PRODUK YANG BERHASIL DI-SCRAPE")
        
        # Cleanup
        scraper.close_driver()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def run_interactive():
    """Jalankan scraper dengan input interaktif"""
    
    print("🤖 TOKOPEDIA SCRAPER - INTERACTIVE MODE")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    try:
        from tokopedia_scraper_improved import TokopediaScraperImproved
        
        # Input dari user
        keyword = input("\n🔍 Masukkan keyword pencarian: ").strip()
        if not keyword or len(keyword) < 2:
            print("❌ Keyword harus minimal 2 karakter!")
            return False
        
        max_pages_input = input("📄 Jumlah halaman (1-10, default=3): ").strip()
        max_pages = int(max_pages_input) if max_pages_input.isdigit() and 1 <= int(max_pages_input) <= 10 else 3
        
        headless_input = input("🖥️  Mode headless? (y/n, default=n): ").strip().lower()
        headless = headless_input in ['y', 'yes', 'ya']
        
        # Inisialisasi scraper
        print(f"\n🔧 Inisialisasi scraper...")
        scraper = TokopediaScraperImproved(headless=headless)
        
        # Konfirmasi
        print(f"\n📋 KONFIGURASI:")
        print(f"   🔍 Keyword: '{keyword}'")
        print(f"   📄 Halaman: {max_pages}")
        print(f"   🖥️  Headless: {headless}")
        
        confirm = input("\n🚀 Lanjutkan scraping? (y/n): ").lower()
        if confirm not in ['y', 'yes', 'ya']:
            print("❌ Scraping dibatalkan")
            return False
        
        # Jalankan scraping
        print(f"\n🎬 MEMULAI SCRAPING...")
        start_time = datetime.now()
        
        products = scraper.search_products_with_scrolling(keyword, max_pages)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Tampilkan hasil
        if products:
            print(f"\n🎉 SCRAPING BERHASIL!")
            print(f"⏱️  Waktu eksekusi: {duration}")
            
            # Tampilkan ringkasan
            scraper.display_summary(products)
            
            # Simpan ke file
            save_option = input("\n💾 Simpan ke file CSV? (y/n): ").lower()
            if save_option in ['y', 'yes', 'ya']:
                custom_filename = input("📁 Nama file (kosongkan untuk auto): ").strip()
                filename = custom_filename if custom_filename else None
                
                if scraper.save_to_csv(products, filename):
                    print("✅ File berhasil disimpan!")
        else:
            print(f"\n❌ TIDAK ADA PRODUK YANG BERHASIL DI-SCRAPE")
        
        # Cleanup
        scraper.close_driver()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("🤖 TOKOPEDIA SCRAPER")
        print("="*30)
        print("1. Quick Start (default config)")
        print("2. Interactive Mode")
        print("3. Test Dependencies")
        print("4. Exit")
        
        choice = input("\nPilih mode (1-4): ").strip()
        
        if choice == "1":
            mode = "quick"
        elif choice == "2":
            mode = "interactive"
        elif choice == "3":
            mode = "test"
        elif choice == "4":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Pilihan tidak valid, menggunakan Quick Start")
            mode = "quick"
    
    if mode == "quick":
        success = run_scraper()
    elif mode == "interactive":
        success = run_interactive()
    elif mode == "test":
        success = check_dependencies()
    else:
        print(f"❌ Mode '{mode}' tidak dikenal")
        success = False
    
    if success:
        print("\n✅ Selesai!")
    else:
        print("\n❌ Gagal!")
        sys.exit(1)

if __name__ == "__main__":
    main()