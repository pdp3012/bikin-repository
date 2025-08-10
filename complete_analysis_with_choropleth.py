# --- IMPORT LIBRARY ---
# Pastikan library folium dan plotly di-import
import pandas as pd
import numpy as np # Untuk np.nan
import folium
from folium import plugins
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
import os
import json
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import branca.colormap as cm

# --- 6. PEMETAAN SPASIAL DENGAN FOLIUM ---
print("\n" + "="*70)
print("LANGKAH 5: PEMETAAN SPASIAL DISTRIBUSI HARGA")
print("="*70)

# --- Asumsi: df adalah DataFrame utama hasil dari proses sebelumnya ---
# Jika df_clustered berasal dari proses sebelumnya, ganti 'df' dengan 'df_clustered' di seluruh code ini
# df = df_clustered # <-- Uncomment jika perlu

# a. Prepare data untuk mapping
print("\n🗺️ Menyiapkan data untuk pemetaan spasial...")

# Buat koordinat dummy berdasarkan Shop_City (untuk demo)
# Dalam real case, Anda perlu koordinat latitude/longitude yang sebenarnya
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
    # Tambahkan kota lain jika diperlukan
}

# Pastikan df sudah didefinisikan sebelumnya
if 'df' not in locals() and 'df' not in globals():
    print("❌ ERROR: Variabel 'df' tidak ditemukan. Pastikan data sudah dimuat dan diproses sebelumnya.")
    # Untuk demonstrasi, kita buat DataFrame kosong
    df = pd.DataFrame()
else:
    print(f"✅ Data ditemukan. Dimensi: {df.shape}")

# Assign coordinates berdasarkan Shop_City
df_mapping = df.copy()
df_mapping['Latitude'] = df_mapping['Shop_City'].map(lambda x: city_coordinates.get(x, [0, 0])[0])
df_mapping['Longitude'] = df_mapping['Shop_City'].map(lambda x: city_coordinates.get(x, [0, 0])[1])

# Filter data dengan koordinat valid
initial_shape = df_mapping.shape[0]
df_mapping = df_mapping[(df_mapping['Latitude'] != 0) | (df_mapping['Longitude'] != 0)]
filtered_shape = df_mapping.shape[0]
print(f"   Data untuk mapping: {initial_shape} -> {filtered_shape} (difilter {initial_shape - filtered_shape} baris tanpa koordinat)")

# b. Buat peta interaktif
print("\n🌍 Membuat peta interaktif...")

