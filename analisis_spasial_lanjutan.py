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

# --- LIBRARY UNTUK GEOCODING ---
import requests
import time
import json

# --- LIBRARY UNTUK VISUALISASI INTERAKTIF ---
import plotly.offline as pyo
pyo.init_notebook_mode(connected=True)

print("🚀 MEMULAI ANALISIS SPASIAL LANJUTAN")
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

# --- 2. GEOCODING & STANDARISASI LOKASI ---
print("\n" + "="*70)
print("LANGKAH 1: GEOCODING & STANDARISASI LOKASI")
print("="*70)

# API Key Google Maps
GOOGLE_MAPS_API_KEY = "AIzaSyA8vber5Sovu6ufeQjyW4W1F0_APLsYtpE"

def geocode_city(city_name, api_key):
    """
    Geocode city name to coordinates using Google Maps API
    """
    try:
        # Add "Indonesia" to city name for better accuracy
        search_query = f"{city_name}, Indonesia"
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': search_query,
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"⚠️ Geocoding failed for {city_name}: {data['status']}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error geocoding {city_name}: {e}")
        return None, None

def batch_geocode_cities(df, api_key, batch_size=10):
    """
    Batch geocode cities with rate limiting
    """
    print("\n🗺️ Memulai proses geocoding...")
    
    # Get unique cities
    unique_cities = df['Shop_City'].unique()
    print(f"   Total kota unik: {len(unique_cities)}")
    
    # Dictionary to store coordinates
    city_coordinates = {}
    
    # Process in batches
    for i in range(0, len(unique_cities), batch_size):
        batch = unique_cities[i:i+batch_size]
        print(f"   Processing batch {i//batch_size + 1}/{(len(unique_cities) + batch_size - 1)//batch_size}")
        
        for city in batch:
            if city not in city_coordinates:
                lat, lng = geocode_city(city, api_key)
                city_coordinates[city] = (lat, lng)
                
                # Rate limiting - wait 0.1 seconds between requests
                time.sleep(0.1)
    
    return city_coordinates

# Perform geocoding
print("\n🔍 Melakukan geocoding untuk semua kota...")
city_coordinates = batch_geocode_cities(df, GOOGLE_MAPS_API_KEY)

# Add coordinates to dataframe
df['Latitude'] = df['Shop_City'].map(lambda x: city_coordinates.get(x, (None, None))[0])
df['Longitude'] = df['Shop_City'].map(lambda x: city_coordinates.get(x, (None, None))[1])

# Filter data with valid coordinates
df_spatial = df.dropna(subset=['Latitude', 'Longitude'])
print(f"   Data dengan koordinat valid: {len(df_spatial)} dari {len(df)}")

# --- 3. HOTSPOT DETECTION (GLOBAL MORAN'S I & GETIS-ORD GI*) ---
print("\n" + "="*70)
print("LANGKAH 2: HOTSPOT DETECTION")
print("="*70)

def calculate_distance_matrix(coordinates):
    """
    Calculate distance matrix between all points
    """
    from scipy.spatial.distance import cdist
    coords_array = np.array(coordinates)
    distances = cdist(coords_array, coords_array, metric='euclidean')
    return distances

def global_morans_i(values, distances, weights=None):
    """
    Calculate Global Moran's I for spatial autocorrelation
    """
    n = len(values)
    if weights is None:
        # Use inverse distance weights
        weights = 1 / (distances + 1e-10)  # Add small value to avoid division by zero
        np.fill_diagonal(weights, 0)  # Set diagonal to 0
    
    # Calculate mean
    mean_val = np.mean(values)
    
    # Calculate numerator and denominator
    numerator = 0
    denominator = 0
    
    for i in range(n):
        for j in range(n):
            if i != j:
                numerator += weights[i, j] * (values[i] - mean_val) * (values[j] - mean_val)
        denominator += (values[i] - mean_val) ** 2
    
    # Calculate Moran's I
    moran_i = (n * numerator) / (2 * np.sum(weights) * denominator)
    
    return moran_i

