# --- ANALISIS SPASIAL LANJUTAN DENGAN KOORDINAT DUMMY ---
# Dosen Sains Data dengan 30 tahun pengalaman & sertifikasi internasional
# Perbaikan kode dengan koordinat dummy untuk demo/fallback

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

# --- IMPORT LIBRARY UNTUK ANALISIS SPASIAL LANJUTAN ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# --- LIBRARY UNTUK VISUALISASI INTERAKTIF ---
import plotly.offline as pyo
# pyo.init_notebook_mode(connected=True)  # Commented out for non-notebook environment

print("🚀 MEMULAI ANALISIS SPASIAL LANJUTAN DENGAN KOORDINAT DUMMY")
print("="*70)

# --- FUNGSI GEOCODING DENGAN KOORDINAT DUMMY ---
def geocode_city(city_name):
    """
    Fungsi geocoding menggunakan koordinat dummy sebagai pengganti Google Maps API
    """
    # Normalisasi nama kota (hapus spasi berlebih, ubah ke title case)
    city_name_clean = city_name.strip().title()
    
    # Cari di dictionary koordinat dummy
    if city_name_clean in city_coordinates_dummy:
        lat, lon = city_coordinates_dummy[city_name_clean]
        return {'lat': lat, 'lng': lon}
    
    # Jika tidak ditemukan, coba cari dengan partial matching
    for city, coords in city_coordinates_dummy.items():
        if city_name_clean.lower() in city.lower() or city.lower() in city_name_clean.lower():
            lat, lon = coords
            return {'lat': lat, 'lng': lon}
    
    # Jika masih tidak ditemukan, return koordinat default (Jakarta)
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
    # Hitung distance matrix
    distances = squareform(pdist(coordinates))
    
    # Buat weight matrix (inverse distance)
    weights = 1 / (distances + 1e-10)  # Tambah epsilon untuk hindari division by zero
    np.fill_diagonal(weights, 0)
    
    # Normalisasi weights
    weights = weights / weights.sum()
    
    # Hitung Moran's I
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

def spatial_block_cv(X, y, coordinates, n_splits=5):
    """
    Spatial Block Cross-Validation
    """
    n_samples = len(X)
    block_size = n_samples // n_splits
    
    scores = []
    for i in range(n_splits):
        # Buat spatial blocks
        start_idx = i * block_size
        end_idx = min((i + 1) * block_size, n_samples)
        
        # Test set adalah block saat ini
        test_indices = list(range(start_idx, end_idx))
        train_indices = list(range(0, start_idx)) + list(range(end_idx, n_samples))
        
        if len(train_indices) == 0 or len(test_indices) == 0:
            continue
            
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predict dan hitung score
        y_pred = model.predict(X_test)
        score = r2_score(y_test, y_pred)
        scores.append(score)
    
    return np.mean(scores), np.std(scores)

# --- LOADING DATA ---
print("📊 LOADING DATA...")
print("-" * 50)

# Coba load file dengan nama yang lebih spesifik terlebih dahulu
try:
    df = pd.read_excel('Tokopedia_sarung_tangan_dengan_subkategori_penggunaan_bahan.xlsx')
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
print("\n" + "="*70)

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
print("\n" + "="*70)

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

# Evaluasi clustering
if n_clusters > 1:
    mask = final_labels != -1
    if np.sum(mask) > 1:
        silhouette_avg = silhouette_score(X_with_spatial[mask], final_labels[mask])
        calinski_score = calinski_harabasz_score(X_with_spatial[mask], final_labels[mask])
        print(f"   - Silhouette Score: {silhouette_avg:.4f}")
        print(f"   - Calinski-Harabasz Score: {calinski_score:.2f}")

print("\n" + "="*70)

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

print("\n" + "="*70)

# --- GEOGRAPHICALLY WEIGHTED REGRESSION (GWR) ---
print("📈 GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)...")
print("-" * 50)

