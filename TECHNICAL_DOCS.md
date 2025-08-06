# 📚 Dokumentasi Teknis - Tokopedia Scraper

## 🏗️ Arsitektur Sistem

### Komponen Utama:
1. **TokopediaScraperImproved**: Class utama yang mengelola seluruh proses scraping
2. **Selenium WebDriver**: Untuk simulasi browser dan interaksi dengan halaman web
3. **BeautifulSoup**: Untuk parsing HTML dan ekstraksi data
4. **Requests**: Sebagai fallback mechanism
5. **Pandas**: Untuk manipulasi dan export data

### Diagram Alur:
```
User Input → Scraper Initialization → Browser Setup → Navigate to Home → Search Products → Scroll & Extract → Save Data
```

## 🔧 Implementasi Detail

### 1. Browser Setup (`setup_driver()`)
```python
def setup_driver(self):
    # Menggunakan undetected_chromedriver untuk anti-detection
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # ... konfigurasi lainnya
```

**Fitur Anti-Detection:**
- Menyembunyikan properti `webdriver`
- Menggunakan user agent yang realistis
- Menonaktifkan automation flags
- Window size yang natural

### 2. Navigasi yang Benar (`navigate_to_tokopedia_home()`)
```python
def navigate_to_tokopedia_home(self):
    # Langkah 1: Akses halaman utama
    self.driver.get("https://www.tokopedia.com/")
    time.sleep(random.uniform(3, 5))
    
    # Langkah 2: Scroll untuk simulasi user behavior
    self.driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(random.uniform(1, 2))
```

**Mengapa Penting:**
- Tokopedia mendeteksi jika user langsung mengakses URL pencarian
- Mengakses halaman utama terlebih dahulu meniru perilaku user normal
- Scrolling awal membantu membangun session yang valid

### 3. Scrolling Otomatis (`auto_scroll_page()`)
```python
def auto_scroll_page(self):
    for i in range(5):
        # Scroll ke bawah
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        # Scroll ke atas sedikit
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
        time.sleep(scroll_pause_time)
```

**Strategi Scrolling:**
- **Lazy Loading**: Tokopedia menggunakan lazy loading untuk konten
- **Infinite Scroll**: Beberapa konten hanya dimuat saat di-scroll
- **User Simulation**: Gerakan scroll yang natural meniru user

### 4. Ekstraksi Data Robust (`extract_product_data_improved()`)

#### Strategi Container Detection:
```python
container_selectors = [
    '[data-testid="master-product-card"]',
    '[data-testid*="product-card"]',
    'div[class*="css-"]',  # CSS modules
    'div[class*="product"]',
    'div[class*="card"]'
]
```

#### Fallback Strategies:
1. **Data-testid**: Selector yang paling reliable
2. **CSS Classes**: Mencari berdasarkan pola class
3. **Link-based**: Mencari berdasarkan link produk
4. **Price-based**: Mencari berdasarkan elemen harga

### 5. Data Extraction Methods

#### Nama Produk:
```python
def extract_product_name_improved(self, element):
    # Strategi 1: Link produk
    links = element.find_all('a', href=re.compile(r'/p/'))
    
    # Strategi 2: Teks terpanjang yang masuk akal
    all_texts = []
    for tag in element.find_all(['span', 'p', 'h1', 'h2', 'h3', 'a', 'div']):
        text = tag.get_text(strip=True)
        if (10 < len(text) < 200 and 
            'Rp' not in text and 
            not re.match(r'^[\d.,]+$', text)):
            all_texts.append(text)
```

#### Harga:
```python
def extract_price_improved(self, element):
    price_pattern = re.compile(r'Rp[\s]*[\d,.\s]+')
    all_text = element.get_text()
    price_matches = price_pattern.findall(all_text)
    return price_matches[0].strip() if price_matches else "Harga tidak ditemukan"
```

## 🛡️ Anti-Detection Mechanisms

### 1. Undetected ChromeDriver
- **Fungsi**: Menyembunyikan automation flags
- **Implementasi**: Menggunakan library `undetected_chromedriver`
- **Keunggulan**: Lebih sulit terdeteksi sebagai bot