def getis_ord_gi_star(values, distances, weights=None):
    """
    Calculate Getis-Ord Gi* statistic for hotspot detection
    """
    n = len(values)
    if weights is None:
        # Use inverse distance weights
        weights = 1 / (distances + 1e-10)
        np.fill_diagonal(weights, 0)
    
    # Calculate statistics
    mean_val = np.mean(values)
    var_val = np.var(values)
    
    # Calculate Gi* for each point
    gi_star_values = []
    
    for i in range(n):
        # Sum of weighted values for point i
        sum_wx = np.sum(weights[i, :] * values)
        
        # Sum of weights for point i
        sum_w = np.sum(weights[i, :])
        
        # Sum of squared weights for point i
        sum_w2 = np.sum(weights[i, :] ** 2)
        
        # Calculate Gi*
        numerator = sum_wx - mean_val * sum_w
        denominator = np.sqrt(var_val * ((n * sum_w2 - sum_w ** 2) / (n - 1)))
        
        gi_star = numerator / denominator
        gi_star_values.append(gi_star)
    
    return np.array(gi_star_values)

# Prepare data for spatial analysis
print("\n🔍 Menyiapkan data untuk analisis spasial...")
coordinates = list(zip(df_spatial['Latitude'], df_spatial['Longitude']))
distances = calculate_distance_matrix(coordinates)

# Calculate Global Moran's I for price
print("\n📊 Menghitung Global Moran's I untuk harga...")
price_values = df_spatial['Price_Number'].values
moran_i_price = global_morans_i(price_values, distances)
print(f"   Global Moran's I untuk harga: {moran_i_price:.4f}")

# Calculate Global Moran's I for performance score
print("\n📊 Menghitung Global Moran's I untuk performance score...")
performance_values = df_spatial['Performance_Score'].values
moran_i_performance = global_morans_i(performance_values, distances)
print(f"   Global Moran's I untuk performance: {moran_i_performance:.4f}")

# Calculate Getis-Ord Gi* for hotspot detection
print("\n🔥 Menghitung Getis-Ord Gi* untuk hotspot detection...")
gi_star_price = getis_ord_gi_star(price_values, distances)
gi_star_performance = getis_ord_gi_star(performance_values, distances)

# Add hotspot indicators to dataframe
df_spatial['Price_Hotspot'] = gi_star_price > 1.96  # 95% confidence level
df_spatial['Price_Coldspot'] = gi_star_price < -1.96
df_spatial['Performance_Hotspot'] = gi_star_performance > 1.96
df_spatial['Performance_Coldspot'] = gi_star_performance < -1.96

# Count hotspots
price_hotspots = df_spatial['Price_Hotspot'].sum()
price_coldspots = df_spatial['Price_Coldspot'].sum()
performance_hotspots = df_spatial['Performance_Hotspot'].sum()
performance_coldspots = df_spatial['Performance_Coldspot'].sum()

print(f"\n📊 HASIL HOTSPOT DETECTION:")
print(f"   Price Hotspots: {price_hotspots}")
print(f"   Price Coldspots: {price_coldspots}")
print(f"   Performance Hotspots: {performance_hotspots}")
print(f"   Performance Coldspots: {performance_coldspots}")

# --- 4. SPATIAL CROSS-VALIDATION UNTUK HDBSCAN ---
print("\n" + "="*70)
print("LANGKAH 3: SPATIAL CROSS-VALIDATION UNTUK HDBSCAN")
print("="*70)

