# --- IMPORT LIBRARY UNTUK ANALISIS KOMPETITOR DAN PEMETAAN SPASIAL ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium import plugins
import warnings
warnings.filterwarnings("ignore")

# --- LIBRARY UNTUK CLUSTERING HDBSCAN (MODEL TERBARU) ---
import hdbscan
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import umap

# --- LIBRARY UNTUK ANALISIS KOMPETITOR ---
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import networkx as nx

# --- LIBRARY UNTUK VISUALISASI INTERAKTIF ---
import plotly.offline as pyo
pyo.init_notebook_mode(connected=True)

print("🚀 MEMULAI ANALISIS KOMPETITOR DAN PEMETAAN SPASIAL")
print("="*70)

# --- 1. LOAD DATA YANG SUDAH DIPROSES ---
print("\n📁 Loading data yang sudah diproses...")
try:
    # Coba load data yang sudah diproses
    df = pd.read_excel("Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx")
    print(f"✅ Data berhasil dimuat dari file yang sudah diproses. Dimensi: {df.shape}")
except FileNotFoundError:
    print("⚠️ File yang sudah diproses tidak ditemukan. Menggunakan data original...")
    # Fallback ke data original
    df = pd.read_excel('Tokopedia_sarung tangan.xlsx', sheet_name='Products Min1000 Sold')
    print(f"✅ Data original berhasil dimuat. Dimensi: {df.shape}")

# --- 2. PREPARASI DATA UNTUK ANALISIS ---
print("\n" + "="*70)
print("LANGKAH 1: PREPARASI DATA UNTUK ANALISIS KOMPETITOR")
print("="*70)

# a. Pastikan kolom numerik sudah bersih
numeric_cols = ['Price_Number', 'Sold_Count', 'Rating', 'Review_Count']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Isi missing values dengan median
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"   ✅ Kolom '{col}' dibersihkan dan missing values diisi dengan median: {median_val:.2f}")

# b. Buat feature engineering tambahan untuk analisis kompetitor
print("\n🔧 Membuat feature engineering tambahan untuk analisis kompetitor...")

# 1. Price per Unit (asumsi 1 unit = 1 pasang)
df['Price_Per_Unit'] = df['Price_Number']

# 2. Revenue Estimate (Price * Sold_Count)
df['Revenue_Estimate'] = df['Price_Number'] * df['Sold_Count']

# 3. Rating Score (normalized 0-100)
df['Rating_Score'] = df['Rating'] * 20  # Convert 0-5 to 0-100

# 4. Popularity Score (combination of sold count and review count)
df['Popularity_Score'] = (df['Sold_Count'] * 0.7 + df['Review_Count'] * 0.3)

# 5. Price Category
df['Price_Category'] = pd.cut(df['Price_Number'], 
                             bins=[0, 50000, 100000, 200000, 500000, float('inf')],
                             labels=['Sangat Murah', 'Murah', 'Sedang', 'Mahal', 'Sangat Mahal'])

# 6. Performance Score (composite metric)
df['Performance_Score'] = (df['Rating_Score'] * 0.4 + 
                          df['Popularity_Score'] * 0.3 + 
                          (1 / (1 + df['Price_Number']/100000)) * 0.3)  # Lower price = higher score

print("   ✅ Feature engineering tambahan selesai dibuat.")

# --- 3. ANALISIS KOMPETITOR DENGAN HDBSCAN CLUSTERING ---
print("\n" + "="*70)
print("LANGKAH 2: ANALISIS KOMPETITOR DENGAN HDBSCAN CLUSTERING")
print("="*70)

# a. Prepare data untuk clustering
print("\n🔍 Menyiapkan data untuk HDBSCAN clustering...")

# Pilih features untuk clustering
clustering_features = ['Price_Number', 'Sold_Count', 'Rating', 'Review_Count', 
                      'Revenue_Estimate', 'Rating_Score', 'Popularity_Score', 'Performance_Score']

# Filter data yang valid
df_clustering = df[clustering_features].dropna()
print(f"   Data untuk clustering: {df_clustering.shape}")

# b. Normalisasi data
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_clustering)
df_scaled = pd.DataFrame(df_scaled, columns=clustering_features, index=df_clustering.index)

# c. Dimensionality Reduction dengan UMAP (lebih modern dari PCA)
print("\n🔬 Melakukan dimensionality reduction dengan UMAP...")
umap_reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
df_umap = umap_reducer.fit_transform(df_scaled)