### 2. Random Delays
```python
time.sleep(random.uniform(3, 6))  # Delay antar halaman
time.sleep(random.uniform(1, 2))  # Delay scrolling
```

### 3. User Agent Rotation
```python
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...')
```

### 4. Session Management
- Menggunakan `requests.Session()` untuk konsistensi
- Menyimpan cookies antar request
- Headers yang realistis

## 🔄 Error Handling & Fallback

### 1. Driver Setup Fallback
```python
try:
    self.driver = uc.Chrome(options=options)
except Exception as e:
    # Fallback ke selenium biasa
    self.setup_fallback_driver()
```

### 2. Scraping Fallback
```python
if not self.navigate_to_tokopedia_home():
    return self.search_products_fallback(keyword, max_pages)
```

### 3. Data Validation
```python
def validate_product_data(self, product_data):
    has_name = product_data.get('nama_produk') and product_data['nama_produk'] != "Nama tidak ditemukan"
    has_price = product_data.get('harga') and product_data['harga'] != "Harga tidak ditemukan"
    return has_name or has_price
```

## 📊 Performance Optimization

### 1. Container Limiting
```python
return unique_containers[:50]  # Batasi maksimal 50 produk per halaman
```

### 2. Duplicate Removal
```python
unique_containers = []
seen_texts = set()
for container in containers:
    text_content = container.get_text()[:100]
    if text_content not in seen_texts:
        unique_containers.append(container)
        seen_texts.add(text_content)
```

### 3. Efficient Parsing
- Menggunakan `lxml` parser untuk speed
- Selective element searching
- Early termination pada kondisi tertentu

## 🔍 Debugging & Monitoring

### 1. Verbose Logging
```python
print(f"🔍 URL Pencarian: {search_url}")
print(f"✅ Ditemukan {len(containers)} container produk")
print(f"📦 Produk {len(products)}: {product_data['nama_produk'][:50]}...")
```

### 2. Data Quality Metrics
```python
def show_data_quality(self, df):
    for col in df.columns:
        valid_count = df[col].apply(lambda x: x != "" and "tidak ditemukan" not in str(x).lower()).sum()
        percentage = (valid_count / len(df)) * 100
        print(f"   • {col}: {valid_count}/{len(df)} ({percentage:.1f}%)")
```

### 3. Error Tracking
- Exception handling di setiap level
- Detailed error messages
- Graceful degradation

## 🚀 Future Improvements

### 1. Proxy Support
```python
# TODO: Implement proxy rotation
def setup_proxy(self):
    proxies = [
        "http://proxy1:port",
        "http://proxy2:port"
    ]
    # Rotate proxies for each request
```

### 2. Multi-threading
```python
# TODO: Implement concurrent scraping
from concurrent.futures import ThreadPoolExecutor
def scrape_concurrent(self, keywords):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(self.scrape_products, keywords)
```

### 3. API Integration
```python
# TODO: Integrate with Tokopedia API (if available)
def get_products_api(self, keyword):
    # Use official API instead of scraping
    pass
```

### 4. Machine Learning
```python
# TODO: Implement ML-based data extraction
def extract_with_ml(self, element):
    # Use trained model to extract product information
    pass
```

## 📋 Testing Strategy

### 1. Unit Tests
- Test individual methods
- Mock external dependencies
- Validate data extraction logic

### 2. Integration Tests
- Test full scraping workflow
- Validate against known data
- Performance benchmarking

### 3. End-to-End Tests
- Test with real Tokopedia website
- Validate anti-detection mechanisms
- Monitor success rates

## 🔐 Security Considerations

### 1. Rate Limiting
- Implement proper delays
- Respect robots.txt
- Monitor request frequency

### 2. Data Privacy
- Don't store sensitive information
- Anonymize data when possible
- Follow data protection regulations

### 3. Ethical Usage
- Respect website terms of service
- Use data responsibly
- Don't overload servers

---

**Note**: Dokumentasi ini akan terus diperbarui seiring dengan perkembangan teknologi dan perubahan pada website Tokopedia.