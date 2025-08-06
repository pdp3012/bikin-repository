#!/usr/bin/env python3
"""
Test script untuk Tokopedia Scraper
Digunakan untuk memverifikasi bahwa scraper berfungsi dengan baik
"""

import sys
import time
from datetime import datetime

def test_imports():
    """Test apakah semua dependensi dapat diimport"""
    print("🧪 Testing imports...")
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import bs4
        print("✅ beautifulsoup4")
    except ImportError as e:
        print(f"❌ beautifulsoup4: {e}")
        return False
    
    try:
        import selenium
        print("✅ selenium")
    except ImportError as e:
        print(f"❌ selenium: {e}")
        return False
    
    try:
        import undetected_chromedriver
        print("✅ undetected-chromedriver")
    except ImportError as e:
        print(f"❌ undetected-chromedriver: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test fungsi dasar scraper"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from tokopedia_scraper_improved import TokopediaScraperImproved
        
        # Test inisialisasi
        print("✅ Import TokopediaScraperImproved berhasil")
        
        # Test dengan headless mode
        scraper = TokopediaScraperImproved(headless=True)
        print("✅ Inisialisasi scraper berhasil")
        
        # Test build search URL
        test_url = scraper.build_search_url("test")
        if "tokopedia.com/search" in test_url:
            print("✅ build_search_url berfungsi")
        else:
            print("❌ build_search_url error")
            return False
        
        # Test close driver
        scraper.close_driver()
        print("✅ close_driver berfungsi")
        
        return True
        
    except Exception as e:
        print(f"❌ Error dalam testing basic functionality: {e}")
        return False

def test_requests_fallback():
    """Test fallback mechanism dengan requests"""
    print("\n🧪 Testing requests fallback...")
    
    try:
        from tokopedia_scraper_improved import TokopediaScraperImproved
        
        # Buat scraper tanpa driver
        scraper = TokopediaScraperImproved(headless=True)
        scraper.driver = None  # Force fallback
        
        # Test fallback method
        products = scraper.search_products_fallback("cabai", max_pages=1)
        
        if isinstance(products, list):
            print(f"✅ Fallback method berfungsi, {len(products)} produk ditemukan")
            return True
        else:
            print("❌ Fallback method error")
            return False
            
    except Exception as e:
        print(f"❌ Error dalam testing fallback: {e}")
        return False

def test_data_extraction():
    """Test ekstraksi data"""
    print("\n🧪 Testing data extraction...")
    
    try:
        from tokopedia_scraper_improved import TokopediaScraperImproved
        from bs4 import BeautifulSoup
        
        scraper = TokopediaScraperImproved(headless=True)
        
        # Test HTML parsing
        test_html = """
        <div>
            <a href="/p/test-product">Test Product Name</a>
            <span>Rp 25.000</span>
            <span>4.5</span>
            <span>100 terjual</span>
            <span>Test Shop</span>
        </div>
        """
        
        soup = BeautifulSoup(test_html, 'html.parser')
        containers = scraper.find_product_containers_improved(soup)
        
        if containers:
            print("✅ find_product_containers_improved berfungsi")
            
            # Test single product extraction
            product_data = scraper.extract_single_product_improved(containers[0], 1)
            
            if product_data and isinstance(product_data, dict):
                print("✅ extract_single_product_improved berfungsi")
                print(f"   Sample data: {product_data}")
                return True
            else:
                print("❌ extract_single_product_improved error")
                return False
        else:
            print("❌ find_product_containers_improved error")
            return False
            
    except Exception as e:
        print(f"❌ Error dalam testing data extraction: {e}")
        return False

def main():
    """Main test function"""
    print("="*60)
    print("🧪 TOKOPEDIA SCRAPER - TEST SUITE")
    print("="*60)
    print(f"⏰ Waktu test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Requests Fallback", test_requests_fallback),
        ("Data Extraction", test_data_extraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        
        print("-" * 40)
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 SEMUA TEST BERHASIL!")
        print("Scraper siap digunakan.")
        return 0
    else:
        print(f"\n⚠️  {total-passed} TEST GAGAL!")
        print("Silakan periksa error di atas dan perbaiki masalahnya.")
        return 1

if __name__ == "__main__":
    sys.exit(main())