#!/usr/bin/env python3
"""
Contoh Penggunaan Tokopedia Scraper
Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman

Script ini menunjukkan berbagai cara menggunakan scraper:
1. Scraping sederhana
2. Scraping dengan konfigurasi custom
3. Batch scraping multiple keywords
4. Analisis data hasil scraping
"""

import time
from datetime import datetime
from tokopedia_scraper import TokopediaScraper
from data_analyzer import TokopediaDataAnalyzer

def example_simple_scraping():
    """Contoh scraping sederhana"""
    print("=== CONTOH 1: SCRAPING SEDERHANA ===")
    
    # Inisialisasi scraper
    scraper = TokopediaScraper(headless=True)
    
    # Lakukan scraping
    products = scraper.scrape_products("cabai", max_scrolls=3)
    
    if products:
        print(f"✅ Berhasil scrape {len(products)} produk")
        
        # Simpan hasil
        scraper.save_to_csv(products, "contoh_cabai.csv")
        scraper.save_to_json(products, "contoh_cabai.json")
        
        # Tampilkan sample
        print("\nSample data:")
        for i, product in enumerate(products[:3], 1):
            print(f"{i}. {product['nama_produk'][:50]}...")
            print(f"   Harga: {product['harga_produk']}")
            print(f"   Rating: {product['rating_produk']}")
    else:
        print("❌ Tidak ada data yang berhasil di-scrape")

def example_custom_scraping():
    """Contoh scraping dengan konfigurasi custom"""
    print("\n=== CONTOH 2: SCRAPING DENGAN KONFIGURASI CUSTOM ===")
    
    # Konfigurasi custom
    config = {
        'search_query': 'laptop gaming',
        'max_scrolls': 8,
        'headless': False  # Tampilkan browser untuk debugging
    }
    
    scraper = TokopediaScraper(headless=config['headless'])
    
    print(f"Scraping: {config['search_query']}")
    print(f"Max scrolls: {config['max_scrolls']}")
    
    products = scraper.scrape_products(
        config['search_query'], 
        max_scrolls=config['max_scrolls']
    )
    
    if products:
        print(f"✅ Berhasil scrape {len(products)} produk")
        
        # Simpan dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"laptop_gaming_{timestamp}.json"
        scraper.save_to_json(products, filename)
        
        print(f"Data disimpan ke: {filename}")
    else:
        print("❌ Tidak ada data yang berhasil di-scrape")

def example_batch_scraping():
    """Contoh batch scraping untuk multiple keywords"""
    print("\n=== CONTOH 3: BATCH SCRAPING ===")
    
    # List kata kunci untuk di-scrape
    keywords = [
        "smartphone",
        "headphone",
        "mouse gaming"
    ]
    
    scraper = TokopediaScraper(headless=True)
    all_results = {}
    
    for keyword in keywords:
        print(f"\nScraping: {keyword}")
        
        try:
            products = scraper.scrape_products(keyword, max_scrolls=3)
            
            if products:
                all_results[keyword] = products
                print(f"✅ {keyword}: {len(products)} produk")
                
                # Simpan individual file
                safe_keyword = keyword.replace(' ', '_')
                scraper.save_to_json(products, f"batch_{safe_keyword}.json")
            else:
                print(f"❌ {keyword}: Tidak ada data")
                
        except Exception as e:
            print(f"❌ Error saat scraping {keyword}: {str(e)}")
        
        # Jeda antar scraping
        time.sleep(5)
    
    # Simpan hasil gabungan
    if all_results:
        combined_data = []
        for keyword, products in all_results.items():
            for product in products:
                product['batch_keyword'] = keyword
                combined_data.append(product)
        
        scraper.save_to_json(combined_data, "batch_combined.json")
        print(f"\n✅ Total produk dari semua keyword: {len(combined_data)}")