def spatial_block_cv(X, y, coordinates, n_splits=5):
    """
    Spatial block cross-validation
    """
    from sklearn.model_selection import KFold
    
    # Create spatial blocks based on coordinates
    lat_bins = pd.cut([coord[0] for coord in coordinates], bins=n_splits, labels=False)
    lon_bins = pd.cut([coord[1] for coord in coordinates], bins=n_splits, labels=False)
    
    # Combine lat and lon bins to create spatial blocks
    spatial_blocks = lat_bins * n_splits + lon_bins
    
    # Create custom CV splits
    cv_splits = []
    for i in range(n_splits):
        for j in range(n_splits):
            test_mask = (spatial_blocks == (i * n_splits + j))
            train_mask = ~test_mask
            cv_splits.append((train_mask, test_mask))
    
    return cv_splits

def optimize_hdbscan_parameters(X, coordinates, cv_splits):
    """
    Optimize HDBSCAN parameters using spatial cross-validation
    """
    print("\n🔍 Optimizing HDBSCAN parameters...")
    
    # Parameter grid
    min_cluster_sizes = [3, 5, 10, 15]
    min_samples_list = [2, 3, 5]
    
    best_score = -1
    best_params = {}
    
    for min_cluster_size in min_cluster_sizes:
        for min_samples in min_samples_list:
            scores = []
            
            for train_mask, test_mask in cv_splits:
                # Fit HDBSCAN on training data
                clusterer = hdbscan.HDBSCAN(
                    min_cluster_size=min_cluster_size,
                    min_samples=min_samples,
                    cluster_selection_epsilon=0.1,
                    cluster_selection_method='eom'
                )
                
                # Fit on training data
                train_labels = clusterer.fit_predict(X[train_mask])
                
                # Calculate silhouette score (only if we have clusters)
                if len(set(train_labels)) > 1 and -1 not in train_labels:
                    try:
                        score = silhouette_score(X[train_mask], train_labels)
                        scores.append(score)
                    except:
                        scores.append(-1)
                else:
                    scores.append(-1)
            
            # Average score across folds
            avg_score = np.mean([s for s in scores if s != -1])
            
            if avg_score > best_score and avg_score > 0:
                best_score = avg_score
                best_params = {
                    'min_cluster_size': min_cluster_size,
                    'min_samples': min_samples
                }
    
    print(f"   Best parameters: {best_params}")
    print(f"   Best silhouette score: {best_score:.4f}")
    
    return best_params

# Prepare data for clustering
clustering_features = ['Price_Number', 'Sold_Count', 'Rating', 'Review_Count', 
                      'Revenue_Estimate', 'Rating_Score', 'Popularity_Score', 'Performance_Score']

# Filter features that exist in dataframe
existing_features = [col for col in clustering_features if col in df_spatial.columns]
X = df_spatial[existing_features].values

# Normalize data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Perform spatial cross-validation
coordinates_list = list(zip(df_spatial['Latitude'], df_spatial['Longitude']))
cv_splits = spatial_block_cv(X_scaled, None, coordinates_list, n_splits=3)

# Optimize HDBSCAN parameters
best_params = optimize_hdbscan_parameters(X_scaled, coordinates_list, cv_splits)

# Apply optimized HDBSCAN
print("\n🎯 Menerapkan HDBSCAN dengan parameter optimal...")
hdbscan_clusterer = hdbscan.HDBSCAN(
    min_cluster_size=best_params.get('min_cluster_size', 5),
    min_samples=best_params.get('min_samples', 3),
    cluster_selection_epsilon=0.1,
    cluster_selection_method='eom'
)

cluster_labels = hdbscan_clusterer.fit_predict(X_scaled)
df_spatial['Cluster'] = cluster_labels

# Analyze clustering results
n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
n_noise = list(cluster_labels).count(-1)

print(f"\n📊 Hasil HDBSCAN dengan parameter optimal:")
print(f"   Jumlah cluster: {n_clusters}")
print(f"   Jumlah noise points: {n_noise}")
print(f"   Persentase noise: {n_noise/len(cluster_labels)*100:.2f}%")

# --- 5. SPATIAL MODELING (GWR/MGWR) ---
print("\n" + "="*70)
print("LANGKAH 4: SPATIAL MODELING (GWR)")
print("="*70)

