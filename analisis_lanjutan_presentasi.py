# --- ANALISIS LANJUTAN UNTUK PRESENTASI GEMASTIK ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# Set style untuk visualisasi yang menarik
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("🎯 ANALISIS LANJUTAN UNTUK PRESENTASI GEMASTIK")
print("="*70)

# --- 1. LOAD DATA DENGAN CLUSTERING ---
print("\n📁 Loading data dengan hasil clustering...")
try:
    df = pd.read_excel("Tokopedia_sarung_tangan_with_clusters.xlsx")
    print(f"✅ Data dengan clustering berhasil dimuat. Dimensi: {df.shape}")
except FileNotFoundError:
    print("⚠️ File dengan clustering tidak ditemukan. Jalankan analisis_kompetitor_pemetaan_spasial.py terlebih dahulu.")
    exit()

# --- 2. ANALISIS TREND DAN INSIGHT UTAMA ---
print("\n" + "="*70)
print("LANGKAH 1: ANALISIS TREND DAN INSIGHT UTAMA")
print("="*70)

# a. Statistik umum dataset
print("\n📊 STATISTIK UMUM DATASET:")
print(f"   Total produk: {len(df):,}")
print(f"   Total toko: {df['Shop_Name'].nunique():,}")
print(f"   Total kota: {df['Shop_City'].nunique():,}")
print(f"   Range harga: Rp{df['Price_Number'].min():,.0f} - Rp{df['Price_Number'].max():,.0f}")
print(f"   Rata-rata rating: {df['Rating'].mean():.2f}")
print(f"   Total terjual: {df['Sold_Count'].sum():,}")

# b. Analisis cluster
print(f"\n🎯 ANALISIS CLUSTER:")
cluster_stats = df.groupby('Cluster').agg({
    'Product_ID': 'count',
    'Price_Number': ['mean', 'std'],
    'Sold_Count': ['mean', 'sum'],
    'Rating': 'mean',
    'Revenue_Estimate': 'sum'
}).round(2)

cluster_stats.columns = ['_'.join(col).strip() for col in cluster_stats.columns]
print(cluster_stats)

# --- 3. VISUALISASI UNTUK PRESENTASI ---
print("\n" + "="*70)
print("LANGKAH 2: VISUALISASI UNTUK PRESENTASI")
print("="*70)

# a. Dashboard Overview
fig_dashboard = make_subplots(
    rows=2, cols=3,
    subplot_titles=('Distribusi Harga', 'Distribusi Rating', 'Top 10 Kota',
                   'Cluster Distribution', 'Price vs Performance', 'Revenue by Cluster'),
    specs=[[{"type": "histogram"}, {"type": "histogram"}, {"type": "bar"}],
           [{"type": "pie"}, {"type": "scatter"}, {"type": "bar"}]]
)

# 1. Distribusi Harga
fig_dashboard.add_trace(
    go.Histogram(x=df['Price_Number'], nbinsx=30, name='Harga'),
    row=1, col=1
)

# 2. Distribusi Rating
fig_dashboard.add_trace(
    go.Histogram(x=df['Rating'], nbinsx=20, name='Rating'),
    row=1, col=2
)

# 3. Top 10 Kota
top_cities = df['Shop_City'].value_counts().head(10)
fig_dashboard.add_trace(
    go.Bar(x=top_cities.index, y=top_cities.values, name='Kota'),
    row=1, col=3
)

# 4. Cluster Distribution
cluster_counts = df['Cluster'].value_counts().sort_index()
fig_dashboard.add_trace(
    go.Pie(labels=[f'Cluster {i}' for i in cluster_counts.index], 
           values=cluster_counts.values, name='Cluster'),
    row=2, col=1
)

# 5. Price vs Performance
fig_dashboard.add_trace(
    go.Scatter(x=df['Price_Number'], y=df['Performance_Score'], 
               mode='markers', marker=dict(color=df['Cluster'], colorscale='viridis'),
               name='Price vs Performance'),
    row=2, col=2
)

# 6. Revenue by Cluster
revenue_by_cluster = df.groupby('Cluster')['Revenue_Estimate'].sum().sort_values(ascending=False)
fig_dashboard.add_trace(
    go.Bar(x=[f'Cluster {i}' for i in revenue_by_cluster.index], 
           y=revenue_by_cluster.values, name='Revenue'),
    row=2, col=3
)

fig_dashboard.update_layout(
    title_text="Dashboard Analisis Tokopedia Sarung Tangan",
    height=800,
    showlegend=False
)

fig_dashboard.show()

# b. Competitive Analysis Matrix
print("\n🎯 Membuat Competitive Analysis Matrix...")

