# --- ANALISIS SPASIAL LANJUTAN DENGAN VISUALISASI HOTSPOT UNTUK ORANG AWAM ---
# Dosen Sains Data dengan 30 tahun pengalaman & sertifikasi internasional
# Modifikasi untuk visualisasi hotspot yang mudah dipahami

# --- KOORDINAT DUMMY SEBAGAI FALLBACK ---
city_coordinates_dummy = {
    'Jakarta': [-6.2088, 106.8456], 'Surabaya': [-7.2575, 112.7521], 'Bandung': [-6.9175, 107.6191],
    'Medan': [3.5952, 98.6722], 'Semarang': [-6.9932, 110.4203], 'Yogyakarta': [-7.7971, 110.3708],
    'Palembang': [-2.9761, 104.7754], 'Makassar': [-5.1477, 119.4327], 'Denpasar': [-8.6500, 115.2167],
    'Manado': [1.4748, 124.8421], 'Batam': [1.0456, 104.0611], 'Padang': [-0.9471, 100.4178],
    'Pontianak': [-0.0235, 109.3303], 'Banjarmasin': [-3.3167, 114.5900], 'Pekanbaru': [0.5333, 101.4500],
    'Malang': [-7.9797, 112.6304], 'Solo': [-7.5500, 110.8000], 'Tangerang': [-6.1700, 106.6300],
    'Bekasi': [-6.2300, 106.9900], 'Depok': [-6.3900, 106.8100], 'Bogor': [-6.5950, 106.8000],
    'Cirebon': [-6.7060, 108.5570], 'Sukabumi': [-6.9230, 106.9260], 'Purwokerto': [-7.4130, 109.2450],
    'Pematangsiantar': [2.9630, 99.0650], 'Tegal': [-6.8640, 109.1400], 'Magelang': [-7.4700, 110.2180],
    'Ponorogo': [-7.8720, 111.4630], 'Kediri': [-7.8160, 112.0100], 'Madiun': [-7.6300, 111.5200],
    'Pasuruan': [-7.6400, 112.9000], 'Probolinggo': [-7.7500, 113.2100], 'Lamongan': [-7.1160, 112.4170],
    'Jember': [-8.1700, 113.7000], 'Banyuwangi': [-8.2100, 114.3600], 'Karawang': [-6.3000, 107.3000],
    'Cikarang': [-6.2600, 107.1500], 'Serang': [-6.1200, 106.1500], 'Cilegon': [-6.1200, 106.0200],
    'Tasikmalaya': [-7.3300, 108.2000], 'Ciamis': [-7.3300, 108.3300], 'Garut': [-7.2200, 107.9000],
    'Sumedang': [-6.8500, 107.9100], 'Majalengka': [-6.8300, 108.2300], 'Indramayu': [-6.3300, 108.3200],
    'Subang': [-6.5600, 107.7600], 'Purwakarta': [-6.4200, 107.4500], 'Karanganyar': [-7.6000, 111.1000],
    'Sragen': [-7.4100, 111.0200], 'Wonogiri': [-8.0000, 110.9000], 'Boyolali': [-7.5300, 110.5900],
    'Klaten': [-7.7000, 110.5800], 'Sleman': [-7.6800, 110.3300], 'Bantul': [-7.8700, 110.3300],
    'Gunungkidul': [-7.9800, 110.5800], 'Kulon Progo': [-7.7800, 110.1000], 'Pacitan': [-8.2000, 111.1200],
    'Trenggalek': [-8.0300, 111.7100], 'Tulungagung': [-8.0500, 111.9000], 'Blitar': [-8.1000, 112.1500],
    'Jombang': [-7.5500, 112.2300], 'Nganjuk': [-7.6000, 111.9000], 'Mojokerto': [-7.4700, 112.4300],
    'Situbondo': [-7.7000, 114.0000], 'Bondowoso': [-7.9200, 113.8100], 'Lumajang': [-8.1300, 113.1800],
    'Batu': [-7.8600, 112.5300], 'Blora': [-6.9500, 111.4200], 'Rembang': [-6.6000, 111.3500],
    'Pati': [-6.7500, 111.0300], 'Kudus': [-6.8000, 110.8500], 'Demak': [-6.8800, 110.6300],
    'Temanggung': [-7.3300, 110.1800], 'Wonosobo': [-7.3600, 110.1100], 'Purworejo': [-7.7100, 110.0100],
    'Kebumen': [-7.7800, 109.6300], 'Cilacap': [-7.7100, 109.0100], 'Banjar': [-3.1600, 105.9200],
    'Palu': [-0.9000, 119.8700], 'Gorontalo': [0.5400, 123.0600], 'Mamuju': [-2.6700, 118.8800],
    'Ambon': [-3.7000, 128.1700], 'Ternate': [0.7900, 127.3700], 'Jayapura': [-2.5300, 140.7200],
    'Manokwari': [-0.8600, 134.0600], 'Merauke': [-8.4900, 140.4000], 'Sorong': [-0.8800, 131.2500],
    'Biak': [-1.0300, 135.9900], 'Fakfak': [-2.9200, 132.2900], 'Kupang': [-10.1700, 123.6000],
    'Mataram': [-8.5800, 116.1000], 'Bima': [-8.4500, 118.7200], 'Ende': [-8.8000, 121.6500],
    'Waingapu': [-9.6600, 120.2600], 'Ruteng': [-8.5800, 120.4800], 'Larantuka': [-8.3300, 122.9300],
    'Maumere': [-8.6100, 122.1500], 'Atambua': [-9.1100, 124.9000], 'Kefamenanu': [-9.4800, 124.4100],
    'Soe': [-9.8300, 124.1400], 'Raba': [-8.5000, 118.8300], 'Sumbawa Besar': [-8.4800, 117.4100],
    'Dompu': [-8.5300, 118.4500], 'Taliwang': [-8.7200, 117.4100], 'Selong': [-8.6500, 116.5300],
    'Praya': [-8.5800, 116.2800], 'Gerung': [-8.6800, 116.0800], 'Labuan Bajo': [-8.7500, 119.9100],
    'Waikabubak': [-9.4100, 119.8800], 'Tambolaka': [-9.4100, 119.2400], 'Rote': [-10.7700, 123.0700],
    'Sabu Raijua': [-10.5800, 121.7800], 'Malaka': [-9.5700, 124.9600], 'Belu': [-9.1800, 124.9000],
    'Alor': [-8.2400, 124.5900], 'Flores Timur': [-8.2300, 122.9600], 'Sikka': [-8.5800, 122.2800],
    'Manggarai': [-8.6000, 120.4800], 'Ngada': [-8.7700, 121.0000], 'Manggarai Barat': [-8.6300, 119.8800],
    'Sumba Timur': [-9.8800, 120.2500], 'Sumba Barat': [-9.6600, 119.5800], 'Lembata': [-8.4000, 123.6800],
    'Rote Ndao': [-10.7700, 123.0700], 'Manggarai Timur': [-8.4800, 120.5800], 'Nagekeo': [-8.7700, 121.0000],
    'Sumba Tengah': [-9.5800, 119.9100], 'Sumba Barat Daya': [-9.6600, 119.5800]
}

