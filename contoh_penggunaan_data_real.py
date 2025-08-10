# --- CONTOH PENGGUNAAN DATA REAL UNTUK ANALISIS SPASIAL ---
"""
Contoh penggunaan data real untuk analisis spasial dengan choropleth map
Dibuat oleh: Dosen Sains Data dengan 30 tahun pengalaman profesional
"""

import pandas as pd
import numpy as np
import folium
from folium import plugins
import plotly.graph_objects as go
import plotly.express as px
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_real_data(file_path):
    """
    Load dan prepare data real untuk analisis
    """
    print("📊 Loading data real...")
    
    try:
        # Load data dari Excel
        df = pd.read_excel(file_path)
        print(f"✅ Data berhasil dimuat: {df.shape}")
        
        # Validasi kolom yang diperlukan
        required_columns = ['Product_Name', 'Shop_City', 'Price_Number', 'Sold_Count', 'Rating']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"⚠️  Kolom yang hilang: {missing_columns}")
            print("   Pastikan data memiliki kolom: Product_Name, Shop_City, Price_Number, Sold_Count, Rating")
            return None
        
        # Tambahkan kolom derived jika belum ada
        if 'Revenue_Estimate' not in df.columns:
            df['Revenue_Estimate'] = df['Price_Number'] * df['Sold_Count']
        
        if 'Performance_Score' not in df.columns:
            df['Performance_Score'] = (df['Rating'] * 0.4 + 
                                      (df['Sold_Count'] / df['Sold_Count'].max()) * 0.4 + 
                                      (df.get('Review_Count', pd.Series([100]*len(df))) / 
                                       df.get('Review_Count', pd.Series([100]*len(df))).max()) * 0.2)
        
        # Clustering jika belum ada
        if 'Cluster' not in df.columns:
            print("🔍 Melakukan clustering...")
            kmeans = KMeans(n_clusters=5, random_state=42)
            df['Cluster'] = kmeans.fit_predict(df[['Price_Number', 'Sold_Count', 'Rating']].values)
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def create_choropleth_from_real_data(df, output_filename="choropleth_real_data.html"):
    """
    Buat choropleth map dari data real
    """
    print("\n🗺️ Membuat choropleth map dari data real...")
    
    # Koordinat kota Indonesia
    city_coordinates = {
        'Jakarta': [-6.2088, 106.8456],
        'Surabaya': [-7.2575, 112.7521],
        'Bandung': [-6.9175, 107.6191],
        'Medan': [3.5952, 98.6722],
        'Semarang': [-6.9932, 110.4203],
        'Yogyakarta': [-7.7971, 110.3708],
        'Palembang': [-2.9761, 104.7754],
        'Makassar': [-5.1477, 119.4327],
        'Denpasar': [-8.6500, 115.2167],
        'Manado': [1.4748, 124.8421],
        'Batam': [1.0456, 104.0611],
        'Padang': [-0.9471, 100.4178],
        'Pontianak': [-0.0235, 109.3303],
        'Banjarmasin': [-3.3167, 114.5900],
        'Pekanbaru': [0.5333, 101.4500],
        'Malang': [-7.9797, 112.6304],
        'Solo': [-7.5500, 110.8000],
        'Tangerang': [-6.1700, 106.6300],
        'Bekasi': [-6.2300, 106.9900],
        'Depok': [-6.3900, 106.8100]
    }
    
    # Aggregasi data per kota
    city_stats = df.groupby('Shop_City').agg({
        'Sold_Count': 'sum',
        'Price_Number': 'mean',
        'Rating': 'mean',
        'Performance_Score': 'mean',
        'Product_Name': 'count'
    }).reset_index()
    
    city_stats.columns = ['City', 'Total_Sold', 'Avg_Price', 'Avg_Rating', 'Avg_Performance', 'Product_Count']
    
    # Tambahkan koordinat
    city_stats['Latitude'] = city_stats['City'].map(lambda x: city_coordinates.get(x, [0, 0])[0])
    city_stats['Longitude'] = city_stats['City'].map(lambda x: city_coordinates.get(x, [0, 0])[1])
    
    # Filter kota dengan koordinat valid
    city_stats = city_stats[(city_stats['Latitude'] != 0) | (city_stats['Longitude'] != 0)]
    
    if city_stats.empty:
        print("❌ Tidak ada data kota yang valid untuk choropleth map")
        return None
    
    # Buat choropleth map
    m = folium.Map(
        location=[city_stats['Latitude'].mean(), city_stats['Longitude'].mean()],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Color scale
    max_sold = city_stats['Total_Sold'].max()
    
    def get_color(sold_count):
        if sold_count >= max_sold * 0.8:
            return 'red'
        elif sold_count >= max_sold * 0.6:
            return 'orange'
        elif sold_count >= max_sold * 0.4:
            return 'yellow'
        elif sold_count >= max_sold * 0.2:
            return 'lightgreen'
        else:
            return 'green'
    
    # Tambahkan circle markers
    for idx, row in city_stats.iterrows():
        color = get_color(row['Total_Sold'])
        radius = np.sqrt(row['Total_Sold']) / 10
        
        popup_content = f"""
        <b>{row['City']}</b><br>
        <b>Total Terjual:</b> {row['Total_Sold']:,}<br>
        <b>Rata-rata Harga:</b> Rp{row['Avg_Price']:,.0f}<br>
        <b>Rata-rata Rating:</b> {row['Avg_Rating']:.2f}<br>
        <b>Rata-rata Performance:</b> {row['Avg_Performance']:.2f}<br>
        <b>Jumlah Produk:</b> {row['Product_Count']}
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=radius,
            popup=folium.Popup(popup_content, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Tambahkan legend
    legend_html = f'''
    <div style="position: fixed;
                top: 50px; right: 50px; width: 150px; height: 200px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:12px; padding: 10px">
                <p><b>Jumlah Kasus:</b></p>
                <p><i class="fa fa-circle" style="color:red"></i> {int(max_sold * 0.8):,}+</p>
                <p><i class="fa fa-circle" style="color:orange"></i> {int(max_sold * 0.6):,}-{int(max_sold * 0.8):,}</p>
                <p><i class="fa fa-circle" style="color:yellow"></i> {int(max_sold * 0.4):,}-{int(max_sold * 0.6):,}</p>
                <p><i class="fa fa-circle" style="color:lightgreen"></i> {int(max_sold * 0.2):,}-{int(max_sold * 0.4):,}</p>
                <p><i class="fa fa-circle" style="color:green"></i> <{int(max_sold * 0.2):,}</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    m.save(output_filename)
    print(f"✅ Choropleth map disimpan sebagai: {output_filename}")
    
    return city_stats

def analyze_real_data(df):
    """
    Analisis data real dan tampilkan insight
    """
    print("\n📈 Analisis Data Real:")
    print("="*50)
    
    # Statistik umum
    print(f"📊 Total Produk: {len(df):,}")
    print(f"🏙️  Jumlah Kota: {df['Shop_City'].nunique()}")
    print(f"💰 Range Harga: Rp{df['Price_Number'].min():,.0f} - Rp{df['Price_Number'].max():,.0f}")
    print(f"📦 Total Terjual: {df['Sold_Count'].sum():,}")
    print(f"⭐ Rata-rata Rating: {df['Rating'].mean():.2f}")
    
    # Top cities
    print("\n🏆 Top 10 Kota berdasarkan Total Penjualan:")
    city_sales = df.groupby('Shop_City')['Sold_Count'].sum().sort_values(ascending=False)
    for i, (city, sales) in enumerate(city_sales.head(10).items(), 1):
        print(f"   {i:2d}. {city:15s}: {sales:,} terjual")
    
    # Cluster analysis
    if 'Cluster' in df.columns:
        print(f"\n🎯 Analisis Cluster ({df['Cluster'].nunique()} cluster):")
        cluster_stats = df.groupby('Cluster').agg({
            'Price_Number': 'mean',
            'Sold_Count': 'mean',
            'Rating': 'mean',
            'Performance_Score': 'mean',
            'Product_Name': 'count'
        }).round(2)
        
        for cluster_id, stats in cluster_stats.iterrows():
            print(f"   Cluster {cluster_id} ({stats['Product_Name']} produk):")
            print(f"      💰 Rata-rata harga: Rp{stats['Price_Number']:,.0f}")
            print(f"      📦 Rata-rata terjual: {stats['Sold_Count']:,.0f}")
            print(f"      ⭐ Rata-rata rating: {stats['Rating']:.2f}")
            print(f"      🎯 Performance score: {stats['Performance_Score']:.2f}")

def main():
    """
    Main function untuk contoh penggunaan data real
    """
    print("🎯 CONTOH PENGGUNAAN DATA REAL UNTUK ANALISIS SPASIAL")
    print("="*60)
    
    # Pilihan file data
    data_files = [
        "sample_data_realistic.xlsx",
        "Tokopedia_sarung_tangan_with_clusters.xlsx"
    ]
    
    print("\n📁 File data yang tersedia:")
    for i, file in enumerate(data_files, 1):
        print(f"   {i}. {file}")
    
    # Gunakan file pertama sebagai default
    selected_file = data_files[0]
    print(f"\n✅ Menggunakan file: {selected_file}")
    
    # Load dan prepare data
    df = load_and_prepare_real_data(selected_file)
    
    if df is not None:
        # Analisis data
        analyze_real_data(df)
        
        # Buat choropleth map
        city_stats = create_choropleth_from_real_data(df)
        
        if city_stats is not None:
            print(f"\n📊 Statistik Kota untuk Choropleth Map:")
            print(city_stats[['City', 'Total_Sold', 'Avg_Price', 'Avg_Rating']].head(10))
        
        print(f"\n🎉 Analisis selesai! File yang dihasilkan:")
        print(f"   • choropleth_real_data.html - Choropleth map dari data real")
        
    else:
        print("❌ Gagal memuat data. Pastikan file data tersedia dan format sesuai.")

if __name__ == "__main__":
    main()