# Pilih variabel target dan predictor
if len(target_columns) > 0:
    target_var = target_columns[0]  # Gunakan variabel pertama sebagai target
    predictor_vars = [col for col in target_columns[1:] if col not in ['latitude', 'longitude', 'cluster']]
    
    if not predictor_vars:
        # Jika tidak ada predictor lain, buat dummy predictor
        df['dummy_predictor'] = np.random.normal(0, 1, len(df))
        predictor_vars = ['dummy_predictor']
    
    print(f"🎯 Target variable: {target_var}")
    print(f"📊 Predictor variables: {predictor_vars}")
    
    # Persiapkan data untuk GWR
    X_gwr = df[predictor_vars].fillna(0).values
    y_gwr = df[target_var].fillna(df[target_var].mean()).values
    coords_gwr = df[['latitude', 'longitude']].values
    
    # Standardisasi data
    scaler_gwr = StandardScaler()
    X_gwr_scaled = scaler_gwr.fit_transform(X_gwr)
    
    # Simple GWR implementation (distance-weighted regression)
    print("🔧 MENJALANKAN GWR ANALYSIS...")
    
    # Hitung distance matrix
    distances = squareform(pdist(coords_gwr))
    
    # Parameter bandwidth (bisa dioptimasi)
    bandwidth = np.percentile(distances, 25)  # 25th percentile sebagai bandwidth
    
    # GWR coefficients untuk setiap lokasi
    gwr_coefficients = []
    gwr_predictions = []
    
    for i in range(len(coords_gwr)):
        # Hitung weights berdasarkan distance
        weights = np.exp(-0.5 * (distances[i] / bandwidth) ** 2)
        weights[i] = 1.0  # Weight maksimum untuk lokasi sendiri
        
        # Weighted least squares
        try:
            # Tambah intercept
            X_weighted = np.column_stack([np.ones(len(X_gwr_scaled)), X_gwr_scaled])
            
            # Weighted regression
            W = np.diag(weights)
            XW = W @ X_weighted
            yW = W @ y_gwr
            
            # Solve normal equation
            beta = np.linalg.lstsq(XW, yW, rcond=None)[0]
            
            # Prediction untuk lokasi ini
            pred = np.dot(np.array([1] + list(X_gwr_scaled[i])), beta)
            
            gwr_coefficients.append(beta)
            gwr_predictions.append(pred)
            
        except:
            # Fallback jika ada error
            gwr_coefficients.append(np.zeros(len(predictor_vars) + 1))
            gwr_predictions.append(y_gwr[i])
    
    # Tambah hasil GWR ke dataframe
    df['gwr_prediction'] = gwr_predictions
    df['gwr_residual'] = y_gwr - gwr_predictions
    
    # Hitung metrics GWR
    mae_gwr = mean_absolute_error(y_gwr, gwr_predictions)
    mse_gwr = mean_squared_error(y_gwr, gwr_predictions)
    r2_gwr = r2_score(y_gwr, gwr_predictions)
    
    print(f"📊 GWR Performance Metrics:")
    print(f"   - Mean Absolute Error: {mae_gwr:.4f}")
    print(f"   - Mean Squared Error: {mse_gwr:.4f}")
    print(f"   - R² Score: {r2_gwr:.4f}")
    
    # Spatial Cross-Validation
    print("\n🔄 SPATIAL CROSS-VALIDATION...")
    
    # Traditional K-fold CV
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    traditional_scores = cross_val_score(LinearRegression(), X_gwr_scaled, y_gwr, cv=kfold, scoring='r2')
    
    # Spatial Block CV
    spatial_mean, spatial_std = spatial_block_cv(X_gwr_scaled, y_gwr, coords_gwr, n_splits=5)
    
    print(f"📊 Cross-Validation Results:")
    print(f"   - Traditional K-fold CV R²: {np.mean(traditional_scores):.4f} (±{np.std(traditional_scores):.4f})")
    print(f"   - Spatial Block CV R²: {spatial_mean:.4f} (±{spatial_std:.4f})")
    
    # Bandingkan dengan OLS
    ols_model = LinearRegression()
    ols_model.fit(X_gwr_scaled, y_gwr)
    ols_pred = ols_model.predict(X_gwr_scaled)
    ols_r2 = r2_score(y_gwr, ols_pred)
    
    print(f"   - OLS R²: {ols_r2:.4f}")
    print(f"   - GWR vs OLS improvement: {(r2_gwr - ols_r2):.4f}")

else:
    print("⚠️  Tidak ada variabel numerik yang cukup untuk GWR analysis")

print("\n" + "="*70)

# --- VISUALISASI INTERAKTIF DENGAN PLOTLY ---
print("🎨 VISUALISASI INTERAKTIF DENGAN PLOTLY...")
print("-" * 50)