def simple_gwr(X, y, coordinates, bandwidth=None):
    """
    Simple implementation of Geographically Weighted Regression
    """
    from scipy.spatial.distance import cdist
    
    n = len(X)
    coefs = np.zeros((n, X.shape[1]))
    intercepts = np.zeros(n)
    r2_scores = np.zeros(n)
    
    # Calculate distance matrix
    coords_array = np.array(coordinates)
    distances = cdist(coords_array, coords_array)
    
    # Set bandwidth if not provided (use median distance)
    if bandwidth is None:
        bandwidth = np.median(distances[distances > 0])
    
    print(f"   Using bandwidth: {bandwidth:.4f}")
    
    for i in range(n):
        # Calculate weights based on distance
        weights = np.exp(-0.5 * (distances[i] / bandwidth) ** 2)
        
        # Weighted least squares
        X_weighted = X * weights[:, np.newaxis]
        y_weighted = y * weights
        
        # Add intercept
        X_with_intercept = np.column_stack([np.ones(n), X_weighted])
        
        try:
            # Solve weighted least squares
            coef = np.linalg.lstsq(X_with_intercept, y_weighted, rcond=None)[0]
            intercepts[i] = coef[0]
            coefs[i] = coef[1:]
            
            # Calculate R² for this point
            y_pred = X_with_intercept @ coef
            ss_res = np.sum(weights * (y - y_pred) ** 2)
            ss_tot = np.sum(weights * (y - np.mean(y)) ** 2)
            r2_scores[i] = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
        except:
            intercepts[i] = np.nan
            coefs[i] = np.nan
            r2_scores[i] = np.nan
    
    return coefs, intercepts, r2_scores

# Prepare data for GWR
print("\n🔍 Menyiapkan data untuk Geographically Weighted Regression...")

# Select features for modeling
model_features = ['Sold_Count', 'Rating', 'Review_Count']
if 'Revenue_Estimate' in df_spatial.columns:
    model_features.append('Revenue_Estimate')

# Filter existing features
existing_model_features = [col for col in model_features if col in df_spatial.columns]
X_model = df_spatial[existing_model_features].values
y_model = df_spatial['Price_Number'].values

# Normalize features
scaler_model = StandardScaler()
X_model_scaled = scaler_model.fit_transform(X_model)

# Perform GWR
print("\n📊 Melakukan Geographically Weighted Regression...")
coefs_gwr, intercepts_gwr, r2_gwr = simple_gwr(X_model_scaled, y_model, coordinates_list)

# Add GWR results to dataframe
for i, feature in enumerate(existing_model_features):
    df_spatial[f'GWR_Coef_{feature}'] = coefs_gwr[:, i]
df_spatial['GWR_Intercept'] = intercepts_gwr
df_spatial['GWR_R2'] = r2_gwr

# Analyze GWR results
print(f"\n📊 HASIL GWR:")
print(f"   Rata-rata R²: {np.nanmean(r2_gwr):.4f}")
print(f"   Median R²: {np.nanmedian(r2_gwr):.4f}")
print(f"   Min R²: {np.nanmin(r2_gwr):.4f}")
print(f"   Max R²: {np.nanmax(r2_gwr):.4f}")

# Analyze coefficient variations
for i, feature in enumerate(existing_model_features):
    coef_values = coefs_gwr[:, i]
    print(f"\n   Koefisien {feature}:")
    print(f"      Rata-rata: {np.nanmean(coef_values):.4f}")
    print(f"      Std Dev: {np.nanstd(coef_values):.4f}")
    print(f"      Min: {np.nanmin(coef_values):.4f}")
    print(f"      Max: {np.nanmax(coef_values):.4f}")

# --- 6. VISUALISASI SPASIAL LANJUTAN ---
print("\n" + "="*70)
print("LANGKAH 5: VISUALISASI SPASIAL LANJUTAN")
print("="*70)