# Buat matrix 4 kuadran
fig_matrix = go.Figure()

# Scatter plot dengan 4 kuadran
fig_matrix.add_trace(go.Scatter(
    x=df['Price_Number'],
    y=df['Performance_Score'],
    mode='markers',
    marker=dict(
        size=8,
        color=df['Cluster'],
        colorscale='viridis',
        opacity=0.7
    ),
    text=df['Product_Name'].str[:30] + '...',
    hovertemplate='<b>%{text}</b><br>' +
                  'Price: Rp%{x:,.0f}<br>' +
                  'Performance: %{y:.2f}<br>' +
                  '<extra></extra>'
))

# Add quadrant lines
price_median = df['Price_Number'].median()
perf_median = df['Performance_Score'].median()

fig_matrix.add_hline(y=perf_median, line_dash="dash", line_color="red", 
                     annotation_text="Performance Median")
fig_matrix.add_vline(x=price_median, line_dash="dash", line_color="red", 
                     annotation_text="Price Median")

# Add quadrant labels
fig_matrix.add_annotation(x=price_median/2, y=perf_median*1.5, 
                         text="Low Price<br>High Performance", 
                         showarrow=False, font=dict(size=12, color="green"))
fig_matrix.add_annotation(x=price_median*1.5, y=perf_median*1.5, 
                         text="High Price<br>High Performance", 
                         showarrow=False, font=dict(size=12, color="blue"))
fig_matrix.add_annotation(x=price_median/2, y=perf_median/2, 
                         text="Low Price<br>Low Performance", 
                         showarrow=False, font=dict(size=12, color="orange"))
fig_matrix.add_annotation(x=price_median*1.5, y=perf_median/2, 
                         text="High Price<br>Low Performance", 
                         showarrow=False, font=dict(size=12, color="red"))

fig_matrix.update_layout(
    title="Competitive Positioning Matrix - Tokopedia Sarung Tangan",
    xaxis_title="Price (Rp)",
    yaxis_title="Performance Score",
    width=1000,
    height=600
)

fig_matrix.show()

# --- 4. ANALISIS KATEGORI PRODUK ---
print("\n" + "="*70)
print("LANGKAH 3: ANALISIS KATEGORI PRODUK")
print("="*70)

# a. Analisis berdasarkan Sub_Kategori_Penggunaan
if 'Sub_Kategori_Penggunaan' in df.columns:
    print("\n📊 Analisis berdasarkan Kategori Penggunaan:")
    usage_analysis = df.groupby('Sub_Kategori_Penggunaan').agg({
        'Product_ID': 'count',
        'Price_Number': ['mean', 'std'],
        'Sold_Count': ['mean', 'sum'],
        'Rating': 'mean',
        'Revenue_Estimate': 'sum'
    }).round(2)
    
    usage_analysis.columns = ['_'.join(col).strip() for col in usage_analysis.columns]
    print(usage_analysis)
    
    # Visualisasi kategori penggunaan
    fig_usage = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Distribusi Kategori Penggunaan', 'Revenue by Kategori Penggunaan'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    usage_counts = df['Sub_Kategori_Penggunaan'].value_counts()
    fig_usage.add_trace(
        go.Pie(labels=usage_counts.index, values=usage_counts.values),
        row=1, col=1
    )
    
    revenue_by_usage = df.groupby('Sub_Kategori_Penggunaan')['Revenue_Estimate'].sum().sort_values(ascending=False)
    fig_usage.add_trace(
        go.Bar(x=revenue_by_usage.index, y=revenue_by_usage.values),
        row=1, col=2
    )
    
    fig_usage.update_layout(title_text="Analisis Kategori Penggunaan", height=500)
    fig_usage.show()

# b. Analisis berdasarkan Sub_Kategori_Bahan
if 'Sub_Kategori_Bahan' in df.columns:
    print("\n📊 Analisis berdasarkan Kategori Bahan:")
    material_analysis = df.groupby('Sub_Kategori_Bahan').agg({
        'Product_ID': 'count',
        'Price_Number': ['mean', 'std'],
        'Sold_Count': ['mean', 'sum'],
        'Rating': 'mean',
        'Revenue_Estimate': 'sum'
    }).round(2)
    
    material_analysis.columns = ['_'.join(col).strip() for col in material_analysis.columns]
    print(material_analysis)

# --- 5. ANALISIS GEOGRAFIS LANJUTAN ---
print("\n" + "="*70)
print("LANGKAH 4: ANALISIS GEOGRAFIS LANJUTAN")
print("="*70)

