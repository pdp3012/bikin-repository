"""
TOKOPEDIA DATA PREPROCESSING CLASS
Dibuat oleh: Dosen Data Mining dengan pengalaman 30 tahun
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TokopediaDataPreprocessing:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.df_all = None
        self.df_filtered = None
        self.city_mapping = {}
        self.product_normalization = {}
        self._load_data()
        
        print("🎓 TOKOPEDIA DATA PREPROCESSING INITIALIZED")
        print("=" * 60)
        print(f"📁 File: {excel_file_path}")
        print("=" * 60)
    
    def _load_data(self):
        try:
            excel_data = pd.read_excel(self.excel_file_path, sheet_name=None)
            available_sheets = list(excel_data.keys())
            print(f"📋 Sheets tersedia: {available_sheets}")
            
            if 'All Products' in available_sheets:
                self.df_all = excel_data['All Products']
                print(f"✅ Loaded 'All Products': {len(self.df_all):,} rows")
            elif available_sheets:
                self.df_all = excel_data[available_sheets[0]]
                print(f"✅ Loaded '{available_sheets[0]}': {len(self.df_all):,} rows")
            
            for sheet in available_sheets:
                if 'Min' in sheet and 'Sold' in sheet:
                    self.df_filtered = excel_data[sheet]
                    print(f"✅ Loaded '{sheet}': {len(self.df_filtered):,} rows")
                    break
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def basic_data_analysis(self, dataset='all'):
        print(f"\n🔍 BASIC DATA ANALYSIS - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None:
            return
        
        print(f"�� SHAPE: {df.shape}")
        print(f"   Rows: {df.shape[0]:,}")
        print(f"   Columns: {df.shape[1]:,}")
        
        print(f"\n📋 HEAD (First 5 rows):")
        print(df.head())
        
        print(f"\n📈 INFO:")
        print(df.info())
        
        print(f"\n📊 DESCRIBE (Numerical columns):")
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            print(df[numerical_cols].describe())
        
        return df
    
    def check_missing_values(self, dataset='all'):
        print(f"\n🔍 MISSING VALUES ANALYSIS - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None:
            return
        
        missing_data = pd.DataFrame({
            'Column': df.columns,
            'Missing_Count': df.isnull().sum().values,
            'Missing_Percentage': (df.isnull().sum().values / len(df) * 100).round(2),
            'Data_Type': df.dtypes.values
        })
        
        missing_data = missing_data.sort_values('Missing_Percentage', ascending=False)
        print(f"📊 Missing Values Summary:")
        print(missing_data)
        
        total_missing = missing_data['Missing_Count'].sum()
        overall_missing_pct = (total_missing / (len(df) * len(df.columns)) * 100).round(2)
        
        print(f"\n📈 Statistics:")
        print(f"   Total missing values: {total_missing:,}")
        print(f"   Overall missing percentage: {overall_missing_pct}%")
        
        return missing_data
    
    def check_duplicates(self, dataset='all'):
        print(f"\n🔍 DUPLICATE ANALYSIS - Dataset: {dataset.upper()}")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None:
            return
        
        complete_duplicates = df.duplicated().sum()
        print(f"📊 Complete Duplicates: {complete_duplicates:,}")
        
        if 'Product_ID' in df.columns:
            product_id_duplicates = df['Product_ID'].duplicated().sum()
            print(f"📱 Product_ID Duplicates: {product_id_duplicates:,}")
        
        if 'Product_Name' in df.columns:
            product_name_duplicates = df['Product_Name'].duplicated().sum()
            print(f"📝 Product_Name Duplicates: {product_name_duplicates:,}")
            
            if product_name_duplicates > 0:
                top_duplicate_names = df['Product_Name'].value_counts().head(5)
                print(f"\n🔥 Top 5 Most Common Product Names:")
                for name, count in top_duplicate_names.items():
                    if count > 1:
                        print(f"   • {name[:50]}... : {count} times")
        
        return complete_duplicates
    
    def create_product_normalization_dictionary(self, dataset='all'):
        print(f"\n🔄 PRODUCT NORMALIZATION DICTIONARY")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None or 'Product_Name' not in df.columns:
            return
        
        product_names = df['Product_Name'].dropna().unique()
        print(f"📊 Total unique product names: {len(product_names):,}")
        
        brand_patterns = {
            'samsung': ['samsung', 'samsu', 'sams'],
            'iphone': ['iphone', 'ip', 'apple'],
            'xiaomi': ['xiaomi', 'mi', 'redmi'],
            'oppo': ['oppo', 'op'],
            'vivo': ['vivo', 'vi']
        }
        
        size_patterns = {
            'xl': ['xl', 'x-l', 'extra large'],
            'l': ['l', 'large'],
            'm': ['m', 'medium'],
            's': ['s', 'small']
        }
        
        color_patterns = {
            'hitam': ['hitam', 'black'],
            'putih': ['putih', 'white'],
            'merah': ['merah', 'red'],
            'biru': ['biru', 'blue']
        }
        
        all_patterns = {'brands': brand_patterns, 'sizes': size_patterns, 'colors': color_patterns}
        
        normalization_dict = {}
        for category, patterns in all_patterns.items():
            for standard_term, variations in patterns.items():
                for variation in variations:
                    normalization_dict[variation.lower()] = standard_term
        
        self.product_normalization = normalization_dict
        print(f"✅ Created {len(normalization_dict):,} normalization rules")
        
        return normalization_dict
    
    def standardize_city_names(self, dataset='all'):
        print(f"\n🏙️ CITY NAME STANDARDIZATION")
        print("=" * 60)
        
        df = self._select_dataset(dataset)
        if df is None or 'Shop_City' not in df.columns:
            return
        
        cities = df['Shop_City'].dropna().str.strip()
        city_counts = cities.value_counts()
        
        print(f"�� Analysis:")
        print(f"   Total cities: {len(city_counts):,}")
        print(f"   Total shops: {len(cities):,}")
        
        city_standardization = {
            'jakarta': ['jakarta', 'dki jakarta', 'jakarta pusat', 'jakarta utara', 
                       'jakarta selatan', 'jakarta timur', 'jakarta barat', 'jkt'],
            'surabaya': ['surabaya', 'sby', 'surabaya timur', 'surabaya utara'],
            'bandung': ['bandung', 'bdg', 'kota bandung'],
            'medan': ['medan', 'kota medan'],
            'semarang': ['semarang', 'kota semarang'],
            'yogyakarta': ['yogyakarta', 'jogja', 'yogya', 'diy'],
            'makassar': ['makassar', 'ujung pandang'],
            'denpasar': ['denpasar', 'bali']
        }
        
        city_mapping = {}
        for standard_city, variations in city_standardization.items():
            for variation in variations:
                city_mapping[variation.lower()] = standard_city.title()
        
        df_standardized = df.copy()
        df_standardized['Shop_City_Standardized'] = df_standardized['Shop_City'].str.lower().map(city_mapping)
        df_standardized['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized'].fillna(
            df_standardized['Shop_City'].str.title()
        )
        
        standardized_cities = df_standardized['Shop_City_Standardized'].value_counts()
        
        print(f"\n📊 Results:")
        print(f"   Cities before: {len(city_counts):,}")
        print(f"   Cities after: {len(standardized_cities):,}")
        
        print(f"\n🏙️ Top 10 Cities:")
        for city, count in standardized_cities.head(10).items():
            percentage = (count / len(df_standardized) * 100)
            print(f"   • {city}: {count:,} shops ({percentage:.1f}%)")
        
        self.city_mapping = city_mapping
        
        if dataset == 'all' and self.df_all is not None:
            self.df_all['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized']
        elif dataset == 'filtered' and self.df_filtered is not None:
            self.df_filtered['Shop_City_Standardized'] = df_standardized['Shop_City_Standardized']
        
        print(f"✅ Standardization completed!")
        
        return city_mapping, standardized_cities
    
    def _select_dataset(self, dataset):
        if dataset == 'all' and self.df_all is not None:
            return self.df_all
        elif dataset == 'filtered' and self.df_filtered is not None:
            return self.df_filtered
        else:
            print(f"❌ Dataset '{dataset}' tidak tersedia")
            return None
    
    def comprehensive_data_summary(self):
        print(f"\n📊 COMPREHENSIVE DATA SUMMARY")
        print("=" * 60)
        
        datasets = [('All Products', self.df_all), ('Filtered Products', self.df_filtered)]
        
        for name, df in datasets:
            if df is not None:
                print(f"\n📋 {name}:")
                print(f"   Shape: {df.shape}")
                
                if 'Price_Number' in df.columns:
                    print(f"   Price range: Rp {df['Price_Number'].min():,.0f} - Rp {df['Price_Number'].max():,.0f}")
                    print(f"   Average price: Rp {df['Price_Number'].mean():,.0f}")
                
                if 'Shop_City' in df.columns:
                    print(f"   Unique cities: {df['Shop_City'].nunique():,}")
                
                if 'Shop_Name' in df.columns:
                    print(f"   Unique shops: {df['Shop_Name'].nunique():,}")
        
        print(f"\n🔧 Preprocessing Status:")
        print(f"   Product normalization rules: {len(self.product_normalization):,}")
        print(f"   City standardization rules: {len(self.city_mapping):,}")
    
    def export_processed_data(self, output_file=None):
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'Tokopedia_Processed_{timestamp}.xlsx'
        
        print(f"\n💾 EXPORTING PROCESSED DATA")
        print("=" * 60)
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                if self.df_all is not None:
                    self.df_all.to_excel(writer, sheet_name='All_Products_Processed', index=False)
                    print(f"✅ Exported All Products: {len(self.df_all):,} rows")
                
                if self.df_filtered is not None:
                    self.df_filtered.to_excel(writer, sheet_name='Filtered_Products_Processed', index=False)
                    print(f"✅ Exported Filtered Products: {len(self.df_filtered):,} rows")
                
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
            
            print(f"\n🎉 Success! File: {output_file}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


# Contoh penggunaan
if __name__ == "__main__":
    excel_file = "Tokopedia_smartphone.xlsx"
    
    try:
        preprocessor = TokopediaDataPreprocessing(excel_file)
        
        print("\n" + "="*60)
        print("�� TAHAP 1: ANALISIS DASAR DATA")
        print("="*60)
        preprocessor.basic_data_analysis(dataset='all')
        
        print("\n" + "="*60)
        print("🔍 TAHAP 2: MISSING VALUES")
        print("="*60)
        preprocessor.check_missing_values(dataset='all')
        
        print("\n" + "="*60)
        print("🔍 TAHAP 3: DUPLIKASI")
        print("="*60)
        preprocessor.check_duplicates(dataset='all')
        
        print("\n" + "="*60)
        print("🔄 TAHAP 4: NORMALISASI PRODUK")
        print("="*60)
        preprocessor.create_product_normalization_dictionary(dataset='all')
        
        print("\n" + "="*60)
        print("🏙️ TAHAP 5: STANDARDISASI KOTA")
        print("="*60)
        preprocessor.standardize_city_names(dataset='all')
        
        print("\n" + "="*60)
        print("📊 TAHAP 6: RINGKASAN")
        print("="*60)
        preprocessor.comprehensive_data_summary()
        
        print("\n" + "="*60)
        print("💾 TAHAP 7: EXPORT")
        print("="*60)
        preprocessor.export_processed_data()
        
        print(f"\n✅ PREPROCESSING COMPLETED!")
        
    except FileNotFoundError:
        print(f"❌ File {excel_file} tidak ditemukan!")
    except Exception as e:
        print(f"❌ Error: {e}")