# d. HDBSCAN Clustering
print("\n🎯 Melakukan HDBSCAN clustering...")
hdbscan_clusterer = hdbscan.HDBSCAN(
    min_cluster_size=5,           # Minimal 5 produk per cluster
    min_samples=3,                # Minimal 3 sampel untuk core point
    cluster_selection_epsilon=0.1, # Epsilon untuk cluster selection
    cluster_selection_method='eom' # Excess of Mass method
)

cluster_labels = hdbscan_clusterer.fit_predict(df_scaled)

# e. Analisis hasil clustering
n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
n_noise = list(cluster_labels).count(-1)

print(f"\n📊 Hasil HDBSCAN Clustering:")
print(f"   Jumlah cluster: {n_clusters}")
print(f"   Jumlah noise points: {n_noise}")
print(f"   Persentase noise: {n_noise/len(cluster_labels)*100:.2f}%")

# f. Tambahkan cluster labels ke dataframe
df.loc[df_clustering.index, 'Cluster'] = cluster_labels

# g. Analisis karakteristik setiap cluster
print("\n📈 Analisis karakteristik setiap cluster:")
cluster_analysis = df[df['Cluster'].notna()].groupby('Cluster').agg({
    'Price_Number': ['mean', 'std', 'count'],
    'Sold_Count': ['mean', 'std'],
    'Rating': ['mean', 'std'],
    'Revenue_Estimate': ['mean', 'std'],
    'Performance_Score': ['mean', 'std']
}).round(2)

print(cluster_analysis)

# --- 4. VISUALISASI CLUSTERING ---
print("\n" + "="*70)
print("LANGKAH 3: VISUALISASI CLUSTERING HDBSCAN")
print("="*70)

# a. UMAP + HDBSCAN Visualization
plt.figure(figsize=(15, 10))

# Subplot 1: UMAP dengan HDBSCAN clusters
plt.subplot(2, 3, 1)
scatter = plt.scatter(df_umap[:, 0], df_umap[:, 1], c=cluster_labels, cmap='viridis', alpha=0.7)
plt.title('HDBSCAN Clustering pada UMAP\nReduced Features', fontsize=12)
plt.xlabel('UMAP Component 1')
plt.ylabel('UMAP Component 2')
plt.colorbar(scatter, label='Cluster')

# Subplot 2: Price vs Sold Count dengan clusters
plt.subplot(2, 3, 2)
df_clustered = df[df['Cluster'].notna()]
scatter = plt.scatter(df_clustered['Price_Number'], df_clustered['Sold_Count'], 
                     c=df_clustered['Cluster'], cmap='viridis', alpha=0.7)
plt.title('Price vs Sold Count\nby HDBSCAN Clusters', fontsize=12)
plt.xlabel('Price (Rp)')
plt.ylabel('Sold Count')
plt.colorbar(scatter, label='Cluster')

# Subplot 3: Rating vs Performance Score
plt.subplot(2, 3, 3)
scatter = plt.scatter(df_clustered['Rating'], df_clustered['Performance_Score'], 
                     c=df_clustered['Cluster'], cmap='viridis', alpha=0.7)
plt.title('Rating vs Performance Score\nby HDBSCAN Clusters', fontsize=12)
plt.xlabel('Rating')
plt.ylabel('Performance Score')
plt.colorbar(scatter, label='Cluster')

# Subplot 4: Cluster size distribution
plt.subplot(2, 3, 4)
cluster_sizes = df_clustered['Cluster'].value_counts().sort_index()
bars = plt.bar(range(len(cluster_sizes)), cluster_sizes.values, color='skyblue')
plt.title('Cluster Size Distribution', fontsize=12)
plt.xlabel('Cluster ID')
plt.ylabel('Number of Products')
# Add value labels on bars
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{int(height)}', ha='center', va='bottom')

# Subplot 5: Average metrics by cluster
plt.subplot(2, 3, 5)
cluster_metrics = df_clustered.groupby('Cluster')[['Price_Number', 'Sold_Count', 'Rating']].mean()
x = np.arange(len(cluster_metrics))
width = 0.25

plt.bar(x - width, cluster_metrics['Price_Number']/1000, width, label='Avg Price (K)', alpha=0.8)
plt.bar(x, cluster_metrics['Sold_Count']/100, width, label='Avg Sold (x100)', alpha=0.8)
plt.bar(x + width, cluster_metrics['Rating']*10, width, label='Avg Rating (x10)', alpha=0.8)