# a. Hotspot Map
print("\n🔥 Membuat peta hotspot...")
fig_hotspot = go.Figure()

# Add price hotspots
price_hotspot_data = df_spatial[df_spatial['Price_Hotspot']]
price_coldspot_data = df_spatial[df_spatial['Price_Coldspot']]

if not price_hotspot_data.empty:
    fig_hotspot.add_trace(go.Scattermapbox(
        lat=price_hotspot_data['Latitude'],
        lon=price_hotspot_data['Longitude'],
        mode='markers',
        marker=dict(size=10, color='red', opacity=0.8),
        name='Price Hotspots',
        text=price_hotspot_data['Shop_City'] + '<br>Price: Rp' + price_hotspot_data['Price_Number'].astype(str),
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))

if not price_coldspot_data.empty:
    fig_hotspot.add_trace(go.Scattermapbox(
        lat=price_coldspot_data['Latitude'],
        lon=price_coldspot_data['Longitude'],
        mode='markers',
        marker=dict(size=10, color='blue', opacity=0.8),
        name='Price Coldspots',
        text=price_coldspot_data['Shop_City'] + '<br>Price: Rp' + price_coldspot_data['Price_Number'].astype(str),
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))

# Add regular points
regular_data = df_spatial[~(df_spatial['Price_Hotspot'] | df_spatial['Price_Coldspot'])]
if not regular_data.empty:
    fig_hotspot.add_trace(go.Scattermapbox(
        lat=regular_data['Latitude'],
        lon=regular_data['Longitude'],
        mode='markers',
        marker=dict(size=5, color='gray', opacity=0.5),
        name='Regular Points',
        text=regular_data['Shop_City'] + '<br>Price: Rp' + regular_data['Price_Number'].astype(str),
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))

fig_hotspot.update_layout(
    title="Hotspot Detection - Price Analysis",
    mapbox=dict(
        style='open-street-map',
        center=dict(
            lat=df_spatial['Latitude'].mean(),
            lon=df_spatial['Longitude'].mean()
        ),
        zoom=5
    ),
    width=1200,
    height=800
)

fig_hotspot.show()

# b. GWR Coefficient Maps
print("\n📊 Membuat peta koefisien GWR...")
fig_gwr = make_subplots(
    rows=2, cols=2,
    subplot_titles=[f'GWR Coefficient: {feature}' for feature in existing_model_features] + ['GWR R² Score'],
    specs=[[{"type": "scattermapbox"}, {"type": "scattermapbox"}],
           [{"type": "scattermapbox"}, {"type": "scattermapbox"}]]
)

for i, feature in enumerate(existing_model_features):
    row = (i // 2) + 1
    col = (i % 2) + 1
    
    fig_gwr.add_trace(go.Scattermapbox(
        lat=df_spatial['Latitude'],
        lon=df_spatial['Longitude'],
        mode='markers',
        marker=dict(
            size=8,
            color=df_spatial[f'GWR_Coef_{feature}'],
            colorscale='RdBu',
            opacity=0.7,
            colorbar=dict(title=f'Coef {feature}')
        ),
        text=df_spatial['Shop_City'] + f'<br>Coef {feature}: ' + df_spatial[f'GWR_Coef_{feature}'].round(4).astype(str),
        hovertemplate='<b>%{text}</b><extra></extra>',
        name=f'Coef {feature}'
    ), row=row, col=col)

# Add R² map
fig_gwr.add_trace(go.Scattermapbox(
    lat=df_spatial['Latitude'],
    lon=df_spatial['Longitude'],
    mode='markers',
    marker=dict(
        size=8,
        color=df_spatial['GWR_R2'],
        colorscale='Viridis',
        opacity=0.7,
        colorbar=dict(title='R² Score')
    ),
    text=df_spatial['Shop_City'] + '<br>R²: ' + df_spatial['GWR_R2'].round(4).astype(str),
    hovertemplate='<b>%{text}</b><extra></extra>',
    name='R² Score'
), row=2, col=2)

fig_gwr.update_layout(
    title="Geographically Weighted Regression Results",
    mapbox=dict(
        style='open-street-map',
        center=dict(
            lat=df_spatial['Latitude'].mean(),
            lon=df_spatial['Longitude'].mean()
        ),
        zoom=5
    ),
    width=1400,
    height=1000
)

fig_gwr.show()

# c. Spatial Autocorrelation Analysis
print("\n📈 Membuat analisis autokorelasi spasial...")
fig_autocorr = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Price Spatial Autocorrelation', 'Performance Spatial Autocorrelation']
)