def example_data_analysis():
    """Contoh analisis data hasil scraping"""
    print("\n=== CONTOH 4: ANALISIS DATA ===")
    
    # Asumsikan kita sudah punya file hasil scraping
    # Jika tidak ada, buat data dummy
    import json
    
    # Data dummy untuk contoh
    dummy_data = [
        {
            "nama_produk": "Cabai Rawit Merah 1kg",
            "harga_produk": "Rp 25.000",
            "jumlah_terjual": "Terjual 1rb+",
            "rating_produk": "4.8",
            "lokasi_toko": "Jakarta Selatan",
            "search_query": "cabai"
        },
        {
            "nama_produk": "Cabai Rawit Hijau 500g",
            "harga_produk": "Rp 15.000",
            "jumlah_terjual": "Terjual 500+",
            "rating_produk": "4.5",
            "lokasi_toko": "Bandung",
            "search_query": "cabai"
        }
    ]
    
    # Simpan data dummy
    with open("dummy_data.json", "w", encoding="utf-8") as f:
        json.dump(dummy_data, f, ensure_ascii=False, indent=2)
    
    # Analisis data
    analyzer = TokopediaDataAnalyzer("dummy_data.json")
    
    if analyzer.df is not None:
        # Bersihkan data
        analyzer.clean_data()
        
        # Generate ringkasan
        analyzer.generate_summary()
        
        # Cari produk terbaik
        analyzer.find_best_products('rating', 5)
        
        print("✅ Analisis data selesai!")

def example_advanced_usage():
    """Contoh penggunaan advanced dengan error handling"""
    print("\n=== CONTOH 5: PENGGUNAAN ADVANCED ===")
    
    # Konfigurasi advanced
    configs = [
        {
            'name': 'Scraping Cepat',
            'query': 'buku',
            'scrolls': 2,
            'headless': True
        },
        {
            'name': 'Scraping Lengkap',
            'query': 'laptop',
            'scrolls': 10,
            'headless': False
        }
    ]
    
    for config in configs:
        print(f"\n--- {config['name']} ---")
        
        try:
            scraper = TokopediaScraper(headless=config['headless'])
            
            start_time = time.time()
            products = scraper.scrape_products(
                config['query'], 
                max_scrolls=config['scrolls']
            )
            end_time = time.time()
            
            if products:
                print(f"✅ Berhasil: {len(products)} produk dalam {end_time - start_time:.2f} detik")
                
                # Analisis cepat
                if len(products) > 0:
                    prices = []
                    ratings = []
                    
                    for product in products:
                        # Ekstrak harga (sederhana)
                        price_str = product.get('harga_produk', '')
                        if 'Rp' in price_str:
                            try:
                                price = float(''.join(filter(str.isdigit, price_str)))
                                prices.append(price)
                            except:
                                pass
                        
                        # Ekstrak rating (sederhana)
                        rating_str = product.get('rating_produk', '')
                        try:
                            rating = float(rating_str)
                            ratings.append(rating)
                        except:
                            pass
                    
                    if prices:
                        print(f"   Harga rata-rata: Rp {sum(prices)/len(prices):,.0f}")
                    if ratings:
                        print(f"   Rating rata-rata: {sum(ratings)/len(ratings):.2f}")
            else:
                print("❌ Tidak ada data")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Fungsi utama untuk menjalankan semua contoh"""
    print("🔍 CONTOH PENGGUNAAN TOKOPEDIA SCRAPER")
    print("Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman")
    print("="*60)
    
    print("\nPilih contoh yang ingin dijalankan:")
    print("1. Scraping Sederhana")
    print("2. Scraping dengan Konfigurasi Custom")
    print("3. Batch Scraping")
    print("4. Analisis Data")
    print("5. Penggunaan Advanced")
    print("6. Jalankan Semua Contoh")
    print("7. Keluar")
    
    choice = input("\nPilihan Anda (1-7): ").strip()
    
    if choice == "1":
        example_simple_scraping()
    elif choice == "2":
        example_custom_scraping()
    elif choice == "3":
        example_batch_scraping()
    elif choice == "4":
        example_data_analysis()
    elif choice == "5":
        example_advanced_usage()
    elif choice == "6":
        print("\n🚀 Menjalankan semua contoh...")
        example_simple_scraping()
        example_custom_scraping()
        example_batch_scraping()
        example_data_analysis()
        example_advanced_usage()
        print("\n✅ Semua contoh selesai!")
    elif choice == "7":
        print("Terima kasih!")
        return
    else:
        print("❌ Pilihan tidak valid!")
    
    print("\n" + "="*60)
    print("🎉 Contoh penggunaan selesai!")
    print("Dibuat dengan ❤️ oleh Dosen Data Mining dengan 30 tahun pengalaman")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")