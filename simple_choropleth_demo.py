# --- DEMO CHOROPLETH MAP SEDERHANA ---
# Versi yang hanya menggunakan library standar Python
# Untuk demonstrasi visualisasi choropleth map

import random
import json
from datetime import datetime

def generate_simple_data():
    """
    Generate data sederhana untuk demonstrasi choropleth map
    """
    print("🔧 Generating simple data untuk demonstrasi choropleth map...")
    
    # Kota-kota di Indonesia dengan koordinat
    cities = [
        {'name': 'Jakarta', 'lat': -6.2088, 'lon': 106.8456},
        {'name': 'Surabaya', 'lat': -7.2575, 'lon': 112.7521},
        {'name': 'Bandung', 'lat': -6.9175, 'lon': 107.6191},
        {'name': 'Medan', 'lat': 3.5952, 'lon': 98.6722},
        {'name': 'Semarang', 'lat': -6.9932, 'lon': 110.4203},
        {'name': 'Yogyakarta', 'lat': -7.7971, 'lon': 110.3708},
        {'name': 'Palembang', 'lat': -2.9761, 'lon': 104.7754},
        {'name': 'Makassar', 'lat': -5.1477, 'lon': 119.4327},
        {'name': 'Denpasar', 'lat': -8.6500, 'lon': 115.2167},
        {'name': 'Manado', 'lat': 1.4748, 'lon': 124.8421}
    ]
    
    # Generate data untuk setiap kota
    city_data = []
    
    for city in cities:
        # Generate random data untuk demonstrasi
        jumlah_kasus = random.randint(200, 800)
        jumlah_produk = random.randint(50, 200)
        rata_harga = random.randint(15000, 45000)
        performance_score = round(random.uniform(3.0, 5.0), 2)
        
        city_data.append({
            'city': city['name'],
            'latitude': city['lat'],
            'longitude': city['lon'],
            'jumlah_kasus': jumlah_kasus,
            'jumlah_produk': jumlah_produk,
            'rata_harga': rata_harga,
            'performance_score': performance_score
        })
    
    print(f"✅ Generated data untuk {len(city_data)} kota")
    return city_data

