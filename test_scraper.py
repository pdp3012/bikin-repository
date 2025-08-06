#!/usr/bin/env python3
"""
Test Script untuk Tokopedia Scraper
Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman
"""

import time
import sys
from tokopedia_scraper import TokopediaScraper

def test_scraper():
    """Test fungsi scraper dengan berbagai kata kunci"""
    
    print("=== TEST TOKOPEDIA SCRAPER ===")
    print("Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "cabai",
        "cabai rawit", 
        "laptop",
        "smartphone"
    ]
    
    scraper = TokopediaScraper(headless=True)  # Gunakan headless untuk testing
    
    for i, search_query in enumerate(test_cases, 1):
        print(f"\n--- TEST CASE {i}: '{search_query}' ---")
        
        try:
            # Lakukan scraping dengan scroll minimal untuk testing
            products = scraper.scrape_products(search_query, max_scrolls=2)
            
            if products:
                print(f"✅ Berhasil scrape {len(products)} produk")
                
                # Tampilkan sample data
                print("Sample data:")
                for j, product in enumerate(products[:2]):  # Tampilkan 2 produk pertama
                    print(f"  Produk {j+1}:")
                    for key, value in product.items():
                        if value:  # Hanya tampilkan yang ada datanya
                            print(f"    {key}: {value}")
                    print()
                    
                # Simpan hasil test
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"test_result_{search_query.replace(' ', '_')}_{timestamp}.json"
                scraper.save_to_json(products, filename)
                
            else:
                print("❌ Tidak ada data yang berhasil di-scrape")
                
        except Exception as e:
            print(f"❌ Error saat testing '{search_query}': {str(e)}")
            
        # Jeda antar test untuk menghindari rate limiting
        if i < len(test_cases):
            print("Menunggu 5 detik sebelum test berikutnya...")
            time.sleep(5)
    
    print("\n" + "=" * 50)
    print("TESTING SELESAI")
    print("=" * 50)

def test_single_query():
    """Test scraper dengan satu kata kunci spesifik"""
    
    print("=== TEST SINGLE QUERY ===")
    
    # Input kata kunci dari user
    search_query = input("Masukkan kata kunci untuk testing: ").strip()
    
    if not search_query:
        print("Kata kunci tidak boleh kosong!")
        return
    
    print(f"\nTesting dengan kata kunci: '{search_query}'")
    
    scraper = TokopediaScraper(headless=False)  # Gunakan GUI untuk debugging
    
    try:
        products = scraper.scrape_products(search_query, max_scrolls=3)
        
        if products:
            print(f"\n✅ Berhasil scrape {len(products)} produk")
            
            # Tampilkan semua data
            print("\nDATA LENGKAP:")
            print("-" * 50)
            for i, product in enumerate(products, 1):
                print(f"Produk {i}:")
                for key, value in product.items():
                    print(f"  {key}: {value}")
                print("-" * 30)
                
            # Simpan hasil
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"single_test_{search_query.replace(' ', '_')}_{timestamp}.json"
            scraper.save_to_json(products, filename)
            print(f"Data disimpan ke: {filename}")
            
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Menu utama untuk testing"""
    
    print("Pilih mode testing:")
    print("1. Test multiple queries (headless)")
    print("2. Test single query (with GUI)")
    print("3. Keluar")
    
    choice = input("\nPilihan Anda (1-3): ").strip()
    
    if choice == "1":
        test_scraper()
    elif choice == "2":
        test_single_query()
    elif choice == "3":
        print("Terima kasih!")
        sys.exit(0)
    else:
        print("Pilihan tidak valid!")

if __name__ == "__main__":
    main()