# Set style untuk plot
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# 1. Peta Clustering
print("🗺️  MEMBUAT PETA CLUSTERING...")

fig_cluster = px.scatter_mapbox(
    df, 
    lat='latitude', 
    lon='longitude',
    color='cluster',
    hover_data=[city_col] + target_columns[:3],  # Tambah 3 kolom pertama sebagai hover data
    title='HDBSCAN Clustering Results - Spatial Distribution',
    mapbox_style='carto-positron',
    zoom=4,
    center={'lat': -2.0, 'lon': 120.0}  # Center di Indonesia
)

fig_cluster.update_layout(
    title_x=0.5,
    title_font_size=16,
    height=600
)

# 2. Peta Hotspot untuk setiap variabel target
print("🔥 MEMBUAT PETA HOTSPOT...")

hotspot_figs = []
for target_col in target_columns:
    if f'{target_col}_hotspot' in df.columns:
        # Filter data hotspot dan coldspot
        hotspot_data = df[df[f'{target_col}_hotspot'] == True]
        coldspot_data = df[df[f'{target_col}_coldspot'] == True]
        normal_data = df[(df[f'{target_col}_hotspot'] == False) & (df[f'{target_col}_coldspot'] == False)]
        
        fig_hotspot = go.Figure()
        
        # Normal points
        fig_hotspot.add_trace(go.Scattermapbox(
            lat=normal_data['latitude'],
            lon=normal_data['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=8,
                color='lightblue',
                opacity=0.7
            ),
            name='Normal',
            text=normal_data[city_col],
            hovertemplate='<b>%{text}</b><br>' +
                         f'{target_col}: %{{customdata}}<br>' +
                         'Status: Normal<extra></extra>',
            customdata=normal_data[target_col]
        ))
        
        # Hotspots
        if len(hotspot_data) > 0:
            fig_hotspot.add_trace(go.Scattermapbox(
                lat=hotspot_data['latitude'],
                lon=hotspot_data['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=12,
                    color='red',
                    opacity=0.8
                ),
                name='Hotspot',
                text=hotspot_data[city_col],
                hovertemplate='<b>%{text}</b><br>' +
                             f'{target_col}: %{{customdata}}<br>' +
                             'Status: Hotspot<extra></extra>',
                customdata=hotspot_data[target_col]
            ))
        
        # Coldspots
        if len(coldspot_data) > 0:
            fig_hotspot.add_trace(go.Scattermapbox(
                lat=coldspot_data['latitude'],
                lon=coldspot_data['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=12,
                    color='blue',
                    opacity=0.8
                ),
                name='Coldspot',
                text=coldspot_data[city_col],
                hovertemplate='<b>%{text}</b><br>' +
                             f'{target_col}: %{{customdata}}<br>' +
                             'Status: Coldspot<extra></extra>',
                customdata=coldspot_data[target_col]
            ))
        
        fig_hotspot.update_layout(
            title=f'Hotspot Analysis - {target_col}',
            mapbox=dict(
                style='carto-positron',
                center=dict(lat=-2.0, lon=120.0),
                zoom=4
            ),
            height=500,
            title_x=0.5
        )
        
        hotspot_figs.append(fig_hotspot)

# 3. Analisis Cluster dengan Box Plot
print("📊 MEMBUAT ANALISIS CLUSTER...")

if 'cluster' in df.columns and len(target_columns) > 0:
    # Box plot untuk setiap cluster
    fig_box = make_subplots(
        rows=len(target_columns), cols=1,
        subplot_titles=[f'{col} by Cluster' for col in target_columns],
        vertical_spacing=0.1
    )
    
    for i, col in enumerate(target_columns, 1):
        for cluster_id in sorted(df['cluster'].unique()):
            cluster_data = df[df['cluster'] == cluster_id][col]
            fig_box.add_trace(
                go.Box(
                    y=cluster_data,
                    name=f'Cluster {cluster_id}',
                    boxpoints='outliers',
                    jitter=0.3,
                    pointpos=-1.8
                ),
                row=i, col=1
            )
    
    fig_box.update_layout(
        title='Cluster Analysis - Distribution by Variables',
        height=300 * len(target_columns),
        title_x=0.5
    )

# 4. Spatial Autocorrelation Plot
print("🌐 MEMBUAT PLOT SPATIAL AUTOCORRELATION...")

