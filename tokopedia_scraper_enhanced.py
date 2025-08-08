import json
import requests
import os
import re
import time
import random
import glob
import math
from urllib.parse import quote, urlencode, urlparse, parse_qs
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

class TokopediaScraperEnhanced:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []
        self.total_available_data = 0
        self.detail_scraping_enabled = True
        
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
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
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
        """GraphQL query untuk mendapatkan daftar produk"""
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
    
    def calculate_optimal_pages(self, total_data, rows_per_page, target_products=None):
        """Hitung jumlah halaman optimal untuk scraping"""
        if total_data == 0:
            return 0

        max_pages_limit = 1000

        if target_products and target_products > 0:
            calculated_pages = math.ceil(target_products / rows_per_page)
        else:
            calculated_pages = math.ceil(total_data / rows_per_page)
        
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

    def scrape_product_detail(self, product_url, product_id):
        """Scrape detail produk untuk mendapatkan sold count"""
        try:
            # Clean URL untuk memastikan format yang benar
            if not product_url.startswith('http'):
                product_url = 'https://www.tokopedia.com' + product_url
            
            # Request ke halaman detail produk
            detail_response = self.session.get(product_url, timeout=30)
            
            if detail_response.status_code != 200:
                print(f"⚠️  Failed to get detail for product {product_id}: HTTP {detail_response.status_code}")
                return None
            
            # Parse HTML untuk mendapatkan sold count
            sold_count = self.extract_sold_count_from_html(detail_response.text, product_id)
            
            # Delay untuk menghindari rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            return sold_count
            
        except Exception as e:
            print(f"❌ Error scraping detail for product {product_id}: {e}")
            return None
    
    def extract_sold_count_from_html(self, html_content, product_id):
        """Extract sold count dari HTML halaman detail produk"""
        try:
            # Method 1: Cari dalam script JSON-LD atau structured data
            sold_count = self.extract_sold_from_scripts(html_content)
            if sold_count is not None:
                return sold_count
            
            # Method 2: Cari dalam text content dengan regex
            sold_count = self.extract_sold_from_text(html_content)
            if sold_count is not None:
                return sold_count
            
            # Method 3: Cari dengan BeautifulSoup parsing
            sold_count = self.extract_sold_with_bs4(html_content)
            if sold_count is not None:
                return sold_count
            
            return 0  # Default jika tidak ditemukan
            
        except Exception as e:
            print(f"❌ Error extracting sold count for product {product_id}: {e}")
            return 0
    
    def extract_sold_from_scripts(self, html_content):
        """Extract sold count dari script tags"""
        try:
            # Cari script yang mengandung data produk
            script_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__APOLLO_STATE__\s*=\s*({.*?});',
                r'"soldCount":\s*(\d+)',
                r'"sold":\s*(\d+)',
                r'"terjual":\s*(\d+)',
                r'terjual.*?(\d+)',
                r'sold.*?(\d+)'
            ]
            
            for pattern in script_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    for match in matches:
                        try:
                            if isinstance(match, str) and match.isdigit():
                                return int(match)
                            elif isinstance(match, tuple) and len(match) > 0:
                                # Jika match adalah tuple, ambil elemen pertama
                                potential_num = str(match[0])
                                if potential_num.isdigit():
                                    return int(potential_num)
                        except:
                            continue
            return None
        except:
            return None
    
    def extract_sold_from_text(self, html_content):
        """Extract sold count dari text content dengan regex"""
        try:
            # Pattern untuk mencari text terjual/sold
            patterns = [
                r'(\d+)\s*terjual',
                r'(\d+)\s*sold',
                r'terjual[:\s]*(\d+)',
                r'sold[:\s]*(\d+)',
                r'>(\d+)\s*terjual<',
                r'>(\d+)\s*sold<',
                r'Terjual\s*(\d+)',
                r'Sold\s*(\d+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    try:
                        # Ambil match pertama dan convert ke int
                        sold_str = str(matches[0]).replace(',', '').replace('.', '')
                        if sold_str.isdigit():
                            return int(sold_str)
                    except:
                        continue
            return None
        except:
            return None
    
    def extract_sold_with_bs4(self, html_content):
        """Extract sold count menggunakan BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Cari elemen yang mungkin mengandung sold count
            potential_elements = soup.find_all(text=re.compile(r'terjual|sold', re.IGNORECASE))
            
            for element in potential_elements:
                text = str(element).strip()
                # Extract angka dari text
                numbers = re.findall(r'\d+', text)
                if numbers:
                    try:
                        return int(numbers[0])
                    except:
                        continue
            
            return None
        except:
            return None

    def scrape_all_products(self, keyword, target_products=None, enable_detail_scraping=True):
        """Main function untuk scraping produk dengan detail"""
        print(f"🚀 TOKOPEDIA ENHANCED SCRAPER")
        print(f"   Keyword: {keyword}")
        if target_products and target_products > 0:
            print(f"   Target: {target_products:,} produk")
        else:
            print(f"   Target: SEMUA PRODUK yang tersedia")
        print(f"   Detail Scraping: {'✅ Enabled' if enable_detail_scraping else '❌ Disabled'}")
        print("=" * 60)
        
        self.detail_scraping_enabled = enable_detail_scraping
        self.all_products_data = []
        
        excel_dir = 'excel_output'
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            print(f"📁 Direktori '{excel_dir}' dibuat")
        
        # Get total available data
        success, payload_template, headers, total_data = self.get_total_available_data(keyword)
        if not success:
            print("❌ Gagal mendapatkan informasi data. Menggunakan fallback...")
            return self.scrape_with_fallback(keyword, 100, target_products)
        
        # Calculate optimal pages
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
        
        if enable_detail_scraping:
            estimated_time = max_pages * 2 + (max_pages * 60 * 1.5)  # Additional time for detail scraping
            print(f"   ⏱️  Estimated time: ~{estimated_time / 60:.1f} minutes (dengan detail scraping)")
        else:
            print(f"   ⏱️  Estimated time: ~{max_pages * 2 / 60:.1f} minutes")
        
        print(f"   💾 Output: basic.xlsx dengan sold count")
        
        # Start scraping
        successful_pages = self.scrape_with_graphql(keyword, max_pages, payload_template, headers, 60, target_products)
        
        if successful_pages > 0:
            print(f"\n📝 Creating Excel file...")
            self.create_basic_excel_only(keyword, excel_dir)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_graphql(self, keyword, max_pages, payload_template, headers, rows_per_page, target_products=None):
        """Scraping dengan GraphQL dan detail scraping"""
        successful_pages = 0
        failed_pages = []
        
        print(f"\n🔄 Phase 1: Scraping daftar produk...")
        print(f"📊 Progress akan ditampilkan setiap 50 halaman")
        
        # Phase 1: Scrape product list
        for page in range(1, max_pages + 1):
            if target_products and target_products > 0 and len(self.all_products_data) >= target_products:
                print(f"\n🎯 Target produk {target_products:,} telah tercapai pada phase 1.")
                break

            try:
                params = self.build_graphql_params(keyword, page, rows_per_page)
                payload = payload_template.copy()
                payload[0]['variables']['params'] = params
                
                response = self.session.post(
                    'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    try:
                        products = data[0]['data']['searchProductV5']['data']['products']
                        if products:
                            page_products = self.extract_products_for_excel(products, keyword)
                            
                            if target_products and target_products > 0:
                                remaining_slots = target_products - len(self.all_products_data)
                                products_to_add = page_products[:remaining_slots]
                                self.all_products_data.extend(products_to_add)
                                successful_pages += 1
                                if len(self.all_products_data) >= target_products:
                                    print(f"\n🎯 Target produk {target_products:,} tercapai pada halaman {page}.")
                                    break
                            else:
                                self.all_products_data.extend(page_products)
                                successful_pages += 1
                        else:
                            print(f"⚠️  Page {page}: Tidak ada produk")
                            break
                            
                    except Exception as e:
                        failed_pages.append(page)
                        print(f"❌ Page {page}: Error extracting - {e}")
                else:
                    failed_pages.append(page)
                    if response.status_code == 429:
                        print(f"⚠️  Page {page}: Rate limited, waiting longer...")
                        time.sleep(10)
                    else:
                        print(f"❌ Page {page}: HTTP {response.status_code}")
                
                if page % 50 == 0 or page == max_pages:
                    collected_count = len(self.all_products_data)
                    print(f"   📊 Progress: Halaman {page:,} | Success: {successful_pages:,} | Produk: {collected_count:,}")
                
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                failed_pages.append(page)
                print(f"❌ Page {page}: Error - {e}")
        
        # Phase 2: Scrape product details untuk sold count
        if self.detail_scraping_enabled and self.all_products_data:
            print(f"\n🔄 Phase 2: Scraping detail produk untuk sold count...")
            print(f"📊 Total produk untuk detail scraping: {len(self.all_products_data):,}")
            
            for idx, product in enumerate(self.all_products_data, 1):
                try:
                    product_url = product.get('Product_URL', '')
                    product_id = product.get('Product_ID', '')
                    
                    if product_url and product_id:
                        sold_count = self.scrape_product_detail(product_url, product_id)
                        product['Sold_Count'] = sold_count if sold_count is not None else 0
                    else:
                        product['Sold_Count'] = 0
                    
                    # Progress display every 100 products
                    if idx % 100 == 0 or idx == len(self.all_products_data):
                        print(f"   📊 Detail Progress: {idx:,}/{len(self.all_products_data):,} produk")
                    
                except Exception as e:
                    print(f"❌ Error getting detail for product {idx}: {e}")
                    product['Sold_Count'] = 0
        else:
            # Jika detail scraping disabled, set default sold count
            for product in self.all_products_data:
                product['Sold_Count'] = 0
        
        print(f"\n📊 SCRAPING SUMMARY:")
        print(f"   ✅ Successful pages: {successful_pages:,}")
        print(f"   ❌ Failed pages: {len(failed_pages):,}")
        print(f"   📦 Total products collected: {len(self.all_products_data):,}")
        if self.detail_scraping_enabled:
            sold_data_count = sum(1 for p in self.all_products_data if p.get('Sold_Count', 0) > 0)
            print(f"   🛒 Products dengan sold data: {sold_data_count:,}")
        
        return successful_pages
    
    def extract_products_for_excel(self, products, keyword):
        """Extract dan normalize product data untuk Excel"""
        excel_products = []
        
        for idx, product in enumerate(products, 1):
            try:
                excel_product = {
                    'Keyword': keyword,
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
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Sold_Count': 0,  # Will be updated in detail scraping phase
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                excel_products.append(excel_product)
                
            except Exception as e:
                print(f"❌ Error processing product {idx}: {e}")
                continue
        
        return excel_products
    
    def scrape_with_fallback(self, keyword, fallback_pages, target_products=None):
        """Fallback method dengan jumlah halaman terbatas"""
        print(f"🔄 Using fallback method dengan {fallback_pages} halaman...")
        
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
        
        return self.scrape_with_graphql(keyword, fallback_pages, payload_template, headers, 60, target_products)
    
    def create_basic_excel_only(self, keyword, excel_dir):
        """Create basic Excel file dengan sold count data"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} produk untuk Excel...")
        
        df = pd.DataFrame(self.all_products_data)
        
        print("🧹 Basic data cleaning...")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"   🗑️  Removed {removed_count:,} duplicates")
        
        # Clean numeric columns
        numeric_columns = ['Price_Number', 'Original_Price', 'Discount_Percentage', 'Rating', 'Review_Count', 'Sold_Count']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Sort by sold count and rating (best selling products first)
        df = df.sort_values(['Sold_Count', 'Rating', 'Review_Count'], ascending=[False, False, False])
        df = df.reset_index(drop=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_{timestamp}_dengan_sold.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        try:
            print(f"💾 Creating Excel file...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Products', index=False)
            
            print(f"\n🎉 EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk unik: {len(df):,} produk")
            print(f"📁 File location: {filepath}")
            try:
                print(f"💾 File size: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB")
            except:
                pass
            
            # Enhanced stats with sold data
            print(f"\n📈 Quick Stats:")
            print(f"   💰 Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
            print(f"   ⭐ Average rating: {df['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops: {df['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities: {df['Shop_City'].nunique():,}")
            if self.detail_scraping_enabled:
                sold_stats = df[df['Sold_Count'] > 0]
                if len(sold_stats) > 0:
                    print(f"   🛒 Products dengan sold data: {len(sold_stats):,}")
                    print(f"   📦 Total sold (sum): {df['Sold_Count'].sum():,}")
                    print(f"   📊 Average sold per product: {df['Sold_Count'].mean():.1f}")
                    print(f"   🥇 Best selling product: {df['Sold_Count'].max():,} terjual")
                else:
                    print(f"   🛒 Sold data: Tidak berhasil diambil untuk produk ini")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA ENHANCED SCRAPER")
    print("🎓 With Product Detail & Sold Count Data")
    print("=" * 70)
    
    scraper = TokopediaScraperEnhanced()
    
    # Input interaktif dari user
    KEYWORD = input("Masukkan keyword pencarian produk (e.g., 'samsung'): ").strip()
    
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

    # Option untuk detail scraping
    detail_choice = input("Ambil data 'terjual berapa banyak' dari halaman detail? (y/n, default: y): ").strip().lower()
    ENABLE_DETAIL = detail_choice != 'n'
    
    print(f"\n⚙️  Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    if TARGET_PRODUCTS and TARGET_PRODUCTS > 0:
        print(f"   🎯 Target: {TARGET_PRODUCTS:,} produk")
    else:
        print(f"   🎯 Target: SEMUA produk yang tersedia")
    print(f"   🛒 Detail Scraping: {'✅ Ya' if ENABLE_DETAIL else '❌ Tidak'}")
    print(f"   📊 Output: Excel dengan sold count data")
    print()
    
    if ENABLE_DETAIL:
        print("⚠️  PERHATIAN:")
        print("   Detail scraping akan memakan waktu lebih lama")
        print("   Namun akan memberikan data 'terjual berapa banyak'")
        print()
    
    # Start scraping
    result = scraper.scrape_all_products(
        keyword=KEYWORD, 
        target_products=TARGET_PRODUCTS,
        enable_detail_scraping=ENABLE_DETAIL
    )
    
    print(f"\n🏁 SCRAPING COMPLETED!")
    print(f"📊 Total produk yang dikumpulkan: {len(scraper.all_products_data):,}")
    
    if result > 0 and scraper.all_products_data:
        print(f"\n📁 Excel file ready di: excel_output/")
        print(f"🎉 Data siap untuk analisis dengan sold count!")
    else:
        print(f"\n❌ No data was scraped. Please check keyword or try again.")
    
    print(f"\n💡 Tips:")
    print(f"   - File Excel akan tersimpan di folder excel_output/")
    print(f"   - Produk diurutkan berdasarkan jumlah terjual (terbanyak di atas)")
    print(f"   - Data sold count diambil dari halaman detail setiap produk")