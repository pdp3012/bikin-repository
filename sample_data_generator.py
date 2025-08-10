# --- GENERATOR DATA SAMPLE UNTUK DEMONSTRASI CHOROPLETH MAP ---
import pandas as pd
import numpy as np
import random

def generate_realistic_data(n_samples=2000):
    """
    Generate realistic sample data untuk demonstrasi choropleth map
    """
    np.random.seed(42)
    
    # Data kota Indonesia dengan koordinat yang lebih akurat
    cities_data = {
        'Jakarta': {'lat': -6.2088, 'lon': 106.8456, 'weight': 0.25},
        'Surabaya': {'lat': -7.2575, 'lon': 112.7521, 'weight': 0.20},
        'Bandung': {'lat': -6.9175, 'lon': 107.6191, 'weight': 0.15},
        'Medan': {'lat': 3.5952, 'lon': 98.6722, 'weight': 0.12},
        'Semarang': {'lat': -6.9932, 'lon': 110.4203, 'weight': 0.08},
        'Yogyakarta': {'lat': -7.7971, 'lon': 110.3708, 'weight': 0.08},
        'Palembang': {'lat': -2.9761, 'lon': 104.7754, 'weight': 0.06},
        'Makassar': {'lat': -5.1477, 'lon': 119.4327, 'weight': 0.05},
        'Denpasar': {'lat': -8.6500, 'lon': 115.2167, 'weight': 0.05},
        'Manado': {'lat': 1.4748, 'lon': 124.8421, 'weight': 0.03},
        'Batam': {'lat': 1.0456, 'lon': 104.0611, 'weight': 0.03},
        'Padang': {'lat': -0.9471, 'lon': 100.4178, 'weight': 0.03},
        'Pontianak': {'lat': -0.0235, 'lon': 109.3303, 'weight': 0.02},
        'Banjarmasin': {'lat': -3.3167, 'lon': 114.5900, 'weight': 0.02},
        'Pekanbaru': {'lat': 0.5333, 'lon': 101.4500, 'weight': 0.02},
        'Malang': {'lat': -7.9797, 'lon': 112.6304, 'weight': 0.02},
        'Solo': {'lat': -7.5500, 'lon': 110.8000, 'weight': 0.02},
        'Tangerang': {'lat': -6.1700, 'lon': 106.6300, 'weight': 0.02},
        'Bekasi': {'lat': -6.2300, 'lon': 106.9900, 'weight': 0.02},
        'Depok': {'lat': -6.3900, 'lon': 106.8100, 'weight': 0.02}
    }
    
    # Generate data berdasarkan weight kota
    cities = []
    for city, info in cities_data.items():
        count = int(n_samples * info['weight'])
        cities.extend([city] * count)
    
    # Jika total tidak tepat, adjust
    while len(cities) < n_samples:
        cities.append(random.choice(list(cities_data.keys())))
    
    cities = cities[:n_samples]
    
    # Generate realistic product data
    data = {
        'Product_Name': [f'Sarung Tangan {i+1}' for i in range(n_samples)],
        'Shop_Name': [f'Toko {np.random.choice(["ABC", "XYZ", "DEF", "GHI", "JKL", "MNO", "PQR", "STU"])}' for _ in range(n_samples)],
        'Shop_City': cities,
        'Price_Number': np.random.lognormal(10.5, 0.6, n_samples),  # Harga yang lebih realistis
        'Sold_Count': np.random.poisson(800, n_samples),  # Penjualan yang lebih tinggi
        'Rating': np.random.uniform(3.8, 5.0, n_samples),  # Rating yang lebih tinggi
        'Review_Count': np.random.poisson(150, n_samples)  # Review yang lebih banyak
    }
    
    df = pd.DataFrame(data)
    
    # Tambahkan kolom derived
    df['Revenue_Estimate'] = df['Price_Number'] * df['Sold_Count']
    df['Performance_Score'] = (df['Rating'] * 0.4 + 
                              (df['Sold_Count'] / df['Sold_Count'].max()) * 0.4 + 
                              (df['Review_Count'] / df['Review_Count'].max()) * 0.2)
    
    # Simulasi clustering yang lebih realistis
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=6, random_state=42)
    df['Cluster'] = kmeans.fit_predict(df[['Price_Number', 'Sold_Count', 'Rating']].values)
    
    return df, cities_data

def create_city_coordinates_dict(cities_data):
    """
    Convert cities_data ke format yang digunakan dalam kode utama
    """
    return {city: [info['lat'], info['lon']] for city, info in cities_data.items()}

if __name__ == "__main__":
    # Generate data
    df, cities_data = generate_realistic_data(2000)
    
    # Save data
    df.to_excel("sample_data_realistic.xlsx", index=False)
    
    # Print summary
    print("✅ Data sample realistis berhasil dibuat!")
    print(f"   Dimensi: {df.shape}")
    print(f"   Jumlah kota: {df['Shop_City'].nunique()}")
    print(f"   Range harga: Rp{df['Price_Number'].min():,.0f} - Rp{df['Price_Number'].max():,.0f}")
    print(f"   Range penjualan: {df['Sold_Count'].min():,} - {df['Sold_Count'].max():,}")
    print(f"   Range rating: {df['Rating'].min():.2f} - {df['Rating'].max():.2f}")
    
    # Print top cities by sales
    print("\n📊 Top 10 Kota berdasarkan Total Penjualan:")
    city_sales = df.groupby('Shop_City')['Sold_Count'].sum().sort_values(ascending=False)
    for i, (city, sales) in enumerate(city_sales.head(10).items(), 1):
        print(f"   {i:2d}. {city:12s}: {sales:,} terjual")
    
    print(f"\n💾 Data disimpan ke: sample_data_realistic.xlsx")