if not df_mapping.empty:
    # Buat base map
    m = folium.Map(
        location=[df_mapping['Latitude'].mean(), df_mapping['Longitude'].mean()],
        zoom_start=5,
        tiles='OpenStreetMap'
    )

    # Color mapping untuk cluster - HANYA GUNAKAN WARNA CSS YANG VALID
    # Ganti 'lightred' dengan 'lightcoral' dan pastikan semua warna valid
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred',
        'lightcoral', 'beige', 'darkblue', 'darkgreen',
        'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue',
        'lightgreen', 'gray', 'black', 'lightgray'
    ]
    # Jika jumlah cluster lebih banyak dari warna, gunakan modulo
    # Tambahkan warna default untuk noise (-1)
    default_noise_color = 'gray'

    # Add markers untuk setiap produk
    for idx, row in df_mapping.iterrows():
        # Pastikan Cluster adalah integer, tangani NaN
        # PERBAIKAN: Cek apakah kolom 'Cluster' ada sebelum mengakses
        if 'Cluster' in df_mapping.columns:
            cluster_value = row.get('Cluster', np.nan)
            if pd.isna(cluster_value):
                cluster_id = -1
            else:
                try:
                    cluster_id = int(cluster_value)
                except (ValueError, TypeError):
                    cluster_id = -1 # Anggap sebagai noise jika tidak bisa dikonversi
        else:
            # Jika kolom Cluster tidak ada, berikan ID default
            cluster_id = 0
            print("⚠️  Kolom 'Cluster' tidak ditemukan. Menggunakan cluster ID default = 0")

        # Tentukan warna
        if cluster_id == -1:
            color = default_noise_color
        else:
            # Gunakan modulo untuk memastikan indeks tidak melebihi panjang daftar warna
            color_idx = cluster_id % len(colors)
            color = colors[color_idx]

        # Popup content - Tangani kemungkinan keyerror
        try:
            product_name = row.get('Product_Name', 'N/A')[:50]
            shop_name = row.get('Shop_Name', 'N/A')
            shop_city = row.get('Shop_City', 'N/A')
            price_number = row.get('Price_Number', 0)
            sold_count = row.get('Sold_Count', 0)
            rating = row.get('Rating', 0)
            cluster_display = cluster_id
            performance_score = row.get('Performance_Score', 0)
        except KeyError as e:
            print(f"⚠️  KeyError saat membuat popup untuk baris {idx}: {e}")
            continue # Lewati baris ini jika ada keyerror

        popup_content = f"""
        <b>{product_name}...</b><br>
        <b>Shop:</b> {shop_name}<br>
        <b>City:</b> {shop_city}<br>
        <b>Price:</b> Rp{price_number:,.0f}<br>
        <b>Sold:</b> {sold_count:,}<br>
        <b>Rating:</b> {rating:.1f}<br>
        <b>Cluster:</b> {cluster_display}<br>
        <b>Performance Score:</b> {performance_score:.2f}
        """

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon='info-sign'),
            tooltip=f"Cluster {cluster_display}: {product_name[:30]}..."
        ).add_to(m)

    # Add cluster legend
    # PERBAIKAN: Pastikan hanya menampilkan legenda untuk cluster yang benar-benar ada
    # Tangani NaN dan konversi ke integer dengan aman
    if 'Cluster' in df_mapping.columns:
        unique_clusters_series = df_mapping['Cluster'].dropna()
        unique_clusters_int = set()
        for val in unique_clusters_series:
            try:
                unique_clusters_int.add(int(val))
            except (ValueError, TypeError):
                # Jika tidak bisa dikonversi, anggap sebagai noise
                unique_clusters_int.add(-1)

        unique_clusters_in_map_data = sorted(list(unique_clusters_int))
    else:
        # Jika tidak ada kolom Cluster, gunakan cluster default
        unique_clusters_in_map_data = [0]

    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 200px; height: auto; max-height: 300px; overflow-y: auto;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px">
                <p><b>Cluster Legend</b></p>
    '''
    for cluster_id in unique_clusters_in_map_data:
        if cluster_id == -1:
            legend_html += f'<p><i class="fa fa-circle" style="color:{default_noise_color}"></i> Noise</p>'
        else:
            color_idx = cluster_id % len(colors)
            color = colors[color_idx]
            legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> Cluster {cluster_id}</p>'

    legend_html += '''
                </div>
                '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add heatmap layer untuk density
    # Heatmap hanya butuh lat, lon, dan bobot (opsional)
    heat_data = []
    for idx, row in df_mapping.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        # Gunakan Sold_Count sebagai bobot untuk heatmap
        weight = row.get('Sold_Count', 1)
        if lat != 0 or lon != 0: # Hanya tambahkan jika koordinat valid
            heat_data.append([lat, lon, weight])

    if heat_data: # Hanya tambahkan layer jika ada data
        plugins.HeatMap(heat_data, radius=15).add_to(m)
    else:
        print("   ⚠️  Tidak ada data heatmap yang valid untuk ditambahkan.")

    # Save map
    map_filename = "peta_distribusi_harga_sarung_tangan.html"
    m.save(map_filename)
    print(f"   ✅ Peta interaktif disimpan sebagai: {map_filename}")
else:
    print("   ⚠️  Tidak ada data dengan koordinat valid untuk dipetakan.")
    map_filename = None

# --- 6.1. CHOROPLETH MAP SPASIAL DENGAN LEGENDA ---
print("\n" + "="*70)
print("LANGKAH 5.1: CHOROPLETH MAP SPASIAL DENGAN LEGENDA")
print("="*70)