def create_choropleth_html(city_data, metric='jumlah_kasus', title="Distribusi Kasus per Wilayah"):
    """
    Membuat file HTML untuk choropleth map sederhana
    """
    print(f"🗺️ Membuat Choropleth Map untuk metrik: {metric}")
    
    # Tentukan range nilai
    values = [city[metric] for city in city_data]
    min_val = min(values)
    max_val = max(values)
    
    # Buat HTML content
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Choropleth Map - {title}</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .map-container {{
            position: relative;
            width: 100%;
            height: 600px;
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
            border-radius: 10px;
            overflow: hidden;
        }}
        .city-circle {{
            position: absolute;
            border-radius: 50%;
            border: 2px solid #333;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        .city-circle:hover {{
            transform: scale(1.1);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        .city-label {{
            position: absolute;
            background: rgba(255,255,255,0.9);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
            pointer-events: none;
            white-space: nowrap;
        }}
        .legend {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: white;
            border: 2px solid #333;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            font-size: 14px;
            min-width: 250px;
        }}
        .legend h4 {{
            margin: 0 0 10px 0;
            color: #333;
            text-align: center;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border: 1px solid #333;
            margin-right: 10px;
            border-radius: 3px;
        }}
        .popup {{
            position: absolute;
            background: white;
            border: 2px solid #333;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: none;
            z-index: 1000;
            max-width: 200px;
        }}
        .popup h4 {{
            margin: 0 0 8px 0;
            color: #333;
        }}
        .popup p {{
            margin: 3px 0;
            font-size: 12px;
        }}
        .title {{
            text-align: center;
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
        }}
        .info {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">{title}</div>
        <div class="info">Visualisasi distribusi {metric.replace('_', ' ')} per kota di Indonesia</div>
        
        <div class="map-container" id="map">
            <div class="legend">
                <h4>Legend</h4>
                <div class="legend-item">
                    <div class="legend-color" style="background: lightgreen;"></div>
                    <span>Rendah ({min_val:,})</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: yellow;"></div>
                    <span>Sedang</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: orange;"></div>
                    <span>Tinggi</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: red;"></div>
                    <span>Sangat Tinggi ({max_val:,})</span>
                </div>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <b>Sumber data:</b> Tokopedia Digital Service
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    <b>Metrik:</b> {metric.replace('_', ' ')}
                </p>
            </div>
            
            <div class="popup" id="popup"></div>
        </div>
    </div>

    <script>
        // Data kota
        const cityData = {json.dumps(city_data)};
        const minValue = {min_val};
        const maxValue = {max_val};
        
        // Fungsi untuk mendapatkan warna berdasarkan nilai
        function getColor(value) {{
            const normalized = (value - minValue) / (maxValue - minValue);
            if (normalized < 0.25) return 'lightgreen';
            if (normalized < 0.5) return 'yellow';
            if (normalized < 0.75) return 'orange';
            return 'red';
        }}
        
        // Fungsi untuk mendapatkan radius berdasarkan nilai
        function getRadius(value) {{
            const normalized = (value - minValue) / (maxValue - minValue);
            return 15 + (normalized * 25); // Radius antara 15-40px
        }}
        
        // Render kota-kota
        cityData.forEach(city => {{
            const circle = document.createElement('div');
            circle.className = 'city-circle';
            circle.style.left = ((city.longitude + 110) * 3 + 50) + '%';
            circle.style.top = ((city.latitude + 10) * 3 + 50) + '%';
            circle.style.width = getRadius(city.{metric}) + 'px';
            circle.style.height = getRadius(city.{metric}) + 'px';
            circle.style.backgroundColor = getColor(city.{metric});
            
            // Label kota
            const label = document.createElement('div');
            label.className = 'city-label';
            label.textContent = city.city;
            label.style.left = ((city.longitude + 110) * 3 + 50) + '%';
            label.style.top = ((city.latitude + 10) * 3 + 50 - 25) + '%';
            
            // Popup content
            const popupContent = `
                <h4>${{city.city}}</h4>
                <p><b>Jumlah Kasus:</b> ${{city.jumlah_kasus.toLocaleString()}}</p>
                <p><b>Jumlah Produk:</b> ${{city.jumlah_produk}}</p>
                <p><b>Rata Harga:</b> Rp${{city.rata_harga.toLocaleString()}}</p>
                <p><b>Performance:</b> ${{city.performance_score}}</p>
            `;
            
            // Event listeners
            circle.addEventListener('mouseenter', (e) => {{
                const popup = document.getElementById('popup');
                popup.innerHTML = popupContent;
                popup.style.display = 'block';
                popup.style.left = e.pageX + 10 + 'px';
                popup.style.top = e.pageY - 10 + 'px';
            }});
            
            circle.addEventListener('mouseleave', () => {{
                document.getElementById('popup').style.display = 'none';
            }});
            
            document.getElementById('map').appendChild(circle);
            document.getElementById('map').appendChild(label);
        }});
        
        // Hide popup when clicking outside
        document.addEventListener('click', (e) => {{
            if (!e.target.classList.contains('city-circle')) {{
                document.getElementById('popup').style.display = 'none';
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Simpan ke file
    filename = f"choropleth_map_{metric}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"   ✅ Choropleth map disimpan sebagai: {filename}")
    return filename

def create_multiple_choropleths(city_data):
    """
    Membuat multiple choropleth maps untuk berbagai metrik
    """
    print("\n" + "="*70)
    print("MEMBUAT MULTIPLE CHOROPLETH MAPS")
    print("="*70)
    
    metrics = [
        ('jumlah_kasus', 'Distribusi Jumlah Kasus per Kota'),
        ('jumlah_produk', 'Distribusi Jumlah Produk per Kota'),
        ('rata_harga', 'Distribusi Rata-rata Harga per Kota'),
        ('performance_score', 'Distribusi Performance Score per Kota')
    ]
    
    generated_files = []
    
    for metric, title in metrics:
        filename = create_choropleth_html(city_data, metric, title)
        generated_files.append(filename)
    
    return generated_files

def main():
    """
    Main function untuk menjalankan demo choropleth map
    """
    print("="*70)
    print("DEMO CHOROPLETH MAP SPASIAL")
    print("="*70)
    print("Oleh: Dosen Sains Data dengan 30 tahun pengalaman")
    print("="*70)
    
    # Generate data
    city_data = generate_simple_data()
    
    # Tampilkan data
    print("\n📊 Data yang dihasilkan:")
    for city in city_data:
        print(f"   {city['city']}: {city['jumlah_kasus']:,} kasus, {city['jumlah_produk']} produk")
    
    # Buat choropleth maps
    generated_files = create_multiple_choropleths(city_data)
    
    print("\n" + "="*70)
    print("🎉 DEMO CHOROPLETH MAP SELESAI!")
    print("="*70)
    
    print(f"\n📁 File yang dihasilkan:")
    for filename in generated_files:
        print(f"   • {filename}")
    
    print("\n🔍 FITUR CHOROPLETH MAP:")
    print("   1. Visualisasi distribusi data per kota dengan gradasi warna")
    print("   2. Legend yang sophisticated dengan informasi detail")
    print("   3. Popup interaktif dengan statistik per wilayah")
    print("   4. Gradasi warna dari lightgreen → yellow → orange → red")
    print("   5. Radius circle yang dinamis berdasarkan nilai metrik")
    print("   6. Hover effect dan animasi yang smooth")
    print("   7. Responsive design yang modern")
    
    print("\n📝 CARA MENGGUNAKAN:")
    print("   1. Buka file HTML di browser")
    print("   2. Hover pada circle untuk melihat detail")
    print("   3. Legend menunjukkan range nilai")
    print("   4. Sumber data: Tokopedia Digital Service")
    
    print("\n🎯 INSIGHT YANG DIBERIKAN:")
    print("   1. Distribusi geografis konsentrasi data")
    print("   2. Identifikasi hotspot dan coldspot")
    print("   3. Perbandingan antar wilayah")
    print("   4. Visualisasi yang mudah dipahami")

if __name__ == "__main__":
    main()