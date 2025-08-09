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

class TokopediaScraperAdvanced:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []
        self.total_available_data = 0
        self.filtered_products_count = 0
        self.data_lock = Lock()
        
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
        """Extract jumlah terjual dari labelGroups dengan parsing yang lebih robust"""
        try:
            label_groups = product.get('labelGroups', [])
            for label in label_groups:
                title = label.get('title', '').lower()
                if 'terjual' in title or 'sold' in title:
                    # Extract number dari format seperti "500+ terjual", "1rb+ terjual", "10rb+ terjual"
                    # Handle format ribuan: "1rb" = 1000, "10rb" = 10000
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
    
    def calculate_advanced_pages(self, total_data, rows_per_page, target_products=None, min_sold_count=0):
        """Hitung jumlah halaman optimal untuk maksimal 18,000 produk dengan filter"""
        if total_data == 0:
            return 0

        # Tingkatkan limit maksimal menjadi 18,000 produk (300 halaman * 60 produk)
        max_products_limit = 18000
        max_pages_limit = math.ceil(max_products_limit / rows_per_page)  # 300 halaman

        if target_products and target_products > 0:
            # Hitung halaman berdasarkan target produk
            calculated_pages = math.ceil(target_products / rows_per_page)
        else:
            # Hitung halaman berdasarkan total data tersedia
            calculated_pages = math.ceil(total_data / rows_per_page)
        
        # Jika ada filter sold count, perkirakan perlu lebih banyak halaman
        if min_sold_count > 0:
            # Estimasi: hanya 5-10% produk memenuhi kriteria sold count tinggi
            filter_ratio = 0.05 if min_sold_count >= 500 else 0.1
            estimated_needed_pages = math.ceil(calculated_pages / filter_ratio)
            calculated_pages = min(estimated_needed_pages, max_pages_limit)
        
        # Ambil yang terkecil antara calculated pages dan limit
        optimal_pages = min(calculated_pages, max_pages_limit)
        
        print(f"📊 Advanced Calculation:")
        print(f"   Total data tersedia: {total_data:,}")
        if target_products and target_products > 0:
             print(f"   Target produk user: {target_products:,}")
        if min_sold_count > 0:
            print(f"   Filter minimal sold: {min_sold_count:,}")
        print(f"   Rows per page: {rows_per_page}")
        print(f"   Calculated pages: {calculated_pages:,}")
        print(f"   Optimal pages (dengan limit 18K): {optimal_pages:,}")
        print(f"   Max possible products: {optimal_pages * rows_per_page:,}")
        
        return optimal_pages

    def scrape_all_products_advanced(self, keyword, target_products=None, include_detail=False, min_sold_count=500):
        """Main function untuk scraping produk dengan filter dan kapasitas tinggi"""
        print(f"🚀 TOKOPEDIA SCRAPER ADVANCED - FILTER & HIGH CAPACITY")
        print(f"   Keyword: {keyword}")
        if target_products and target_products > 0:
            print(f"   Target: {target_products:,} produk")
        else:
            print(f"   Target: MAKSIMAL 18,000 PRODUK")
        print(f"   Minimal Sold Count: {min_sold_count:,}")
        print(f"   Include Detail Scraping: {'Ya' if include_detail else 'Tidak'}")
        print("=" * 75)
        
        # Reset data storage
        self.all_products_data = []
        self.filtered_products_count = 0
        
        # Setup directory
        excel_dir = 'excel_output'
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            print(f"📁 Direktori '{excel_dir}' dibuat")
        
        # Get total available data
        success, payload_template, headers, total_data = self.get_total_available_data(keyword)
        if not success:
            print("❌ Gagal mendapatkan informasi data. Menggunakan fallback...")
            return self.scrape_with_fallback_advanced(keyword, 300, target_products, include_detail, min_sold_count)
        
        # Calculate optimal pages dengan filter consideration
        max_pages = self.calculate_advanced_pages(total_data, 60, target_products, min_sold_count)
        if max_pages == 0:
            print("❌ Tidak ada data untuk di-scrape")
            return 0
        
        # Confirm before scraping
        print(f"\n⚠️  KONFIRMASI ADVANCED SCRAPING:")
        print(f"   📝 Keyword: {keyword}")
        print(f"   📄 Total pages: {max_pages:,}")
        print(f"   🔥 Filter sold count: ≥{min_sold_count:,}")
        if target_products and target_products > 0:
            print(f"   📊 Target products: {target_products:,}")
        else:
            print(f"   📊 Max possible products: {max_pages * 60:,}")
        
        if include_detail:
            estimated_time = max_pages * 3 / 60 + (max_pages * 60 * 2) / 60  # Base time + detail scraping time
            print(f"   ⏱️  Estimated time: ~{estimated_time:.1f} minutes (dengan detail scraping)")
        else:
            print(f"   ⏱️  Estimated time: ~{max_pages * 3 / 60:.1f} minutes")
        
        print(f"   💾 Output: advanced.xlsx dengan filter results")
        
        # Start multi-strategy scraping
        successful_pages = self.scrape_with_multi_strategy(keyword, max_pages, payload_template, headers, 60, target_products, include_detail, min_sold_count)
        
        if successful_pages > 0:
            print(f"\n📝 Creating Advanced Excel file...")
            self.create_advanced_excel(keyword, excel_dir, min_sold_count)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_multi_strategy(self, keyword, max_pages, payload_template, headers, rows_per_page, target_products=None, include_detail=False, min_sold_count=500):
        """Scraping dengan multiple strategies untuk maksimal coverage"""
        successful_pages = 0
        failed_pages = []
        
        print(f"\n🔄 Memulai Advanced Multi-Strategy Scraping...")
        print(f"📊 Filter: Minimal {min_sold_count:,} terjual")
        print(f"📊 Progress akan ditampilkan setiap 25 halaman")
        
        # Strategy 1: Sort by relevance (default)
        print(f"\n🎯 Strategy 1: Relevance-based scraping...")
        strategy1_pages = min(max_pages // 3, 100)  # 1/3 dari total atau max 100 halaman
        successful_pages += self.scrape_with_strategy(keyword, strategy1_pages, payload_template, headers, rows_per_page, '23', target_products, include_detail, min_sold_count, "Relevance")
        
        # Check if target reached
        if self.check_target_reached(target_products):
            return successful_pages
        
        # Strategy 2: Sort by sold count (paling banyak terjual)
        print(f"\n🔥 Strategy 2: Best-selling products...")
        strategy2_pages = min(max_pages // 3, 100)  # 1/3 dari total atau max 100 halaman
        successful_pages += self.scrape_with_strategy(keyword, strategy2_pages, payload_template, headers, rows_per_page, '9', target_products, include_detail, min_sold_count, "Best Selling")
        
        # Check if target reached
        if self.check_target_reached(target_products):
            return successful_pages
        
        # Strategy 3: Sort by newest untuk produk baru yang potensial viral
        print(f"\n🆕 Strategy 3: Newest products...")
        strategy3_pages = min(max_pages - strategy1_pages - strategy2_pages, 100)
        successful_pages += self.scrape_with_strategy(keyword, strategy3_pages, payload_template, headers, rows_per_page, '5', target_products, include_detail, min_sold_count, "Newest")
        
        # Final summary
        print(f"\n📊 ADVANCED SCRAPING SUMMARY:")
        print(f"   ✅ Total successful pages: {successful_pages:,}")
        print(f"   📦 Total products collected: {len(self.all_products_data):,}")
        print(f"   🔥 Products meeting filter (≥{min_sold_count:,}): {self.filtered_products_count:,}")
        if self.filtered_products_count > 0:
            print(f"   📈 Filter success rate: {(self.filtered_products_count/len(self.all_products_data))*100:.1f}%")
        
        return successful_pages
    
    def scrape_with_strategy(self, keyword, max_pages, payload_template, headers, rows_per_page, sort_by, target_products, include_detail, min_sold_count, strategy_name):
        """Scraping dengan strategy tertentu"""
        successful_pages = 0
        
        for page in range(1, max_pages + 1):
            # Cek apakah sudah mencapai target
            if self.check_target_reached(target_products):
                print(f"   🎯 Target tercapai di {strategy_name} strategy, halaman {page}")
                break

            try:
                # Update payload dengan sort strategy
                params = self.build_graphql_params(keyword, page, rows_per_page, sort_by)
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
                    
                    try:
                        products = data[0]['data']['searchProductV5']['data']['products']
                        if products:
                            # Extract dan filter products
                            page_products = self.extract_and_filter_products(products, keyword, include_detail, min_sold_count)
                            
                            # Thread-safe data addition
                            with self.data_lock:
                                # Check for duplicates berdasarkan Product_ID sebelum menambah
                                existing_ids = {p.get('Product_ID') for p in self.all_products_data}
                                new_products = [p for p in page_products if p.get('Product_ID') not in existing_ids]
                                
                                if target_products and target_products > 0:
                                    remaining_slots = target_products - len(self.all_products_data)
                                    products_to_add = new_products[:remaining_slots]
                                    self.all_products_data.extend(products_to_add)
                                else:
                                    self.all_products_data.extend(new_products)
                                
                                successful_pages += 1
                        else:
                            print(f"   ⚠️  {strategy_name} Page {page}: Tidak ada produk")
                            break
                            
                    except Exception as e:
                        print(f"   ❌ {strategy_name} Page {page}: Error extracting - {e}")
                else:
                    if response.status_code == 429:
                        print(f"   ⚠️  {strategy_name} Page {page}: Rate limited, waiting...")
                        time.sleep(10)
                    else:
                        print(f"   ❌ {strategy_name} Page {page}: HTTP {response.status_code}")
                
                # Progress display
                if page % 25 == 0 or page == max_pages:
                    with self.data_lock:
                        collected_count = len(self.all_products_data)
                        print(f"   📊 {strategy_name} Progress: Halaman {page:,} | Produk: {collected_count:,} | Filter passed: {self.filtered_products_count:,}")
                
                # Smart delay dengan variasi berdasarkan strategy
                if page < max_pages:
                    base_delay = random.uniform(0.3, 1.5)
                    if sort_by == '9':  # Best selling strategy - lebih hati-hati
                        base_delay += 0.5
                    if page % 50 == 0:
                        base_delay += 2
                    time.sleep(base_delay)
                
            except Exception as e:
                print(f"   ❌ {strategy_name} Page {page}: Error - {e}")
                if "timeout" in str(e).lower():
                    time.sleep(5)
        
        return successful_pages
    
    def extract_and_filter_products(self, products, keyword, include_detail=False, min_sold_count=500):
        """Extract dan filter products berdasarkan sold count minimum"""
        filtered_products = []
        
        for idx, product in enumerate(products, 1):
            try:
                # Extract sold count terlebih dahulu
                sold_count = self.extract_sold_count_from_labels(product)
                
                # Filter berdasarkan minimal sold count
                if sold_count < min_sold_count:
                    continue
                
                # Increment filtered count
                self.filtered_products_count += 1
                
                # Basic product info
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
                    'Sold_Count': sold_count,  # ✨ Sudah memenuhi filter minimum
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Filter_Passed': 'Yes',  # 🔥 NEW: Marker bahwa produk lolos filter
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Optional: Scrape detail produk jika diminta
                if include_detail and product.get('url'):
                    try:
                        detail_data = self.scrape_product_detail(product.get('url'))
                        enhanced_product.update({
                            'Description': detail_data['description'],
                            'Sold_Count_Detail': detail_data['sold_count_detail'],
                            'Stock_Info': detail_data['stock_info'],
                            'Weight': detail_data['weight'],
                            'Condition': detail_data['condition'],
                            'Minimum_Order': detail_data['minimum_order']
                        })
                    except Exception as e:
                        # Set default values jika detail scraping gagal
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
                print(f"   ❌ Error processing product {idx}: {e}")
                continue
        
        return filtered_products
    
    def check_target_reached(self, target_products):
        """Check apakah target sudah tercapai"""
        if target_products and target_products > 0:
            with self.data_lock:
                return len(self.all_products_data) >= target_products
        return False
    
    def scrape_product_detail(self, product_url):
        """Scrape detail produk dari halaman produk individual - sama seperti sebelumnya"""
        try:
            time.sleep(random.uniform(1, 2))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'id,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(product_url, headers=headers, timeout=15)
            
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
                
                # Extract deskripsi produk
                desc_selectors = [
                    '[data-testid="lblPDPDescriptionProduk"]',
                    '.pdp-product-detail-description',
                    '[data-testid="pdpDescriptionSection"]'
                ]
                
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        detail_data['description'] = desc_elem.get_text(strip=True)[:500]
                        break
                
                # Extract sold count detail
                sold_selectors = [
                    '[data-testid="lblPDPDetailProductSoldCounter"]',
                    'span:contains("terjual")',
                    '.sold-count'
                ]
                
                for selector in sold_selectors:
                    sold_elem = soup.select_one(selector)
                    if sold_elem:
                        sold_text = sold_elem.get_text()
                        # Handle format ribuan juga
                        if 'rb' in sold_text.lower():
                            rb_match = re.search(r'(\d+(?:\.\d+)?)rb', sold_text.lower())
                            if rb_match:
                                number = float(rb_match.group(1))
                                detail_data['sold_count_detail'] = int(number * 1000)
                                break
                        else:
                            numbers = re.findall(r'\d+', sold_text)
                            if numbers:
                                detail_data['sold_count_detail'] = int(numbers[0])
                                break
                
                # Extract informasi lainnya (sama seperti sebelumnya)
                stock_selectors = [
                    '[data-testid="lblPDPDetailProductStockNumber"]',
                    '.stock-info'
                ]
                
                for selector in stock_selectors:
                    stock_elem = soup.select_one(selector)
                    if stock_elem:
                        detail_data['stock_info'] = stock_elem.get_text(strip=True)
                        break
                
                weight_selectors = [
                    '[data-testid="lblPDPDetailProductWeight"]',
                    'span:contains("gram")',
                    'span:contains("kg")'
                ]
                
                for selector in weight_selectors:
                    weight_elem = soup.select_one(selector)
                    if weight_elem:
                        weight_text = weight_elem.get_text(strip=True)
                        if any(unit in weight_text.lower() for unit in ['gram', 'kg', 'g']):
                            detail_data['weight'] = weight_text
                            break
                
                condition_selectors = [
                    '[data-testid="lblPDPDetailProductCondition"]',
                    'span:contains("Baru")',
                    'span:contains("Bekas")'
                ]
                
                for selector in condition_selectors:
                    condition_elem = soup.select_one(selector)
                    if condition_elem:
                        detail_data['condition'] = condition_elem.get_text(strip=True)
                        break
                
                return detail_data
                
        except Exception as e:
            print(f"   ❌ Error scraping detail: {e}")
            return {
                'description': '',
                'sold_count_detail': 0,
                'stock_info': '',
                'weight': '',
                'condition': '',
                'minimum_order': 1
            }
    
    def scrape_with_fallback_advanced(self, keyword, fallback_pages, target_products=None, include_detail=False, min_sold_count=500):
        """Fallback method dengan filter"""
        print(f"🔄 Using advanced fallback method dengan {fallback_pages} halaman...")
        
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
        
        return self.scrape_with_multi_strategy(keyword, fallback_pages, payload_template, headers, 60, target_products, include_detail, min_sold_count)
    
    def create_advanced_excel(self, keyword, excel_dir, min_sold_count):
        """Create advanced Excel file dengan filtered results dan analytics"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return
        
        print(f"📊 Processing {len(self.all_products_data):,} filtered produk untuk Advanced Excel...")
        
        # Create DataFrame
        df = pd.DataFrame(self.all_products_data)
        
        # Advanced cleaning
        print("🧹 Advanced data cleaning...")
        
        # Remove duplicates berdasarkan Product_ID
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"   🗑️  Removed {removed_count:,} duplicates")
        
        # Clean numeric columns
        numeric_columns = ['Price_Number', 'Original_Price', 'Discount_Percentage', 'Rating', 'Review_Count', 'Sold_Count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Advanced sorting: Sold Count (descending) → Rating → Review Count
        df = df.sort_values(['Sold_Count', 'Rating', 'Review_Count'], ascending=[False, False, False])
        df = df.reset_index(drop=True)
        
        # Generate filename dengan filter info
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'tokopedia_{keyword}_sold{min_sold_count}plus_{timestamp}_advanced.xlsx'
        filepath = os.path.join(excel_dir, filename)
        
        # Create Excel dengan multiple sheets
        try:
            print(f"💾 Creating Advanced Excel file...")
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main products sheet
                df.to_excel(writer, sheet_name='Filtered Products', index=False)
                
                # Summary analytics sheet
                summary_data = {
                    'Metric': [
                        'Total Filtered Products',
                        'Filter Criteria',
                        'Min Sold Count Filter',
                        'Unique Shops',
                        'Unique Cities',
                        'Average Price',
                        'Median Price',
                        'Average Rating',
                        'Average Sold Count',
                        'Median Sold Count',
                        'Total Sales Volume',
                        'Highest Sold Count',
                        'Most Expensive Product',
                        'Best Rating',
                        'Top Shop by Volume',
                        'Top City by Products',
                        'Keyword',
                        'Scraped At',
                        'Filter Success Rate'
                    ],
                    'Value': [
                        len(df),
                        f'Sold Count ≥ {min_sold_count:,}',
                        f'{min_sold_count:,}',
                        df['Shop_Name'].nunique(),
                        df['Shop_City'].nunique(),
                        f"Rp {df['Price_Number'].mean():,.0f}",
                        f"Rp {df['Price_Number'].median():,.0f}",
                        f"{df['Rating'].mean():.2f}",
                        f"{df['Sold_Count'].mean():,.0f}",
                        f"{df['Sold_Count'].median():,.0f}",
                        f"{df['Sold_Count'].sum():,}",
                        f"{df['Sold_Count'].max():,}",
                        f"Rp {df['Price_Number'].max():,.0f}",
                        f"{df['Rating'].max():.1f}",
                        df.groupby('Shop_Name')['Sold_Count'].sum().idxmax() if not df.empty else 'N/A',
                        df['Shop_City'].value_counts().index[0] if not df.empty else 'N/A',
                        keyword,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        f'{self.filtered_products_count:,} products passed filter'
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Advanced Summary', index=False)
                
                # Top performers analysis
                if not df.empty:
                    top_performers = {
                        'Top 20 by Sales': df.nlargest(20, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name', 'Shop_City']],
                        'Top 20 by Rating': df.nlargest(20, 'Rating')[['Product_Name', 'Rating', 'Review_Count', 'Sold_Count', 'Shop_Name']],
                        'Top 20 Most Expensive': df.nlargest(20, 'Price_Number')[['Product_Name', 'Price_Text', 'Sold_Count', 'Rating', 'Shop_Name']]
                    }
                    
                    # Add top performers to separate sheets
                    for sheet_name, data in top_performers.items():
                        data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Shop analysis
                if not df.empty:
                    shop_analysis = df.groupby('Shop_Name').agg({
                        'Sold_Count': ['sum', 'mean', 'count'],
                        'Price_Number': 'mean',
                        'Rating': 'mean'
                    }).round(2)
                    
                    shop_analysis.columns = ['Total_Sales', 'Avg_Sales_Per_Product', 'Product_Count', 'Avg_Price', 'Avg_Rating']
                    shop_analysis = shop_analysis.sort_values('Total_Sales', ascending=False).head(50)
                    shop_analysis.to_excel(writer, sheet_name='Top Shops Analysis')
            
            print(f"\n🎉 ADVANCED EXCEL FILE BERHASIL DIBUAT!")
            print(f"📊 Total produk filtered: {len(df):,} produk")
            print(f"📁 File location: {filepath}")
            try:
                print(f"💾 File size: {os.path.getsize(filepath) / 1024 / 1024:.1f} MB")
            except:
                pass
            
            # Advanced stats
            print(f"\n📈 Advanced Filtered Stats:")
            print(f"   🔥 Filter criteria: Sold Count ≥ {min_sold_count:,}")
            print(f"   💰 Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
            print(f"   📊 Sold count range: {df['Sold_Count'].min():,} - {df['Sold_Count'].max():,}")
            print(f"   ⭐ Average rating: {df['Rating'].mean():.2f}")
            print(f"   🏪 Unique shops: {df['Shop_Name'].nunique():,}")
            print(f"   🌍 Cities: {df['Shop_City'].nunique():,}")
            print(f"   🛒 Total sales volume: {df['Sold_Count'].sum():,}")
            print(f"   📈 Average sold per product: {df['Sold_Count'].mean():,.0f}")
            
        except Exception as e:
            print(f"❌ Error creating Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA SCRAPER ADVANCED - HIGH CAPACITY & FILTERING")
    print("🎓 Optimized for 18,000+ Products dengan Smart Filtering")
    print("=" * 75)
    
    scraper = TokopediaScraperAdvanced()
    
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

    # Opsi untuk detail scraping
    detail_input = input("Scrape detail produk juga? (y/n, default: n): ").strip().lower()
    INCLUDE_DETAIL = detail_input in ['y', 'yes', 'ya']
    
    print(f"\n⚙️  Advanced Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    if TARGET_PRODUCTS and TARGET_PRODUCTS > 0:
        print(f"   🎯 Target: {TARGET_PRODUCTS:,} produk")
    else:
        print(f"   🎯 Target: MAKSIMAL 18,000 produk")
    print(f"   🔥 Filter minimal sold: {MIN_SOLD_COUNT:,}")
    print(f"   📊 Output: advanced.xlsx dengan multi-sheet analytics")
    print(f"   🔍 Detail scraping: {'Ya' if INCLUDE_DETAIL else 'Tidak'}")
    print(f"   🚀 Multi-strategy scraping: Relevance + Best Selling + Newest")
    print()
    
    # Start advanced scraping
    result = scraper.scrape_all_products_advanced(
        keyword=KEYWORD, 
        target_products=TARGET_PRODUCTS, 
        include_detail=INCLUDE_DETAIL,
        min_sold_count=MIN_SOLD_COUNT
    )
    
    print(f"\n🏁 ADVANCED SCRAPING COMPLETED!")
    print(f"📊 Total produk yang dikumpulkan: {len(scraper.all_products_data):,}")
    print(f"🔥 Produk lolos filter (≥{MIN_SOLD_COUNT:,}): {scraper.filtered_products_count:,}")
    
    if result > 0 and scraper.all_products_data:
        print(f"\n📁 Advanced Excel file ready di: excel_output/")
        print(f"🎉 Data dengan filter dan analytics siap untuk analisis!")
        
        # Show top products by sold count
        if scraper.all_products_data:
            df_preview = pd.DataFrame(scraper.all_products_data)
            df_preview['Sold_Count'] = pd.to_numeric(df_preview.get('Sold_Count', 0), errors='coerce').fillna(0)
            top_sold = df_preview.nlargest(10, 'Sold_Count')[['Product_Name', 'Sold_Count', 'Price_Text', 'Shop_Name']]
            print(f"\n🔥 Top 10 Produk Terlaris (≥{MIN_SOLD_COUNT:,} terjual):")
            for i, (_, row) in enumerate(top_sold.iterrows(), 1):
                print(f"   {i:2d}. {row['Product_Name'][:60]}...")
                print(f"       💰 {row['Price_Text']} | 🛒 {row['Sold_Count']:,} terjual | 🏪 {row['Shop_Name']}")
    else:
        print(f"\n❌ No data was scraped. Coba turunkan filter atau ganti keyword.")
    
    print(f"\n💡 Advanced Features:")
    print(f"   ✨ Filter produk dengan minimal {MIN_SOLD_COUNT:,} terjual")
    print(f"   🚀 Multi-strategy scraping untuk maksimal coverage")
    print(f"   📊 Kapasitas hingga 18,000 produk")
    print(f"   📈 Advanced analytics dengan multiple sheets")
    print(f"   🔍 Smart deduplication dan error handling")
    print(f"   📋 Top performers analysis by sales, rating, dan price")