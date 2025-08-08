import json
import os
import re
import glob
from datetime import datetime
import pandas as pd
import xlsxwriter

class JSONToExcelConverter:
    """Convert JSON scraping results to professional Excel files"""
    
    def __init__(self):
        self.all_products_data = []
    
    def load_json_files(self, keyword='samsung', json_dir='scrape_tokopedia_requests'):
        """Load all JSON files dari direktori scraping"""
        print(f"📂 Loading JSON files dari '{json_dir}'...")
        
        # Cari file JSON dengan berbagai pattern
        patterns = [
            f'{json_dir}/page_*_enhanced.json',
            f'{json_dir}/page_*_graphql.json',
            f'{json_dir}/page_*.json'
        ]
        
        json_files = []
        for pattern in patterns:
            files = glob.glob(pattern)
            if files:
                json_files = files
                break
        
        if not json_files:
            print(f"❌ Tidak ada file JSON ditemukan di '{json_dir}'")
            return False
        
        print(f"   📄 Ditemukan {len(json_files)} file JSON")
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract page number dari filename
                page_match = re.search(r'page_(\d+)', json_file)
                page = int(page_match.group(1)) if page_match else 1
                
                # Extract products dari berbagai struktur JSON
                products = self.extract_products_from_json(data)
                
                if products:
                    page_products = self.normalize_products_for_excel(products, keyword, page)
                    self.all_products_data.extend(page_products)
                    print(f"   ✅ Loaded {len(page_products)} produk dari page {page}")
                else:
                    print(f"   ⚠️  Tidak ada produk ditemukan di page {page}")
                
            except Exception as e:
                print(f"   ❌ Error loading {json_file}: {e}")
        
        print(f"📊 Total loaded: {len(self.all_products_data)} produk")
        return len(self.all_products_data) > 0
    
    def extract_products_from_json(self, data):
        """Extract products dari berbagai format JSON"""
        # Pattern untuk berbagai struktur GraphQL response
        search_paths = [
            # Enhanced GraphQL
            ['data', 'searchProductV5', 'data', 'products'],
            # Basic GraphQL  
            ['searchProductV5', 'data', 'products'],
            # Array format
            [0, 'data', 'searchProductV5', 'data', 'products'],
            # Direct products
            ['products'],
            ['data', 'products']
        ]
        
        for path in search_paths:
            current = data
            try:
                for key in path:
                    if isinstance(current, (list, dict)) and key in current:
                        current = current[key]
                    elif isinstance(current, list) and isinstance(key, int) and len(current) > key:
                        current = current[key]
                    else:
                        break
                else:
                    # Path berhasil diikuti
                    if isinstance(current, list) and len(current) > 0:
                        # Verify ini adalah list produk dengan checking first item
                        first_item = current[0]
                        if isinstance(first_item, dict) and ('id' in first_item or 'name' in first_item):
                            return current
            except:
                continue
        
        return []
    
    def normalize_products_for_excel(self, products, keyword, page):
        """Normalize product data untuk Excel dengan struktur yang konsisten"""
        excel_products = []
        
        for idx, product in enumerate(products, 1):
            try:
                # Helper function untuk safely get nested values
                def safe_get(obj, path, default=''):
                    current = obj
                    for key in path.split('.'):
                        if isinstance(current, dict) and key in current:
                            current = current[key]
                        else:
                            return default
                    return current if current is not None else default
                
                # Normalize product data
                normalized_product = {
                    'No': len(self.all_products_data) + idx,
                    'Keyword': keyword,
                    'Page': page,
                    'Product_ID': str(safe_get(product, 'id', '')),
                    'Product_Name': safe_get(product, 'name', '').strip(),
                    'Product_URL': safe_get(product, 'url', ''),
                    'App_Link': safe_get(product, 'applink', ''),
                    
                    # Price information
                    'Price_Text': safe_get(product, 'price.text', ''),
                    'Price_Number': self.safe_numeric(safe_get(product, 'price.number', 0)),
                    'Price_Range': safe_get(product, 'price.range', ''),
                    'Original_Price': self.safe_numeric(safe_get(product, 'price.original', 0)),
                    'Discount_Percentage': self.safe_numeric(safe_get(product, 'price.discountPercentage', 0)),
                    
                    # Shop information
                    'Shop_ID': safe_get(product, 'shop.id', ''),
                    'Shop_Name': safe_get(product, 'shop.name', ''),
                    'Shop_URL': safe_get(product, 'shop.url', ''),
                    'Shop_City': safe_get(product, 'shop.city', ''),
                    'Shop_Tier': safe_get(product, 'shop.tier', ''),
                    
                    # Product details
                    'Rating': self.safe_numeric(safe_get(product, 'rating', 0)),
                    'Wishlist': bool(safe_get(product, 'wishlist', False)),
                    'Free_Shipping': bool(safe_get(product, 'freeShipping.url', False)),
                    
                    # Images
                    'Image_URL': safe_get(product, 'mediaURL.image', ''),
                    'Image_300_URL': safe_get(product, 'mediaURL.image300', ''),
                    
                    # Category
                    'Category_ID': safe_get(product, 'category.id', ''),
                    'Category_Name': safe_get(product, 'category.name', ''),
                    'Category_Breadcrumb': safe_get(product, 'category.breadcrumb', ''),
                    
                    # Badge
                    'Badge_Title': safe_get(product, 'badge.title', ''),
                    'Badge_URL': safe_get(product, 'badge.url', ''),
                    
                    # Meta information
                    'Review_Count': self.safe_numeric(safe_get(product, 'meta.countReview', 0)),
                    'Parent_ID': safe_get(product, 'meta.parentID', ''),
                    'Warehouse_ID': safe_get(product, 'meta.warehouseID', ''),
                    'Is_Image_Blurred': bool(safe_get(product, 'meta.isImageBlurred', False)),
                    'Is_Portrait': bool(safe_get(product, 'meta.isPortrait', False)),
                    
                    # Labels
                    'Labels': self.extract_labels_from_product(product),
                    
                    # Metadata
                    'Scraped_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Source': 'Tokopedia_GraphQL'
                }
                
                excel_products.append(normalized_product)
                
            except Exception as e:
                print(f"❌ Error processing product {idx}: {e}")
                continue
        
        return excel_products
    
    def safe_numeric(self, value):
        """Safely convert value to numeric"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Remove non-numeric characters except decimal point
                cleaned = re.sub(r'[^\d.]', '', value)
                return float(cleaned) if cleaned else 0
            else:
                return 0
        except:
            return 0
    
    def extract_labels_from_product(self, product):
        """Extract labels dari labelGroups"""
        try:
            label_groups = product.get('labelGroups', [])
            if not label_groups:
                return ''
            
            labels = []
            for label_group in label_groups:
                if isinstance(label_group, dict) and 'title' in label_group:
                    labels.append(label_group['title'])
            
            return '; '.join(labels)
        except:
            return ''
    
    def clean_and_process_dataframe(self, df):
        """Clean dan enrich DataFrame"""
        print("🧹 Cleaning dan processing data...")
        
        # Remove duplicates berdasarkan Product_ID
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Product_ID'], keep='first')
        print(f"   🗑️  Removed {initial_count - len(df)} duplicates")
        
        # Ensure numeric columns
        numeric_columns = ['Price_Number', 'Original_Price', 'Discount_Percentage', 'Rating', 'Review_Count']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calculate derived fields
        df['Discount_Amount'] = df['Original_Price'] - df['Price_Number']
        
        # Price categories
        df['Price_Category'] = pd.cut(df['Price_Number'], 
                                    bins=[0, 100000, 500000, 1000000, float('inf')],
                                    labels=['Budget (<100K)', 'Middle (100K-500K)', 'Premium (500K-1M)', 'Luxury (>1M)'])
        
        # Rating categories
        df['Rating_Category'] = pd.cut(df['Rating'],
                                     bins=[0, 3, 4, 4.5, 5],
                                     labels=['Poor (<3)', 'Good (3-4)', 'Very Good (4-4.5)', 'Excellent (>4.5)'])
        
        # Sort by rating and review count (best products first)
        df = df.sort_values(['Rating', 'Review_Count'], ascending=[False, False])
        
        # Reset index dan renumber
        df = df.reset_index(drop=True)
        df['No'] = range(1, len(df) + 1)
        
        return df
    
    def create_excel_files(self, keyword='samsung', output_dir='excel_output'):
        """Create multiple Excel files dengan format yang berbeda"""
        if not self.all_products_data:
            print("❌ Tidak ada data untuk di-export")
            return False
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create DataFrame
        df = pd.DataFrame(self.all_products_data)
        df = self.clean_and_process_dataframe(df)
        
        # Generate filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f'tokopedia_{keyword}_{timestamp}'
        
        # 1. Basic Excel dengan semua data
        basic_path = os.path.join(output_dir, f'{base_filename}_complete.xlsx')
        self.create_complete_excel(df, basic_path, keyword)
        
        # 2. Professional Excel dengan formatting
        pro_path = os.path.join(output_dir, f'{base_filename}_professional.xlsx')
        self.create_professional_excel(df, pro_path, keyword)
        
        # 3. Summary & Analytics Excel
        summary_path = os.path.join(output_dir, f'{base_filename}_analytics.xlsx')
        self.create_analytics_excel(df, summary_path, keyword)
        
        print(f"\n🎉 EXCEL FILES BERHASIL DIBUAT!")
        print(f"📊 Total produk: {len(df):,} produk")
        print(f"📁 Output directory: {output_dir}/")
        print(f"   📄 Complete Data: {basic_path}")
        print(f"   ✨ Professional: {pro_path}")
        print(f"   📈 Analytics: {summary_path}")
        
        return True
    
    def create_complete_excel(self, df, filepath, keyword):
        """Create Excel dengan semua data mentah"""
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Products', index=False)
                print(f"   ✅ Complete Excel: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"   ❌ Error creating complete Excel: {e}")
    
    def create_professional_excel(self, df, filepath, keyword):
        """Create Excel dengan formatting professional"""
        try:
            workbook = xlsxwriter.Workbook(filepath)
            
            # Define formats
            title_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'font_color': '#1f4788',
                'align': 'center'
            })
            
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#1f4788',
                'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
            })
            
            cell_format = workbook.add_format({
                'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True
            })
            
            number_format = workbook.add_format({
                'border': 1, 'align': 'right', 'num_format': '#,##0'
            })
            
            currency_format = workbook.add_format({
                'border': 1, 'align': 'right', 'num_format': '"Rp "#,##0'
            })
            
            percentage_format = workbook.add_format({
                'border': 1, 'align': 'right', 'num_format': '0.0%'
            })
            
            # Main worksheet
            worksheet = workbook.add_worksheet('Products')
            
            # Title
            worksheet.merge_range('A1:Q1', f'TOKOPEDIA SCRAPING RESULTS - {keyword.upper()}', title_format)
            worksheet.write('A2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Headers (starting from row 4)
            headers = [
                'No', 'Product Name', 'Price', 'Original Price', 'Discount %', 'Discount Amount',
                'Shop Name', 'Shop City', 'Rating', 'Reviews', 'Category',
                'Price Category', 'Rating Category', 'Free Shipping', 'Labels',
                'Product URL', 'Scraped Date'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(3, col, header, header_format)
            
            # Data rows
            for row, (_, product) in enumerate(df.iterrows(), 4):
                worksheet.write(row, 0, product['No'], number_format)
                worksheet.write(row, 1, product['Product_Name'], cell_format)
                worksheet.write(row, 2, product['Price_Number'], currency_format)
                worksheet.write(row, 3, product['Original_Price'], currency_format)
                
                discount_pct = product['Discount_Percentage'] / 100 if product['Discount_Percentage'] > 0 else 0
                worksheet.write(row, 4, discount_pct, percentage_format)
                
                worksheet.write(row, 5, product['Discount_Amount'], currency_format)
                worksheet.write(row, 6, product['Shop_Name'], cell_format)
                worksheet.write(row, 7, product['Shop_City'], cell_format)
                worksheet.write(row, 8, product['Rating'], number_format)
                worksheet.write(row, 9, product['Review_Count'], number_format)
                worksheet.write(row, 10, product['Category_Name'], cell_format)
                worksheet.write(row, 11, str(product.get('Price_Category', '')), cell_format)
                worksheet.write(row, 12, str(product.get('Rating_Category', '')), cell_format)
                worksheet.write(row, 13, 'Yes' if product['Free_Shipping'] else 'No', cell_format)
                worksheet.write(row, 14, product['Labels'], cell_format)
                worksheet.write(row, 15, product['Product_URL'], cell_format)
                worksheet.write(row, 16, product['Scraped_At'], cell_format)
            
            # Column widths
            col_widths = [5, 50, 15, 15, 10, 15, 25, 20, 8, 10, 20, 20, 20, 12, 30, 60, 20]
            for col, width in enumerate(col_widths):
                worksheet.set_column(col, col, width)
            
            # Freeze panes
            worksheet.freeze_panes(4, 2)  # Freeze header and product name
            
            # Add autofilter
            worksheet.autofilter(3, 0, len(df) + 3, len(headers) - 1)
            
            workbook.close()
            print(f"   ✨ Professional Excel: {os.path.basename(filepath)}")
            
        except Exception as e:
            print(f"   ❌ Error creating professional Excel: {e}")
    
    def create_analytics_excel(self, df, filepath, keyword):
        """Create Excel dengan analytics dan summary"""
        try:
            workbook = xlsxwriter.Workbook(filepath)
            
            # Formats
            title_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'font_color': '#1f4788'
            })
            header_format = workbook.add_format({
                'bold': True, 'bg_color': '#f0f0f0', 'border': 1
            })
            currency_format = workbook.add_format({'num_format': '"Rp "#,##0'})
            
            # Summary worksheet
            summary_ws = workbook.add_worksheet('Summary')
            
            # Title
            summary_ws.write(0, 0, f'TOKOPEDIA ANALYTICS - {keyword.upper()}', title_format)
            summary_ws.write(1, 0, f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            row = 3
            
            # Basic Statistics
            summary_ws.write(row, 0, 'BASIC STATISTICS', header_format)
            row += 1
            
            stats = [
                ('Total Products Scraped', f"{len(df):,}"),
                ('Unique Shops', f"{df['Shop_Name'].nunique():,}"),
                ('Cities Covered', f"{df['Shop_City'].nunique():,}"),
                ('Average Price', f"Rp {df['Price_Number'].mean():,.0f}"),
                ('Median Price', f"Rp {df['Price_Number'].median():,.0f}"),
                ('Price Range', f"Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}"),
                ('Average Rating', f"{df['Rating'].mean():.2f}"),
                ('Total Reviews', f"{df['Review_Count'].sum():,}"),
                ('Products with Free Shipping', f"{df['Free_Shipping'].sum():,} ({df['Free_Shipping'].mean()*100:.1f}%)"),
                ('Products with Discounts', f"{(df['Discount_Percentage'] > 0).sum():,}"),
            ]
            
            for stat_name, stat_value in stats:
                summary_ws.write(row, 0, stat_name)
                summary_ws.write(row, 1, stat_value)
                row += 1
            
            # Price Analysis
            row += 2
            summary_ws.write(row, 0, 'PRICE ANALYSIS', header_format)
            row += 1
            
            price_analysis = df['Price_Category'].value_counts()
            for category, count in price_analysis.items():
                summary_ws.write(row, 0, str(category))
                summary_ws.write(row, 1, f"{count:,} products ({count/len(df)*100:.1f}%)")
                row += 1
            
            # Top Performers
            row += 2
            summary_ws.write(row, 0, 'TOP 10 SHOPS BY PRODUCT COUNT', header_format)
            row += 1
            
            top_shops = df['Shop_Name'].value_counts().head(10)
            for shop, count in top_shops.items():
                summary_ws.write(row, 0, shop)
                summary_ws.write(row, 1, f"{count} products")
                row += 1
            
            # Top Cities
            row += 2
            summary_ws.write(row, 0, 'TOP CITIES', header_format)
            row += 1
            
            top_cities = df['Shop_City'].value_counts().head(10)
            for city, count in top_cities.items():
                summary_ws.write(row, 0, city)
                summary_ws.write(row, 1, f"{count} products")
                row += 1
            
            # Set column widths
            summary_ws.set_column(0, 0, 30)
            summary_ws.set_column(1, 1, 25)
            
            workbook.close()
            print(f"   📈 Analytics Excel: {os.path.basename(filepath)}")
            
        except Exception as e:
            print(f"   ❌ Error creating analytics Excel: {e}")

def main():
    """Main function untuk convert JSON ke Excel"""
    print("🔥 JSON TO EXCEL CONVERTER")
    print("🎓 Professional Data Mining Tool")
    print("=" * 60)
    
    converter = JSONToExcelConverter()
    
    # Configuration
    KEYWORD = 'samsung'
    JSON_DIR = 'scrape_tokopedia_requests'
    OUTPUT_DIR = 'excel_output'
    
    print(f"⚙️  Configuration:")
    print(f"   📝 Keyword: {KEYWORD}")
    print(f"   📂 JSON Directory: {JSON_DIR}")
    print(f"   📊 Output Directory: {OUTPUT_DIR}")
    print()
    
    # Load JSON files
    if converter.load_json_files(KEYWORD, JSON_DIR):
        # Create Excel files
        success = converter.create_excel_files(KEYWORD, OUTPUT_DIR)
        
        if success:
            print(f"\n🎉 CONVERSION COMPLETED SUCCESSFULLY!")
            print(f"📊 {len(converter.all_products_data):,} products converted to Excel")
            print(f"\n💡 Files ready untuk analisis data mining!")
        else:
            print(f"\n❌ Failed to create Excel files")
    else:
        print(f"\n❌ No JSON data found to convert")

if __name__ == "__main__":
    main()