# --- IMPORT LIBRARY ---
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

# --- LIBRARY UNTUK CLUSTERING HDBSCAN ---
import hdbscan
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import umap

# --- LIBRARY UNTUK ANALISIS SPASIAL ---
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import networkx as nx
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("🚀 MEMULAI ANALISIS SPASIAL DENGAN VISUALISASI HOTSPOT UNTUK ORANG AWAM")
print("="*80)

# --- FUNGSI GEOCODING DENGAN KOORDINAT DUMMY ---
def geocode_city(city_name):
    """
    Fungsi geocoding menggunakan koordinat dummy sebagai pengganti Google Maps API
    """
    city_name_clean = city_name.strip().title()

    if city_name_clean in city_coordinates_dummy:
        lat, lon = city_coordinates_dummy[city_name_clean]
        return {'lat': lat, 'lng': lon}

    for city, coords in city_coordinates_dummy.items():
        if city_name_clean.lower() in city.lower() or city.lower() in city_name_clean.lower():
            lat, lon = coords
            return {'lat': lat, 'lng': lon}

    print(f"⚠️  Kota '{city_name}' tidak ditemukan, menggunakan koordinat default Jakarta")
    return {'lat': -6.2088, 'lng': 106.8456}

def batch_geocode_cities(city_list):
    """
    Fungsi batch geocoding untuk multiple cities
    """
    results = []
    for city in city_list:
        coords = geocode_city(city)
        results.append(coords)
    return results

