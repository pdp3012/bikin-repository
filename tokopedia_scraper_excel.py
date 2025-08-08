import json
import requests
import os
import re
import time
import random
import glob
from urllib.parse import quote, urlencode
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import xlsxwriter

class TokopediaScraperExcel:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.all_products_data = []  # Store all scraped products
        
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
    
    def debug_response(self, response, label="Response"):
        """Debug helper untuk melihat response detail"""
        print(f"\n🔍 {label} Debug:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(list(response.headers.items())[:5])}")
        
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(f"   JSON Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"   First Item Keys: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
                return data
            else:
                print(f"   Content Length: {len(response.text)}")
                print(f"   Content Preview: {response.text[:200]}...")
                return response.text
        except Exception as e:
            print(f"   Parse Error: {e}")
            return None
    
    def build_graphql_params(self, keyword, page=1, rows=60):
        """Build GraphQL parameters yang valid"""
        start = (page - 1) * rows
        
        # Parameter yang sudah diverifikasi untuk Tokopedia
        params = {
            'device': 'desktop',
            'navsource': '',
            'ob': '23',  # sorting parameter
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
    
    def create_enhanced_graphql_query(self):
        """GraphQL query yang lebih lengkap untuk data yang komprehensif"""
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
                applink
                mediaURL {
                  image
                  image300
                  __typename
                }
                price {
                  text
                  number
                  range
                  original
                  discountPercentage
                  __typename
                }
                shop {
                  id
                  name
                  url
                  city
                  tier
                  __typename
                }
                badge {
                  id
                  title
                  url
                  __typename
                }
                freeShipping {
                  url
                  __typename
                }
                labelGroups {
                  position
                  title
                  type
                  url
                  __typename
                }
                category {
                  id
                  name
                  breadcrumb
                  gaKey
                  __typename
                }
                rating
                wishlist
                meta {
                  countReview
                  parentID
                  warehouseID
                  isImageBlurred
                  isPortrait
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
    
    def test_graphql_enhanced(self, keyword):
        """Test GraphQL dengan query yang enhanced"""
        print("🧪 Testing Enhanced GraphQL endpoint...")
        
        params = self.build_graphql_params(keyword, page=1, rows=10)
        
        payload = [{
            "operationName": "SearchProductQueryV5",
            "query": self.create_enhanced_graphql_query(),
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
            
            data = self.debug_response(response, "Enhanced GraphQL Test")
            
            if response.status_code == 200 and data:
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    if 'data' in first_item and first_item['data']:
                        search_data = first_item['data'].get('searchProductV5', {})
                        if search_data and 'header' in search_data:
                            total_data = search_data['header'].get('totalData', 0)
                            print(f"✅ Enhanced GraphQL berhasil! Total data: {total_data}")
                            return True, payload, headers
                        
            print("❌ Enhanced GraphQL response tidak sesuai format yang diharapkan")
            return False, None, None
            
        except Exception as e:
            print(f"❌ Error pada Enhanced GraphQL test: {e}")
            return False, None, None
    
    def scrape_products_for_excel(self, keyword='samsung', max_pages=30):
        """Main scraping function dengan focus pada Excel output"""
        print(f"🚀 TOKOPEDIA SCRAPER EXCEL EDITION")
        print(f"   Keyword: {keyword}")
        print(f"   Max Pages: {max_pages}")
        print("=" * 60)
        
        # Reset data storage
        self.all_products_data = []
        
        # Setup directories
        output_dir = 'scrape_tokopedia_requests'
        excel_dir = 'excel_output'
        
        for directory in [output_dir, excel_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Direktori '{directory}' dibuat")
        
        # Test GraphQL
        success, payload, headers = self.test_graphql_enhanced(keyword)
        if success:
            print("📊 Enhanced GraphQL endpoint berhasil!")
            successful_pages = self.scrape_with_enhanced_graphql(keyword, max_pages, payload, headers)
        else:
            print("🔄 Menggunakan fallback method...")
            successful_pages = self.scrape_with_fallback(keyword, max_pages)
        
        if successful_pages > 0:
            print(f"\n📝 Processing data untuk Excel export...")
            self.process_json_to_excel(keyword, excel_dir)
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")
        
        return successful_pages
    
    def scrape_with_enhanced_graphql(self, keyword, max_pages, payload_template, headers):
        """Scraping dengan GraphQL enhanced dan collect data untuk Excel"""
        output_dir = 'scrape_tokopedia_requests'
        successful_pages = 0
        
        print(f"🔄 Memulai scraping {max_pages} halaman...")
        
        for page in range(1, max_pages + 1):
            try:
                # Update payload untuk page ini
                params = self.build_graphql_params(keyword, page, 60)
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
                    
                    # Save JSON
                    filename = os.path.join(output_dir, f'page_{page}_enhanced.json')
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    # Extract and store products for Excel
                    try:
                        products = data[0]['data']['searchProductV5']['data']['products']
                        page_products = self.extract_products_for_excel(products, keyword, page)
                        self.all_products_data.extend(page_products)
                        
                        successful_pages += 1
                        print(f"✅ Page {page}: {len(products)} produk → Total: {len(self.all_products_data)} produk")
                    except Exception as e:
                        print(f"⚠️  Page {page}: Error extracting products - {e}")
                
                # Random delay
                if page < max_pages:
                    delay = random.uniform(1, 2)
                    time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Page {page}: Error - {e}")
        
        return successful_pages
    
    def extract_products_for_excel(self, products, keyword, page):
        """Extract dan normalize product data untuk Excel"""
        excel_products = []
        
        for idx, product in enumerate(products, 1):
            try:
                # Normalize data dengan default values
                excel_product = {
                    'No': len(self.all_products_data) + idx,
                    'Keyword': keyword,
                    'Page': page,
                    'Product_ID': str(product.get('id', '')),
                    'Product_Name': product.get('name', '').strip(),
                    'Product_URL': product.get('url', ''),
                    'App_Link': product.get('applink', ''),
                    
                    # Price information
                    'Price_Text': product.get('price', {}).get('text', ''),
                    'Price_Number': product.get('price', {}).get('number', 0),
                    'Price_Range': product.get('price', {}).get('range', ''),
                    'Original_Price': product.get('price', {}).get('original', 0),
                    'Discount_Percentage': product.get('price', {}).get('discountPercentage', 0),
                    
                    # Shop information
                    'Shop_ID': product.get('shop', {}).get('id', ''),
                    'Shop_Name': product.get('shop', {}).get('name', ''),
                    'Shop_URL': product.get('shop', {}).get('url', ''),
                    'Shop_City': product.get('shop', {}).get('city', ''),
                    'Shop_Tier': product.get('shop', {}).get('tier', ''),
                    
                    # Product details
                    'Rating': float(product.get('rating', 0)) if product.get('rating') else 0,
                    'Wishlist': product.get('wishlist', False),
                    'Free_Shipping': bool(product.get('freeShipping', {}).get('url')),
                    
                    # Images
                    'Image_URL': product.get('mediaURL', {}).get('image', ''),
                    'Image_300_URL': product.get('mediaURL', {}).get('image300', ''),
                    
                    # Category
                    'Category_ID': product.get('category', {}).get('id', ''),
                    'Category_Name': product.get('category', {}).get('name', ''),
                    'Category_Breadcrumb': product.get('category', {}).get('breadcrumb', ''),
                    
                    # Badge information
                    'Badge_Title': product.get('badge', {}).get('title', ''),
                    'Badge_URL': product.get('badge', {}).get('url', ''),
                    
                    # Meta information
                    'Review_Count': product.get('meta', {}).get('countReview', 0),
                    'Parent_ID': product.get('meta', {}).get('parentID', ''),
                    'Warehouse_ID': product.get('meta', {}).get('warehouseID', ''),
                    'Is_Image_Blurred': product.get('meta', {}).get('isImageBlurred', False),
                    'Is_Portrait': product.get('meta', {}).get('isPortrait', False),
                    
                    # Labels
                    'Labels': self.extract_labels(product.get('labelGroups', [])),
                    
                    # Scraping metadata
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Scraping_Method': 'Enhanced_GraphQL'
                }
                
                excel_products.append(excel_product)
                
            except Exception as e:
                print(f"❌ Error processing product {idx}: {e}")
                continue
        
        return excel_products
    
    def extract_labels(self, label_groups):
        """Extract label information dari labelGroups"""
        if not label_groups:
            return ''
        
        labels = []
        for label_group in label_groups:
            if isinstance(label_group, dict) and 'title' in label_group:
                labels.append(label_group['title'])
        
        return '; '.join(labels)
    
    def scrape_with_fallback(self, keyword, max_pages):
        """Fallback scraping method"""
        print("🔄 Menggunakan fallback scraping method...")
        # Bisa implementasi HTML scraping di sini jika diperlukan
        return 0
    
    def process_json_to_excel(self, keyword, excel_dir):
        """Process all collected data dan export ke Excel dengan formatting professional"""
        if not self.all_products_data:
            # Coba load dari existing JSON files
            self.load_existing_json_data(keyword)
        
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export ke Excel")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.all_products_data)
        
        # Clean and process data
        df = self.clean_dataframe(df)
        
        # Generate multiple Excel formats
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f'tokopedia_{keyword}_{timestamp}'
        
        # 1. Basic Excel with pandas
        basic_excel_path = os.path.join(excel_dir, f'{base_filename}_basic.xlsx')
        self.create_basic_excel(df, basic_excel_path, keyword)
        
        # 2. Professional Excel with formatting
        pro_excel_path = os.path.join(excel_dir, f'{base_filename}_professional.xlsx')
        self.create_professional_excel(df, pro_excel_path, keyword)
        
        # 3. Summary Excel with analytics
        summary_excel_path = os.path.join(excel_dir, f'{base_filename}_summary.xlsx')
        self.create_summary_excel(df, summary_excel_path, keyword)
        
        print(f"\n🎉 EXCEL FILES BERHASIL DIBUAT!")
        print(f"📊 Total produk: {len(df)} produk")
        print(f"📁 File locations:")
        print(f"   📄 Basic: {basic_excel_path}")
        print(f"   ✨ Professional: {pro_excel_path}")
        print(f"   📈 Summary: {summary_excel_path}")
    
    def load_existing_json_data(self, keyword):
        """Load data dari existing JSON files jika belum ada di memory"""
        print("📂 Loading data dari JSON files yang sudah ada...")
        
        json_files = glob.glob('scrape_tokopedia_requests/page_*_enhanced.json')
        if not json_files:
            json_files = glob.glob('scrape_tokopedia_requests/page_*_graphql.json')
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract page number from filename
                page_match = re.search(r'page_(\d+)', json_file)
                page = int(page_match.group(1)) if page_match else 1
                
                # Extract products
                if isinstance(data, list) and len(data) > 0:
                    products = data[0].get('data', {}).get('searchProductV5', {}).get('data', {}).get('products', [])
                    if products:
                        page_products = self.extract_products_for_excel(products, keyword, page)
                        self.all_products_data.extend(page_products)
                        print(f"   ✅ Loaded {len(page_products)} produk dari {json_file}")
                
            except Exception as e:
                print(f"   ❌ Error loading {json_file}: {e}")
        
        print(f"📊 Total loaded: {len(self.all_products_data)} produk")
    
    def clean_dataframe(self, df):
        """Clean dan normalize DataFrame"""
        print("🧹 Cleaning dan processing data...")
        
        # Remove duplicates berdasarkan Product_ID
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        print(f"   🗑️  Removed {initial_count - len(df)} duplicates")
        
        # Clean price data
        df['Price_Number'] = pd.to_numeric(df['Price_Number'], errors='coerce').fillna(0)
        df['Original_Price'] = pd.to_numeric(df['Original_Price'], errors='coerce').fillna(0)
        df['Discount_Percentage'] = pd.to_numeric(df['Discount_Percentage'], errors='coerce').fillna(0)
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
        df['Review_Count'] = pd.to_numeric(df['Review_Count'], errors='coerce').fillna(0)
        
        # Calculate discount amount
        df['Discount_Amount'] = df['Original_Price'] - df['Price_Number']
        
        # Price category
        df['Price_Category'] = pd.cut(df['Price_Number'], 
                                    bins=[0, 100000, 500000, 1000000, float('inf')],
                                    labels=['Budget (<100K)', 'Middle (100K-500K)', 'Premium (500K-1M)', 'Luxury (>1M)'])
        
        # Rating category
        df['Rating_Category'] = pd.cut(df['Rating'],
                                     bins=[0, 3, 4, 4.5, 5],
                                     labels=['Poor (<3)', 'Good (3-4)', 'Very Good (4-4.5)', 'Excellent (>4.5)'])
        
        # Sort by rating and review count
        df = df.sort_values(['Rating', 'Review_Count'], ascending=[False, False])
        
        # Reset index
        df = df.reset_index(drop=True)
        df['No'] = range(1, len(df) + 1)
        
        return df
    
    def create_basic_excel(self, df, filepath, keyword):
        """Create basic Excel file dengan pandas"""
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Products', index=False)
                print(f"   ✅ Basic Excel created: {filepath}")
        except Exception as e:
            print(f"   ❌ Error creating basic Excel: {e}")
    
    def create_professional_excel(self, df, filepath, keyword):
        """Create professional Excel dengan formatting lengkap"""
        try:
            workbook = xlsxwriter.Workbook(filepath)
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'font_color': 'white',
                'bg_color': '#1f4788',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            })
            
            cell_format = workbook.add_format({
                'border': 1,
                'align': 'left',
                'valign': 'top',
                'text_wrap': True
            })
            
            number_format = workbook.add_format({
                'border': 1,
                'align': 'right',
                'num_format': '#,##0'
            })
            
            currency_format = workbook.add_format({
                'border': 1,
                'align': 'right',
                'num_format': '"Rp "#,##0'
            })
            
            percentage_format = workbook.add_format({
                'border': 1,
                'align': 'right',
                'num_format': '0.0%'
            })
            
            # Main worksheet
            worksheet = workbook.add_worksheet('Products Data')
            
            # Headers
            headers = [
                'No', 'Product Name', 'Price', 'Original Price', 'Discount %', 'Discount Amount',
                'Shop Name', 'Shop City', 'Rating', 'Review Count', 'Category',
                'Price Category', 'Rating Category', 'Free Shipping', 'Labels',
                'Product URL', 'Scraped At'
            ]
            
            # Write headers
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Write data
            for row, (_, product) in enumerate(df.iterrows(), 1):
                worksheet.write(row, 0, product['No'], number_format)
                worksheet.write(row, 1, product['Product_Name'], cell_format)
                worksheet.write(row, 2, product['Price_Number'], currency_format)
                worksheet.write(row, 3, product['Original_Price'], currency_format)
                worksheet.write(row, 4, product['Discount_Percentage']/100 if product['Discount_Percentage'] > 0 else 0, percentage_format)
                worksheet.write(row, 5, product['Discount_Amount'], currency_format)
                worksheet.write(row, 6, product['Shop_Name'], cell_format)
                worksheet.write(row, 7, product['Shop_City'], cell_format)
                worksheet.write(row, 8, product['Rating'], number_format)
                worksheet.write(row, 9, product['Review_Count'], number_format)
                worksheet.write(row, 10, product['Category_Name'], cell_format)
                worksheet.write(row, 11, str(product['Price_Category']), cell_format)
                worksheet.write(row, 12, str(product['Rating_Category']), cell_format)
                worksheet.write(row, 13, 'Yes' if product['Free_Shipping'] else 'No', cell_format)
                worksheet.write(row, 14, product['Labels'], cell_format)
                worksheet.write(row, 15, product['Product_URL'], cell_format)
                worksheet.write(row, 16, product['Scraped_At'], cell_format)
            
            # Auto-fit columns
            for col in range(len(headers)):
                worksheet.set_column(col, col, 15)
            
            # Specific column widths
            worksheet.set_column(1, 1, 40)  # Product Name
            worksheet.set_column(14, 14, 30)  # Labels
            worksheet.set_column(15, 15, 50)  # URL
            
            # Freeze header row
            worksheet.freeze_panes(1, 0)
            
            # Add filters
            worksheet.autofilter(0, 0, len(df), len(headers) - 1)
            
            workbook.close()
            print(f"   ✨ Professional Excel created: {filepath}")
            
        except Exception as e:
            print(f"   ❌ Error creating professional Excel: {e}")
    
    def create_summary_excel(self, df, filepath, keyword):
        """Create summary Excel dengan analytics"""
        try:
            workbook = xlsxwriter.Workbook(filepath)
            
            # Summary worksheet
            summary_ws = workbook.add_worksheet('Summary')
            
            # Formats
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'font_color': '#1f4788'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#f0f0f0',
                'border': 1
            })
            
            # Title
            summary_ws.write(0, 0, f'Tokopedia Scraping Summary - {keyword.upper()}', title_format)
            summary_ws.write(1, 0, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Basic stats
            row = 3
            summary_ws.write(row, 0, 'BASIC STATISTICS', header_format)
            row += 1
            
            stats = [
                ('Total Products', len(df)),
                ('Average Price', f"Rp {df['Price_Number'].mean():,.0f}"),
                ('Median Price', f"Rp {df['Price_Number'].median():,.0f}"),
                ('Min Price', f"Rp {df['Price_Number'].min():,.0f}"),
                ('Max Price', f"Rp {df['Price_Number'].max():,.0f}"),
                ('Average Rating', f"{df['Rating'].mean():.2f}"),
                ('Total Reviews', f"{df['Review_Count'].sum():,}"),
                ('Free Shipping Products', df['Free_Shipping'].sum()),
            ]
            
            for stat_name, stat_value in stats:
                summary_ws.write(row, 0, stat_name)
                summary_ws.write(row, 1, stat_value)
                row += 1
            
            # Price categories
            row += 2
            summary_ws.write(row, 0, 'PRICE CATEGORIES', header_format)
            row += 1
            
            price_cats = df['Price_Category'].value_counts()
            for cat, count in price_cats.items():
                summary_ws.write(row, 0, str(cat))
                summary_ws.write(row, 1, count)
                row += 1
            
            # Top shops
            row += 2
            summary_ws.write(row, 0, 'TOP 10 SHOPS', header_format)
            row += 1
            
            top_shops = df['Shop_Name'].value_counts().head(10)
            for shop, count in top_shops.items():
                summary_ws.write(row, 0, shop)
                summary_ws.write(row, 1, count)
                row += 1
            
            # Cities
            row += 2
            summary_ws.write(row, 0, 'TOP CITIES', header_format)
            row += 1
            
            top_cities = df['Shop_City'].value_counts().head(10)
            for city, count in top_cities.items():
                summary_ws.write(row, 0, city)
                summary_ws.write(row, 1, count)
                row += 1
            
            workbook.close()
            print(f"   📈 Summary Excel created: {filepath}")
            
        except Exception as e:
            print(f"   ❌ Error creating summary Excel: {e}")

# Usage dan Main execution
if __name__ == "__main__":
    print("🔥 TOKOPEDIA SCRAPER EXCEL EDITION")
    print("🎓 Developed by: Senior Data Mining Expert (30+ years)")
    print("=" * 70)
    
    scraper = TokopediaScraperExcel()
    
    # Configuration
    KEYWORD = 'samsung'
    MAX_PAGES = 30  # Bisa disesuaikan
    
    print(f"⚙️  Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    print(f"   📄 Max Pages: {MAX_PAGES}")
    print(f"   📊 Expected Products: ~{MAX_PAGES * 60} products")
    print()
    
    # Start scraping
    result = scraper.scrape_products_for_excel(
        keyword=KEYWORD,
        max_pages=MAX_PAGES
    )
    
    print(f"\n🏁 SCRAPING COMPLETED!")
    print(f"✅ Successfully scraped: {result} pages")
    print(f"📊 Total products collected: {len(scraper.all_products_data)}")
    
    if result > 0:
        print(f"\n📁 Files created in:")
        print(f"   🗂️  JSON: scrape_tokopedia_requests/")
        print(f"   📊 Excel: excel_output/")
        print(f"\n🎉 Excel files ready untuk analisis data mining!")
    else:
        print(f"\n❌ No data was scraped. Please check your connection or try again.")