# a. Analisis per kota
print("\n🌍 Analisis per Kota:")
city_analysis = df.groupby('Shop_City').agg({
    'Product_ID': 'count',
    'Price_Number': 'mean',
    'Sold_Count': 'sum',
    'Rating': 'mean',
    'Revenue_Estimate': 'sum'
}).round(2).sort_values('Revenue_Estimate', ascending=False)

print(city_analysis.head(10))

# b. Heatmap kota vs cluster
city_cluster_matrix = pd.crosstab(df['Shop_City'], df['Cluster'])
print(f"\n📊 Matrix Kota vs Cluster:")
print(city_cluster_matrix)

# Visualisasi heatmap
fig_heatmap = go.Figure(data=go.Heatmap(
    z=city_cluster_matrix.values,
    x=[f'Cluster {i}' for i in city_cluster_matrix.columns],
    y=city_cluster_matrix.index,
    colorscale='Viridis'
))

fig_heatmap.update_layout(
    title="Heatmap: Distribusi Cluster per Kota",
    xaxis_title="Cluster",
    yaxis_title="Kota",
    width=800,
    height=600
)

fig_heatmap.show()

# --- 6. INSIGHT DAN REKOMENDASI STRATEGIS ---
print("\n" + "="*70)
print("LANGKAH 5: INSIGHT DAN REKOMENDASI STRATEGIS")
print("="*70)

print("\n🎯 INSIGHT UTAMA:")

# 1. Market Size
total_market_size = df['Revenue_Estimate'].sum()
print(f"\n💰 UKURAN PASAR:")
print(f"   Total market size: Rp{total_market_size:,.0f}")
print(f"   Rata-rata revenue per produk: Rp{df['Revenue_Estimate'].mean():,.0f}")

# 2. Price Analysis
print(f"\n💵 ANALISIS HARGA:")
print(f"   Harga tertinggi: Rp{df['Price_Number'].max():,.0f}")
print(f"   Harga terendah: Rp{df['Price_Number'].min():,.0f}")
print(f"   Harga median: Rp{df['Price_Number'].median():,.0f}")
print(f"   Standar deviasi harga: Rp{df['Price_Number'].std():,.0f}")

# 3. Performance Analysis
print(f"\n⭐ ANALISIS PERFORMANCE:")
print(f"   Rating tertinggi: {df['Rating'].max():.1f}")
print(f"   Rating terendah: {df['Rating'].min():.1f}")
print(f"   Rating rata-rata: {df['Rating'].mean():.2f}")
print(f"   Produk dengan rating 5.0: {len(df[df['Rating'] == 5.0])}")

# 4. Geographic Insights
print(f"\n🌍 INSIGHT GEOGRAFIS:")
top_city = df.groupby('Shop_City')['Revenue_Estimate'].sum().idxmax()
top_city_revenue = df.groupby('Shop_City')['Revenue_Estimate'].sum().max()
print(f"   Kota dengan revenue tertinggi: {top_city} (Rp{top_city_revenue:,.0f})")

# 5. Cluster Insights
print(f"\n🎯 INSIGHT CLUSTER:")
for cluster_id in sorted(df['Cluster'].unique()):
    if cluster_id == -1:
        continue
    cluster_data = df[df['Cluster'] == cluster_id]
    print(f"\n   Cluster {cluster_id}:")
    print(f"      Jumlah produk: {len(cluster_data)}")
    print(f"      Rata-rata harga: Rp{cluster_data['Price_Number'].mean():,.0f}")
    print(f"      Rata-rata rating: {cluster_data['Rating'].mean():.2f}")
    print(f"      Total revenue: Rp{cluster_data['Revenue_Estimate'].sum():,.0f}")

# --- 7. REKOMENDASI STRATEGIS ---
print("\n" + "="*70)
print("REKOMENDASI STRATEGIS UNTUK GEMASTIK")
print("="*70)

print("\n🎯 REKOMENDASI STRATEGIS:")

# 1. Market Entry Strategy
print("\n🚀 STRATEGI MASUK PASAR:")
print("   1. Fokus pada segment Cluster 1 (mass market) untuk volume tinggi")
print("   2. Target kota dengan konsentrasi tinggi: Jakarta, Surabaya, Bandung")
print("   3. Pricing strategy: Competitive pricing dengan value proposition")

# 2. Product Strategy
print("\n📦 STRATEGI PRODUK:")
print("   1. Kembangkan produk dengan rating tinggi (target 4.5+)")
print("   2. Fokus pada kategori penggunaan yang paling laris")
print("   3. Optimalkan product description dan gambar")