# --- FUNGSI ANALISIS SPASIAL ---
def calculate_morans_i(data, coordinates):
    """
    Menghitung Global Moran's I untuk spatial autocorrelation
    """
    distances = squareform(pdist(coordinates))
    weights = 1 / (distances + 1e-10)
    np.fill_diagonal(weights, 0)
    weights = weights / weights.sum()

    n = len(data)
    mean_data = np.mean(data)
    numerator = 0
    denominator = 0

    for i in range(n):
        for j in range(n):
            numerator += weights[i,j] * (data[i] - mean_data) * (data[j] - mean_data)
        denominator += (data[i] - mean_data) ** 2

    morans_i = (n / (2 * weights.sum())) * (numerator / denominator)
    return morans_i

def calculate_getis_ord_gi(data, coordinates):
    """
    Menghitung Getis-Ord Gi* untuk hotspot detection
    """
    distances = squareform(pdist(coordinates))
    weights = 1 / (distances + 1e-10)
    np.fill_diagonal(weights, 0)

    n = len(data)
    mean_data = np.mean(data)
    std_data = np.std(data)

    gi_star = []
    for i in range(n):
        numerator = np.sum(weights[i] * data) - mean_data * np.sum(weights[i])
        denominator = std_data * np.sqrt((n * np.sum(weights[i]**2) - np.sum(weights[i])**2) / (n-1))
        gi_star.append(numerator / denominator)

    return np.array(gi_star)

