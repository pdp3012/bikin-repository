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

class TokopediaScraper20K:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []
        self.total_available_data = 0
        self.data_lock = threading.Lock()
        self.collected_product_ids = set()
        
    def setup_session(self):
        """Setup session dengan headers yang realistis dan optimized untuk 20K products"""
        # Configure session for high volume scraping
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10, 
            pool_maxsize=20,
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
        """GraphQL query optimized untuk 20K products dengan semua data yang diperlukan"""
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
    
    def calculate_20k_pages(self, total_data, rows_per_page, target_products=20000):
        """Hitung strategi halaman untuk mencapai 20K produk dengan multi-sorting"""
        if total_data == 0:
            return {}

        # Maksimal halaman per strategy (lebih konservatif untuk stabilitas)
        max_pages_per_strategy = 500
        
        # Hitung distribusi pages untuk multiple strategies
        if target_products > total_data:
            target_products = total_data
            
        # Strategy: 3 sorting methods untuk maksimum coverage
        strategies = {
            'relevance': {'sort': '23', 'pages': 0},
            'bestseller': {'sort': '5', 'pages': 0}, 
            'newest': {'sort': '9', 'pages': 0}
        }
        
        # Distribusi target per strategy
        products_per_strategy = target_products // 3
        pages_per_strategy = min(
            math.ceil(products_per_strategy / rows_per_page),
            max_pages_per_strategy
        )
        
        for strategy in strategies:
            strategies[strategy]['pages'] = pages_per_strategy
        
        total_estimated = sum(s['pages'] for s in strategies.values()) * rows_per_page
        
        print(f"📊 Strategi 20K Products:")
        print(f"   🎯 Target: {target_products:,} produk")
        print(f"   📄 Total data tersedia: {total_data:,}")
        print(f"   🔄 Strategies: {len(strategies)} sorting methods")
        for name, info in strategies.items():
            print(f"      • {name.title()}: {info['pages']:,} pages (sort: {info['sort']})")
        print(f"   📊 Estimated products: ~{total_estimated:,}")
        
        return strategies
    
    def scrape_all_products_20k(self, keyword, target_products=20000):
        """Main function untuk scraping hingga 20K produk dengan multi-strategy"""
        print(f"🚀 TOKOPEDIA SCRAPER 20K - MAXIMUM COVERAGE")
        print(f"   Keyword: {keyword}")
        print(f"   Target: {target_products:,} produk")
        print("=" * 70)
        
        # Reset data storage
        self.all_products_data = []
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
            return self.scrape_with_fallback(keyword, 200, target_products)
        
        # Calculate 20K strategy
        strategies = self.calculate_20k_pages(total_data, 60, target_products)
        if not strategies:
            print("❌ Tidak ada strategi untuk di-scrape")
            return 0
        
        # Confirm before scraping
        total_pages = sum(s['pages'] for s in strategies.values())
        estimated_time = total_pages * 1.5 / 60  # Optimized timing for 20K
        
        print(f"\n⚠️  KONFIRMASI SCRAPING 20K:")
        print(f"   📝 Keyword: {keyword}")
        print(f"   📄 Total pages: {total_pages:,}")
        print(f"   🎯 Target: {target_products:,} produk")
        print(f"   ⏱️  Estimated time: ~{estimated_time:.1f} minutes")
        print(f"   💾 Output: 20k.xlsx dengan sold count")
        
        # Start multi-strategy scraping
        successful_pages = self.scrape_with_multi_strategy_20k(
            keyword, strategies, payload_template, headers, target_products
        )
        
        if successful_pages > 0:
            print(f"\n📝 Creating 20K Excel file...")
            self.create_20k_excel(keyword, excel_dir)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_multi_strategy_20k(self, keyword, strategies, payload_template, headers, target_products):
        """Multi-strategy scraping untuk mencapai 20K products dengan concurrent execution"""
        print(f"\n🔄 Memulai Multi-Strategy Scraping 20K...")
        
        total_successful_pages = 0
        strategy_results = {}
        
        # Execute strategies sequentially untuk stability, tapi dengan optimized speed
        for strategy_name, strategy_info in strategies.items():
            if len(self.all_products_data) >= target_products:
                print(f"🎯 Target {target_products:,} tercapai, stopping strategies.")
                break
                
            print(f"\n🔄 Strategy: {strategy_name.upper()}")
            print(f"   Sort method: {strategy_info['sort']}")
            print(f"   Pages to scrape: {strategy_info['pages']:,}")
            
            remaining_target = target_products - len(self.all_products_data)
            strategy_successful_pages = self.scrape_strategy_20k(
                keyword, strategy_info['sort'], strategy_info['pages'], 
                payload_template, headers, remaining_target
            )
            
            strategy_results[strategy_name] = {
                'pages': strategy_successful_pages,
                'products': len(self.all_products_data) - sum(r.get('products', 0) for r in list(strategy_results.values())[:-1]) if strategy_results else len(self.all_products_data)
            }
            
            total_successful_pages += strategy_successful_pages
            
            print(f"   ✅ Strategy {strategy_name}: {strategy_successful_pages:,} pages completed")
            print(f"   📦 Total products so far: {len(self.all_products_data):,}")
            
            # Break jika sudah mencapai target
            if len(self.all_products_data) >= target_products:
                break
        
        # Final summary
        print(f"\n📊 MULTI-STRATEGY SUMMARY:")
        print(f"   ✅ Total successful pages: {total_successful_pages:,}")
        print(f"   📦 Total unique products: {len(self.all_products_data):,}")
        print(f"   🔄 Strategies completed: {len(strategy_results)}")
        
        for name, result in strategy_results.items():
            print(f"      • {name.title()}: {result['pages']:,} pages, ~{result.get('products', 0):,} products")
        
        return total_successful_pages
    
    def scrape_strategy_20k(self, keyword, sort_by, max_pages, payload_template, headers, remaining_target):
        """Scrape single strategy dengan optimized speed untuk 20K products"""
        successful_pages = 0
        failed_pages = []
        
        for page in range(1, max_pages + 1):
            # Check if target reached or remaining target is very small
            if len(self.all_products_data) >= remaining_target:
                break
                
            try:
                # Update payload dengan sort parameter
                params = self.build_graphql_params(keyword, page, 60, sort_by)
                payload = payload_template.copy()
                payload[0]['variables']['params'] = params
                
                # Make request dengan timeout yang lebih pendek untuk speed
                response = self.session.post(
                    'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    try:
                        products = data[0]['data']['searchProductV5']['data']['products']
                        if products:
                            # Extract dan filter untuk uniqueness
                            new_products = self.extract_and_dedupe_20k(products, keyword)
                            
                            # Thread-safe addition
                            with self.data_lock:
                                # Only add up to remaining target
                                remaining_slots = remaining_target - len(self.all_products_data)
                                products_to_add = new_products[:remaining_slots]
                                self.all_products_data.extend(products_to_add)
                                
                                # Track IDs untuk deduplication
                                for product in products_to_add:
                                    self.collected_product_ids.add(product['Product_ID'])
                            
                            successful_pages += 1
                            
                            # Early termination jika target tercapai
                            if len(self.all_products_data) >= remaining_target:
                                break
                        else:
                            # No more products in this strategy
                            break
                            
                    except Exception as e:
                        failed_pages.append(page)
                        print(f"❌ Page {page}: Error extracting - {e}")
                        
                else:
                    failed_pages.append(page)
                    if response.status_code == 429:
                        print(f"⚠️  Rate limited, brief pause...")
                        time.sleep(3)
                    
                # Optimized delay untuk speed (shorter untuk 20K target)
                if page < max_pages and page % 50 != 0:  # Skip delay every 50 pages
                    time.sleep(random.uniform(0.3, 0.8))
                elif page % 50 == 0:
                    # Progress report every 50 pages
                    print(f"   📊 Page {page:,} | Products: {len(self.all_products_data):,}")
                    time.sleep(1)  # Slightly longer pause untuk stability
                
            except Exception as e:
                failed_pages.append(page)
                if "timeout" in str(e).lower():
                    time.sleep(2)
        
        return successful_pages
    
    def extract_and_dedupe_20k(self, products, keyword):
        """Extract products dengan deduplication untuk 20K target"""
        unique_products = []
        
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
                
                unique_products.append(product_data)
                
            except Exception as e:
                continue
        
        return unique_products
    
    def scrape_with_fallback(self, keyword, fallback_pages, target_products):
        """Fallback method untuk 20K products"""
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
        return self.scrape_with_multi_strategy_20k(keyword, strategies, payload_template, headers, target_products)
    
    def create_20k_excel(self, keyword, excel_dir):
        """Create enhanced Excel file untuk 20K products dengan comprehensive analysis"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} produk untuk 20K Excel...")
        
        # Create DataFrame
        df = pd.DataFrame(self.all_products_data)
        
        # Enhanced cleaning untuk 20K dataset
        print("🧹 Enhanced data cleaning untuk 20K dataset...")
        
        # Remove duplicates berdasarkan Product_ID (should be minimal due to deduplication)
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"   🗑️  Removed {removed_count:,} duplicates")
        
        # Clean numeric columns
        numeric_columns = ['Price_Number', 'Rating', 'Review_Count', 'Sold_Count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Sort by sold count first untuk best products on top
        sort_columns = ['Sold_Count', 'Rating', 'Review_Count']
        df = df.sort_values(sort_columns, ascending=[False, False, False])
        df = df.reset_index(drop=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_{timestamp}_20k.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        # Create comprehensive Excel
        try:
            print(f"💾 Creating 20K Excel file dengan multiple sheets...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main products sheet
                df.to_excel(writer, sheet_name='All Products', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Products',
                        'Unique Shops',
                        'Unique Cities',
                        'Average Price',
                        'Median Price',
                        'Average Rating',
                        'Total Sold Count',
                        'Products with Sales Data',
                        'Highest Sold Count',
                        'Products >1000 Sold',
                        'Products >500 Sold',
                        'Top Price Range',
                        'Keyword',
                        'Scraping Mode',
                        'Scraped At'
                    ],
                    'Value': [
                        len(df),
                        df['Shop_Name'].nunique(),
                        df['Shop_City'].nunique(),
                        f"Rp {df['Price_Number'].mean():,.0f}",
                        f"Rp {df['Price_Number'].median():,.0f}",
                        f"{df['Rating'].mean():.2f}",
                        f"{df['Sold_Count'].sum():,}",
                        f"{(df['Sold_Count'] > 0).sum():,} ({(df['Sold_Count'] > 0).mean()*100:.1f}%)",
                        f"{df['Sold_Count'].max():,}",
                        f"{(df['Sold_Count'] > 1000).sum():,}",
                        f"{(df['Sold_Count'] > 500).sum():,}",
                        f"Rp {df['Price_Number'].quantile(0.9):,.0f}",
                        keyword,
                        '20K MULTI-STRATEGY',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Top products by sales (top 100)
                if len(df) > 0:
                    top_sales = df.nlargest(100, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name', 'Rating', 'Review_Count']]
                    top_sales.to_excel(writer, sheet_name='Top 100 Sales', index=False)
                
                # Top shops analysis
                if 'Shop_Name' in df.columns:
                    shop_analysis = df.groupby('Shop_Name').agg({
                        'Product_ID': 'count',
                        'Sold_Count': 'sum',
                        'Rating': 'mean',
                        'Price_Number': 'mean'
                    }).round(2)
                    shop_analysis.columns = ['Product_Count', 'Total_Sales', 'Avg_Rating', 'Avg_Price']
                    shop_analysis = shop_analysis.sort_values('Total_Sales', ascending=False).head(50)
                    shop_analysis.to_excel(writer, sheet_name='Top 50 Shops', index=True)
            
            print(f"\n🎉 20K EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk unik: {len(df):,} produk")
            print(f"📁 File location: {filepath}")
            try:
                file_size_mb = os.path.getsize(filepath) / 1024 / 1024
                print(f"💾 File size: {file_size_mb:.1f} MB")
            except:
                pass
            
            # Comprehensive stats untuk 20K dataset
            print(f"\n📈 20K Dataset Stats:")
            print(f"   💰 Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
            print(f"   📊 Median price: Rp {df['Price_Number'].median():,.0f}")
            print(f"   ⭐ Average rating: {df['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops: {df['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities covered: {df['Shop_City'].nunique():,}")
            print(f"   🛒 Total sold count: {df['Sold_Count'].sum():,}")
            print(f"   📊 Products with sales: {(df['Sold_Count'] > 0).sum():,} ({(df['Sold_Count'] > 0).mean()*100:.1f}%)")
            print(f"   🔥 Products >500 sold: {(df['Sold_Count'] > 500).sum():,}")
            print(f"   🚀 Products >1000 sold: {(df['Sold_Count'] > 1000).sum():,}")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA SCRAPER 20K - MAXIMUM COVERAGE")
    print("🎓 Multi-Strategy Approach untuk Maximum Data Collection")
    print("=" * 70)
    
    scraper = TokopediaScraper20K()
    
    # Input interaktif dari user
    KEYWORD = input("Masukkan keyword pencarian produk (e.g., 'telur'): ").strip()
    
    if not KEYWORD:
        print("❌ Keyword tidak boleh kosong.")
        exit()

    target_input = input("Masukkan target produk (default: 20000, max: 25000): ").strip()
    
    TARGET_PRODUCTS = 20000  # Default 20K
    if target_input:
        try:
            TARGET_PRODUCTS = int(target_input)
            if TARGET_PRODUCTS <= 0:
                print("❌ Target harus lebih dari 0. Menggunakan default 20,000.")
                TARGET_PRODUCTS = 20000
            elif TARGET_PRODUCTS > 25000:
                print("⚠️  Target maksimal 25,000. Menggunakan 25,000.")
                TARGET_PRODUCTS = 25000
        except ValueError:
            print("❌ Input tidak valid. Menggunakan default 20,000.")
            TARGET_PRODUCTS = 20000

    print(f"\n⚙️  20K Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    print(f"   🎯 Target: {TARGET_PRODUCTS:,} produk")
    print(f"   📊 Output: 20k.xlsx dengan comprehensive analysis")
    print(f"   🔄 Mode: Multi-strategy (relevance + bestseller + newest)")
    print(f"   ⚡ Optimized: Deduplication + enhanced speed")
    print()
    
    # Start scraping
    start_time = time.time()
    result = scraper.scrape_all_products_20k(keyword=KEYWORD, target_products=TARGET_PRODUCTS)
    end_time = time.time()
    
    execution_time = (end_time - start_time) / 60
    
    print(f"\n🏁 20K SCRAPING COMPLETED!")
    print(f"📊 Total produk yang dikumpulkan: {len(scraper.all_products_data):,}")
    print(f"⏱️  Total waktu eksekusi: {execution_time:.1f} menit")
    
    if result > 0 and scraper.all_products_data:
        print(f"\n📁 20K Excel file ready di: excel_output/")
        print(f"🎉 Comprehensive dataset siap untuk analisis mendalam!")
        
        # Show top products by sold count
        if scraper.all_products_data:
            df_preview = pd.DataFrame(scraper.all_products_data)
            df_preview['Sold_Count'] = pd.to_numeric(df_preview.get('Sold_Count', 0), errors='coerce').fillna(0)
            top_sold = df_preview.nlargest(10, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name']]
            print(f"\n🔥 Top 10 Produk Terlaris dari {len(df_preview):,} produk:")
            for i, (_, row) in enumerate(top_sold.iterrows(), 1):
                print(f"   {i:2d}. {row['Product_Name'][:50]}... | {row['Sold_Count']:,} terjual | {row['Price_Text']} | {row['Shop_Name']}")
                
        # Performance metrics
        products_per_minute = len(scraper.all_products_data) / execution_time if execution_time > 0 else 0
        print(f"\n📈 Performance Metrics:")
        print(f"   ⚡ Products per minute: {products_per_minute:.0f}")
        print(f"   🎯 Target achievement: {len(scraper.all_products_data)/TARGET_PRODUCTS*100:.1f}%")
        
    else:
        print(f"\n❌ No data was scraped. Please check keyword or try again.")
    
    print(f"\n💡 20K Features:")
    print(f"   🔄 Multi-strategy sorting untuk maximum coverage")
    print(f"   🗑️ Real-time deduplication untuk data quality")
    print(f"   📊 Comprehensive Excel dengan 4 sheets analysis")
    print(f"   ⚡ Optimized performance untuk large datasets")
    print(f"   🎯 Smart targeting dengan early termination")