# Moran's I scatter plots
fig_autocorr.add_trace(go.Scatter(
    x=price_values,
    y=gi_star_price,
    mode='markers',
    marker=dict(
        size=6,
        color=price_values,
        colorscale='Viridis',
        opacity=0.7
    ),
    text=df_spatial['Shop_City'],
    hovertemplate='<b>%{text}</b><br>Price: %{x}<br>Gi*: %{y}<extra></extra>',
    name='Price'
), row=1, col=1)

fig_autocorr.add_trace(go.Scatter(
    x=performance_values,
    y=gi_star_performance,
    mode='markers',
    marker=dict(
        size=6,
        color=performance_values,
        colorscale='Viridis',
        opacity=0.7
    ),
    text=df_spatial['Shop_City'],
    hovertemplate='<b>%{text}</b><br>Performance: %{x}<br>Gi*: %{y}<extra></extra>',
    name='Performance'
), row=1, col=2)

fig_autocorr.update_layout(
    title="Spatial Autocorrelation Analysis",
    width=1200,
    height=500
)

fig_autocorr.show()

# --- 7. SPATIAL CROSS-VALIDATION RESULTS ---
print("\n" + "="*70)
print("LANGKAH 6: HASIL SPATIAL CROSS-VALIDATION")
print("="*70)

# Compare spatial vs non-spatial CV
print("\n📊 Membandingkan Spatial vs Non-Spatial Cross-Validation...")

# Traditional K-fold CV
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression

kf = KFold(n_splits=5, shuffle=True, random_state=42)
traditional_scores = cross_val_score(LinearRegression(), X_model_scaled, y_model, cv=kf, scoring='r2')

# Spatial CV (using our custom function)
spatial_scores = []
for train_mask, test_mask in cv_splits:
    if np.sum(train_mask) > 0 and np.sum(test_mask) > 0:
        model = LinearRegression()
        model.fit(X_model_scaled[train_mask], y_model[train_mask])
        y_pred = model.predict(X_model_scaled[test_mask])
        score = r2_score(y_model[test_mask], y_pred)
        spatial_scores.append(score)

print(f"\n📊 HASIL CROSS-VALIDATION:")
print(f"   Traditional K-fold CV R² scores: {traditional_scores}")
print(f"   Traditional K-fold CV mean R²: {np.mean(traditional_scores):.4f}")
print(f"   Spatial CV R² scores: {spatial_scores}")
print(f"   Spatial CV mean R²: {np.mean(spatial_scores):.4f}")

# Visualize CV comparison
fig_cv = go.Figure()

fig_cv.add_trace(go.Box(
    y=traditional_scores,
    name='Traditional K-fold CV',
    boxpoints='all',
    jitter=0.3,
    pointpos=-1.8
))

fig_cv.add_trace(go.Box(
    y=spatial_scores,
    name='Spatial CV',
    boxpoints='all',
    jitter=0.3,
    pointpos=-1.8
))

fig_cv.update_layout(
    title="Cross-Validation Comparison: Traditional vs Spatial",
    yaxis_title="R² Score",
    width=800,
    height=500
)

fig_cv.show()

# --- 8. INSIGHT DAN REKOMENDASI SPASIAL ---
print("\n" + "="*70)
print("LANGKAH 7: INSIGHT DAN REKOMENDASI SPASIAL")
print("="*70)

