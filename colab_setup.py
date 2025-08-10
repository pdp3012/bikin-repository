# --- GOOGLE COLAB SETUP UNTUK GEMASTIK 2024 ---
# Jalankan cell ini terlebih dahulu untuk setup environment

# Install dependencies
!pip install hdbscan umap-learn folium plotly networkx

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium import plugins
import hdbscan
from sklearn.preprocessing import StandardScaler
import umap
import warnings
warnings.filterwarnings("ignore")

print("✅ Setup Google Colab selesai!")
print("🚀 Siap untuk analisis Gemastik 2024!")

# Upload file Excel
from google.colab import files
print("\n📁 Silakan upload file 'Tokopedia_sarung tangan.xlsx'")
uploaded = files.upload()

# List uploaded files
for filename in uploaded.keys():
    print(f'✅ File uploaded: {filename}')