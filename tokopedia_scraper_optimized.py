import json
import requests
import os
import re
import time
import random
import glob
import math
from urllib.parse import quote, urlencode
from datetime import datetime
import pandas as pd

class TokopediaScraperOptimized:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []
        self.total_available_data = 0
        
    def setup_session(self):
        """Setup session dengan headers yang realistis"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
    
    def build_graphql_params(self, keyword, page=1, rows=60):
        """Build GraphQL parameters yang valid"""
        start = (page - 1) * rows
        
        params = {
            'device': 'desktop',
            'navsource': '',
            'ob': '23',
            'page': str(page),
            'q': keyword,
            'related': 'true',
            'rows': str(rows),
            'safe_search': 'false',
            'scheme': 'https',
            'shipping': '',
            'source': 'search',
            'srp_component_id': '02.01.00.00',
            'st': 'product',
            'start': str(start),
            'topads_bucket': 'true',
            'unique_id': f'{int(time.time())}{random.randint(1000, 9999)}'
        }
        
        return urlencode(params)
    
    def create_graphql_query(self):
        """GraphQL query yang optimized untuk performa"""
        return """
        query SearchProductQueryV5($params: String!) {
          searchProductV5(params: $params) {
            header {
              totalData
              responseCode
              __typename
            }
            data {
              products {
                id
                name
                url
                price {
                  text
                  number
                  original
                  discountPercentage
                  __typename
                }
                shop {
                  id
                  name
                  city
                  tier
                  __typename
                }
                rating
                meta {
                  countReview
                  __typename
                }
                freeShipping {
                  url
                  __typename
                }
                category {
                  name
                  __typename
                }
                __typename
              }
              __typename
            }
            __typename
          }
        }
        """
    
    def get_total_available_data(self, keyword):
        """Dapatkan total data yang tersedia untuk keyword"""
        print(f"🔍 Checking total available data untuk keyword: '{keyword}'...")
        
        params = self.build_graphql_params(keyword, page=1, rows=1)
        
        payload = [{
            "operationName": "SearchProductQueryV5",
            "query": self.create_graphql_query(),
            "variables": {
                "params": params
            }
        }]
        
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Origin': 'https://www.tokopedia.com',
            'Referer': 'https://www.tokopedia.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        
        try:
            response = self.session.post(
                'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    if 'data' in first_item and first_item['data']:
                        search_data = first_item['data'].get('searchProductV5', {})
                        if search_data and 'header' in search_data:
                            total_data = search_data['header'].get('totalData', 0)
                            self.total_available_data = total_data
                            print(f"✅ Total data tersedia: {total_data:,} produk")
                            return True, payload, headers, total_data
            
            print("❌ Tidak dapat mendapatkan informasi total data")
            return False, None, None, 0
            
        except Exception as e:
            print(f"❌ Error checking total data: {e}")
            return False, None, None, 0
    
    def calculate_optimal_pages(self, total_data, rows_per_page=60):
        """Hitung jumlah halaman optimal untuk scraping"""
        if total_data == 0:
            return 0
        
        # Tokopedia biasanya membatasi hasil maksimal sekitar 1000-2000 halaman
        max_pages_limit = 1000
        calculated_pages = math.ceil(total_data / rows_per_page)
        
        # Ambil yang terkecil antara calculated pages dan limit
        optimal_pages = min(calculated_pages, max_pages_limit)
        
        print(f"📊 Perhitungan halaman:")
        print(f"   Total data: {total_data:,}")
        print(f"   Rows per page: {rows_per_page}")
        print(f"   Calculated pages: {calculated_pages:,}")
        print(f"   Optimal pages (dengan limit): {optimal_pages:,}")
        print(f"   Estimated products to scrape: {optimal_pages * rows_per_page:,}")
        
        return optimal_pages
    
    def scrape_all_products(self, keyword='samsung', rows_per_page=60):
        """Main function untuk scraping seluruh produk dengan keyword"""
        print(f"🚀 TOKOPEDIA COMPLETE SCRAPER")
        print(f"   Keyword: {keyword}")
        print(f"   Target: SEMUA PRODUK yang tersedia")
        print("=" * 60)
        
        # Reset data storage
        self.all_products_data = []
        
        # Setup directory
        excel_dir = 'excel_output'
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            print(f"📁 Direktori '{excel_dir}' dibuat")
        
        # Get total available data
        success, payload_template, headers, total_data = self.get_total_available_data(keyword)
        if not success:
            print("❌ Gagal mendapatkan informasi data. Menggunakan fallback...")
            return self.scrape_with_fallback(keyword, 100)  # Fallback 100 pages
        
        # Calculate optimal pages
        max_pages = self.calculate_optimal_pages(total_data, rows_per_page)
        if max_pages == 0:
            print("❌ Tidak ada data untuk di-scrape")
            return 0
        
        # Confirm before scraping
        print(f"\n⚠️  KONFIRMASI SCRAPING:")
        print(f"   📝 Keyword: {keyword}")
        print(f"   📄 Total pages: {max_pages:,}")
        print(f"   📊 Expected products: ~{max_pages * rows_per_page:,}")
        print(f"   ⏱️  Estimated time: ~{max_pages * 2 / 60:.1f} minutes")
        print(f"   💾 Output: basic.xlsx only")
        
        # Start scraping
        successful_pages = self.scrape_with_graphql(keyword, max_pages, payload_template, headers, rows_per_page)
        
        if successful_pages > 0:
            print(f"\n📝 Creating Excel file...")
            self.create_basic_excel_only(keyword, excel_dir)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_graphql(self, keyword, max_pages, payload_template, headers, rows_per_page):
        """Scraping dengan GraphQL optimized"""
        successful_pages = 0
        failed_pages = []
        
        print(f"\n🔄 Memulai scraping {max_pages:,} halaman...")
        print(f"📊 Progress akan ditampilkan setiap 50 halaman")
        
        for page in range(1, max_pages + 1):
            try:
                # Update payload
                params = self.build_graphql_params(keyword, page, rows_per_page)
                payload = payload_template.copy()
                payload[0]['variables']['params'] = params
                
                # Make request
                response = self.session.post(
                    'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract products
                    try:
                        products = data[0]['data']['searchProductV5']['data']['products']
                        if products:
                            page_products = self.extract_products_for_excel(products, keyword, page)
                            self.all_products_data.extend(page_products)
                            successful_pages += 1
                        else:
                            print(f"⚠️  Page {page}: Tidak ada produk")
                            break  # Jika tidak ada produk, kemungkinan sudah habis
                            
                    except Exception as e:
                        failed_pages.append(page)
                        print(f"❌ Page {page}: Error extracting - {e}")
                else:
                    failed_pages.append(page)
                    if response.status_code == 429:  # Rate limited
                        print(f"⚠️  Page {page}: Rate limited, waiting longer...")
                        time.sleep(10)
                    else:
                        print(f"❌ Page {page}: HTTP {response.status_code}")
                
                # Progress display every 50 pages
                if page % 50 == 0 or page == max_pages:
                    print(f"   📊 Progress: {page:,}/{max_pages:,} pages | Success: {successful_pages:,} | Products: {len(self.all_products_data):,}")
                
                # Smart delay
                if page < max_pages:
                    delay = random.uniform(0.5, 2.0)
                    if page % 100 == 0:  # Longer delay every 100 pages
                        delay += 3
                    time.sleep(delay)
                
            except Exception as e:
                failed_pages.append(page)
                print(f"❌ Page {page}: Error - {e}")
                if "timeout" in str(e).lower():
                    time.sleep(5)  # Wait longer for timeout
        
        # Final summary
        print(f"\n📊 SCRAPING SUMMARY:")
        print(f"   ✅ Successful pages: {successful_pages:,}/{max_pages:,}")
        print(f"   ❌ Failed pages: {len(failed_pages):,}")
        print(f"   📦 Total products collected: {len(self.all_products_data):,}")
        
        if failed_pages and len(failed_pages) < 20:  # Show failed pages if not too many
            print(f"   Failed pages: {failed_pages[:10]}{'...' if len(failed_pages) > 10 else ''}")
        
        return successful_pages
    
    def extract_products_for_excel(self, products, keyword, page):
        """Extract dan normalize product data untuk Excel dengan minimal overhead"""
        excel_products = []
        
        for idx, product in enumerate(products, 1):
            try:
                excel_product = {
                    'No': len(self.all_products_data) + idx,
                    'Keyword': keyword,
                    'Page': page,
                    'Product_ID': str(product.get('id', '')),
                    'Product_Name': product.get('name', '').strip(),
                    'Product_URL': product.get('url', ''),
                    'Price_Text': product.get('price', {}).get('text', ''),
                    'Price_Number': product.get('price', {}).get('number', 0),
                    'Original_Price': product.get('price', {}).get('original', 0),
                    'Discount_Percentage': product.get('price', {}).get('discountPercentage', 0),
                    'Shop_ID': product.get('shop', {}).get('id', ''),
                    'Shop_Name': product.get('shop', {}).get('name', ''),
                    'Shop_City': product.get('shop', {}).get('city', ''),
                    'Shop_Tier': product.get('shop', {}).get('tier', ''),
                    'Rating': float(product.get('rating', 0)) if product.get('rating') else 0,
                    'Review_Count': product.get('meta', {}).get('countReview', 0),
                    'Free_Shipping': bool(product.get('freeShipping', {}).get('url')),
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                excel_products.append(excel_product)
                
            except Exception as e:
                print(f"❌ Error processing product {idx} on page {page}: {e}")
                continue
        
        return excel_products
    
    def scrape_with_fallback(self, keyword, fallback_pages):
        """Fallback method dengan jumlah halaman terbatas"""
        print(f"🔄 Using fallback method dengan {fallback_pages} halaman...")
        
        # Coba dengan query sederhana
        simple_query = """
        query SearchProductQueryV5($params: String!) {
          searchProductV5(params: $params) {
            data {
              products {
                id
                name
                url
                price { text number __typename }
                shop { name city __typename }
                rating
                __typename
              }
              __typename
            }
            __typename
          }
        }
        """
        
        payload_template = [{
            "operationName": "SearchProductQueryV5",
            "query": simple_query,
            "variables": {"params": ""}
        }]
        
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        return self.scrape_with_graphql(keyword, fallback_pages, payload_template, headers, 60)
    
    def create_basic_excel_only(self, keyword, excel_dir):
        """Create basic Excel file only dengan pandas"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} produk untuk Excel...")
        
        # Create DataFrame
        df = pd.DataFrame(self.all_products_data)
        
        # Basic cleaning
        print("🧹 Basic data cleaning...")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        print(f"   🗑️  Removed {initial_count - len(df):,} duplicates")
        
        # Clean numeric columns
        numeric_columns = ['Price_Number', 'Original_Price', 'Discount_Percentage', 'Rating', 'Review_Count']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calculate discount amount
        df['Discount_Amount'] = df['Original_Price'] - df['Price_Number']
        
        # Sort by rating and review count (best products first)
        df = df.sort_values(['Rating', 'Review_Count'], ascending=[False, False])
        df = df.reset_index(drop=True)
        df['No'] = range(1, len(df) + 1)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_{timestamp}_basic.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        # Create Excel
        try:
            print(f"💾 Creating Excel file...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Products', index=False)
            
            print(f"\n🎉 EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk: {len(df):,} produk")
            print(f"📁 File location: {filepath}")
            print(f"💾 File size: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB")
            
            # Quick stats
            print(f"\n📈 Quick Stats:")
            print(f"   💰 Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
            print(f"   ⭐ Average rating: {df['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops: {df['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities: {df['Shop_City'].nunique():,}")
            print(f"   🚚 Free shipping: {df['Free_Shipping'].sum():,} products ({df['Free_Shipping'].mean()*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA COMPLETE SCRAPER")
    print("🎓 Optimized for Complete Data Collection")
    print("=" * 70)
    
    scraper = TokopediaScraperOptimized()
    
    # Configuration - GANTI KEYWORD DI SINI
    KEYWORD = 'samsung'  # <-- Ganti keyword sesuai kebutuhan
    
    print(f"⚙️  Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    print(f"   🎯 Target: ALL available products")
    print(f"   📊 Output: basic.xlsx only")
    print()
    
    # Start scraping
    result = scraper.scrape_all_products(keyword=KEYWORD)
    
    print(f"\n🏁 SCRAPING COMPLETED!")
    print(f"✅ Successfully scraped: {result:,} pages")
    print(f"📊 Total products: {len(scraper.all_products_data):,}")
    
    if result > 0:
        print(f"\n📁 Excel file ready di: excel_output/")
        print(f"🎉 Data siap untuk analisis!")
    else:
        print(f"\n❌ No data was scraped. Please check keyword or try again.")
    
    print(f"\n💡 Tips:")
    print(f"   - Ganti KEYWORD = 'samsung' dengan keyword lain")
    print(f"   - File Excel akan tersimpan di folder excel_output/")
    print(f"   - Script ini akan scrape SEMUA produk yang tersedia")