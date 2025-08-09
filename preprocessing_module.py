import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TokopediaDataPreprocessing:
    """
    Class untuk preprocessing data hasil scraping Tokopedia
    Dibuat oleh: Dosen Data Mining dengan pengalaman 30 tahun
    """
    
    def __init__(self, excel_file_path):
        """
        Inisialisasi dengan membaca file Excel hasil scraping
        
        Args:
            excel_file_path (str): Path ke file Excel hasil scraping
        """
        self.excel_file_path = excel_file_path
        self.df_all = None
        self.df_filtered = None
        self.df_commodity = None
        self.city_mapping = {}
        self.product_normalization = {}
        
        # Load data dari Excel
        self._load_data()
        
        print("🎓 TOKOPEDIA DATA PREPROCESSING INITIALIZED")
        print("=" * 60)
        print(f"📁 File: {excel_file_path}")
        print(f"📊 Data loaded successfully")
        print("=" * 60)
    
    def _load_data(self):
        """Load data dari file Excel dengan multiple sheets"""
        try:
            # Baca semua sheets
            excel_data = pd.read_excel(self.excel_file_path, sheet_name=None)
            
            # Identifikasi sheets yang tersedia
            available_sheets = list(excel_data.keys())
            print(f"📋 Sheets tersedia: {available_sheets}")
            
            # Load sheet utama (yang pertama atau yang paling besar)
            if 'All Products' in available_sheets:
                self.df_all = excel_data['All Products']
                print(f"✅ Loaded 'All Products': {len(self.df_all):,} rows")
            
            # Load filtered products
            filtered_sheet = None
            for sheet in available_sheets:
                if 'Min' in sheet and 'Sold' in sheet:
                    filtered_sheet = sheet
                    break
            
            if filtered_sheet:
                self.df_filtered = excel_data[filtered_sheet]
                print(f"✅ Loaded '{filtered_sheet}': {len(self.df_filtered):,} rows")
            
            # Load commodity data jika ada
            for sheet in available_sheets:
                if 'Commodity' in sheet:
                    self.df_commodity = excel_data[sheet]
                    print(f"✅ Loaded '{sheet}': {len(self.df_commodity):,} rows")
                    break
            
            # Jika tidak ada sheet terpisah, gunakan sheet pertama
            if self.df_all is None and available_sheets:
                self.df_all = excel_data[available_sheets[0]]
                print(f"✅ Loaded '{available_sheets[0]}': {len(self.df_all):,} rows")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def basic_data_analysis(self, dataset='all'):
        """
        Analisis dasar data: head(), info(), describe(), shape
        
        Args:
            dataset (str): 'all', 'filtered', atau 'commodity'
        """
        print(f"\n🔍 BASIC DATA ANALYSIS - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        # Pilih dataset
        df = self._select_dataset(dataset)
        if df is None:
            return
        
        # 1. Shape
        print(f"📊 SHAPE: {df.shape}")
        print(f"   Rows: {df.shape[0]:,}")
        print(f"   Columns: {df.shape[1]:,}")
        
        # 2. Head
        print(f"\n📋 HEAD (First 5 rows):")
        print(df.head())
        
        # 3. Info
        print(f"\n📈 INFO:")
        print(df.info())
        
        # 4. Describe untuk kolom numerik
        print(f"\n📊 DESCRIBE (Numerical columns):")
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            print(df[numerical_cols].describe())
        else:
            print("No numerical columns found")
        
        # 5. Describe untuk kolom kategorikal
        print(f"\n📝 DESCRIBE (Categorical columns):")
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:5]:  # Show first 5 categorical columns
                print(f"\n{col}:")
                print(df[col].describe())
        
        return df
    
    def check_missing_values(self, dataset='all'):
        """
        Comprehensive missing value analysis
        
        Args:
            dataset (str): 'all', 'filtered', atau 'commodity'
        """
        print(f"\n🔍 MISSING VALUES ANALYSIS - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None:
            return
        
        # Hitung missing values
        missing_data = pd.DataFrame({
            'Column': df.columns,
            'Missing_Count': df.isnull().sum().values,
            'Missing_Percentage': (df.isnull().sum().values / len(df) * 100).round(2),
            'Data_Type': df.dtypes.values,
            'Non_Null_Count': df.count().values
        })
        
        # Sort by missing percentage
        missing_data = missing_data.sort_values('Missing_Percentage', ascending=False)
        
        # Display results
        print(f"📊 Missing Values Summary:")
        print(missing_data)
        
        # Summary statistics
        total_missing = missing_data['Missing_Count'].sum()
        total_cells = len(df) * len(df.columns)
        overall_missing_pct = (total_missing / total_cells * 100).round(2)
        
        print(f"\n📈 Missing Values Statistics:")
        print(f"   Total missing values: {total_missing:,}")
        print(f"   Total cells: {total_cells:,}")
        print(f"   Overall missing percentage: {overall_missing_pct}%")
        
        # Columns with missing values
        columns_with_missing = missing_data[missing_data['Missing_Count'] > 0]
        if len(columns_with_missing) > 0:
            print(f"\n⚠️  Columns with missing values:")
            for _, row in columns_with_missing.iterrows():
                print(f"   • {row['Column']}: {row['Missing_Count']:,} ({row['Missing_Percentage']}%)")
        else:
            print(f"\n✅ No missing values found!")
        
        return missing_data
    
    def check_duplicates(self, dataset='all'):
        """
        Comprehensive duplicate analysis
        
        Args:
            dataset (str): 'all', 'filtered', atau 'commodity'
        """
        print(f"\n🔍 DUPLICATE ANALYSIS - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None:
            return
        
        # 1. Complete duplicates
        complete_duplicates = df.duplicated().sum()
        complete_duplicate_pct = (complete_duplicates / len(df) * 100).round(2)
        
        print(f"📊 Complete Duplicates:")
        print(f"   Count: {complete_duplicates:,}")
        print(f"   Percentage: {complete_duplicate_pct}%")
        
        # 2. Duplicates by Product_ID (if exists)
        if 'Product_ID' in df.columns:
            product_id_duplicates = df['Product_ID'].duplicated().sum()
            product_id_duplicate_pct = (product_id_duplicates / len(df) * 100).round(2)
            
            print(f"\n📱 Product_ID Duplicates:")
            print(f"   Count: {product_id_duplicates:,}")
            print(f"   Percentage: {product_id_duplicate_pct}%")
        
        # 3. Duplicates by Product_Name (if exists)
        if 'Product_Name' in df.columns:
            product_name_duplicates = df['Product_Name'].duplicated().sum()
            product_name_duplicate_pct = (product_name_duplicates / len(df) * 100).round(2)
            
            print(f"\n📝 Product_Name Duplicates:")
            print(f"   Count: {product_name_duplicates:,}")
            print(f"   Percentage: {product_name_duplicate_pct}%")
            
            # Show most common product names
            if product_name_duplicates > 0:
                top_duplicate_names = df['Product_Name'].value_counts().head(10)
                print(f"\n🔥 Top 10 Most Common Product Names:")
                for name, count in top_duplicate_names.items():
                    if count > 1:
                        print(f"   • {name[:50]}... : {count} times")
        
        # 4. Duplicates by combination of key fields
        key_columns = []
        for col in ['Product_Name', 'Shop_Name', 'Price_Number']:
            if col in df.columns:
                key_columns.append(col)
        
        if len(key_columns) >= 2:
            combination_duplicates = df.duplicated(subset=key_columns).sum()
            combination_duplicate_pct = (combination_duplicates / len(df) * 100).round(2)
            
            print(f"\n🔗 Combination Duplicates ({' + '.join(key_columns)}):")
            print(f"   Count: {combination_duplicates:,}")
            print(f"   Percentage: {combination_duplicate_pct}%")
        
        return {
            'complete_duplicates': complete_duplicates,
            'product_id_duplicates': product_id_duplicates if 'Product_ID' in df.columns else 0,
            'product_name_duplicates': product_name_duplicates if 'Product_Name' in df.columns else 0,
            'combination_duplicates': combination_duplicates if len(key_columns) >= 2 else 0
        }
    
    def create_product_normalization_dictionary(self, dataset='all'):
        """
        Buat dictionary untuk normalisasi nama produk
        """
        print(f"\n🔄 PRODUCT NORMALIZATION DICTIONARY - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None or 'Product_Name' not in df.columns:
            return
        
        # Ambil semua nama produk
        product_names = df['Product_Name'].dropna().unique()
        
        print(f"📊 Total unique product names: {len(product_names):,}")
        
        # Dictionary untuk normalisasi
        normalization_dict = {}
        
        # 1. Normalisasi brand/merk
        brand_patterns = {
            'samsung': ['samsung', 'samsu', 'sams'],
            'iphone': ['iphone', 'ip', 'apple'],
            'xiaomi': ['xiaomi', 'mi', 'redmi'],
            'oppo': ['oppo', 'op'],
            'vivo': ['vivo', 'vi'],
            'huawei': ['huawei', 'hw'],
            'adidas': ['adidas', 'adi'],
            'nike': ['nike', 'nk'],
            'uniqlo': ['uniqlo', 'uql']
        }
        
        # 2. Normalisasi ukuran
        size_patterns = {
            'xl': ['xl', 'x-l', 'extra large'],
            'l': ['l', 'large'],
            'm': ['m', 'medium', 'med'],
            's': ['s', 'small'],
            'xs': ['xs', 'x-small', 'extra small']
        }
        
        # 3. Normalisasi warna
        color_patterns = {
            'hitam': ['hitam', 'black', 'blck'],
            'putih': ['putih', 'white', 'wht'],
            'merah': ['merah', 'red', 'rd'],
            'biru': ['biru', 'blue', 'blu'],
            'hijau': ['hijau', 'green', 'grn'],
            'kuning': ['kuning', 'yellow', 'ylw']
        }
        
        # 4. Normalisasi unit/satuan
        unit_patterns = {
            'kg': ['kg', 'kilogram', 'kilo'],
            'gram': ['gram', 'gr', 'g'],
            'liter': ['liter', 'l', 'lt'],
            'ml': ['ml', 'milliliter', 'mililiter'],
            'pcs': ['pcs', 'pieces', 'piece', 'buah'],
            'pack': ['pack', 'pak', 'kemasan']
        }
        
        # Combine all patterns
        all_patterns = {
            'brands': brand_patterns,
            'sizes': size_patterns,
            'colors': color_patterns,
            'units': unit_patterns
        }
        
        # Generate normalization dictionary
        print(f"\n🔧 Generating normalization patterns...")
        
        normalization_stats = {}
        for category, patterns in all_patterns.items():
            normalization_stats[category] = {}
            for standard_term, variations in patterns.items():
                matches = 0
                for variation in variations:
                    # Count products that contain this variation
                    pattern_matches = df['Product_Name'].str.contains(variation, case=False, na=False).sum()
                    matches += pattern_matches
                
                normalization_stats[category][standard_term] = matches
                
                # Add to normalization dictionary
                for variation in variations:
                    normalization_dict[variation.lower()] = standard_term
        
        # Display normalization statistics
        print(f"\n📊 Normalization Statistics:")
        for category, stats in normalization_stats.items():
            print(f"\n{category.upper()}:")
            for term, count in stats.items():
                if count > 0:
                    print(f"   • {term}: {count:,} products")
        
        # Store normalization dictionary
        self.product_normalization = normalization_dict
        
        print(f"\n✅ Product normalization dictionary created!")
        print(f"   Total normalization rules: {len(normalization_dict):,}")
        
        return normalization_dict
    
    def standardize_city_names(self, dataset='all'):
        """
        Standardisasi nama kota lokasi toko
        """
        print(f"\n🏙️ CITY NAME STANDARDIZATION - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None or 'Shop_City' not in df.columns:
            return
        
        # Analisis kota yang ada
        cities = df['Shop_City'].dropna().str.strip()
        city_counts = cities.value_counts()
        
        print(f"📊 City Analysis:")
        print(f"   Total cities: {len(city_counts):,}")
        print(f"   Total shops: {len(cities):,}")
        
        # Dictionary standardisasi kota
        city_standardization = {
            # Jakarta variations
            'jakarta': ['jakarta', 'dki jakarta', 'jakarta pusat', 'jakarta utara', 
                       'jakarta selatan', 'jakarta timur', 'jakarta barat', 'jkt'],
            
            # Surabaya variations
            'surabaya': ['surabaya', 'sby', 'surabaya timur', 'surabaya utara',
                        'surabaya selatan', 'surabaya barat'],
            
            # Bandung variations
            'bandung': ['bandung', 'bdg', 'kota bandung', 'bandung kota'],
            
            # Medan variations
            'medan': ['medan', 'kota medan'],
            
            # Semarang variations
            'semarang': ['semarang', 'kota semarang', 'smg'],
            
            # Yogyakarta variations
            'yogyakarta': ['yogyakarta', 'jogja', 'yogya', 'diy'],
            
            # Makassar variations
            'makassar': ['makassar', 'ujung pandang'],
            
            # Palembang variations
            'palembang': ['palembang', 'plg'],
            
            # Denpasar variations
            'denpasar': ['denpasar', 'bali', 'denpasar bali'],
            
            # Banjarmasin variations
            'banjarmasin': ['banjarmasin', 'bjm'],
        }
        
        # Create reverse mapping
        city_mapping = {}
        for standard_city, variations in city_standardization.items():
            for variation in variations:
                city_mapping[variation.lower()] = standard_city.title()
        
        # Apply standardization
        df_standardized = df.copy()
        df_standardized['Shop_City_Standardized'] = df_standardized['Shop_City'].str.lower().map(city_mapping)
        
        # Fill unmapped cities with original names (title case)
        df_standardized['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized'].fillna(
            df_standardized['Shop_City'].str.title()
        )
        
        # Statistics
        standardized_cities = df_standardized['Shop_City_Standardized'].value_counts()
        
        print(f"\n📊 Standardization Results:")
        print(f"   Cities after standardization: {len(standardized_cities):,}")
        print(f"   Reduction: {len(city_counts) - len(standardized_cities):,} cities")
        
        print(f"\n🏙️ Top 15 Cities (After Standardization):")
        for city, count in standardized_cities.head(15).items():
            percentage = (count / len(df_standardized) * 100)
            print(f"   • {city}: {count:,} shops ({percentage:.1f}%)")
        
        # Store mapping
        self.city_mapping = city_mapping
        
        # Update dataset with standardized cities
        if dataset == 'all' and self.df_all is not None:
            self.df_all['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized']
        elif dataset == 'filtered' and self.df_filtered is not None:
            self.df_filtered['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized']
        elif dataset == 'commodity' and self.df_commodity is not None:
            self.df_commodity['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized']
        
        print(f"\n✅ City standardization completed!")
        
        return city_mapping, standardized_cities
    
    def _select_dataset(self, dataset):
        """Helper method untuk memilih dataset"""
        if dataset == 'all' and self.df_all is not None:
            return self.df_all
        elif dataset == 'filtered' and self.df_filtered is not None:
            return self.df_filtered
        elif dataset == 'commodity' and self.df_commodity is not None:
            return self.df_commodity
        else:
            print(f"❌ Dataset '{dataset}' tidak tersedia atau kosong")
            return None
    
    def export_processed_data(self, output_file=None):
        """
        Export hasil preprocessing ke Excel baru
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'Tokopedia_Processed_{timestamp}.xlsx'
        
        print(f"\n💾 EXPORTING PROCESSED DATA")
        print("=" * 60)
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Export processed datasets
                if self.df_all is not None:
                    self.df_all.to_excel(writer, sheet_name='All_Products_Processed', index=False)
                    print(f"✅ Exported All Products: {len(self.df_all):,} rows")
                
                if self.df_filtered is not None:
                    self.df_filtered.to_excel(writer, sheet_name='Filtered_Products_Processed', index=False)
                    print(f"✅ Exported Filtered Products: {len(self.df_filtered):,} rows")
                
                if self.df_commodity is not None:
                    self.df_commodity.to_excel(writer, sheet_name='Commodity_Products_Processed', index=False)
                    print(f"✅ Exported Commodity Products: {len(self.df_commodity):,} rows")
                
                # Export normalization dictionaries
                if self.product_normalization:
                    norm_df = pd.DataFrame(list(self.product_normalization.items()), 
                                         columns=['Original_Term', 'Standardized_Term'])
                    norm_df.to_excel(writer, sheet_name='Product_Normalization', index=False)
                    print(f"✅ Exported Product Normalization: {len(norm_df):,} rules")
                
                if self.city_mapping:
                    city_df = pd.DataFrame(list(self.city_mapping.items()), 
                                         columns=['Original_City', 'Standardized_City'])
                    city_df.to_excel(writer, sheet_name='City_Standardization', index=False)
                    print(f"✅ Exported City Standardization: {len(city_df):,} rules")
            
            print(f"\n🎉 Processed data exported successfully!")
            print(f"📁 File: {output_file}")
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
    
    def comprehensive_data_summary(self):
        """
        Ringkasan komprehensif dari semua dataset
        """
        print(f"\n📊 COMPREHENSIVE DATA SUMMARY")
        print("=" * 60)
        
        datasets = [
            ('All Products', self.df_all),
            ('Filtered Products', self.df_filtered),
            ('Commodity Products', self.df_commodity)
        ]
        
        for name, df in datasets:
            if df is not None:
                print(f"\n📋 {name}:")
                print(f"   Shape: {df.shape}")
                print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
                
                if 'Price_Number' in df.columns:
                    print(f"   Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
                    print(f"   Average price: Rp {df['Price_Number'].mean():,.0f}")
                
                if 'Shop_City' in df.columns:
                    print(f"   Unique cities: {df['Shop_City'].nunique():,}")
                
                if 'Shop_Name' in df.columns:
                    print(f"   Unique shops: {df['Shop_Name'].nunique():,}")
                
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                print(f"   Missing data: {missing_pct:.2f}%")
        
        print(f"\n🔧 Preprocessing Status:")
        print(f"   Product normalization rules: {len(self.product_normalization):,}")
        print(f"   City standardization rules: {len(self.city_mapping):,}")