# 3. Competitive Strategy
print("\n⚔️ STRATEGI KOMPETITIF:")
print("   1. Analisis kompetitor di setiap cluster")
print("   2. Identifikasi gap pasar yang belum terisi")
print("   3. Benchmark performance dengan top performers")

# 4. Geographic Strategy
print("\n🌍 STRATEGI GEOGRAFIS:")
print("   1. Ekspansi ke kota dengan potensi tinggi")
print("   2. Optimalkan logistik untuk delivery cepat")
print("   3. Adaptasi produk sesuai kebutuhan lokal")

# 5. Technology Strategy
print("\n💻 STRATEGI TEKNOLOGI:")
print("   1. Implementasi AI untuk personalisasi rekomendasi")
print("   2. Optimasi SEO dan digital marketing")
print("   3. Analisis data real-time untuk decision making")

# --- 8. METRICS KPI ---
print("\n" + "="*70)
print("METRICS KPI UNTUK MONITORING")
print("="*70)

print("\n📊 KEY PERFORMANCE INDICATORS (KPI):")

# 1. Revenue Metrics
print("\n💰 METRICS PENDAPATAN:")
print("   • Total Revenue Growth")
print("   • Average Order Value (AOV)")
print("   • Revenue per Product Category")
print("   • Revenue per Geographic Region")

# 2. Performance Metrics
print("\n⭐ METRICS PERFORMANCE:")
print("   • Average Rating")
print("   • Customer Satisfaction Score")
print("   • Product Performance Score")
print("   • Market Share per Cluster")

# 3. Operational Metrics
print("\n⚙️ METRICS OPERASIONAL:")
print("   • Inventory Turnover")
print("   • Delivery Time")
print("   • Customer Acquisition Cost")
print("   • Customer Lifetime Value")

# 4. Competitive Metrics
print("\n🎯 METRICS KOMPETITIF:")
print("   • Market Position vs Competitors")
print("   • Price Competitiveness")
print("   • Product Differentiation")
print("   • Customer Loyalty")

# --- 9. SAVE PRESENTATION DATA ---
print("\n" + "="*70)
print("MENYIMPAN DATA UNTUK PRESENTASI")
print("="*70)

# Save summary statistics
summary_stats = {
    'Total_Products': len(df),
    'Total_Shops': df['Shop_Name'].nunique(),
    'Total_Cities': df['Shop_City'].nunique(),
    'Total_Revenue': df['Revenue_Estimate'].sum(),
    'Average_Price': df['Price_Number'].mean(),
    'Average_Rating': df['Rating'].mean(),
    'Total_Sold': df['Sold_Count'].sum(),
    'Number_of_Clusters': len(df['Cluster'].unique()) - 1  # Exclude noise
}

summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
summary_df.to_excel("summary_statistics_presentation.xlsx", index=False)
print("✅ Summary statistics disimpan ke 'summary_statistics_presentation.xlsx'")

# Save cluster analysis
cluster_summary = df.groupby('Cluster').agg({
    'Product_ID': 'count',
    'Price_Number': ['mean', 'std'],
    'Sold_Count': ['mean', 'sum'],
    'Rating': 'mean',
    'Revenue_Estimate': 'sum'
}).round(2)

cluster_summary.columns = ['_'.join(col).strip() for col in cluster_summary.columns]
cluster_summary.to_excel("cluster_analysis_presentation.xlsx")
print("✅ Cluster analysis disimpan ke 'cluster_analysis_presentation.xlsx'")

# Save city analysis
city_summary = df.groupby('Shop_City').agg({
    'Product_ID': 'count',
    'Price_Number': 'mean',
    'Sold_Count': 'sum',
    'Rating': 'mean',
    'Revenue_Estimate': 'sum'
}).round(2).sort_values('Revenue_Estimate', ascending=False)

city_summary.to_excel("city_analysis_presentation.xlsx")
print("✅ City analysis disimpan ke 'city_analysis_presentation.xlsx'")

print("\n" + "="*70)
print("🎉 ANALISIS LANJUTAN UNTUK PRESENTASI SELESAI!")
print("="*70)

print("\n📁 File yang dihasilkan untuk presentasi:")
print("   • summary_statistics_presentation.xlsx")
print("   • cluster_analysis_presentation.xlsx")
print("   • city_analysis_presentation.xlsx")
print("   • Visualisasi interaktif (Plotly)")

print("\n🎯 SIAP UNTUK PRESENTASI GEMASTIK!")
print("   Semua insight dan rekomendasi strategis telah disiapkan.")
print("   Visualisasi interaktif siap untuk demonstrasi.")
print("   Data analisis tersimpan dalam format Excel untuk referensi.")