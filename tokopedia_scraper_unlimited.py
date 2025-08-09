import json
import requests
import os
import re
import time
import random
import glob
import math
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlencode
from datetime import datetime
import pandas as pd

class TokopediaScraperUnlimited:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []
        self.filtered_products_data = []  # Untuk produk dengan minimal 1000 sold
        self.total_available_data = 0
        self.data_lock = threading.Lock()
        self.collected_product_ids = set()
        
    def setup_session(self):
        """Setup session dengan headers yang realistis dan optimized untuk unlimited scraping"""
        # Configure session for high volume scraping
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=15, 
            pool_maxsize=30,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
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
    
    def build_graphql_params(self, keyword, page=1, rows=60, sort_by='23'):
        """Build GraphQL parameters dengan multiple sorting options untuk coverage maksimal"""
        start = (page - 1) * rows
        
        params = {
            'device': 'desktop',
            'navsource': '',
            'ob': sort_by,  # Variable sort parameter
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
        """GraphQL query optimized untuk unlimited products dengan semua data yang diperlukan"""
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
        """Extract jumlah terjual dari labelGroups dengan improved parsing"""
        try:
            label_groups = product.get('labelGroups', [])
            for label in label_groups:
                title = label.get('title', '').lower()
                if 'terjual' in title or 'sold' in title:
                    # Enhanced parsing untuk format "1rb+", "10rb+", dll
                    if 'rb' in title:
                        rb_match = re.search(r'(\d+(?:\.\d+)?)rb', title)
                        if rb_match:
                            number = float(rb_match.group(1))
                            return int(number * 1000)
                    else:
                        # Extract regular numbers, handle "+" signs
                        numbers = re.findall(r'\d+', title)
                        if numbers:
                            return int(numbers[0])
            return 0
        except:
            return 0
    
    def calculate_unlimited_pages(self, total_data, rows_per_page, min_sold_count=1000):
        """Hitung strategi halaman untuk mengambil SEMUA data tersedia dengan filter"""
        if total_data == 0:
            return {}

        # UNLIMITED: Target = semua data tersedia
        target_products = total_data
        
        # Increase pages per strategy untuk coverage maksimal
        # Tokopedia usually allows up to 1000-2000 pages
        max_pages_per_strategy = 1000  # Conservative limit per strategy
        
        # Strategy: 3 sorting methods untuk maksimum coverage
        strategies = {
            'relevance': {'sort': '23', 'pages': 0},
            'bestseller': {'sort': '5', 'pages': 0}, 
            'newest': {'sort': '9', 'pages': 0}
        }
        
        # Distribusi target per strategy untuk coverage maksimal
        products_per_strategy = target_products // 3
        pages_per_strategy = min(
            math.ceil(products_per_strategy / rows_per_page),
            max_pages_per_strategy
        )
        
        # Jika total data sangat besar, gunakan semua halaman yang tersedia
        if target_products > (max_pages_per_strategy * 3 * rows_per_page):
            pages_per_strategy = max_pages_per_strategy
        
        for strategy in strategies:
            strategies[strategy]['pages'] = pages_per_strategy
        
        total_estimated = sum(s['pages'] for s in strategies.values()) * rows_per_page
        
        print(f"📊 Strategi UNLIMITED Products:")
        print(f"   🎯 Target: SEMUA DATA TERSEDIA ({target_products:,} produk)")
        print(f"   📄 Total data tersedia: {total_data:,}")
        print(f"   🔄 Strategies: {len(strategies)} sorting methods")
        print(f"   🎯 Filter: Produk dengan minimal {min_sold_count:,} terjual")
        for name, info in strategies.items():
            print(f"      • {name.title()}: {info['pages']:,} pages (sort: {info['sort']})")
        print(f"   📊 Estimated products to scrape: ~{total_estimated:,}")
        print(f"   ⚠️  Note: Akan mengambil SEMUA data sampai habis atau limit Tokopedia")
        
        return strategies
    
    def scrape_all_products_unlimited(self, keyword, min_sold_count=1000):
        """Main function untuk scraping UNLIMITED produk dengan filter minimal sold"""
        print(f"🚀 TOKOPEDIA SCRAPER UNLIMITED - MAXIMUM DATA EXTRACTION")
        print(f"   Keyword: {keyword}")
        print(f"   Target: SEMUA DATA TERSEDIA")
        print(f"   Filter: Minimal {min_sold_count:,} terjual")
        print("=" * 70)
        
        # Reset data storage
        self.all_products_data = []
        self.filtered_products_data = []
        self.collected_product_ids = set()
        
        # Setup directory
        excel_dir = 'excel_output'
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            print(f"📁 Direktori '{excel_dir}' dibuat")
        
        # Get total available data
        success, payload_template, headers, total_data = self.get_total_available_data(keyword)
        if not success:
            print("❌ Gagal mendapatkan informasi data. Menggunakan fallback...")
            return self.scrape_with_fallback(keyword, 500, total_data, min_sold_count)
        
        # Calculate unlimited strategy
        strategies = self.calculate_unlimited_pages(total_data, 60, min_sold_count)
        if not strategies:
            print("❌ Tidak ada strategi untuk di-scrape")
            return 0
        
        # Confirm before scraping
        total_pages = sum(s['pages'] for s in strategies.values())
        estimated_time = total_pages * 1.2 / 60  # Optimized timing for unlimited
        
        print(f"\n⚠️  KONFIRMASI SCRAPING UNLIMITED:")
        print(f"   📝 Keyword: {keyword}")
        print(f"   📄 Total pages: {total_pages:,}")
        print(f"   🎯 Target: SEMUA DATA ({total_data:,} produk)")
        print(f"   🔍 Filter: Minimal {min_sold_count:,} terjual")
        print(f"   ⏱️  Estimated time: ~{estimated_time:.1f} minutes")
        print(f"   💾 Output: unlimited.xlsx dengan filter {min_sold_count}+ sold")
        
        # Start multi-strategy scraping
        successful_pages = self.scrape_with_multi_strategy_unlimited(
            keyword, strategies, payload_template, headers, total_data, min_sold_count
        )
        
        if successful_pages > 0:
            print(f"\n📝 Creating Unlimited Excel file...")
            self.create_unlimited_excel(keyword, excel_dir, min_sold_count)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_multi_strategy_unlimited(self, keyword, strategies, payload_template, headers, target_products, min_sold_count):
        """Multi-strategy scraping untuk unlimited products dengan filter"""
        print(f"\n🔄 Memulai Multi-Strategy Unlimited Scraping...")
        
        total_successful_pages = 0
        strategy_results = {}
        
        # Execute strategies sequentially untuk stability
        for strategy_name, strategy_info in strategies.items():
            print(f"\n🔄 Strategy: {strategy_name.upper()}")
            print(f"   Sort method: {strategy_info['sort']}")
            print(f"   Pages to scrape: {strategy_info['pages']:,}")
            
            # Untuk unlimited, kita tidak ada remaining target limit
            strategy_successful_pages = self.scrape_strategy_unlimited(
                keyword, strategy_info['sort'], strategy_info['pages'], 
                payload_template, headers, min_sold_count
            )
            
            strategy_results[strategy_name] = {
                'pages': strategy_successful_pages,
                'total_products': len(self.all_products_data),
                'filtered_products': len(self.filtered_products_data)
            }
            
            total_successful_pages += strategy_successful_pages
            
            print(f"   ✅ Strategy {strategy_name}: {strategy_successful_pages:,} pages completed")
            print(f"   📦 Total products scraped: {len(self.all_products_data):,}")
            print(f"   🎯 Filtered products (>{min_sold_count-1} sold): {len(self.filtered_products_data):,}")
        
        # Final summary
        print(f"\n📊 MULTI-STRATEGY UNLIMITED SUMMARY:")
        print(f"   ✅ Total successful pages: {total_successful_pages:,}")
        print(f"   📦 Total unique products scraped: {len(self.all_products_data):,}")
        print(f"   🎯 Products with ≥{min_sold_count:,} sold: {len(self.filtered_products_data):,}")
        print(f"   📈 Filter success rate: {len(self.filtered_products_data)/len(self.all_products_data)*100:.1f}%" if self.all_products_data else "0%")
        print(f"   🔄 Strategies completed: {len(strategy_results)}")
        
        for name, result in strategy_results.items():
            print(f"      • {name.title()}: {result['pages']:,} pages, {result['total_products']:,} total, {result['filtered_products']:,} filtered")
        
        return total_successful_pages
    
    def scrape_strategy_unlimited(self, keyword, sort_by, max_pages, payload_template, headers, min_sold_count):
        """Scrape single strategy dengan unlimited target dan filter"""
        successful_pages = 0
        failed_pages = []
        consecutive_empty_pages = 0
        max_consecutive_empty = 5  # Stop jika 5 halaman berturut-turut kosong
        
        for page in range(1, max_pages + 1):
            try:
                # Update payload dengan sort parameter
                params = self.build_graphql_params(keyword, page, 60, sort_by)
                payload = payload_template.copy()
                payload[0]['variables']['params'] = params
                
                # Make request
                response = self.session.post(
                    'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                    headers=headers,
                    json=payload,
                    timeout=25
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    try:
                        products = data[0]['data']['searchProductV5']['data']['products']
                        if products:
                            consecutive_empty_pages = 0  # Reset counter
                            
                            # Extract dan filter untuk uniqueness + sold count
                            new_products, filtered_products = self.extract_and_filter_unlimited(
                                products, keyword, min_sold_count
                            )
                            
                            # Thread-safe addition
                            with self.data_lock:
                                # Add all products to main collection
                                self.all_products_data.extend(new_products)
                                
                                # Add filtered products separately
                                self.filtered_products_data.extend(filtered_products)
                                
                                # Track IDs untuk deduplication
                                for product in new_products:
                                    self.collected_product_ids.add(product['Product_ID'])
                            
                            successful_pages += 1
                        else:
                            consecutive_empty_pages += 1
                            print(f"   ⚠️  Page {page}: Tidak ada produk (consecutive empty: {consecutive_empty_pages})")
                            
                            # Jika terlalu banyak halaman kosong berturut-turut, stop strategy ini
                            if consecutive_empty_pages >= max_consecutive_empty:
                                print(f"   🛑 Stopping strategy - {max_consecutive_empty} consecutive empty pages")
                                break
                            
                    except Exception as e:
                        failed_pages.append(page)
                        print(f"❌ Page {page}: Error extracting - {e}")
                        
                else:
                    failed_pages.append(page)
                    if response.status_code == 429:
                        print(f"⚠️  Rate limited, longer pause...")
                        time.sleep(5)
                    else:
                        print(f"❌ Page {page}: HTTP {response.status_code}")
                    
                # Optimized delay untuk unlimited scraping
                if page < max_pages and page % 100 != 0:
                    time.sleep(random.uniform(0.2, 0.6))  # Faster untuk unlimited
                elif page % 100 == 0:
                    # Progress report every 100 pages
                    print(f"   📊 Page {page:,} | Total: {len(self.all_products_data):,} | Filtered: {len(self.filtered_products_data):,}")
                    time.sleep(2)  # Longer pause for stability
                
            except Exception as e:
                failed_pages.append(page)
                if "timeout" in str(e).lower():
                    time.sleep(3)
        
        print(f"   📊 Strategy completed. Failed pages: {len(failed_pages)}")
        return successful_pages
    
    def extract_and_filter_unlimited(self, products, keyword, min_sold_count):
        """Extract products dengan deduplication dan filter sold count"""
        unique_products = []
        filtered_products = []
        
        for product in products:
            try:
                product_id = str(product.get('id', ''))
                
                # Skip jika sudah ada
                if product_id in self.collected_product_ids:
                    continue
                
                # Extract sold count
                sold_count = self.extract_sold_count_from_labels(product)
                
                # Create product data
                product_data = {
                    'Keyword': keyword,
                    'Product_ID': product_id,
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
                    'Sold_Count': sold_count,
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Tambahkan ke semua produk
                unique_products.append(product_data)
                
                # Filter berdasarkan sold count
                if sold_count >= min_sold_count:
                    filtered_products.append(product_data)
                
            except Exception as e:
                continue
        
        return unique_products, filtered_products
    
    def scrape_with_fallback(self, keyword, fallback_pages, target_products, min_sold_count):
        """Fallback method untuk unlimited products"""
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
        
        # Use single strategy fallback
        strategies = {'relevance': {'sort': '23', 'pages': fallback_pages}}
        return self.scrape_with_multi_strategy_unlimited(keyword, strategies, payload_template, headers, target_products, min_sold_count)
    
    def create_unlimited_excel(self, keyword, excel_dir, min_sold_count):
        """Create comprehensive Excel file untuk unlimited products dengan filter analysis"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} total produk ({len(self.filtered_products_data):,} filtered)...")
        
        # Create DataFrames
        df_all = pd.DataFrame(self.all_products_data)
        df_filtered = pd.DataFrame(self.filtered_products_data) if self.filtered_products_data else pd.DataFrame()
        
        # Enhanced cleaning untuk unlimited dataset
        print("🧹 Enhanced data cleaning untuk unlimited dataset...")
        
        # Clean all products
        initial_count = len(df_all)
        df_all = df_all.drop_duplicates(subset=['Product_ID'], keep='first')
        removed_count = initial_count - len(df_all)
        if removed_count > 0:
            print(f"   🗑️  Removed {removed_count:,} duplicates from all products")
        
        # Clean filtered products
        if not df_filtered.empty:
            initial_filtered = len(df_filtered)
            df_filtered = df_filtered.drop_duplicates(subset=['Product_ID'], keep='first')
            removed_filtered = initial_filtered - len(df_filtered)
            if removed_filtered > 0:
                print(f"   🗑️  Removed {removed_filtered:,} duplicates from filtered products")
        
        # Clean numeric columns
        numeric_columns = ['Price_Number', 'Rating', 'Review_Count', 'Sold_Count']
        for df in [df_all, df_filtered]:
            if not df.empty:
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Sort by sold count first
        sort_columns = ['Sold_Count', 'Rating', 'Review_Count']
        df_all = df_all.sort_values(sort_columns, ascending=[False, False, False])
        df_all = df_all.reset_index(drop=True)
        
        if not df_filtered.empty:
            df_filtered = df_filtered.sort_values(sort_columns, ascending=[False, False, False])
            df_filtered = df_filtered.reset_index(drop=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_{timestamp}_unlimited_min{min_sold_count}sold.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        # Create comprehensive Excel
        try:
            print(f"💾 Creating Unlimited Excel file dengan multiple sheets...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Sheet 1: Filtered products (main focus)
                if not df_filtered.empty:
                    df_filtered.to_excel(writer, sheet_name=f'Products Min{min_sold_count} Sold', index=False)
                
                # Sheet 2: All products (for reference)
                df_all.to_excel(writer, sheet_name='All Products', index=False)
                
                # Sheet 3: Summary comparison
                summary_data = {
                    'Metric': [
                        'Total Products Scraped',
                        f'Products ≥{min_sold_count:,} Sold',
                        'Filter Success Rate',
                        'Unique Shops (All)',
                        f'Unique Shops (≥{min_sold_count:,})',
                        'Unique Cities (All)',
                        f'Unique Cities (≥{min_sold_count:,})',
                        'Average Price (All)',
                        f'Average Price (≥{min_sold_count:,})',
                        'Average Rating (All)',
                        f'Average Rating (≥{min_sold_count:,})',
                        'Total Sold Count (All)',
                        f'Total Sold Count (≥{min_sold_count:,})',
                        'Highest Sold Count',
                        'Keyword',
                        'Scraping Mode',
                        'Scraped At'
                    ],
                    'Value': [
                        len(df_all),
                        len(df_filtered) if not df_filtered.empty else 0,
                        f"{len(df_filtered)/len(df_all)*100:.1f}%" if len(df_all) > 0 else "0%",
                        df_all['Shop_Name'].nunique() if not df_all.empty else 0,
                        df_filtered['Shop_Name'].nunique() if not df_filtered.empty else 0,
                        df_all['Shop_City'].nunique() if not df_all.empty else 0,
                        df_filtered['Shop_City'].nunique() if not df_filtered.empty else 0,
                        f"Rp {df_all['Price_Number'].mean():,.0f}" if not df_all.empty else "Rp 0",
                        f"Rp {df_filtered['Price_Number'].mean():,.0f}" if not df_filtered.empty else "Rp 0",
                        f"{df_all['Rating'].mean():.2f}" if not df_all.empty else "0.00",
                        f"{df_filtered['Rating'].mean():.2f}" if not df_filtered.empty else "0.00",
                        f"{df_all['Sold_Count'].sum():,}" if not df_all.empty else "0",
                        f"{df_filtered['Sold_Count'].sum():,}" if not df_filtered.empty else "0",
                        f"{df_all['Sold_Count'].max():,}" if not df_all.empty else "0",
                        keyword,
                        f'UNLIMITED - Min {min_sold_count:,} Sold Filter',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Sheet 4: Top products by sales (dari filtered)
                if not df_filtered.empty:
                    top_sales = df_filtered.nlargest(50, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name', 'Rating', 'Review_Count']]
                    top_sales.to_excel(writer, sheet_name='Top 50 High Sellers', index=False)
                
                # Sheet 5: Sold count distribution analysis
                if not df_all.empty:
                    sold_ranges = [
                        ('1000-5000', (df_all['Sold_Count'] >= 1000) & (df_all['Sold_Count'] < 5000)),
                        ('5000-10000', (df_all['Sold_Count'] >= 5000) & (df_all['Sold_Count'] < 10000)),
                        ('10000-50000', (df_all['Sold_Count'] >= 10000) & (df_all['Sold_Count'] < 50000)),
                        ('50000+', df_all['Sold_Count'] >= 50000)
                    ]
                    
                    distribution_data = {
                        'Sold_Range': [r[0] for r in sold_ranges],
                        'Product_Count': [df_all[r[1]].shape[0] for r in sold_ranges],
                        'Percentage': [f"{df_all[r[1]].shape[0]/len(df_all)*100:.1f}%" for r in sold_ranges],
                        'Avg_Price': [f"Rp {df_all[r[1]]['Price_Number'].mean():,.0f}" if df_all[r[1]].shape[0] > 0 else "Rp 0" for r in sold_ranges],
                        'Avg_Rating': [f"{df_all[r[1]]['Rating'].mean():.2f}" if df_all[r[1]].shape[0] > 0 else "0.00" for r in sold_ranges]
                    }
                    
                    distribution_df = pd.DataFrame(distribution_data)
                    distribution_df.to_excel(writer, sheet_name='Sold Count Distribution', index=False)
            
            print(f"\n🎉 UNLIMITED EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk scraped: {len(df_all):,} produk")
            print(f"🎯 Produk dengan ≥{min_sold_count:,} sold: {len(df_filtered):,} produk")
            print(f"📁 File location: {filepath}")
            try:
                file_size_mb = os.path.getsize(filepath) / 1024 / 1024
                print(f"💾 File size: {file_size_mb:.1f} MB")
            except:
                pass
            
            # Comprehensive stats
            print(f"\n📈 Unlimited Dataset Stats:")
            print(f"   📦 Total products scraped: {len(df_all):,}")
            print(f"   🎯 High-seller products (≥{min_sold_count:,}): {len(df_filtered):,}")
            print(f"   📈 Filter success rate: {len(df_filtered)/len(df_all)*100:.1f}%" if len(df_all) > 0 else "0%")
            print(f"   💰 Price range (all): Rp {df_all['Price_Number'].min():,.0f} - Rp {df_all['Price_Number'].max():,.0f}")
            if not df_filtered.empty:
                print(f"   💰 Price range (filtered): Rp {df_filtered['Price_Number'].min():,.0f} - Rp {df_filtered['Price_Number'].max():,.0f}")
            print(f"   ⭐ Average rating (all): {df_all['Rating'].mean():.2f}")
            if not df_filtered.empty:
                print(f"   ⭐ Average rating (filtered): {df_filtered['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops (all): {df_all['Shop_Name'].nunique():,}")
            if not df_filtered.empty:
                print(f"   🏪 Unique shops (filtered): {df_filtered['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities covered (all): {df_all['Shop_City'].nunique():,}")
            print(f"   🛒 Total sold count: {df_all['Sold_Count'].sum():,}")
            print(f"   🔥 Highest sold count: {df_all['Sold_Count'].max():,}")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA SCRAPER UNLIMITED - MAXIMUM DATA EXTRACTION")
    print("🎓 Scrape SEMUA data tersedia dengan filter minimal sold count")
    print("=" * 70)
    
    scraper = TokopediaScraperUnlimited()
    
    # Input interaktif dari user
    KEYWORD = input("Masukkan keyword pencarian produk (e.g., 'smartphone'): ").strip()
    
    if not KEYWORD:
        print("❌ Keyword tidak boleh kosong.")
        exit()

    min_sold_input = input("Masukkan minimal sold count (default: 1000): ").strip()
    
    MIN_SOLD_COUNT = 1000  # Default 1000
    if min_sold_input:
        try:
            MIN_SOLD_COUNT = int(min_sold_input)
            if MIN_SOLD_COUNT < 0:
                print("❌ Minimal sold count harus ≥ 0. Menggunakan default 1000.")
                MIN_SOLD_COUNT = 1000
        except ValueError:
            print("❌ Input tidak valid. Menggunakan default 1000.")
            MIN_SOLD_COUNT = 1000

    print(f"\n⚙️  Unlimited Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    print(f"   🎯 Target: SEMUA DATA TERSEDIA (unlimited)")
    print(f"   🔍 Filter: Minimal {MIN_SOLD_COUNT:,} terjual")
    print(f"   📊 Output: unlimited.xlsx dengan comprehensive analysis")
    print(f"   🔄 Mode: Multi-strategy (relevance + bestseller + newest)")
    print(f"   ⚡ Optimized: Real-time deduplication + enhanced speed")
    print(f"   📈 Result: 2 datasets (all products + filtered products)")
    print()
    
    # Start scraping
    start_time = time.time()
    result = scraper.scrape_all_products_unlimited(keyword=KEYWORD, min_sold_count=MIN_SOLD_COUNT)
    end_time = time.time()
    
    execution_time = (end_time - start_time) / 60
    
    print(f"\n🏁 UNLIMITED SCRAPING COMPLETED!")
    print(f"📊 Total produk scraped: {len(scraper.all_products_data):,}")
    print(f"🎯 Produk dengan ≥{MIN_SOLD_COUNT:,} sold: {len(scraper.filtered_products_data):,}")
    print(f"📈 Filter success rate: {len(scraper.filtered_products_data)/len(scraper.all_products_data)*100:.1f}%" if scraper.all_products_data else "0%")
    print(f"⏱️  Total waktu eksekusi: {execution_time:.1f} menit")
    
    if result > 0 and scraper.all_products_data:
        print(f"\n📁 Unlimited Excel file ready di: excel_output/")
        print(f"🎉 Comprehensive unlimited dataset siap untuk analisis!")
        
        # Show top products by sold count (dari filtered data)
        if scraper.filtered_products_data:
            df_preview = pd.DataFrame(scraper.filtered_products_data)
            df_preview['Sold_Count'] = pd.to_numeric(df_preview.get('Sold_Count', 0), errors='coerce').fillna(0)
            top_sold = df_preview.nlargest(10, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name']]
            print(f"\n🔥 Top 10 High-Seller Products (≥{MIN_SOLD_COUNT:,} sold):")
            for i, (_, row) in enumerate(top_sold.iterrows(), 1):
                print(f"   {i:2d}. {row['Product_Name'][:50]}... | {row['Sold_Count']:,} terjual | {row['Price_Text']} | {row['Shop_Name']}")
        else:
            print(f"\n⚠️  Tidak ada produk yang memenuhi filter ≥{MIN_SOLD_COUNT:,} terjual")
            
        # Performance metrics
        products_per_minute = len(scraper.all_products_data) / execution_time if execution_time > 0 else 0
        filtered_per_minute = len(scraper.filtered_products_data) / execution_time if execution_time > 0 else 0
        
        print(f"\n📈 Performance Metrics:")
        print(f"   ⚡ Total products per minute: {products_per_minute:.0f}")
        print(f"   🎯 Filtered products per minute: {filtered_per_minute:.0f}")
        print(f"   📊 Data utilization rate: {len(scraper.filtered_products_data)/len(scraper.all_products_data)*100:.1f}%")
        
    else:
        print(f"\n❌ No data was scraped. Please check keyword or try again.")
    
    print(f"\n💡 Unlimited Features:")
    print(f"   🎯 UNLIMITED capacity - scrape ALL available data")
    print(f"   🔍 Smart filtering - hanya produk high-performing (≥{MIN_SOLD_COUNT:,} sold)")
    print(f"   🔄 Multi-strategy sorting untuk maximum coverage")
    print(f"   🗑️ Real-time deduplication untuk data quality")
    print(f"   📊 5-sheet Excel analysis (filtered + all + comparison)")
    print(f"   ⚡ Optimized performance untuk unlimited datasets")
    print(f"   📈 Comprehensive analytics dengan sold count distribution")