plt.title('Average Metrics by Cluster', fontsize=12)
plt.xlabel('Cluster ID')
plt.ylabel('Normalized Values')
plt.legend()
plt.xticks(x, cluster_metrics.index)

# Subplot 6: Revenue distribution by cluster
plt.subplot(2, 3, 6)
df_clustered.boxplot(column='Revenue_Estimate', by='Cluster', ax=plt.gca())
plt.title('Revenue Distribution by Cluster', fontsize=12)
plt.suptitle('')  # Remove default suptitle
plt.xlabel('Cluster ID')
plt.ylabel('Revenue Estimate (Rp)')

plt.tight_layout()
plt.show()

# --- 5. ANALISIS KOMPETITOR DETAIL ---
print("\n" + "="*70)
print("LANGKAH 4: ANALISIS KOMPETITOR DETAIL")
print("="*70)

# a. Identifikasi Top Competitors berdasarkan cluster
print("\n🏆 Analisis Top Competitors berdasarkan cluster...")

for cluster_id in sorted(df_clustered['Cluster'].unique()):
    if cluster_id == -1:  # Skip noise points
        continue
        
    cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
    
    print(f"\n📊 Cluster {cluster_id} - {len(cluster_data)} produk:")
    
    # Top 5 berdasarkan Performance Score
    top_performers = cluster_data.nlargest(5, 'Performance_Score')
    print(f"   🥇 Top 5 Performers:")
    for idx, row in top_performers.iterrows():
        print(f"      • {row['Product_Name'][:50]}... | Score: {row['Performance_Score']:.2f} | "
              f"Price: Rp{row['Price_Number']:,.0f} | Sold: {row['Sold_Count']:,}")

# b. Market Share Analysis
print("\n📈 Analisis Market Share berdasarkan cluster...")
cluster_market_share = df_clustered.groupby('Cluster').agg({
    'Revenue_Estimate': 'sum',
    'Sold_Count': 'sum',
    'Product_ID': 'count'
}).rename(columns={'Product_ID': 'Product_Count'})

cluster_market_share['Revenue_Share'] = cluster_market_share['Revenue_Estimate'] / cluster_market_share['Revenue_Estimate'].sum() * 100
cluster_market_share['Volume_Share'] = cluster_market_share['Sold_Count'] / cluster_market_share['Sold_Count'].sum() * 100

print(cluster_market_share.round(2))

# --- 6. PEMETAAN SPASIAL DENGAN FOLIUM ---
print("\n" + "="*70)
print("LANGKAH 5: PEMETAAN SPASIAL DISTRIBUSI HARGA")
print("="*70)

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
    'Manado': [1.4748, 124.8421]
}

# Assign coordinates berdasarkan Shop_City
df_mapping = df_clustered.copy()
df_mapping['Latitude'] = df_mapping['Shop_City'].map(lambda x: city_coordinates.get(x, [0, 0])[0])
df_mapping['Longitude'] = df_mapping['Shop_City'].map(lambda x: city_coordinates.get(x, [0, 0])[1])

# Filter data dengan koordinat valid
df_mapping = df_mapping[(df_mapping['Latitude'] != 0) | (df_mapping['Longitude'] != 0)]

print(f"   Data untuk mapping: {df_mapping.shape}")

# b. Buat peta interaktif
print("\n🌍 Membuat peta interaktif...")

# Buat base map
m = folium.Map(
    location=[df_mapping['Latitude'].mean(), df_mapping['Longitude'].mean()],
    zoom_start=5,
    tiles='OpenStreetMap'
)

# Color mapping untuk cluster
colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 
          'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 
          'lightgreen', 'gray', 'black', 'lightgray']

# Add markers untuk setiap produk
for idx, row in df_mapping.iterrows():
    cluster_id = int(row['Cluster'])
    color = colors[cluster_id % len(colors)] if cluster_id != -1 else 'gray'
    
    # Popup content
    popup_content = f"""
    <b>{row['Product_Name'][:50]}...</b><br>
    <b>Shop:</b> {row['Shop_Name']}<br>
    <b>City:</b> {row['Shop_City']}<br>
    <b>Price:</b> Rp{row['Price_Number']:,.0f}<br>
    <b>Sold:</b> {row['Sold_Count']:,}<br>
    <b>Rating:</b> {row['Rating']:.1f}<br>
    <b>Cluster:</b> {cluster_id}<br>
    <b>Performance Score:</b> {row['Performance_Score']:.2f}
    """
    
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_content, max_width=300),
        icon=folium.Icon(color=color, icon='info-sign'),
        tooltip=f"Cluster {cluster_id}: {row['Product_Name'][:30]}..."
    ).add_to(m)