# --- FUNGSI VISUALISASI HOTSPOT UNTUK ORANG AWAM ---
def create_hotspot_map_simple(df, target_col, city_col):
    """
    Membuat peta hotspot yang mudah dipahami orang awam
    """
    print(f"🗺️  Membuat peta hotspot untuk {target_col}...")
    
    # Buat base map
    m = folium.Map(
        location=[df['latitude'].mean(), df['longitude'].mean()],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Hitung threshold untuk hotspot
    mean_val = df[target_col].mean()
    std_val = df[target_col].std()
    
    # Klasifikasi sederhana untuk orang awam
    high_threshold = mean_val + std_val
    low_threshold = mean_val - std_val
    
    # Klasifikasi hotspot
    df[f'{target_col}_category'] = 'Normal'
    df.loc[df[target_col] > high_threshold, f'{target_col}_category'] = 'Hotspot (Tinggi)'
    df.loc[df[target_col] < low_threshold, f'{target_col}_category'] = 'Coldspot (Rendah)'
    
    # Color mapping yang mudah dipahami
    color_map = {
        'Hotspot (Tinggi)': 'red',
        'Normal': 'yellow',
        'Coldspot (Rendah)': 'blue'
    }
    
    # Size mapping berdasarkan nilai
    max_val = df[target_col].max()
    min_val = df[target_col].min()
    
    # Tambah markers
    for idx, row in df.iterrows():
        # Hitung ukuran marker (5-20)
        size = 5 + (row[target_col] - min_val) / (max_val - min_val) * 15
        
        # Tentukan warna
        color = color_map[row[f'{target_col}_category']]
        
        # Popup content yang mudah dipahami
        popup_content = f"""
        <div style="width: 250px;">
            <h4 style="color: {color}; margin-bottom: 10px;">{row[city_col]}</h4>
            <p><strong>Status:</strong> {row[f'{target_col}_category']}</p>
            <p><strong>{target_col}:</strong> {row[target_col]:,.0f}</p>
            <p><strong>Rata-rata:</strong> {mean_val:,.0f}</p>
            <hr style="margin: 10px 0;">
            <p style="font-size: 12px; color: #666;">
                🔴 Hotspot = Nilai di atas rata-rata<br>
                🟡 Normal = Nilai sekitar rata-rata<br>
                🔵 Coldspot = Nilai di bawah rata-rata
            </p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=size,
            popup=folium.Popup(popup_content, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Tambah legend yang mudah dipahami
    legend_html = f'''
    <div style="position: fixed;
                top: 50px; right: 50px; width: 200px; height: 200px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 15px; border-radius: 10px;">
        <h4 style="margin-top: 0; color: #333;">Peta Hotspot {target_col}</h4>
        <p style="margin: 5px 0;"><span style="color: red; font-weight: bold;">🔴 Hotspot (Tinggi)</span></p>
        <p style="margin: 5px 0; font-size: 12px;">Nilai di atas {high_threshold:,.0f}</p>
        <p style="margin: 5px 0;"><span style="color: orange; font-weight: bold;">🟡 Normal</span></p>
        <p style="margin: 5px 0; font-size: 12px;">Nilai sekitar rata-rata</p>
        <p style="margin: 5px 0;"><span style="color: blue; font-weight: bold;">🔵 Coldspot (Rendah)</span></p>
        <p style="margin: 5px 0; font-size: 12px;">Nilai di bawah {low_threshold:,.0f}</p>
        <hr style="margin: 10px 0;">
        <p style="font-size: 11px; color: #666;">
            Ukuran lingkaran = Besarnya nilai
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_hotspot_summary_chart(df, target_col):
    """
    Membuat chart ringkasan hotspot yang mudah dipahami
    """
    print(f"📊 Membuat chart ringkasan hotspot untuk {target_col}...")
    
    # Hitung statistik
    mean_val = df[target_col].mean()
    std_val = df[target_col].std()
    high_threshold = mean_val + std_val
    low_threshold = mean_val - std_val
    
    # Klasifikasi
    hotspot_count = len(df[df[target_col] > high_threshold])
    coldspot_count = len(df[df[target_col] < low_threshold])
    normal_count = len(df) - hotspot_count - coldspot_count
    
    # Buat pie chart
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=['Hotspot (Tinggi)', 'Normal', 'Coldspot (Rendah)'],
        values=[hotspot_count, normal_count, coldspot_count],
        marker_colors=['red', 'yellow', 'blue'],
        textinfo='label+percent+value',
        textfont_size=14,
        hole=0.3
    ))
    
    fig.update_layout(
        title=f'Distribusi Hotspot - {target_col}<br><sub>Total: {len(df)} lokasi</sub>',
        title_x=0.5,
        title_font_size=16,
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_hotspot_ranking(df, target_col, city_col):
    """
    Membuat ranking hotspot yang mudah dipahami
    """
    print(f"🏆 Membuat ranking hotspot untuk {target_col}...")
    
    # Hitung threshold
    mean_val = df[target_col].mean()
    std_val = df[target_col].std()
    high_threshold = mean_val + std_val
    low_threshold = mean_val - std_val
    
    # Klasifikasi
    df[f'{target_col}_category'] = 'Normal'
    df.loc[df[target_col] > high_threshold, f'{target_col}_category'] = 'Hotspot'
    df.loc[df[target_col] < low_threshold, f'{target_col}_category'] = 'Coldspot'
    
    # Top hotspots
    top_hotspots = df[df[f'{target_col}_category'] == 'Hotspot'].nlargest(10, target_col)
    top_coldspots = df[df[f'{target_col}_category'] == 'Coldspot'].nsmallest(10, target_col)
    
    # Buat bar chart untuk top hotspots
    fig_hotspots = go.Figure()
    
    fig_hotspots.add_trace(go.Bar(
        x=top_hotspots[city_col],
        y=top_hotspots[target_col],
        marker_color='red',
        name='Top Hotspots',
        text=[f'{val:,.0f}' for val in top_hotspots[target_col]],
        textposition='auto'
    ))
    
    fig_hotspots.update_layout(
        title=f'Top 10 Hotspot - {target_col}',
        xaxis_title='Kota',
        yaxis_title=f'Nilai {target_col}',
        height=400,
        title_x=0.5
    )
    
    # Buat bar chart untuk top coldspots
    fig_coldspots = go.Figure()
    
    fig_coldspots.add_trace(go.Bar(
        x=top_coldspots[city_col],
        y=top_coldspots[target_col],
        marker_color='blue',
        name='Top Coldspots',
        text=[f'{val:,.0f}' for val in top_coldspots[target_col]],
        textposition='auto'
    ))
    
    fig_coldspots.update_layout(
        title=f'Top 10 Coldspot - {target_col}',
        xaxis_title='Kota',
        yaxis_title=f'Nilai {target_col}',
        height=400,
        title_x=0.5
    )
    
    return fig_hotspots, fig_coldspots

# --- LOADING DATA ---
print("📊 LOADING DATA...")
print("-" * 50)

# Coba load file dengan nama yang lebih spesifik terlebih dahulu
try:
    df = pd.read_excel('excel_output/Tokopedia_sarung_tangan_with_cluster.xlsx')
    print("✅ Berhasil load file: Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx")
except FileNotFoundError:
    try:
        df = pd.read_excel('Tokopedia_sarung tangan.xlsx')
        print("✅ Berhasil load file: Tokopedia_sarung tangan.xlsx")
    except FileNotFoundError:
        print("❌ File tidak ditemukan. Membuat data dummy untuk demo...")
        # Buat data dummy untuk demo
        np.random.seed(42)
        cities = list(city_coordinates_dummy.keys())[:50]  # Ambil 50 kota pertama
        n_samples = len(cities)

        df = pd.DataFrame({
            'city': cities,
            'price': np.random.uniform(50000, 500000, n_samples),
            'rating': np.random.uniform(3.0, 5.0, n_samples),
            'sold': np.random.randint(10, 1000, n_samples),
            'review_count': np.random.randint(5, 500, n_samples)
        })

print(f"📈 Shape data: {df.shape}")
print(f"📋 Kolom yang tersedia: {list(df.columns)}")
print("\n" + "="*80)

# --- DATA PREPROCESSING ---
print("🔧 DATA PREPROCESSING...")
print("-" * 50)

# Cari kolom yang berisi nama kota
city_columns = [col for col in df.columns if 'city' in col.lower() or 'kota' in col.lower() or 'lokasi' in col.lower()]
if city_columns:
    city_col = city_columns[0]
    print(f"📍 Kolom kota ditemukan: {city_col}")
else:
    # Jika tidak ada kolom kota, gunakan kolom pertama yang berisi string
    string_columns = df.select_dtypes(include=['object']).columns
    if len(string_columns) > 0:
        city_col = string_columns[0]
        print(f"📍 Menggunakan kolom string pertama: {city_col}")
    else:
        print("❌ Tidak ada kolom kota yang ditemukan. Membuat kolom dummy...")
        df['city'] = list(city_coordinates_dummy.keys())[:len(df)]
        city_col = 'city'

# Bersihkan data kota
df[city_col] = df[city_col].astype(str).str.strip()

# Geocoding dengan koordinat dummy
print("🌍 GEOCODING DENGAN KOORDINAT DUMMY...")
cities = df[city_col].unique()
print(f"📍 Jumlah kota unik: {len(cities)}")

# Geocode semua kota
geocoded_cities = batch_geocode_cities(cities)
city_coords_dict = dict(zip(cities, geocoded_cities))

# Tambah koordinat ke dataframe
df['latitude'] = df[city_col].map(lambda x: city_coords_dict[x]['lat'])
df['longitude'] = df[city_col].map(lambda x: city_coords_dict[x]['lng'])

print(f"✅ Geocoding selesai untuk {len(cities)} kota")
print("\n" + "="*80)

# --- HDBSCAN CLUSTERING DENGAN SPATIAL FEATURES ---
print("🔍 HDBSCAN CLUSTERING DENGAN SPATIAL FEATURES...")
print("-" * 50)

# Pilih kolom numerik untuk clustering
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
# Hapus kolom koordinat dari features
if 'latitude' in numeric_columns:
    numeric_columns.remove('latitude')
if 'longitude' in numeric_columns:
    numeric_columns.remove('longitude')

print(f"📊 Kolom numerik untuk clustering: {numeric_columns}")

# Persiapkan data untuk clustering
X_cluster = df[numeric_columns].fillna(0)
coordinates = df[['latitude', 'longitude']].values

# Standardisasi data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

# Tambah koordinat sebagai features (normalized)
coord_scaler = MinMaxScaler()
coordinates_normalized = coord_scaler.fit_transform(coordinates)

# Gabungkan features numerik dengan koordinat
X_with_spatial = np.hstack([X_scaled, coordinates_normalized])

print(f"🔢 Shape data untuk clustering: {X_with_spatial.shape}")

# HDBSCAN Clustering
print("🎯 MENJALANKAN HDBSCAN CLUSTERING...")

# Optimasi parameter HDBSCAN
best_score = -1
best_params = {}
best_labels = None

# Grid search untuk parameter optimal
min_cluster_sizes = [5, 10, 15, 20]
min_samples_list = [3, 5, 7, 10]

for min_cluster_size in min_cluster_sizes:
    for min_samples in min_samples_list:
        try:
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                metric='euclidean'
            )
            labels = clusterer.fit_predict(X_with_spatial)

            # Hitung silhouette score (hanya jika ada lebih dari 1 cluster)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            if n_clusters > 1:
                # Filter data yang tidak noise untuk silhouette score
                mask = labels != -1
                if np.sum(mask) > 1:
                    score = silhouette_score(X_with_spatial[mask], labels[mask])
                    if score > best_score:
                        best_score = score
                        best_params = {'min_cluster_size': min_cluster_size, 'min_samples': min_samples}
                        best_labels = labels.copy()
        except:
            continue

if best_labels is not None:
    final_labels = best_labels
    print(f"✅ Parameter optimal: {best_params}")
    print(f"🎯 Silhouette Score: {best_score:.4f}")
else:
    # Fallback dengan parameter default
    clusterer = hdbscan.HDBSCAN(min_cluster_size=10, min_samples=5)
    final_labels = clusterer.fit_predict(X_with_spatial)
    print("⚠️  Menggunakan parameter default HDBSCAN")

# Tambah cluster labels ke dataframe
df['cluster'] = final_labels

# Analisis cluster
n_clusters = len(set(final_labels)) - (1 if -1 in final_labels else 0)
n_noise = list(final_labels).count(-1)

print(f"📊 Hasil Clustering:")
print(f"   - Jumlah cluster: {n_clusters}")
print(f"   - Jumlah noise points: {n_noise}")
print(f"   - Persentase noise: {(n_noise/len(final_labels)*100):.2f}%")

print("\n" + "="*80)

# --- ANALISIS SPASIAL & HOTSPOT DETECTION ---
print("🌍 ANALISIS SPASIAL & HOTSPOT DETECTION...")
print("-" * 50)

# Pilih variabel target untuk analisis spasial
target_columns = [col for col in numeric_columns if col not in ['latitude', 'longitude', 'cluster']]
if not target_columns:
    target_columns = ['price']  # Default jika tidak ada kolom numerik lain

print(f"🎯 Variabel target untuk analisis spasial: {target_columns}")

# Analisis untuk setiap variabel target
spatial_results = {}

for target_col in target_columns:
    print(f"\n📊 Analisis spasial untuk: {target_col}")

    # Data untuk analisis
    target_data = df[target_col].fillna(df[target_col].mean()).values
    coords = df[['latitude', 'longitude']].values

    # 1. Global Moran's I
    try:
        morans_i = calculate_morans_i(target_data, coords)
        print(f"   🌐 Global Moran's I: {morans_i:.4f}")

        # Interpretasi Moran's I
        if morans_i > 0.3:
            interpretation = "Spatial clustering yang kuat (positive autocorrelation)"
        elif morans_i > 0.1:
            interpretation = "Spatial clustering sedang (positive autocorrelation)"
        elif morans_i > -0.1:
            interpretation = "Spatial randomness"
        elif morans_i > -0.3:
            interpretation = "Spatial dispersion sedang (negative autocorrelation)"
        else:
            interpretation = "Spatial dispersion yang kuat (negative autocorrelation)"

        print(f"   📝 Interpretasi: {interpretation}")

    except Exception as e:
        print(f"   ❌ Error menghitung Moran's I: {e}")
        morans_i = None

    # 2. Getis-Ord Gi* (Hotspot Detection)
    try:
        gi_star = calculate_getis_ord_gi(target_data, coords)

        # Klasifikasi hotspot
        hotspot_threshold = 1.96  # 95% confidence level
        coldspot_threshold = -1.96

        hotspots = gi_star > hotspot_threshold
        coldspots = gi_star < coldspot_threshold

        n_hotspots = np.sum(hotspots)
        n_coldspots = np.sum(coldspots)

        print(f"   🔥 Hotspots (Gi* > {hotspot_threshold}): {n_hotspots} lokasi")
        print(f"   ❄️  Coldspots (Gi* < {coldspot_threshold}): {n_coldspots} lokasi")

        # Tambah hotspot indicators ke dataframe
        df[f'{target_col}_hotspot'] = hotspots
        df[f'{target_col}_coldspot'] = coldspots
        df[f'{target_col}_gi_star'] = gi_star

    except Exception as e:
        print(f"   ❌ Error menghitung Getis-Ord Gi*: {e}")
        gi_star = None

    # Simpan hasil
    spatial_results[target_col] = {
        'morans_i': morans_i,
        'gi_star': gi_star,
        'n_hotspots': n_hotspots if 'n_hotspots' in locals() else 0,
        'n_coldspots': n_coldspots if 'n_coldspots' in locals() else 0
    }

print("\n" + "="*80)

# --- VISUALISASI HOTSPOT UNTUK ORANG AWAM ---
print("🎨 VISUALISASI HOTSPOT UNTUK ORANG AWAM...")
print("-" * 50)

# Buat visualisasi untuk setiap variabel target
hotspot_maps = []
hotspot_charts = []
hotspot_rankings = []

for target_col in target_columns:
    print(f"\n🎯 Membuat visualisasi untuk: {target_col}")
    
    # 1. Peta hotspot sederhana
    hotspot_map = create_hotspot_map_simple(df, target_col, city_col)
    hotspot_maps.append((target_col, hotspot_map))
    
    # 2. Chart ringkasan
    summary_chart = create_hotspot_summary_chart(df, target_col)
    hotspot_charts.append((target_col, summary_chart))
    
    # 3. Ranking hotspot
    ranking_hot, ranking_cold = create_hotspot_ranking(df, target_col, city_col)
    hotspot_rankings.append((target_col, ranking_hot, ranking_cold))

print("\n" + "="*80)

# --- EXPORT VISUALISASI ---
print("💾 EXPORT VISUALISASI...")
print("-" * 50)

# 1. Export peta hotspot
print("🗺️  Exporting peta hotspot...")
for target_col, map_obj in hotspot_maps:
    filename = f"hotspot_map_{target_col}_awam.html"
    map_obj.save(filename)
    print(f"   ✅ {filename}")

# 2. Export chart ringkasan
print("📊 Exporting chart ringkasan...")
for target_col, chart_obj in hotspot_charts:
    filename = f"hotspot_summary_{target_col}_awam.html"
    chart_obj.write_html(filename)
    print(f"   ✅ {filename}")

# 3. Export ranking
print("🏆 Exporting ranking hotspot...")
for target_col, ranking_hot, ranking_cold in hotspot_rankings:
    filename_hot = f"hotspot_ranking_{target_col}_awam.html"
    filename_cold = f"coldspot_ranking_{target_col}_awam.html"
    ranking_hot.write_html(filename_hot)
    ranking_cold.write_html(filename_cold)
    print(f"   ✅ {filename_hot}")
    print(f"   ✅ {filename_cold}")

# 4. Export dataset dengan hasil analisis
print("📈 Exporting dataset dengan hasil analisis...")
df['analysis_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
df['data_source'] = 'Tokopedia_Sarung_Tangan_Analysis'
df['analysis_type'] = 'Spatial_Analysis_with_Simple_Hotspot'

df.to_excel('hotspot_analysis_awam.xlsx', index=False)
print("   ✅ hotspot_analysis_awam.xlsx")

# 5. Buat summary report
print("📋 Membuat summary report...")
summary_data = []
for target_col in target_columns:
    mean_val = df[target_col].mean()
    std_val = df[target_col].std()
    high_threshold = mean_val + std_val
    low_threshold = mean_val - std_val
    
    hotspot_count = len(df[df[target_col] > high_threshold])
    coldspot_count = len(df[df[target_col] < low_threshold])
    normal_count = len(df) - hotspot_count - coldspot_count
    
    summary_data.append({
        'Variabel': target_col,
        'Rata-rata': f"{mean_val:,.0f}",
        'Standar Deviasi': f"{std_val:,.0f}",
        'Threshold Tinggi': f"{high_threshold:,.0f}",
        'Threshold Rendah': f"{low_threshold:,.0f}",
        'Jumlah Hotspot': hotspot_count,
        'Jumlah Normal': normal_count,
        'Jumlah Coldspot': coldspot_count,
        'Persentase Hotspot': f"{(hotspot_count/len(df)*100):.1f}%"
    })

summary_df = pd.DataFrame(summary_data)
summary_df.to_excel('hotspot_summary_report_awam.xlsx', index=False)
print("   ✅ hotspot_summary_report_awam.xlsx")

print("\n" + "="*80)
print("🎉 ANALISIS SPASIAL DENGAN VISUALISASI HOTSPOT UNTUK ORANG AWAM SELESAI!")
print("="*80)

print(f"📊 Total data points: {len(df)}")
print(f"🔍 Jumlah cluster: {n_clusters}")
print(f"🌍 Jumlah kota: {len(cities)}")
print(f"📈 Variabel target: {len(target_columns)}")

print("\n📋 FILE OUTPUT YANG DIHASILKAN:")
print("   🗺️  Peta Hotspot:")
for target_col, _ in hotspot_maps:
    print(f"      • hotspot_map_{target_col}_awam.html")
print("   📊 Chart Ringkasan:")
for target_col, _ in hotspot_charts:
    print(f"      • hotspot_summary_{target_col}_awam.html")
print("   🏆 Ranking Hotspot:")
for target_col, _, _ in hotspot_rankings:
    print(f"      • hotspot_ranking_{target_col}_awam.html")
    print(f"      • coldspot_ranking_{target_col}_awam.html")
print("   📈 Data:")
print("      • hotspot_analysis_awam.xlsx")
print("      • hotspot_summary_report_awam.xlsx")

print("\n🎯 FITUR VISUALISASI HOTSPOT UNTUK ORANG AWAM:")
print("   ✅ Peta dengan warna yang mudah dipahami (Merah=Hotspot, Kuning=Normal, Biru=Coldspot)")
print("   ✅ Legend yang jelas dengan penjelasan sederhana")
print("   ✅ Popup informasi yang mudah dibaca")
print("   ✅ Ukuran marker berdasarkan besarnya nilai")
print("   ✅ Chart ringkasan distribusi hotspot")
print("   ✅ Ranking top hotspot dan coldspot")
print("   ✅ Threshold otomatis berdasarkan statistik")

print("\n🔧 CARA MEMBACA HASIL:")
print("   🔴 Hotspot (Merah) = Nilai di atas rata-rata + standar deviasi")
print("   🟡 Normal (Kuning) = Nilai sekitar rata-rata")
print("   🔵 Coldspot (Biru) = Nilai di bawah rata-rata - standar deviasi")
print("   📏 Ukuran lingkaran = Semakin besar nilai, semakin besar lingkaran")

print("\n🎯 ANALISIS SPASIAL BERHASIL DILAKUKAN DENGAN VISUALISASI YANG MUDAH DIPAHAMI!")
print("="*80)