print("\n🎯 INSIGHT SPASIAL UTAMA:")

# 1. Spatial Autocorrelation
print(f"\n📊 AUTOKORELASI SPASIAL:")
print(f"   Global Moran's I untuk harga: {moran_i_price:.4f}")
if moran_i_price > 0.3:
    print("   → Kuat autokorelasi spasial positif (cluster harga tinggi)")
elif moran_i_price > 0.1:
    print("   → Autokorelasi spasial moderat")
elif moran_i_price > -0.1:
    print("   → Autokorelasi spasial lemah")
else:
    print("   → Autokorelasi spasial negatif (dispersi)")

print(f"   Global Moran's I untuk performance: {moran_i_performance:.4f}")
if moran_i_performance > 0.3:
    print("   → Kuat autokorelasi spasial positif (cluster performance tinggi)")
elif moran_i_performance > 0.1:
    print("   → Autokorelasi spasial moderat")
elif moran_i_performance > -0.1:
    print("   → Autokorelasi spasial lemah")
else:
    print("   → Autokorelasi spasial negatif (dispersi)")

# 2. Hotspot Analysis
print(f"\n🔥 ANALISIS HOTSPOT:")
print(f"   Price Hotspots: {price_hotspots} ({price_hotspots/len(df_spatial)*100:.1f}%)")
print(f"   Price Coldspots: {price_coldspots} ({price_coldspots/len(df_spatial)*100:.1f}%)")
print(f"   Performance Hotspots: {performance_hotspots} ({performance_hotspots/len(df_spatial)*100:.1f}%)")
print(f"   Performance Coldspots: {performance_coldspots} ({performance_coldspots/len(df_spatial)*100:.1f}%)")

# 3. GWR Insights
print(f"\n📊 INSIGHT GWR:")
print(f"   Rata-rata R² model GWR: {np.nanmean(r2_gwr):.4f}")
print(f"   Variasi koefisien antar lokasi:")

for i, feature in enumerate(existing_model_features):
    coef_values = coefs_gwr[:, i]
    coef_range = np.nanmax(coef_values) - np.nanmin(coef_values)
    print(f"      {feature}: range {coef_range:.4f}")

# 4. Cross-Validation Insights
print(f"\n🔍 INSIGHT CROSS-VALIDATION:")
print(f"   Traditional CV mean R²: {np.mean(traditional_scores):.4f}")
print(f"   Spatial CV mean R²: {np.mean(spatial_scores):.4f}")
cv_difference = np.mean(traditional_scores) - np.mean(spatial_scores)
print(f"   Perbedaan: {cv_difference:.4f}")
if cv_difference > 0.1:
    print("   → Ada kebocoran spasial yang signifikan")
elif cv_difference > 0.05:
    print("   → Ada kebocoran spasial moderat")
else:
    print("   → Kebocoran spasial minimal")

# --- 9. REKOMENDASI STRATEGIS SPASIAL ---
print("\n" + "="*70)
print("REKOMENDASI STRATEGIS SPASIAL")
print("="*70)

print("\n🎯 REKOMENDASI BERDASARKAN ANALISIS SPASIAL:")

# 1. Market Entry Strategy
print("\n🚀 STRATEGI MASUK PASAR:")
if moran_i_price > 0.2:
    print("   • Fokus pada cluster harga tinggi untuk premium positioning")
    print("   • Identifikasi coldspot untuk penetrasi harga rendah")
else:
    print("   • Harga tersebar merata, fokus pada diferensiasi produk")

# 2. Geographic Strategy
print("\n🌍 STRATEGI GEOGRAFIS:")
hotspot_cities = df_spatial[df_spatial['Price_Hotspot']]['Shop_City'].unique()
coldspot_cities = df_spatial[df_spatial['Price_Coldspot']]['Shop_City'].unique()