# Add cluster legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 200px; height: 200px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 10px">
            <p><b>Cluster Legend</b></p>
'''
for i in range(n_clusters):
    color = colors[i % len(colors)]
    legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> Cluster {i}</p>'

legend_html += '''
            <p><i class="fa fa-circle" style="color:gray"></i> Noise</p>
            </div>
            '''
m.get_root().html.add_child(folium.Element(legend_html))

# Add heatmap layer untuk density
heat_data = [[row['Latitude'], row['Longitude'], row['Price_Number']] 
             for idx, row in df_mapping.iterrows()]

plugins.HeatMap(heat_data, radius=15).add_to(m)

# Save map
map_filename = "peta_distribusi_harga_sarung_tangan.html"
m.save(map_filename)
print(f"   ✅ Peta interaktif disimpan sebagai: {map_filename}")

# --- 7. VISUALISASI INTERAKTIF DENGAN PLOTLY ---
print("\n" + "="*70)
print("LANGKAH 6: VISUALISASI INTERAKTIF DENGAN PLOTLY")
print("="*70)

# a. 3D Scatter Plot
fig_3d = go.Figure()

for cluster_id in sorted(df_clustered['Cluster'].unique()):
    cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
    color = colors[cluster_id % len(colors)] if cluster_id != -1 else 'gray'
    
    fig_3d.add_trace(go.Scatter3d(
        x=cluster_data['Price_Number'],
        y=cluster_data['Sold_Count'],
        z=cluster_data['Rating'],
        mode='markers',
        marker=dict(size=5, color=color, opacity=0.7),
        name=f'Cluster {cluster_id}',
        text=cluster_data['Product_Name'].str[:30] + '...',
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

fig_3d.show()

# b. Parallel Coordinates Plot
fig_parallel = go.Figure()

# Prepare data untuk parallel coordinates
parallel_data = df_clustered[['Price_Number', 'Sold_Count', 'Rating', 'Review_Count', 'Performance_Score', 'Cluster']].copy()
parallel_data['Cluster'] = parallel_data['Cluster'].astype(str)

fig_parallel = go.Figure(data=
    go.Parcoords(
        line=dict(
            color=parallel_data['Cluster'].astype(int),
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Cluster")
        ),
        dimensions=[
            dict(range=[parallel_data['Price_Number'].min(), parallel_data['Price_Number'].max()],
                 label='Price', values=parallel_data['Price_Number']),
            dict(range=[parallel_data['Sold_Count'].min(), parallel_data['Sold_Count'].max()],
                 label='Sold Count', values=parallel_data['Sold_Count']),
            dict(range=[parallel_data['Rating'].min(), parallel_data['Rating'].max()],
                 label='Rating', values=parallel_data['Rating']),
            dict(range=[parallel_data['Review_Count'].min(), parallel_data['Review_Count'].max()],
                 label='Review Count', values=parallel_data['Review_Count']),
            dict(range=[parallel_data['Performance_Score'].min(), parallel_data['Performance_Score'].max()],
                 label='Performance Score', values=parallel_data['Performance_Score'])
        ]
    )
)

fig_parallel.update_layout(
    title='Parallel Coordinates Plot: Feature Relationships by HDBSCAN Clusters',
    width=1200,
    height=600
)

fig_parallel.show()

# --- 8. ANALISIS KOMPETITOR LANJUTAN ---
print("\n" + "="*70)
print("LANGKAH 7: ANALISIS KOMPETITOR LANJUTAN")
print("="*70)

# a. Competitive Positioning Matrix
print("\n🎯 Competitive Positioning Matrix...")

# Buat matrix positioning berdasarkan Price vs Performance
fig_matrix = go.Figure()

for cluster_id in sorted(df_clustered['Cluster'].unique()):
    cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
    color = colors[cluster_id % len(colors)] if cluster_id != -1 else 'gray'
    
    fig_matrix.add_trace(go.Scatter(
        x=cluster_data['Price_Number'],
        y=cluster_data['Performance_Score'],
        mode='markers',
        marker=dict(size=8, color=color, opacity=0.7),
        name=f'Cluster {cluster_id}',
        text=cluster_data['Product_Name'].str[:30] + '...',
        hovertemplate='<b>%{text}</b><br>' +
                     'Price: Rp%{x:,.0f}<br>' +
                     'Performance: %{y:.2f}<br>' +
                     '<extra></extra>'
    ))

# Add quadrant lines
price_median = df_clustered['Price_Number'].median()
perf_median = df_clustered['Performance_Score'].median()

fig_matrix.add_hline(y=perf_median, line_dash="dash", line_color="gray", 
                     annotation_text="Performance Median")
fig_matrix.add_vline(x=price_median, line_dash="dash", line_color="gray", 
                     annotation_text="Price Median")

fig_matrix.update_layout(
    title='Competitive Positioning Matrix: Price vs Performance Score',
    xaxis_title='Price (Rp)',
    yaxis_title='Performance Score',
    width=1000,
    height=600
)

fig_matrix.show()

# b. Market Segment Analysis
print("\n📊 Market Segment Analysis berdasarkan cluster...")

segment_analysis = df_clustered.groupby('Cluster').agg({
    'Price_Number': ['mean', 'std', 'min', 'max'],
    'Sold_Count': ['mean', 'sum'],
    'Rating': ['mean', 'std'],
    'Revenue_Estimate': ['mean', 'sum'],
    'Performance_Score': ['mean', 'std'],
    'Shop_City': 'nunique',
    'Shop_Name': 'nunique'
}).round(2)

segment_analysis.columns = ['_'.join(col).strip() for col in segment_analysis.columns]
print(segment_analysis)

# --- 9. REKOMENDASI STRATEGI ---
print("\n" + "="*70)
print("LANGKAH 8: REKOMENDASI STRATEGI BERDASARKAN ANALISIS")
print("="*70)

print("\n🎯 REKOMENDASI STRATEGI KOMPETITOR:")

# Analisis setiap cluster untuk rekomendasi
for cluster_id in sorted(df_clustered['Cluster'].unique()):
    if cluster_id == -1:
        continue
        
    cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
    
    avg_price = cluster_data['Price_Number'].mean()
    avg_performance = cluster_data['Performance_Score'].mean()
    avg_sold = cluster_data['Sold_Count'].mean()
    total_revenue = cluster_data['Revenue_Estimate'].sum()
    
    print(f"\n📊 Cluster {cluster_id} - {len(cluster_data)} produk:")
    print(f"   💰 Rata-rata harga: Rp{avg_price:,.0f}")
    print(f"   ⭐ Rata-rata performance: {avg_performance:.2f}")
    print(f"   📦 Rata-rata terjual: {avg_sold:,.0f}")
    print(f"   💵 Total revenue: Rp{total_revenue:,.0f}")
    
    # Rekomendasi berdasarkan karakteristik cluster
    if avg_price < df_clustered['Price_Number'].quantile(0.25):
        price_strategy = "Low-Cost Leadership"
    elif avg_price > df_clustered['Price_Number'].quantile(0.75):
        price_strategy = "Premium Pricing"
    else:
        price_strategy = "Competitive Pricing"
    
    if avg_performance > df_clustered['Performance_Score'].quantile(0.75):
        perf_strategy = "High-Performance Focus"
    elif avg_performance < df_clustered['Performance_Score'].quantile(0.25):
        perf_strategy = "Improve Quality & Service"
    else:
        perf_strategy = "Balanced Approach"
    
    print(f"   🎯 Rekomendasi Strategi:")
    print(f"      • Pricing: {price_strategy}")
    print(f"      • Performance: {perf_strategy}")

print("\n" + "="*70)
print("🎉 ANALISIS KOMPETITOR DAN PEMETAAN SPASIAL SELESAI!")
print("="*70)

print(f"\n📁 File yang dihasilkan:")
print(f"   • Peta interaktif: {map_filename}")
print(f"   • Dataset dengan clustering: Tokopedia_sarung_tangan_with_clusters.xlsx")

# Save final dataset dengan clustering
df_clustered.to_excel("Tokopedia_sarung_tangan_with_clusters.xlsx", index=False)
print(f"\n💾 Dataset dengan hasil clustering telah disimpan!")

print("\n🔍 INSIGHT UTAMA:")
print("   1. HDBSCAN clustering berhasil mengidentifikasi segmentasi pasar yang jelas")
print("   2. Peta spasial menunjukkan distribusi geografis produk")
print("   3. Analisis kompetitor memberikan insight positioning yang strategis")
print("   4. Visualisasi interaktif memudahkan eksplorasi data")
print("   5. Rekomendasi strategi dapat digunakan untuk pengambilan keputusan bisnis")