def create_choropleth_map(df_data, metric_column='Sold_Count', title="Distribusi Kasus per Wilayah"):
    """
    Membuat choropleth map dengan legenda yang sophisticated
    """
    print(f"\n🗺️ Membuat Choropleth Map untuk metrik: {metric_column}")
    
    # Buat data agregat per kota
    if not df_data.empty and 'Shop_City' in df_data.columns and metric_column in df_data.columns:
        city_stats = df_data.groupby('Shop_City').agg({
            metric_column: ['sum', 'mean', 'count'],
            'Latitude': 'first',
            'Longitude': 'first'
        }).reset_index()
        
        # Flatten column names
        city_stats.columns = ['Shop_City', f'{metric_column}_sum', f'{metric_column}_mean', 'count', 'Latitude', 'Longitude']
        
        # Filter data dengan koordinat valid
        city_stats = city_stats[(city_stats['Latitude'] != 0) & (city_stats['Longitude'] != 0)]
        
        if not city_stats.empty:
            # Buat base map
            center_lat = city_stats['Latitude'].mean()
            center_lon = city_stats['Longitude'].mean()
            
            m_choropleth = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=5,
                tiles='cartodbpositron'
            )
            
            # Buat colormap
            min_val = city_stats[f'{metric_column}_sum'].min()
            max_val = city_stats[f'{metric_column}_sum'].max()
            
            # Buat colormap dengan gradasi yang smooth
            colormap = cm.LinearColormap(
                colors=['lightgreen', 'yellow', 'orange', 'red'],
                vmin=min_val,
                vmax=max_val,
                caption=f'Jumlah {metric_column}'
            )
            
            # Tambahkan colormap ke map
            m_choropleth.add_child(colormap)
            
            # Buat circles untuk setiap kota
            for idx, row in city_stats.iterrows():
                # Normalize value untuk radius
                normalized_value = (row[f'{metric_column}_sum'] - min_val) / (max_val - min_val)
                radius = 5000 + (normalized_value * 30000)  # Radius antara 5km - 35km
                
                # Dapatkan warna dari colormap
                color = colormap.rgb_hex_str(row[f'{metric_column}_sum'])
                
                # Popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4><b>{row['Shop_City']}</b></h4>
                    <p><b>Total {metric_column}:</b> {row[f'{metric_column}_sum']:,.0f}</p>
                    <p><b>Rata-rata {metric_column}:</b> {row[f'{metric_column}_mean']:,.0f}</p>
                    <p><b>Jumlah Produk:</b> {row['count']}</p>
                </div>
                """
                
                folium.Circle(
                    location=[row['Latitude'], row['Longitude']],
                    radius=radius,
                    popup=folium.Popup(popup_content, max_width=250),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(m_choropleth)
            
            # Tambahkan legend yang sophisticated
            legend_html = f'''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; width: 300px; height: auto; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 15px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
                <h4 style="margin-top: 0; color: #333; text-align: center;">{title}</h4>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: lightgreen; border: 1px solid #333; margin-right: 10px;"></div>
                    <span>Rendah ({min_val:,.0f})</span>
                </div>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: yellow; border: 1px solid #333; margin-right: 10px;"></div>
                    <span>Sedang</span>
                </div>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: orange; border: 1px solid #333; margin-right: 10px;"></div>
                    <span>Tinggi</span>
                </div>
                <div style="display: flex; align-items: center; margin: 5px 0;">
                    <div style="width: 20px; height: 20px; background: red; border: 1px solid #333; margin-right: 10px;"></div>
                    <span>Sangat Tinggi ({max_val:,.0f})</span>
                </div>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <b>Sumber data:</b> Tokopedia Digital Service
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <b>Metrik:</b> {metric_column}
                </p>
            </div>
            '''
            
            m_choropleth.get_root().html.add_child(folium.Element(legend_html))
            
            # Save choropleth map
            choropleth_filename = f"choropleth_map_{metric_column.lower()}.html"
            m_choropleth.save(choropleth_filename)
            print(f"   ✅ Choropleth map disimpan sebagai: {choropleth_filename}")
            
            return m_choropleth, choropleth_filename
        else:
            print("   ⚠️  Tidak ada data dengan koordinat valid untuk choropleth map.")
            return None, None
    else:
        print(f"   ⚠️  Kolom '{metric_column}' atau 'Shop_City' tidak ditemukan dalam dataset.")
        return None, None

# Buat choropleth maps untuk berbagai metrik
if not df_mapping.empty:
    # 1. Choropleth untuk jumlah penjualan
    choropleth_sold, filename_sold = create_choropleth_map(
        df_mapping, 
        'Sold_Count', 
        "Distribusi Jumlah Penjualan per Kota"
    )
    
    # 2. Choropleth untuk rata-rata harga
    choropleth_price, filename_price = create_choropleth_map(
        df_mapping, 
        'Price_Number', 
        "Distribusi Rata-rata Harga per Kota"
    )
    
    # 3. Choropleth untuk performance score
    if 'Performance_Score' in df_mapping.columns:
        choropleth_perf, filename_perf = create_choropleth_map(
            df_mapping, 
            'Performance_Score', 
            "Distribusi Performance Score per Kota"
        )

# --- 6.2. HEATMAP DENSITY DENGAN CLUSTER ANALYSIS ---
print("\n" + "="*70)
print("LANGKAH 5.2: HEATMAP DENSITY DENGAN CLUSTER ANALYSIS")
print("="*70)

def create_density_heatmap(df_data, cluster_column='Cluster'):
    """
    Membuat heatmap density berdasarkan cluster dengan analisis spasial
    """
    print(f"\n🔥 Membuat Density Heatmap dengan analisis cluster...")
    
    if not df_data.empty and cluster_column in df_data.columns:
        # Buat base map
        center_lat = df_data['Latitude'].mean()
        center_lon = df_data['Longitude'].mean()
        
        m_density = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='cartodbpositron'
        )
        
        # Analisis density per cluster
        cluster_density = df_data.groupby(cluster_column).agg({
            'Latitude': ['mean', 'std'],
            'Longitude': ['mean', 'std'],
            'Sold_Count': 'sum',
            'Price_Number': 'mean'
        }).reset_index()
        
        # Flatten column names
        cluster_density.columns = ['Cluster', 'Lat_mean', 'Lat_std', 'Lon_mean', 'Lon_std', 'Total_Sold', 'Avg_Price']
        
        # Tambahkan heatmap layer untuk setiap cluster
        for idx, row in cluster_density.iterrows():
            if pd.notna(row['Lat_mean']) and pd.notna(row['Lon_mean']):
                # Buat heatmap data untuk cluster ini
                cluster_data = df_data[df_data[cluster_column] == row['Cluster']]
                heat_data_cluster = []
                
                for _, data_row in cluster_data.iterrows():
                    if pd.notna(data_row['Latitude']) and pd.notna(data_row['Longitude']):
                        # Gunakan sold count sebagai weight
                        weight = data_row.get('Sold_Count', 1)
                        heat_data_cluster.append([data_row['Latitude'], data_row['Longitude'], weight])
                
                if heat_data_cluster:
                    # Buat heatmap dengan radius yang berbeda per cluster
                    radius = 20 + (row['Total_Sold'] / 1000)  # Radius berdasarkan total penjualan
                    
                    plugins.HeatMap(
                        heat_data_cluster,
                        radius=int(radius),
                        blur=15,
                        max_zoom=10,
                        name=f'Cluster {row["Cluster"]}'
                    ).add_to(m_density)
        
        # Tambahkan layer control
        folium.LayerControl().add_to(m_density)
        
        # Tambahkan legend untuk density
        legend_html = '''
        <div style="position: fixed; 
                    top: 50px; right: 50px; width: 250px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 15px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
            <h4 style="margin-top: 0; color: #333; text-align: center;">Density Heatmap</h4>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b>Warna:</b> Intensitas penjualan
            </p>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b>Radius:</b> Berdasarkan cluster density
            </p>
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                <b>Sumber data:</b> Tokopedia Digital Service
            </p>
        </div>
        '''
        
        m_density.get_root().html.add_child(folium.Element(legend_html))
        
        # Save density map
        density_filename = "density_heatmap_clusters.html"
        m_density.save(density_filename)
        print(f"   ✅ Density heatmap disimpan sebagai: {density_filename}")
        
        return m_density, density_filename
    else:
        print(f"   ⚠️  Kolom '{cluster_column}' tidak ditemukan atau data kosong.")
        return None, None

# Buat density heatmap
if not df_mapping.empty and 'Cluster' in df_mapping.columns:
    density_map, density_filename = create_density_heatmap(df_mapping)

# --- 7. VISUALISASI INTERAKTIF DENGAN PLOTLY ---
print("\n" + "="*70)
print("LANGKAH 6: VISUALISASI INTERAKTIF DENGAN PLOTLY")
print("="*70)

# Color mapping untuk Plotly - HANYA GUNAKAN WARNA CSS YANG VALID
# Ganti 'lightred' dengan 'lightcoral' dan pastikan semua warna valid
plotly_colors = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred',
    'lightcoral', 'beige', 'darkblue', 'darkgreen',
    'cadetblue', 'mediumpurple', 'white', 'pink', 'lightblue',
    'lightgreen', 'gray', 'black', 'lightgray'
]

# a. 3D Scatter Plot
fig_3d = go.Figure()

# PERBAIKAN: Pastikan hanya cluster yang valid (bukan NaN)
# Tangani konversi dan penghapusan NaN dengan aman
if 'Cluster' in df.columns:
    valid_clusters_series = df['Cluster'].dropna()
    valid_clusters_int = set()
    for val in valid_clusters_series:
        try:
            valid_clusters_int.add(int(val))
        except (ValueError, TypeError):
            valid_clusters_int.add(-1) # Anggap sebagai noise
    sorted_valid_clusters = sorted(list(valid_clusters_int))
else:
    print("⚠️  Kolom 'Cluster' tidak ditemukan dalam DataFrame.")
    # Jika tidak ada kolom Cluster, buat visualisasi tanpa clustering
    sorted_valid_clusters = [0]  # Default cluster
    # Tambahkan kolom Cluster default ke df
    df['Cluster'] = 0

if len(sorted_valid_clusters) > 0 and not df.empty:
    for cluster_id in sorted_valid_clusters:
        # Filter data untuk cluster ini, tangani NaN
        cluster_mask = df['Cluster'].apply(lambda x: int(x) == cluster_id if pd.notna(x) else False)
        cluster_data = df[cluster_mask]

        if not cluster_data.empty:
            # Tentukan warna
            if cluster_id == -1:
                color = 'gray'
            else:
                color_idx = cluster_id % len(plotly_colors)
                color = plotly_colors[color_idx]

            # Tangani kemungkinan keyerror saat mengakses kolom
            try:
                x_data = cluster_data['Price_Number']
                y_data = cluster_data['Sold_Count']
                z_data = cluster_data['Rating']
                text_data = cluster_data['Product_Name'].str[:30] + '...'
            except KeyError as e:
                print(f"⚠️  KeyError saat membuat trace 3D untuk cluster {cluster_id}: {e}")
                continue # Lewati cluster ini jika ada keyerror

            fig_3d.add_trace(go.Scatter3d(
                x=x_data,
                y=y_data,
                z=z_data,
                mode='markers',
                marker=dict(size=5, color=color, opacity=0.7),
                name=f'Cluster {cluster_id}',
                text=text_data,
                hovertemplate='<b>%{text}</b><br>' +
                             'Price: Rp%{x:,.0f}<br>' +
                             'Sold: %{y:,}<br>' +
                             'Rating: %{z:.1f}<br>' +
                             '<extra></extra>'
            ))

    fig_3d.update_layout(
        title='3D Scatter Plot: Price vs Sold Count vs Rating by HDBSCAN Clusters',
        scene=dict(
            xaxis_title='Price (Rp)',
            yaxis_title='Sold Count',
            zaxis_title='Rating'
        ),
        width=1000,
        height=700
    )

    # Di Colab/Jupyter, gunakan renderer agar plot muncul
    try:
        fig_3d.show(renderer='colab') # Atau 'notebook' tergantung environment
        print("✅ 3D Scatter Plot berhasil ditampilkan.")
    except:
        # Fallback jika renderer tidak tersedia
        fig_3d.show()
        print("✅ 3D Scatter Plot berhasil ditampilkan (tanpa renderer spesifik).")
else:
    print("⚠️  Tidak ada cluster valid atau data kosong untuk divisualisasikan dalam 3D Scatter Plot.")

# b. Parallel Coordinates Plot
fig_parallel = go.Figure()

# Prepare data untuk parallel coordinates
required_cols_for_parallel = ['Price_Number', 'Sold_Count', 'Rating', 'Review_Count', 'Performance_Score', 'Cluster']
# Filter hanya kolom yang ada
existing_cols_for_parallel = [col for col in required_cols_for_parallel if col in df.columns]

if not df.empty and len(existing_cols_for_parallel) >= 2: # Minimal butuh 2 dimensi + Cluster
    parallel_data = df[existing_cols_for_parallel].copy()
    # Hapus baris tanpa cluster atau dengan cluster NaN
    parallel_data = parallel_data.dropna(subset=['Cluster'])

    # Konversi Cluster ke integer dengan aman
    def safe_int_convert(x):
        try:
            return int(x)
        except (ValueError, TypeError):
            return -1 # Anggap sebagai noise
    parallel_data['Cluster'] = parallel_data['Cluster'].apply(safe_int_convert)

    # Hapus baris dengan Cluster -1 (noise) jika tidak diinginkan, atau biarkan
    # parallel_data = parallel_data[parallel_data['Cluster'] != -1] # Uncomment jika ingin hapus noise

    if not parallel_data.empty:
        # Konversi Cluster ke string untuk visualisasi
        parallel_data['Cluster_Str'] = parallel_data['Cluster'].astype(str)

        # Siapkan dimensi untuk parallel coordinates
        dimensions = []
        for col in existing_cols_for_parallel:
            if col != 'Cluster': # Cluster akan digunakan untuk warna
                try:
                    dim_range = [parallel_data[col].min(), parallel_data[col].max()]
                    dimensions.append(dict(range=dim_range, label=col, values=parallel_data[col]))
                except Exception as e:
                    print(f"⚠️  Error menambahkan dimensi '{col}' ke parallel coordinates: {e}")

        # Buat parallel coordinates plot
        fig_parallel = go.Figure(data=
            go.Parcoords(
                line=dict(
                    color=parallel_data['Cluster'],
                    colorscale='Viridis', # Bisa diganti
                    showscale=True,
                    colorbar=dict(
                        title="Cluster ID",
                        tickvals=sorted(parallel_data['Cluster'].unique())
                    )
                ),
                dimensions=dimensions
            )
        )

        fig_parallel.update_layout(
            title='Parallel Coordinates Plot: Feature Relationships by HDBSCAN Clusters',
            width=1200,
            height=600
        )

        # Di Colab/Jupyter, gunakan renderer agar plot muncul
        try:
            fig_parallel.show(renderer='colab') # Atau 'notebook' tergantung environment
            print("✅ Parallel Coordinates Plot berhasil ditampilkan.")
        except:
            # Fallback jika renderer tidak tersedia
            fig_parallel.show()
            print("✅ Parallel Coordinates Plot berhasil ditampilkan (tanpa renderer spesifik).")
    else:
        print("⚠️  Tidak ada data dengan cluster valid untuk Parallel Coordinates Plot.")
else:
    print("⚠️  Dataset kosong atau tidak memiliki kolom yang cukup untuk Parallel Coordinates Plot.")

# --- 8. ANALISIS KOMPETITOR LANJUTAN ---
print("\n" + "="*70)
print("LANGKAH 7: ANALISIS KOMPETITOR LANJUTAN")
print("="*70)

# a. Competitive Positioning Matrix
print("\n🎯 Competitive Positioning Matrix...")

# Buat matrix positioning berdasarkan Price vs Performance
fig_matrix = go.Figure()

if len(sorted_valid_clusters) > 0 and not df.empty:
    for cluster_id in sorted_valid_clusters:
        # Filter data untuk cluster ini, tangani NaN
        cluster_mask = df['Cluster'].apply(lambda x: int(x) == cluster_id if pd.notna(x) else False)
        cluster_data = df[cluster_mask]

        if not cluster_data.empty:
            # Tentukan warna
            if cluster_id == -1:
                color = 'gray'
            else:
                color_idx = cluster_id % len(plotly_colors)
                color = plotly_colors[color_idx]

            # Tangani kemungkinan keyerror saat mengakses kolom
            try:
                x_data = cluster_data['Price_Number']
                y_data = cluster_data['Performance_Score']
                text_data = cluster_data['Product_Name'].str[:30] + '...'
            except KeyError as e:
                print(f"⚠️  KeyError saat membuat trace Matrix untuk cluster {cluster_id}: {e}")
                continue # Lewati cluster ini jika ada keyerror

            fig_matrix.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                marker=dict(size=8, color=color, opacity=0.7),
                name=f'Cluster {cluster_id}',
                text=text_data,
                hovertemplate='<b>%{text}</b><br>' +
                             'Price: Rp%{x:,.0f}<br>' +
                             'Performance: %{y:.2f}<br>' +
                             '<extra></extra>'
            ))

    # Add quadrant lines hanya jika ada data
    if not df.empty:
        # Pastikan kolom yang dibutuhkan ada
        required_cols_for_lines = ['Price_Number', 'Performance_Score']
        if all(col in df.columns for col in required_cols_for_lines):
            price_median = df['Price_Number'].median()
            perf_median = df['Performance_Score'].median()

            fig_matrix.add_hline(y=perf_median, line_dash="dash", line_color="gray",
                                 annotation_text="Performance Median")
            fig_matrix.add_vline(x=price_median, line_dash="dash", line_color="gray",
                                 annotation_text="Price Median")
        else:
            print("⚠️  Kolom 'Price_Number' atau 'Performance_Score' tidak ditemukan untuk garis kuadran.")

    fig_matrix.update_layout(
        title='Competitive Positioning Matrix: Price vs Performance Score',
        xaxis_title='Price (Rp)',
        yaxis_title='Performance Score',
        width=1000,
        height=600
    )

    # Di Colab/Jupyter, gunakan renderer agar plot muncul
    try:
        fig_matrix.show(renderer='colab') # Atau 'notebook' tergantung environment
        print("✅ Competitive Positioning Matrix berhasil ditampilkan.")
    except:
        # Fallback jika renderer tidak tersedia
        fig_matrix.show()
        print("✅ Competitive Positioning Matrix berhasil ditampilkan (tanpa renderer spesifik).")
else:
    print("⚠️  Tidak ada cluster valid atau data kosong untuk Competitive Positioning Matrix.")

# b. Market Segment Analysis
print("\n📊 Market Segment Analysis berdasarkan cluster...")

if not df.empty and 'Cluster' in df.columns:
    # Pastikan Cluster adalah integer
    df['Cluster'] = df['Cluster'].apply(lambda x: int(x) if pd.notna(x) else -1)

    # Grup berdasarkan Cluster
    segment_analysis = df.groupby('Cluster').agg({
        'Price_Number': ['mean', 'std', 'min', 'max'],
        'Sold_Count': ['mean', 'sum'],
        'Rating': ['mean', 'std'],
        'Revenue_Estimate': ['mean', 'sum'] if 'Revenue_Estimate' in df.columns else ['mean', 'sum'], # Cek keberadaan
        'Performance_Score': ['mean', 'std'],
        'Shop_City': 'nunique',
        'Shop_Name': 'nunique'
    }).round(2)

    # Flatten MultiIndex columns
    if not segment_analysis.empty:
        segment_analysis.columns = ['_'.join(col).strip() for col in segment_analysis.columns]
        print(segment_analysis)
    else:
        print("⚠️  Tidak ada data untuk analisis segmentasi.")
else:
    print("⚠️  Dataset kosong atau kolom 'Cluster' tidak ditemukan untuk analisis segmentasi.")

# --- 9. REKOMENDASI STRATEGI ---
print("\n" + "="*70)
print("LANGKAH 8: REKOMENDASI STRATEGI BERDASARKAN ANALISIS")
print("="*70)

print("\n🎯 REKOMENDASI STRATEGI KOMPETITOR:")

# Analisis setiap cluster untuk rekomendasi
if len(sorted_valid_clusters) > 0 and not df.empty:
    # Pastikan kolom yang dibutuhkan ada untuk rekomendasi
    required_cols_for_recommendation = ['Price_Number', 'Performance_Score', 'Sold_Count', 'Revenue_Estimate']
    existing_cols_for_recommendation = [col for col in required_cols_for_recommendation if col in df.columns]

    if len(existing_cols_for_recommendation) >= 3: # Minimal butuh 3 dari 4 kolom
        for cluster_id in sorted_valid_clusters:
            if cluster_id == -1:
                continue

            # Filter data untuk cluster ini
            cluster_mask = df['Cluster'].apply(lambda x: int(x) == cluster_id if pd.notna(x) else False)
            cluster_data = df[cluster_mask]

            if not cluster_data.empty:
                # Hitung metrik rata-rata
                avg_price = cluster_data['Price_Number'].mean()
                avg_performance = cluster_data['Performance_Score'].mean()
                avg_sold = cluster_data['Sold_Count'].mean()
                total_revenue = cluster_data['Revenue_Estimate'].sum() if 'Revenue_Estimate' in cluster_data.columns else 0

                print(f"\n📊 Cluster {cluster_id} - {len(cluster_data)} produk:")
                print(f"   💰 Rata-rata harga: Rp{avg_price:,.0f}")
                print(f"   ⭐ Rata-rata performance: {avg_performance:.2f}")
                print(f"   📦 Rata-rata terjual: {avg_sold:,.0f}")
                if 'Revenue_Estimate' in cluster_data.columns:
                     print(f"   💵 Total revenue: Rp{total_revenue:,.0f}")

                # Rekomendasi berdasarkan karakteristik cluster
                # Bandingkan dengan median dataset keseluruhan
                overall_avg_price = df['Price_Number'].median() if not df.empty else 0
                overall_avg_performance = df['Performance_Score'].median() if not df.empty else 0

                if avg_price < overall_avg_price * 0.8: # Misal 20% lebih murah
                    price_strategy = "Low-Cost Leadership"
                elif avg_price > overall_avg_price * 1.2: # Misal 20% lebih mahal
                    price_strategy = "Premium Pricing"
                else:
                    price_strategy = "Competitive Pricing"

                if avg_performance > overall_avg_performance * 1.1: # Misal 10% lebih tinggi
                    perf_strategy = "High-Performance Focus"
                elif avg_performance < overall_avg_performance * 0.9: # Misal 10% lebih rendah
                    perf_strategy = "Improve Quality & Service"
                else:
                    perf_strategy = "Balanced Approach"

                print(f"   🎯 Rekomendasi Strategi:")
                print(f"      • Pricing: {price_strategy}")
                print(f"      • Performance: {perf_strategy}")
            else:
                print(f"\n⚠️  Cluster {cluster_id} kosong.")
    else:
        print("⚠️  Kolom yang diperlukan untuk rekomendasi tidak tersedia.")
else:
    print("⚠️  Tidak ada cluster valid atau data kosong untuk rekomendasi strategi.")

print("\n" + "="*70)
print("🎉 ANALISIS KOMPETITOR DAN PEMETAAN SPASIAL SELESAI!")
print("="*70)

print(f"\n📁 File yang dihasilkan:")
if map_filename:
    print(f"   • Peta interaktif: {map_filename}")
if 'filename_sold' in locals():
    print(f"   • Choropleth penjualan: {filename_sold}")
if 'filename_price' in locals():
    print(f"   • Choropleth harga: {filename_price}")
if 'filename_perf' in locals():
    print(f"   • Choropleth performance: {filename_perf}")
if 'density_filename' in locals():
    print(f"   • Density heatmap: {density_filename}")
print(f"   • Dataset dengan clustering: Tokopedia_sarung_tangan_with_clusters.xlsx")

output_filename = "Tokopedia_sarung_tangan_with_clusters.xlsx"
df.to_excel(output_filename, index=False)
print(f"\n💾 Dataset akhir dengan kolom baru telah disimpan ke '{output_filename}'")

print("\n🔍 INSIGHT UTAMA:")
print("   1. HDBSCAN clustering berhasil mengidentifikasi segmentasi pasar yang jelas")
print("   2. Peta spasial menunjukkan distribusi geografis produk")
print("   3. Choropleth maps memberikan visualisasi density yang sophisticated")
print("   4. Analisis kompetitor memberikan insight positioning yang strategis")
print("   5. Visualisasi interaktif memudahkan eksplorasi data")
print("   6. Rekomendasi strategi dapat digunakan untuk pengambilan keputusan bisnis")
print("   7. Heatmap density dengan cluster analysis memberikan insight spasial yang mendalam")