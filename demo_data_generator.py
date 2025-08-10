# --- GENERATOR DATA DUMMY UNTUK DEMONSTRASI ---
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_dummy_data(n_samples=1000):
    """
    Generate data dummy untuk demonstrasi analisis spasial
    """
    print("🔧 Generating dummy data untuk demonstrasi...")
    
    # Kota-kota di Indonesia dengan koordinat
    cities = [
        'Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Semarang', 
        'Yogyakarta', 'Palembang', 'Makassar', 'Denpasar', 'Manado',
        'Batam', 'Padang', 'Pontianak', 'Banjarmasin', 'Pekanbaru',
        'Malang', 'Solo', 'Tangerang', 'Bekasi', 'Depok'
    ]
    
    # Jenis sarung tangan
    glove_types = [
        'Sarung Tangan Latex', 'Sarung Tangan Nitril', 'Sarung Tangan Vinyl',
        'Sarung Tangan Karet', 'Sarung Tangan Medis', 'Sarung Tangan Safety',
        'Sarung Tangan Motor', 'Sarung Tangan Gym', 'Sarung Tangan Kulit',
        'Sarung Tangan Wol'
    ]
    
    # Brand sarung tangan
    brands = [
        'Medisafe', 'SafetyPro', 'Guardian', 'ProtectPlus', 'SafeHand',
        'MediCare', 'SafetyFirst', 'ProtectMax', 'SafeGuard', 'MediPro'
    ]
    
    # Generate data
    data = []
    
    for i in range(n_samples):
        # Basic info
        product_name = f"{random.choice(glove_types)} {random.choice(brands)}"
        shop_name = f"Toko {random.choice(['Medis', 'Safety', 'Pro', 'Care', 'Plus'])} {random.randint(1, 100)}"
        shop_city = random.choice(cities)
        
        # Price (dalam Rupiah)
        base_price = random.randint(5000, 50000)
        price_variation = random.uniform(0.8, 1.5)
        price_number = int(base_price * price_variation)
        
        # Sold count
        sold_count = random.randint(10, 5000)
        
        # Rating (1-5)
        rating = round(random.uniform(3.0, 5.0), 1)
        
        # Review count
        review_count = random.randint(5, 500)
        
        # Performance score (calculated)
        performance_score = round((rating * 0.4) + (min(sold_count/1000, 1) * 0.4) + (min(review_count/100, 1) * 0.2), 2)
        
        # Revenue estimate
        revenue_estimate = price_number * sold_count
        
        # Cluster (akan diisi nanti oleh HDBSCAN)
        cluster = random.randint(0, 4)  # Dummy cluster untuk demo
        
        data.append({
            'Product_Name': product_name,
            'Shop_Name': shop_name,
            'Shop_City': shop_city,
            'Price_Number': price_number,
            'Sold_Count': sold_count,
            'Rating': rating,
            'Review_Count': review_count,
            'Performance_Score': performance_score,
            'Revenue_Estimate': revenue_estimate,
            'Cluster': cluster
        })
    
    df = pd.DataFrame(data)
    
    print(f"✅ Generated {len(df)} samples")
    print(f"📊 Data shape: {df.shape}")
    print(f"🏙️ Cities covered: {df['Shop_City'].nunique()}")
    print(f"💰 Price range: Rp{df['Price_Number'].min():,} - Rp{df['Price_Number'].max():,}")
    print(f"📦 Sold range: {df['Sold_Count'].min():,} - {df['Sold_Count'].max():,}")
    print(f"⭐ Rating range: {df['Rating'].min():.1f} - {df['Rating'].max():.1f}")
    
    return df

# Generate dan simpan data dummy
if __name__ == "__main__":
    df_dummy = generate_dummy_data(1000)
    
    # Simpan ke file
    df_dummy.to_excel("dummy_tokopedia_data.xlsx", index=False)
    print("\n💾 Data dummy disimpan ke 'dummy_tokopedia_data.xlsx'")
    
    # Tampilkan sample data
    print("\n📋 Sample data:")
    print(df_dummy.head())
    
    # Tampilkan statistik
    print("\n📈 Statistik data:")
    print(df_dummy.describe())