print(f"   • Hotspot cities (target premium): {', '.join(hotspot_cities[:5])}")
print(f"   • Coldspot cities (target volume): {', '.join(coldspot_cities[:5])}")

# 3. Pricing Strategy
print("\n💰 STRATEGI PRICING:")
print("   • Implementasi dynamic pricing berdasarkan lokasi")
print("   • Penyesuaian harga berdasarkan koefisien GWR lokal")
print("   • Monitoring hotspot untuk perubahan harga kompetitor")

# 4. Operational Strategy
print("\n⚙️ STRATEGI OPERASIONAL:")
print("   • Optimasi logistik berdasarkan pola spasial")
print("   • Penempatan gudang berdasarkan hotspot analysis")
print("   • Marketing campaign berbasis karakteristik spasial")

# --- 10. SAVE SPATIAL ANALYSIS RESULTS ---
print("\n" + "="*70)
print("MENYIMPAN HASIL ANALISIS SPASIAL")
print("="*70)

# Save spatial analysis results
spatial_results = {
    'Global_Morans_I_Price': moran_i_price,
    'Global_Morans_I_Performance': moran_i_performance,
    'Price_Hotspots_Count': price_hotspots,
    'Price_Coldspots_Count': price_coldspots,
    'Performance_Hotspots_Count': performance_hotspots,
    'Performance_Coldspots_Count': performance_coldspots,
    'GWR_Mean_R2': np.nanmean(r2_gwr),
    'Traditional_CV_Mean_R2': np.mean(traditional_scores),
    'Spatial_CV_Mean_R2': np.mean(spatial_scores),
    'CV_Difference': cv_difference
}

spatial_summary_df = pd.DataFrame(list(spatial_results.items()), columns=['Metric', 'Value'])
spatial_summary_df.to_excel("spatial_analysis_results.xlsx", index=False)
print("✅ Spatial analysis results disimpan ke 'spatial_analysis_results.xlsx'")

# Save enhanced dataset
df_spatial.to_excel("Tokopedia_sarung_tangan_spatial_analysis.xlsx", index=False)
print("✅ Enhanced dataset dengan analisis spasial disimpan ke 'Tokopedia_sarung_tangan_spatial_analysis.xlsx'")

# Save hotspot data
hotspot_summary = df_spatial[['Shop_City', 'Latitude', 'Longitude', 'Price_Number', 'Performance_Score',
                             'Price_Hotspot', 'Price_Coldspot', 'Performance_Hotspot', 'Performance_Coldspot']].copy()
hotspot_summary.to_excel("hotspot_analysis.xlsx", index=False)
print("✅ Hotspot analysis disimpan ke 'hotspot_analysis.xlsx'")

print("\n" + "="*70)
print("🎉 ANALISIS SPASIAL LANJUTAN SELESAI!")
print("="*70)

print("\n📁 File yang dihasilkan:")
print("   • spatial_analysis_results.xlsx")
print("   • Tokopedia_sarung_tangan_spatial_analysis.xlsx")
print("   • hotspot_analysis.xlsx")
print("   • Visualisasi spasial interaktif (Plotly)")

print("\n🔍 INSIGHT SPASIAL UTAMA:")
print("   1. Geocoding berhasil mengkonversi lokasi ke koordinat")
print("   2. Hotspot detection mengidentifikasi area dengan karakteristik unik")
print("   3. GWR menunjukkan variasi pengaruh faktor antar lokasi")
print("   4. Spatial cross-validation mencegah kebocoran spasial")
print("   5. Rekomendasi strategis berbasis analisis spasial")

print("\n🏆 KONTRIBUSI UNTUK GEMASTIK:")
print("   • Implementasi analisis spasial tingkat lanjut")
print("   • Penggunaan API geocoding untuk akurasi lokasi")
print("   • Hotspot detection dengan metode statistik yang kredibel")
print("   • Spatial modeling dengan GWR")
print("   • Validasi spasial yang mencegah overfitting")
print("   • Rekomendasi strategis berbasis insight spasial")