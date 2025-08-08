#!/usr/bin/env python3

# Test file untuk Tokopedia Enhanced Scraper
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tokopedia_scraper_enhanced import TokopediaScraperEnhanced

def test_enhanced_scraper():
    """Test enhanced scraper dengan parameter fixed"""
    print("🧪 TESTING TOKOPEDIA ENHANCED SCRAPER")
    print("=" * 60)
    
    # Configuration untuk testing
    TEST_KEYWORD = 'samsung'
    TEST_TARGET = 5  # Hanya 5 produk untuk testing cepat
    TEST_DETAIL_SCRAPING = True
    
    print(f"📝 Test Configuration:")
    print(f"   Keyword: {TEST_KEYWORD}")
    print(f"   Target: {TEST_TARGET} produk")
    print(f"   Detail Scraping: {'✅ Enabled' if TEST_DETAIL_SCRAPING else '❌ Disabled'}")
    print()
    
    # Initialize scraper
    scraper = TokopediaScraperEnhanced()
    
    # Run test
    try:
        result = scraper.scrape_all_products(
            keyword=TEST_KEYWORD,
            target_products=TEST_TARGET,
            enable_detail_scraping=TEST_DETAIL_SCRAPING
        )
        
        print(f"\n🏁 TEST COMPLETED!")
        print(f"📊 Result: {result} pages scraped")
        print(f"📦 Products collected: {len(scraper.all_products_data)}")
        
        if scraper.all_products_data:
            print(f"\n📄 Sample Product Data:")
            sample_product = scraper.all_products_data[0]
            for key, value in sample_product.items():
                print(f"   {key}: {value}")
            
            # Check sold count data
            sold_counts = [p.get('Sold_Count', 0) for p in scraper.all_products_data]
            successful_sold = sum(1 for count in sold_counts if count > 0)
            print(f"\n🛒 Sold Count Analysis:")
            print(f"   Products with sold data: {successful_sold}/{len(scraper.all_products_data)}")
            print(f"   Sold counts: {sold_counts}")
        
        return result > 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_scraper()
    
    if success:
        print(f"\n✅ TEST PASSED!")
        print(f"📁 Check excel_output/ folder for results")
    else:
        print(f"\n❌ TEST FAILED!")
    
    exit(0 if success else 1)