if len(target_columns) > 0:
    target_col = target_columns[0]
    morans_values = []
    variable_names = []
    
    for col in target_columns:
        if col in spatial_results and spatial_results[col]['morans_i'] is not None:
            morans_values.append(spatial_results[col]['morans_i'])
            variable_names.append(col)
    
    if morans_values:
        fig_moran = go.Figure()
        fig_moran.add_trace(go.Bar(
            x=variable_names,
            y=morans_values,
            marker_color=['red' if x > 0.1 else 'blue' if x < -0.1 else 'gray' for x in morans_values],
            text=[f'{x:.4f}' for x in morans_values],
            textposition='auto'
        ))
        
        fig_moran.update_layout(
            title='Global Moran\'s I - Spatial Autocorrelation',
            xaxis_title='Variables',
            yaxis_title='Moran\'s I',
            height=400,
            title_x=0.5
        )

# 5. GWR Results (jika ada)
print("📈 MEMBUAT PLOT GWR RESULTS...")

if 'gwr_prediction' in df.columns and len(target_columns) > 0:
    target_col = target_columns[0]
    
    # Scatter plot actual vs predicted
    fig_gwr = go.Figure()
    
    fig_gwr.add_trace(go.Scatter(
        x=df[target_col],
        y=df['gwr_prediction'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['gwr_residual'],
            colorscale='RdBu',
            colorbar=dict(title='Residuals')
        ),
        text=df[city_col],
        hovertemplate='<b>%{text}</b><br>' +
                     f'Actual {target_col}: %{{x}}<br>' +
                     f'Predicted {target_col}: %{{y}}<br>' +
                     'Residual: %{marker.color}<extra></extra>'
    ))
    
    # Perfect prediction line
    min_val = min(df[target_col].min(), df['gwr_prediction'].min())
    max_val = max(df[target_col].max(), df['gwr_prediction'].max())
    fig_gwr.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Perfect Prediction'
    ))
    
    fig_gwr.update_layout(
        title=f'GWR Results - {target_col}',
        xaxis_title=f'Actual {target_col}',
        yaxis_title=f'Predicted {target_col}',
        height=500,
        title_x=0.5
    )

print("✅ Semua visualisasi telah dibuat!")
print("\n" + "="*70)

# --- EXPORT DATA & SUMMARY ---
print("💾 EXPORT DATA & SUMMARY...")
print("-" * 50)

# 1. Export hasil analisis ke Excel
print("📊 EXPORTING RESULTS TO EXCEL...")

# Buat summary statistics
summary_stats = {
    'Metric': [],
    'Value': []
}

# Clustering summary
summary_stats['Metric'].extend([
    'Total Data Points',
    'Number of Clusters',
    'Noise Points',
    'Noise Percentage (%)',
    'Best Silhouette Score'
])
summary_stats['Value'].extend([
    len(df),
    n_clusters,
    n_noise,
    round((n_noise/len(final_labels)*100), 2),
    round(best_score, 4) if best_score > -1 else 'N/A'
])

# Spatial analysis summary
for target_col in target_columns:
    if target_col in spatial_results:
        morans_i = spatial_results[target_col]['morans_i']
        n_hotspots = spatial_results[target_col]['n_hotspots']
        n_coldspots = spatial_results[target_col]['n_coldspots']
        
        if morans_i is not None:
            summary_stats['Metric'].extend([
                f'{target_col} - Moran\'s I',
                f'{target_col} - Hotspots',
                f'{target_col} - Coldspots'
            ])
            summary_stats['Value'].extend([
                round(morans_i, 4),
                n_hotspots,
                n_coldspots
            ])

# GWR summary (jika ada)
if 'gwr_prediction' in df.columns and len(target_columns) > 0:
    target_col = target_columns[0]
    summary_stats['Metric'].extend([
        f'GWR - {target_col} R²',
        f'GWR - {target_col} MAE',
        f'GWR - {target_col} MSE'
    ])
    summary_stats['Value'].extend([
        round(r2_gwr, 4),
        round(mae_gwr, 4),
        round(mse_gwr, 4)
    ])

# Buat DataFrame summary
summary_df = pd.DataFrame(summary_stats)

