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
from bs4 import BeautifulSoup
import concurrent.futures
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

class TokopediaScraperTurbo:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []
        self.total_available_data = 0
        self.filtered_products_count = 0
        self.data_lock = Lock()
        self.progress_lock = Lock()
        self.request_count = 0
        self.success_count = 0
        
    def setup_session(self):
        """Setup session dengan headers yang realistis dan optimized"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
        
        # Optimasi session untuk performa
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,  # Increase connection pool
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def build_graphql_params(self, keyword, page=1, rows=60, sort_by='23'):
        """Build GraphQL parameters dengan opsi sorting yang berbeda"""
        start = (page - 1) * rows
        
        params = {
            'device': 'desktop',
            'navsource': '',
            'ob': sort_by,  # 23=relevance, 9=sold count desc, 5=newest, 3=highest price, 4=lowest price
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
        """Dapatkan total data yang tersedia untuk keyword dengan timeout optimized"""
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
            'Accept': 'application/json',
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
                timeout=15  # Reduced timeout for speed
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
        """Extract jumlah terjual dari labelGroups dengan parsing yang lebih robust dan cepat"""
        try:
            label_groups = product.get('labelGroups', [])
            for label in label_groups:
                title = label.get('title', '').lower()
                if 'terjual' in title or 'sold' in title:
                    # Extract number dengan regex yang lebih efisien
                    if 'rb' in title:
                        # Extract number before 'rb' - optimized regex
                        rb_match = re.search(r'(\d+(?:\.\d+)?)rb', title)
                        if rb_match:
                            number = float(rb_match.group(1))
                            return int(number * 1000)
                    else:
                        # Extract regular numbers - simple and fast
                        numbers = re.findall(r'\d+', title)
                        if numbers:
                            return int(numbers[0])
            return 0
        except:
            return 0
    
    def calculate_turbo_pages(self, total_data, rows_per_page, target_products=None, min_sold_count=0):
        """Hitung jumlah halaman optimal untuk turbo scraping"""
        if total_data == 0:
            return 0

        # Tingkatkan limit maksimal menjadi 18,000 produk (300 halaman * 60 produk)
        max_products_limit = 18000
        max_pages_limit = math.ceil(max_products_limit / rows_per_page)  # 300 halaman

        if target_products and target_products > 0:
            calculated_pages = math.ceil(target_products / rows_per_page)
        else:
            calculated_pages = math.ceil(total_data / rows_per_page)
        
        # Jika ada filter sold count, estimasi lebih konservatif untuk efisiensi
        if min_sold_count > 0:
            # Estimasi berdasarkan filter level
            if min_sold_count >= 1000:
                filter_ratio = 0.02  # 2% untuk filter tinggi
            elif min_sold_count >= 500:
                filter_ratio = 0.05  # 5% untuk filter sedang
            else:
                filter_ratio = 0.1   # 10% untuk filter rendah
            
            estimated_needed_pages = math.ceil(calculated_pages / filter_ratio)
            calculated_pages = min(estimated_needed_pages, max_pages_limit)
        
        optimal_pages = min(calculated_pages, max_pages_limit)
        
        print(f"🚀 Turbo Calculation:")
        print(f"   Total data tersedia: {total_data:,}")
        if target_products and target_products > 0:
             print(f"   Target produk user: {target_products:,}")
        if min_sold_count > 0:
            print(f"   Filter minimal sold: {min_sold_count:,}")
        print(f"   Rows per page: {rows_per_page}")
        print(f"   Calculated pages: {calculated_pages:,}")
        print(f"   Turbo pages (optimal): {optimal_pages:,}")
        print(f"   Max possible products: {optimal_pages * rows_per_page:,}")
        
        return optimal_pages

    def scrape_all_products_turbo(self, keyword, target_products=None, include_detail=False, min_sold_count=500):
        """Main function untuk turbo scraping dengan concurrent processing"""
        print(f"🚀 TOKOPEDIA SCRAPER TURBO - MAXIMUM SPEED & EFFICIENCY")
        print(f"   Keyword: {keyword}")
        if target_products and target_products > 0:
            print(f"   Target: {target_products:,} produk")
        else:
            print(f"   Target: MAKSIMAL 18,000 PRODUK")
        print(f"   Minimal Sold Count: {min_sold_count:,}")
        print(f"   Include Detail Scraping: {'Ya' if include_detail else 'Tidak'}")
        print(f"   ⚡ TURBO MODE: Concurrent processing enabled")
        print("=" * 75)
        
        # Reset data storage
        self.all_products_data = []
        self.filtered_products_count = 0
        self.request_count = 0
        self.success_count = 0
        
        # Setup directory
        excel_dir = 'excel_output'
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            print(f"📁 Direktori '{excel_dir}' dibuat")
        
        # Get total available data
        success, payload_template, headers, total_data = self.get_total_available_data(keyword)
        if not success:
            print("❌ Gagal mendapatkan informasi data. Menggunakan fallback...")
            return self.scrape_with_fallback_turbo(keyword, 300, target_products, include_detail, min_sold_count)
        
        # Calculate optimal pages dengan turbo optimization
        max_pages = self.calculate_turbo_pages(total_data, 60, target_products, min_sold_count)
        if max_pages == 0:
            print("❌ Tidak ada data untuk di-scrape")
            return 0
        
        # Confirm before scraping
        print(f"\n⚠️  KONFIRMASI TURBO SCRAPING:")
        print(f"   📝 Keyword: {keyword}")
        print(f"   📄 Total pages: {max_pages:,}")
        print(f"   🔥 Filter sold count: ≥{min_sold_count:,}")
        if target_products and target_products > 0:
            print(f"   📊 Target products: {target_products:,}")
        else:
            print(f"   📊 Max possible products: {max_pages * 60:,}")
        
        # Estimasi waktu dengan turbo mode
        estimated_time = max_pages * 1.5 / 60  # Lebih cepat dengan concurrent processing
        if include_detail:
            estimated_time += (max_pages * 60 * 1) / 60  # Faster detail scraping
        print(f"   ⚡ Estimated time (TURBO): ~{estimated_time:.1f} minutes")
        print(f"   💾 Output: turbo.xlsx dengan concurrent processing")
        
        # Start turbo scraping dengan concurrent processing
        start_time = time.time()
        successful_pages = self.scrape_with_turbo_concurrent(keyword, max_pages, payload_template, headers, 60, target_products, include_detail, min_sold_count)
        end_time = time.time()
        
        actual_time = (end_time - start_time) / 60
        print(f"\n⚡ TURBO PERFORMANCE:")
        print(f"   🕐 Actual time: {actual_time:.1f} minutes")
        print(f"   📊 Request rate: {self.request_count / (end_time - start_time):.1f} req/sec")
        print(f"   ✅ Success rate: {(self.success_count / self.request_count * 100):.1f}%")
        
        if successful_pages > 0:
            print(f"\n📝 Creating Turbo Excel file...")
            self.create_turbo_excel(keyword, excel_dir, min_sold_count)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_turbo_concurrent(self, keyword, max_pages, payload_template, headers, rows_per_page, target_products=None, include_detail=False, min_sold_count=500):
        """Turbo scraping dengan concurrent processing untuk maksimal speed"""
        print(f"\n🔄 Memulai TURBO Concurrent Scraping...")
        print(f"📊 Filter: Minimal {min_sold_count:,} terjual")
        print(f"📊 Concurrent processing enabled - Multiple strategies parallel")
        
        # Divide pages between strategies untuk parallel processing
        strategy_pages = max_pages // 3
        remaining_pages = max_pages % 3
        
        strategies = [
            ('23', 'Relevance', strategy_pages + (1 if remaining_pages > 0 else 0)),
            ('9', 'Best Selling', strategy_pages + (1 if remaining_pages > 1 else 0)),
            ('5', 'Newest', strategy_pages)
        ]
        
        # Use ThreadPoolExecutor untuk concurrent strategy execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_strategy = {}
            
            for sort_by, strategy_name, pages in strategies:
                if pages > 0:
                    future = executor.submit(
                        self.scrape_strategy_turbo,
                        keyword, pages, payload_template, headers, rows_per_page,
                        sort_by, target_products, include_detail, min_sold_count, strategy_name
                    )
                    future_to_strategy[future] = strategy_name
            
            total_successful_pages = 0
            for future in concurrent.futures.as_completed(future_to_strategy):
                strategy_name = future_to_strategy[future]
                try:
                    successful_pages = future.result()
                    total_successful_pages += successful_pages
                    print(f"   ✅ {strategy_name} strategy completed: {successful_pages} pages")
                except Exception as e:
                    print(f"   ❌ {strategy_name} strategy failed: {e}")
        
        # Final summary
        print(f"\n📊 TURBO SCRAPING SUMMARY:")
        print(f"   ✅ Total successful pages: {total_successful_pages:,}")
        print(f"   📦 Total products collected: {len(self.all_products_data):,}")
        print(f"   🔥 Products meeting filter (≥{min_sold_count:,}): {self.filtered_products_count:,}")
        if self.filtered_products_count > 0 and len(self.all_products_data) > 0:
            print(f"   📈 Filter success rate: {(self.filtered_products_count/len(self.all_products_data))*100:.1f}%")
        
        return total_successful_pages
    
    def scrape_strategy_turbo(self, keyword, max_pages, payload_template, headers, rows_per_page, sort_by, target_products, include_detail, min_sold_count, strategy_name):
        """Turbo scraping untuk strategy tertentu dengan optimized delays"""
        successful_pages = 0
        
        # Batch requests untuk efficiency - process 5 pages at a time
        batch_size = 5
        page_batches = [range(i, min(i + batch_size, max_pages + 1)) for i in range(1, max_pages + 1, batch_size)]
        
        for batch in page_batches:
            # Check target sebelum batch
            if self.check_target_reached(target_products):
                print(f"   🎯 Target tercapai di {strategy_name} strategy")
                break
            
            # Process batch dengan minimal delay
            batch_results = []
            for page in batch:
                try:
                    # Track requests
                    with self.progress_lock:
                        self.request_count += 1
                    
                    # Update payload dengan sort strategy
                    params = self.build_graphql_params(keyword, page, rows_per_page, sort_by)
                    payload = payload_template.copy()
                    payload[0]['variables']['params'] = params
                    
                    # Make request dengan reduced timeout
                    response = self.session.post(
                        'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                        headers=headers,
                        json=payload,
                        timeout=20  # Reduced timeout for speed
                    )
                    
                    if response.status_code == 200:
                        with self.progress_lock:
                            self.success_count += 1
                        
                        data = response.json()
                        
                        try:
                            products = data[0]['data']['searchProductV5']['data']['products']
                            if products:
                                # Extract dan filter products
                                page_products = self.extract_and_filter_products_turbo(products, keyword, include_detail, min_sold_count)
                                batch_results.extend(page_products)
                                successful_pages += 1
                            else:
                                print(f"   ⚠️  {strategy_name} Page {page}: Tidak ada produk")
                                break
                                
                        except Exception as e:
                            print(f"   ❌ {strategy_name} Page {page}: Error extracting - {e}")
                    else:
                        if response.status_code == 429:
                            print(f"   ⚠️  {strategy_name} Page {page}: Rate limited")
                            time.sleep(2)  # Shorter wait for rate limit
                        else:
                            print(f"   ❌ {strategy_name} Page {page}: HTTP {response.status_code}")
                    
                    # Micro delay untuk prevent blocking - sangat minimal
                    time.sleep(random.uniform(0.1, 0.3))  # Sangat cepat
                    
                except Exception as e:
                    print(f"   ❌ {strategy_name} Page {page}: Error - {e}")
                    continue
            
            # Add batch results dengan thread safety
            if batch_results:
                with self.data_lock:
                    # Check for duplicates berdasarkan Product_ID
                    existing_ids = {p.get('Product_ID') for p in self.all_products_data}
                    new_products = [p for p in batch_results if p.get('Product_ID') not in existing_ids]
                    
                    if target_products and target_products > 0:
                        remaining_slots = target_products - len(self.all_products_data)
                        products_to_add = new_products[:remaining_slots]
                        self.all_products_data.extend(products_to_add)
                    else:
                        self.all_products_data.extend(new_products)
            
            # Progress display setiap batch (lebih sering untuk turbo mode)
            with self.data_lock:
                collected_count = len(self.all_products_data)
                if collected_count % 50 == 0 or batch == page_batches[-1]:  # Every 50 products or last batch
                    print(f"   📊 {strategy_name} Progress: Batch {page_batches.index(batch)+1}/{len(page_batches)} | Produk: {collected_count:,} | Filter passed: {self.filtered_products_count:,}")
            
            # Minimal batch delay
            time.sleep(random.uniform(0.2, 0.5))  # Sangat cepat antar batch
        
        return successful_pages
    
    def extract_and_filter_products_turbo(self, products, keyword, include_detail=False, min_sold_count=500):
        """Extract dan filter products dengan optimized processing untuk speed"""
        filtered_products = []
        
        for product in products:
            try:
                # Extract sold count terlebih dahulu - optimized
                sold_count = self.extract_sold_count_from_labels(product)
                
                # Filter berdasarkan minimal sold count - early exit
                if sold_count < min_sold_count:
                    continue
                
                # Increment filtered count dengan thread safety
                with self.progress_lock:
                    self.filtered_products_count += 1
                
                # Basic product info - streamlined extraction
                enhanced_product = {
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
                    'Sold_Count': sold_count,
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Filter_Passed': 'Yes',
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Skip detail scraping untuk turbo mode kecuali explicitly requested
                if include_detail and product.get('url'):
                    try:
                        detail_data = self.scrape_product_detail_turbo(product.get('url'))
                        enhanced_product.update({
                            'Description': detail_data['description'],
                            'Sold_Count_Detail': detail_data['sold_count_detail'],
                            'Stock_Info': detail_data['stock_info'],
                            'Weight': detail_data['weight'],
                            'Condition': detail_data['condition'],
                            'Minimum_Order': detail_data['minimum_order']
                        })
                    except Exception as e:
                        # Set minimal default values untuk speed
                        enhanced_product.update({
                            'Description': '',
                            'Sold_Count_Detail': 0,
                            'Stock_Info': '',
                            'Weight': '',
                            'Condition': '',
                            'Minimum_Order': 1
                        })
                
                filtered_products.append(enhanced_product)
                
            except Exception as e:
                continue  # Skip error products untuk maintain speed
        
        return filtered_products
    
    def scrape_product_detail_turbo(self, product_url):
        """Turbo detail scraping dengan timeout yang lebih cepat"""
        try:
            # Reduced sleep untuk turbo mode
            time.sleep(random.uniform(0.5, 1.0))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'id,en;q=0.9',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(product_url, headers=headers, timeout=10)  # Faster timeout
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                detail_data = {
                    'description': '',
                    'sold_count_detail': 0,
                    'stock_info': '',
                    'weight': '',
                    'condition': '',
                    'minimum_order': 1
                }
                
                # Optimized selectors - hanya yang paling penting
                desc_elem = soup.select_one('[data-testid="lblPDPDescriptionProduk"]')
                if desc_elem:
                    detail_data['description'] = desc_elem.get_text(strip=True)[:300]  # Shorter description
                
                # Optimized sold count extraction
                sold_elem = soup.select_one('[data-testid="lblPDPDetailProductSoldCounter"]')
                if sold_elem:
                    sold_text = sold_elem.get_text()
                    if 'rb' in sold_text.lower():
                        rb_match = re.search(r'(\d+(?:\.\d+)?)rb', sold_text.lower())
                        if rb_match:
                            number = float(rb_match.group(1))
                            detail_data['sold_count_detail'] = int(number * 1000)
                    else:
                        numbers = re.findall(r'\d+', sold_text)
                        if numbers:
                            detail_data['sold_count_detail'] = int(numbers[0])
                
                return detail_data
                
        except Exception as e:
            # Return minimal data untuk maintain speed
            return {
                'description': '',
                'sold_count_detail': 0,
                'stock_info': '',
                'weight': '',
                'condition': '',
                'minimum_order': 1
            }
    
    def check_target_reached(self, target_products):
        """Check apakah target sudah tercapai dengan thread safety"""
        if target_products and target_products > 0:
            with self.data_lock:
                return len(self.all_products_data) >= target_products
        return False
    
    def scrape_with_fallback_turbo(self, keyword, fallback_pages, target_products=None, include_detail=False, min_sold_count=500):
        """Turbo fallback method"""
        print(f"🔄 Using turbo fallback method dengan {fallback_pages} halaman...")
        
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
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        return self.scrape_with_turbo_concurrent(keyword, fallback_pages, payload_template, headers, 60, target_products, include_detail, min_sold_count)
    
    def create_turbo_excel(self, keyword, excel_dir, min_sold_count):
        """Create turbo Excel file dengan processing yang dioptimasi"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} filtered produk untuk Turbo Excel...")
        
        # Create DataFrame dengan optimized processing
        df = pd.DataFrame(self.all_products_data)
        
        print("🧹 Turbo data cleaning...")
        
        # Optimized duplicate removal
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"   🗑️  Removed {removed_count:,} duplicates")
        
        # Fast numeric conversion
        numeric_columns = ['Price_Number', 'Original_Price', 'Discount_Percentage', 'Rating', 'Review_Count', 'Sold_Count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Fast sorting
        df = df.sort_values(['Sold_Count', 'Rating', 'Review_Count'], ascending=[False, False, False])
        df = df.reset_index(drop=True)
        
        # Generate filename dengan turbo identifier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_sold{min_sold_count}plus_{timestamp}_turbo.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        # Create Excel dengan streamlined sheets
        try:
            print(f"💾 Creating Turbo Excel file...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main products sheet
                df.to_excel(writer, sheet_name='Filtered Products', index=False)
                
                # Streamlined summary
                summary_data = {
                    'Metric': [
                        'Total Filtered Products',
                        'Filter Criteria',
                        'Average Price',
                        'Average Rating',
                        'Average Sold Count',
                        'Total Sales Volume',
                        'Highest Sold Count',
                        'Unique Shops',
                        'Unique Cities',
                        'Keyword',
                        'Scraped At (Turbo)',
                        'Processing Mode'
                    ],
                    'Value': [
                        len(df),
                        f'Sold Count ≥ {min_sold_count:,}',
                        f"Rp {df['Price_Number'].mean():,.0f}",
                        f"{df['Rating'].mean():.2f}",
                        f"{df['Sold_Count'].mean():,.0f}",
                        f"{df['Sold_Count'].sum():,}",
                        f"{df['Sold_Count'].max():,}",
                        df['Shop_Name'].nunique(),
                        df['Shop_City'].nunique(),
                        keyword,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'TURBO MODE - Concurrent Processing'
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Turbo Summary', index=False)
                
                # Top 10 performers only (streamlined)
                if not df.empty:
                    top_sales = df.nlargest(10, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name', 'Shop_City']]
                    top_sales.to_excel(writer, sheet_name='Top 10 by Sales', index=False)
            
            print(f"\n🎉 TURBO EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk filtered: {len(df):,} produk")
            print(f"📁 File location: {filepath}")
            try:
                print(f"💾 File size: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB")
            except:
                pass
            
            # Turbo stats
            print(f"\n📈 Turbo Filtered Stats:")
            print(f"   🔥 Filter criteria: Sold Count ≥ {min_sold_count:,}")
            print(f"   💰 Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
            print(f"   📊 Sold count range: {df['Sold_Count'].min():,} - {df['Sold_Count'].max():,}")
            print(f"   ⭐ Average rating: {df['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops: {df['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities: {df['Shop_City'].nunique():,}")
            print(f"   🛒 Total sales volume: {df['Sold_Count'].sum():,}")
            print(f"   ⚡ Processing mode: TURBO (Concurrent)")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🚀 TOKOPEDIA SCRAPER TURBO - MAXIMUM SPEED OPTIMIZATION")
    print("⚡ Concurrent Processing • Optimized Delays • Streamlined Operations")
    print("=" * 75)
    
    scraper = TokopediaScraperTurbo()
    
    # Input interaktif dari user
    KEYWORD = input("Masukkan keyword pencarian produk (e.g., 'telur'): ").strip()
    
    if not KEYWORD:
        print("❌ Keyword tidak boleh kosong.")
        exit()

    target_input = input("Masukkan jumlah produk yang ingin diambil (kosong = maksimal 18,000): ").strip()
    
    TARGET_PRODUCTS = None
    if target_input:
        try:
            TARGET_PRODUCTS = int(target_input)
            if TARGET_PRODUCTS <= 0:
                print("❌ Jumlah produk harus lebih dari 0. Mengambil maksimal 18,000.")
                TARGET_PRODUCTS = None
            elif TARGET_PRODUCTS > 18000:
                print(f"⚠️  Target {TARGET_PRODUCTS:,} melebihi kapasitas. Dibatasi ke 18,000.")
                TARGET_PRODUCTS = 18000
        except ValueError:
            print("❌ Input jumlah produk tidak valid. Mengambil maksimal 18,000.")
            TARGET_PRODUCTS = None

    # Filter minimal sold count
    sold_filter_input = input("Masukkan minimal sold count (default: 500): ").strip()
    MIN_SOLD_COUNT = 500
    if sold_filter_input:
        try:
            MIN_SOLD_COUNT = int(sold_filter_input)
            if MIN_SOLD_COUNT < 0:
                print("❌ Minimal sold count tidak boleh negatif. Menggunakan default 500.")
                MIN_SOLD_COUNT = 500
        except ValueError:
            print("❌ Input minimal sold count tidak valid. Menggunakan default 500.")
            MIN_SOLD_COUNT = 500

    # Opsi untuk detail scraping (not recommended for turbo mode)
    detail_input = input("Scrape detail produk juga? (y/n, default: n, NOT RECOMMENDED for turbo): ").strip().lower()
    INCLUDE_DETAIL = detail_input in ['y', 'yes', 'ya']
    if INCLUDE_DETAIL:
        print("⚠️  Detail scraping will reduce turbo speed significantly!")
    
    print(f"\n⚙️  Turbo Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    if TARGET_PRODUCTS and TARGET_PRODUCTS > 0:
        print(f"   🎯 Target: {TARGET_PRODUCTS:,} produk")
    else:
        print(f"   🎯 Target: MAKSIMAL 18,000 produk")
    print(f"   🔥 Filter minimal sold: {MIN_SOLD_COUNT:,}")
    print(f"   📊 Output: turbo.xlsx dengan streamlined analytics")
    print(f"   🔍 Detail scraping: {'Ya (akan mengurangi speed!)' if INCLUDE_DETAIL else 'Tidak'}")
    print(f"   ⚡ Turbo mode: Concurrent processing + optimized delays")
    print(f"   🚀 Processing: 3 strategies parallel + batch processing")
    print()
    
    # Start turbo scraping
    result = scraper.scrape_all_products_turbo(
        keyword=KEYWORD, 
        target_products=TARGET_PRODUCTS, 
        include_detail=INCLUDE_DETAIL,
        min_sold_count=MIN_SOLD_COUNT
    )
    
    print(f"\n🏁 TURBO SCRAPING COMPLETED!")
    print(f"📊 Total produk yang dikumpulkan: {len(scraper.all_products_data):,}")
    print(f"🔥 Produk lolos filter (≥{MIN_SOLD_COUNT:,}): {scraper.filtered_products_count:,}")
    print(f"⚡ Request rate: {scraper.request_count} total requests")
    print(f"✅ Success rate: {(scraper.success_count / max(scraper.request_count, 1) * 100):.1f}%")
    
    if result > 0 and scraper.all_products_data:
        print(f"\n📁 Turbo Excel file ready di: excel_output/")
        print(f"🎉 Data dengan turbo processing siap untuk analisis!")
        
        # Show top products by sold count
        if scraper.all_products_data:
            df_preview = pd.DataFrame(scraper.all_products_data)
            df_preview['Sold_Count'] = pd.to_numeric(df_preview.get('Sold_Count', 0), errors='coerce').fillna(0)
            top_sold = df_preview.nlargest(5, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name']]
            print(f"\n🔥 Top 5 Produk Terlaris (≥{MIN_SOLD_COUNT:,} terjual):")
            for i, (_, row) in enumerate(top_sold.iterrows(), 1):
                print(f"   {i}. {row['Product_Name'][:60]}...")
                print(f"      💰 {row['Price_Text']} | 🛒 {row['Sold_Count']:,} terjual | 🏪 {row['Shop_Name']}")
    else:
        print(f"\n❌ No data was scraped. Coba turunkan filter atau ganti keyword.")
    
    print(f"\n⚡ TURBO Features:")
    print(f"   🚀 Concurrent strategy processing (3 parallel)")
    print(f"   ⚡ Optimized request delays (0.1-0.3s)")
    print(f"   📊 Batch processing (5 pages per batch)")
    print(f"   🔥 Streamlined data extraction")
    print(f"   💾 Fast Excel generation (3 sheets)")
    print(f"   📈 Real-time performance metrics")