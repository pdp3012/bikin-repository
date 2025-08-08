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

class TokopediaScraperSimplified:
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
            'ob': '23', # Default sort by relevance
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
        """GraphQL query yang optimized untuk performa dengan tambahan sold count"""
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
                labelGroups {
                  title
                  type
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
    
    def extract_sold_count_from_labels(self, product):
        """Extract jumlah terjual dari labelGroups"""
        try:
            label_groups = product.get('labelGroups', [])
            for label in label_groups:
                title = label.get('title', '').lower()
                if 'terjual' in title or 'sold' in title:
                    # Extract number dari format seperti "100+ terjual", "1rb+ terjual"
                    if 'rb' in title:
                        # Extract number before 'rb'
                        rb_match = re.search(r'(\d+(?:\.\d+)?)rb', title)
                        if rb_match:
                            number = float(rb_match.group(1))
                            return int(number * 1000)
                    else:
                        # Extract regular numbers
                        numbers = re.findall(r'\d+', title)
                        if numbers:
                            return int(numbers[0])
            return 0
        except:
            return 0
    
    def calculate_optimal_pages(self, total_data, rows_per_page, target_products=None):
        """Hitung jumlah halaman optimal untuk scraping berdasarkan target atau total data"""
        if total_data == 0:
            return 0

        # Tokopedia biasanya membatasi hasil maksimal sekitar 1000-2000 halaman
        max_pages_limit = 1000

        if target_products and target_products > 0:
            # Hitung halaman berdasarkan target produk
            calculated_pages = math.ceil(target_products / rows_per_page)
        else:
            # Hitung halaman berdasarkan total data tersedia
            calculated_pages = math.ceil(total_data / rows_per_page)
        
        # Ambil yang terkecil antara calculated pages dan limit
        optimal_pages = min(calculated_pages, max_pages_limit)
        
        print(f"📊 Perhitungan halaman:")
        print(f"   Total data tersedia: {total_data:,}")
        if target_products and target_products > 0:
             print(f"   Target produk user: {target_products:,}")
        print(f"   Rows per page: {rows_per_page}")
        print(f"   Calculated pages: {calculated_pages:,}")
        print(f"   Optimal pages (dengan limit): {optimal_pages:,}")
        print(f"   Estimated products to scrape: {optimal_pages * rows_per_page:,}")
        
        return optimal_pages

    def scrape_all_products(self, keyword, target_products=None):
        """Main function untuk scraping produk dengan keyword dan target jumlah"""
        print(f"🚀 TOKOPEDIA SCRAPER SIMPLIFIED - FAST & EFFICIENT")
        print(f"   Keyword: {keyword}")
        if target_products and target_products > 0:
            print(f"   Target: {target_products:,} produk")
        else:
            print(f"   Target: SEMUA PRODUK yang tersedia")
        print("=" * 70)
        
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
            return self.scrape_with_fallback(keyword, 100, target_products) # Fallback 100 pages
        
        # Calculate optimal pages based on target or total data
        max_pages = self.calculate_optimal_pages(total_data, 60, target_products)
        if max_pages == 0:
            print("❌ Tidak ada data untuk di-scrape")
            return 0
        
        # Confirm before scraping
        print(f"\n⚠️  KONFIRMASI SCRAPING:")
        print(f"   📝 Keyword: {keyword}")
        print(f"   📄 Total pages: {max_pages:,}")
        if target_products and target_products > 0:
            print(f"   📊 Target products: ~{min(target_products, max_pages * 60):,}")
        else:
            print(f"   📊 Expected products: ~{max_pages * 60:,}")
        
        estimated_time = max_pages * 2 / 60  # Base time only (no detail scraping)
        print(f"   ⏱️  Estimated time: ~{estimated_time:.1f} minutes")
        print(f"   💾 Output: simplified.xlsx dengan sold count")
        
        # Start scraping
        successful_pages = self.scrape_with_graphql(keyword, max_pages, payload_template, headers, 60, target_products)
        
        if successful_pages > 0:
            print(f"\n📝 Creating Simplified Excel file...")
            self.create_simplified_excel(keyword, excel_dir)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_graphql(self, keyword, max_pages, payload_template, headers, rows_per_page, target_products=None):
        """Scraping dengan GraphQL optimized dan kontrol jumlah produk"""
        successful_pages = 0
        failed_pages = []
        
        print(f"\n🔄 Memulai scraping...")
        print(f"📊 Progress akan ditampilkan setiap 25 halaman atau saat target tercapai")
        
        for page in range(1, max_pages + 1):
            # Cek apakah sudah mencapai target sebelum memulai request
            if target_products and target_products > 0 and len(self.all_products_data) >= target_products:
                print(f"\n🎯 Target produk {target_products:,} telah tercapai.")
                break

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
                            page_products = self.extract_products_simplified(products, keyword)
                            # Tambahkan produk sampai batas target
                            if target_products and target_products > 0:
                                remaining_slots = target_products - len(self.all_products_data)
                                products_to_add = page_products[:remaining_slots]
                                self.all_products_data.extend(products_to_add)
                                successful_pages += 1
                                # Jika sudah penuh setelah menambahkan, keluar dari loop
                                if len(self.all_products_data) >= target_products:
                                    print(f"\n🎯 Target produk {target_products:,} telah tercapai setelah halaman {page}.")
                                    break
                            else:
                                # Tambahkan semua produk jika tidak ada target
                                self.all_products_data.extend(page_products)
                                successful_pages += 1
                        else:
                            print(f"⚠️  Page {page}: Tidak ada produk")
                            break # Jika tidak ada produk, kemungkinan sudah habis
                            
                    except Exception as e:
                        failed_pages.append(page)
                        print(f"❌ Page {page}: Error extracting - {e}")
                else:
                    failed_pages.append(page)
                    if response.status_code == 429: # Rate limited
                        print(f"⚠️  Page {page}: Rate limited, waiting longer...")
                        time.sleep(10)
                    else:
                        print(f"❌ Page {page}: HTTP {response.status_code}")
                
                # Progress display every 25 pages
                if page % 25 == 0 or page == max_pages or (target_products and len(self.all_products_data) >= target_products):
                    collected_count = len(self.all_products_data)
                    print(f"   📊 Progress: Halaman {page:,} | Success: {successful_pages:,} | Produk terkumpul: {collected_count:,}")
                    if target_products and target_products > 0:
                         print(f"   🎯 Target: {target_products:,} | Sisa: {max(0, target_products - collected_count):,}")
                
                # Smart delay
                if page < max_pages:
                    delay = random.uniform(0.5, 2.0)
                    if page % 100 == 0: # Longer delay every 100 pages
                        delay += 3
                    time.sleep(delay)
                
            except Exception as e:
                failed_pages.append(page)
                print(f"❌ Page {page}: Error - {e}")
                if "timeout" in str(e).lower():
                    time.sleep(5) # Wait longer for timeout
        
        # Final summary
        print(f"\n📊 SCRAPING SUMMARY:")
        print(f"   ✅ Successful pages processed: {successful_pages:,}")
        print(f"   ❌ Failed pages: {len(failed_pages):,}")
        print(f"   📦 Total products collected: {len(self.all_products_data):,}")
        
        if failed_pages and len(failed_pages) < 20: # Show failed pages if not too many
            print(f"   Failed pages: {failed_pages[:10]}{'...' if len(failed_pages) > 10 else ''}")
        
        return successful_pages
    
    def extract_products_simplified(self, products, keyword):
        """Extract dan normalize product data dengan sold count - simplified version"""
        simplified_products = []
        
        for idx, product in enumerate(products, 1):
            try:
                # Extract sold count dari labelGroups
                sold_count = self.extract_sold_count_from_labels(product)
                
                # Simplified product info - removed Original_Price, Discount_Percentage, detail scraping
                simplified_product = {
                    'Keyword': keyword,
                    'Product_ID': str(product.get('id', '')),
                    'Product_Name': product.get('name', '').strip(),
                    'Product_URL': product.get('url', ''),
                    'Price_Text': product.get('price', {}).get('text', ''),
                    'Price_Number': product.get('price', {}).get('number', 0),
                    'Shop_ID': product.get('shop', {}).get('id', ''),
                    'Shop_Name': product.get('shop', {}).get('name', ''),
                    'Shop_City': product.get('shop', {}).get('city', ''),
                    'Shop_Tier': product.get('shop', {}).get('tier', ''),
                    'Rating': float(product.get('rating', 0)) if product.get('rating') else 0,
                    'Review_Count': product.get('meta', {}).get('countReview', 0),
                    'Sold_Count': sold_count,  # Jumlah terjual dari listing
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                simplified_products.append(simplified_product)
                
            except Exception as e:
                print(f"❌ Error processing product {idx} on current page: {e}")
                continue
        
        return simplified_products
    
    def scrape_with_fallback(self, keyword, fallback_pages, target_products=None):
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
                labelGroups { title type __typename }
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
        
        return self.scrape_with_graphql(keyword, fallback_pages, payload_template, headers, 60, target_products)
    
    def create_simplified_excel(self, keyword, excel_dir):
        """Create simplified Excel file dengan sold count"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} produk untuk Simplified Excel...")
        
        # Create DataFrame
        df = pd.DataFrame(self.all_products_data)
        
        # Basic cleaning
        print("🧹 Simplified data cleaning...")
        
        # Remove duplicates berdasarkan Product_ID
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"   🗑️  Removed {removed_count:,} duplicates")
        
        # Clean numeric columns (simplified - no Original_Price, Discount_Percentage)
        numeric_columns = ['Price_Number', 'Rating', 'Review_Count', 'Sold_Count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Sort by sold count first, then rating and review count (best performing products first)
        sort_columns = ['Sold_Count', 'Rating', 'Review_Count']
        df = df.sort_values(sort_columns, ascending=[False, False, False])
        df = df.reset_index(drop=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_{timestamp}_simplified.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        # Create Excel
        try:
            print(f"💾 Creating Simplified Excel file...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Products', index=False)
                
                # Create summary sheet
                summary_data = {
                    'Metric': [
                        'Total Products',
                        'Unique Shops',
                        'Unique Cities',
                        'Average Price',
                        'Average Rating',
                        'Total Sold Count',
                        'Products with Sales Data',
                        'Highest Sold Count',
                        'Keyword',
                        'Processing Mode',
                        'Scraped At'
                    ],
                    'Value': [
                        len(df),
                        df['Shop_Name'].nunique(),
                        df['Shop_City'].nunique(),
                        f"Rp {df['Price_Number'].mean():,.0f}",
                        f"{df['Rating'].mean():.2f}",
                        f"{df['Sold_Count'].sum():,}",
                        f"{(df['Sold_Count'] > 0).sum():,} ({(df['Sold_Count'] > 0).mean()*100:.1f}%)",
                        f"{df['Sold_Count'].max():,}",
                        keyword,
                        'SIMPLIFIED - No Detail Scraping',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"\n🎉 SIMPLIFIED EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk unik: {len(df):,} produk")
            print(f"📁 File location: {filepath}")
            try:
                print(f"💾 File size: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB")
            except:
                 pass # Abaikan jika tidak bisa mendapatkan ukuran file
            
            # Simplified stats
            print(f"\n📈 Simplified Stats:")
            print(f"   💰 Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
            print(f"   ⭐ Average rating: {df['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops: {df['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities: {df['Shop_City'].nunique():,}")
            print(f"   🛒 Total sold count: {df['Sold_Count'].sum():,}")
            print(f"   📊 Products with sales data: {(df['Sold_Count'] > 0).sum():,} ({(df['Sold_Count'] > 0).mean()*100:.1f}%)")
            print(f"   🔥 Highest sold count: {df['Sold_Count'].max():,}")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA SCRAPER SIMPLIFIED - FAST & EFFICIENT")
    print("🎓 Streamlined Data Collection - No Detail Scraping")
    print("=" * 70)
    
    scraper = TokopediaScraperSimplified()
    
    # Input interaktif dari user
    KEYWORD = input("Masukkan keyword pencarian produk (e.g., 'telur'): ").strip()
    
    if not KEYWORD:
        print("❌ Keyword tidak boleh kosong.")
        exit()

    target_input = input("Masukkan jumlah produk yang ingin diambil (kosongkan untuk mengambil SEMUA): ").strip()
    
    TARGET_PRODUCTS = None
    if target_input:
        try:
            TARGET_PRODUCTS = int(target_input)
            if TARGET_PRODUCTS <= 0:
                print("❌ Jumlah produk harus lebih dari 0. Mengambil SEMUA produk.")
                TARGET_PRODUCTS = None
        except ValueError:
            print("❌ Input jumlah produk tidak valid. Mengambil SEMUA produk.")
            TARGET_PRODUCTS = None

    print(f"\n⚙️  Simplified Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    if TARGET_PRODUCTS and TARGET_PRODUCTS > 0:
        print(f"   🎯 Target: {TARGET_PRODUCTS:,} produk")
    else:
        print(f"   🎯 Target: SEMUA produk yang tersedia")
    print(f"   📊 Output: simplified.xlsx dengan sold count")
    print(f"   ⚡ Mode: Fast scraping - No detail scraping")
    print(f"   📋 Fields: Essential data only (no Original_Price, Discount_Percentage)")
    print()
    
    # Start scraping
    result = scraper.scrape_all_products(keyword=KEYWORD, target_products=TARGET_PRODUCTS)
    
    print(f"\n🏁 SCRAPING COMPLETED!")
    print(f"📊 Total produk yang dikumpulkan: {len(scraper.all_products_data):,}")
    
    if result > 0 and scraper.all_products_data:
        print(f"\n📁 Simplified Excel file ready di: excel_output/")
        print(f"🎉 Data dengan sold count siap untuk analisis!")
        
        # Show top products by sold count
        if scraper.all_products_data:
            df_preview = pd.DataFrame(scraper.all_products_data)
            df_preview['Sold_Count'] = pd.to_numeric(df_preview.get('Sold_Count', 0), errors='coerce').fillna(0)
            top_sold = df_preview.nlargest(5, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name']]
            print(f"\n🔥 Top 5 Produk Terlaris:")
            for _, row in top_sold.iterrows():
                print(f"   • {row['Product_Name'][:50]}... | {row['Sold_Count']:,} terjual | {row['Price_Text']} | {row['Shop_Name']}")
    else:
        print(f"\n❌ No data was scraped. Please check keyword or try again.")
    
    print(f"\n💡 Simplified Features:")
    print(f"   ✨ Sold count dari halaman listing")
    print(f"   📊 Summary sheet dengan statistik essential")
    print(f"   ⚡ Fast processing - No detail scraping")
    print(f"   📈 Sorting berdasarkan performa penjualan")
    print(f"   🗂️ Streamlined fields untuk analisis cepat")