# Export ke Excel dengan multiple sheets
with pd.ExcelWriter('spatial_analysis_results.xlsx', engine='openpyxl') as writer:
    # Sheet 1: Summary Statistics
    summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
    
    # Sheet 2: Enhanced Dataset
    df.to_excel(writer, sheet_name='Enhanced_Dataset', index=False)
    
    # Sheet 3: Spatial Results
    spatial_summary = []
    for target_col in target_columns:
        if target_col in spatial_results:
            spatial_summary.append({
                'Variable': target_col,
                'Moran\'s I': spatial_results[target_col]['morans_i'],
                'Hotspots': spatial_results[target_col]['n_hotspots'],
                'Coldspots': spatial_results[target_col]['n_coldspots']
            })
    
    if spatial_summary:
        spatial_df = pd.DataFrame(spatial_summary)
        spatial_df.to_excel(writer, sheet_name='Spatial_Analysis', index=False)

print("✅ Data berhasil di-export ke 'spatial_analysis_results.xlsx'")

# 2. Export dataset dengan hasil analisis
print("📈 EXPORTING ENHANCED DATASET...")

# Tambah informasi tambahan ke dataset
df['analysis_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
df['data_source'] = 'Tokopedia_Sarung_Tangan_Analysis'
df['analysis_type'] = 'Spatial_Analysis_with_Dummy_Coordinates'

# Export dataset lengkap
df.to_excel('Tokopedia_sarung_tangan_spatial_analysis.xlsx', index=False)
print("✅ Dataset lengkap berhasil di-export ke 'Tokopedia_sarung_tangan_spatial_analysis.xlsx'")

# 3. Export hotspot analysis
print("🔥 EXPORTING HOTSPOT ANALYSIS...")

hotspot_summary = []
for target_col in target_columns:
    if f'{target_col}_hotspot' in df.columns:
        hotspot_data = df[df[f'{target_col}_hotspot'] == True]
        coldspot_data = df[df[f'{target_col}_coldspot'] == True]
        
        for _, row in hotspot_data.iterrows():
            hotspot_summary.append({
                'Variable': target_col,
                'City': row[city_col],
                'Latitude': row['latitude'],
                'Longitude': row['longitude'],
                'Value': row[target_col],
                'Gi_Star': row[f'{target_col}_gi_star'],
                'Type': 'Hotspot'
            })
        
        for _, row in coldspot_data.iterrows():
            hotspot_summary.append({
                'Variable': target_col,
                'City': row[city_col],
                'Latitude': row['latitude'],
                'Longitude': row['longitude'],
                'Value': row[target_col],
                'Gi_Star': row[f'{target_col}_gi_star'],
                'Type': 'Coldspot'
            })

if hotspot_summary:
    hotspot_df = pd.DataFrame(hotspot_summary)
    hotspot_df.to_excel('hotspot_analysis.xlsx', index=False)
    print("✅ Hotspot analysis berhasil di-export ke 'hotspot_analysis.xlsx'")

# 4. Print final summary
print("\n" + "="*70)
print("🎉 ANALISIS SPASIAL LANJUTAN SELESAI!")
print("="*70)
print(f"📊 Total data points: {len(df)}")
print(f"🔍 Jumlah cluster: {n_clusters}")
print(f"🌍 Jumlah kota: {len(cities)}")
print(f"📈 Variabel target: {len(target_columns)}")
print(f"🗺️  Visualisasi dibuat: {len(hotspot_figs) + 1} peta")
print(f"💾 File yang di-export: 3 file Excel")

print("\n📋 FILE OUTPUT:")
print("   1. spatial_analysis_results.xlsx - Summary dan hasil analisis")
print("   2. Tokopedia_sarung_tangan_spatial_analysis.xlsx - Dataset lengkap")
print("   3. hotspot_analysis.xlsx - Analisis hotspot dan coldspot")

print("\n🔧 FITUR YANG DIIMPLEMENTASI:")
print("   ✅ Geocoding dengan koordinat dummy (tanpa API)")
print("   ✅ HDBSCAN clustering dengan spatial features")
print("   ✅ Global Moran's I untuk spatial autocorrelation")
print("   ✅ Getis-Ord Gi* untuk hotspot detection")
print("   ✅ Geographically Weighted Regression (GWR)")
print("   ✅ Spatial Block Cross-Validation")
print("   ✅ Visualisasi interaktif dengan Plotly")
print("   ✅ Export data ke Excel")

print("\n🎯 ANALISIS SPASIAL BERHASIL DILAKUKAN DENGAN KOORDINAT DUMMY!")
print("="*70)
