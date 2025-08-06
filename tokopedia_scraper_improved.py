import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import quote
import json
import csv
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import os

class TokopediaScraperAdvanced:
    def __init__(self, headless=False):
        """
        Inisialisasi scraper dengan fitur advanced untuk scraping otomatis
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.setup_driver()
        
        # Headers untuk requests fallback
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def setup_driver(self):
        """
        Setup Chrome driver dengan konfigurasi anti-detection
        """
        try:
            # Gunakan undetected_chromedriver untuk menghindari deteksi bot
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # Konfigurasi untuk menghindari deteksi
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent yang realistis
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Window size yang realistis
            options.add_argument('--window-size=1920,1080')
            
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Setup wait
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Browser driver berhasil diinisialisasi")
            
        except Exception as e:
            print(f"❌ Error setup driver: {e}")
            print("🔄 Mencoba setup driver alternatif...")
            self.setup_fallback_driver()

    def setup_fallback_driver(self):
        """
        Setup driver alternatif jika undetected_chromedriver gagal
        """
        try:
            options = Options()
            
            if self.headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Browser driver alternatif berhasil diinisialisasi")
            
        except Exception as e:
            print(f"❌ Error setup driver alternatif: {e}")
            print("⚠️  Akan menggunakan requests sebagai fallback")

    def navigate_to_tokopedia_home(self):
        """
        Navigasi ke halaman utama Tokopedia terlebih dahulu
        """
        try:
            print("🏠 Mengakses halaman utama Tokopedia...")
            
            if self.driver:
                # Akses halaman utama
                self.driver.get("https://www.tokopedia.com/")
                
                # Tunggu halaman dimuat
                time.sleep(random.uniform(3, 5))
                
                # Scroll sedikit untuk simulasi user behavior
                self.driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(random.uniform(1, 2))
                
                print("✅ Berhasil mengakses halaman utama Tokopedia")
                return True
            else:
                print("⚠️  Driver tidak tersedia, menggunakan requests")
                return False
                
        except Exception as e:
            print(f"❌ Error mengakses halaman utama: {e}")
            return False

    def scrape_until_target_reached(self, keyword, target_count, max_pages=50):
        """
        Scrape produk hingga mencapai target jumlah yang diinginkan
        """
        all_products = []
        current_page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        print(f"🎯 Target scraping: {target_count} produk")
        print(f"🔍 Keyword: '{keyword}'")
        
        try:
            # Langkah 1: Akses halaman utama terlebih dahulu
            if not self.navigate_to_tokopedia_home():
                print("⚠️  Gagal mengakses halaman utama, menggunakan metode alternatif")
                return self.scrape_until_target_fallback(keyword, target_count, max_pages)
            
            while len(all_products) < target_count and current_page <= max_pages:
                print(f"\n📄 Halaman {current_page} - Progress: {len(all_products)}/{target_count} produk")
                
                # Langkah 2: Navigasi ke halaman pencarian
                if current_page == 1:
                    search_url = self.build_search_url(keyword)
                else:
                    search_url = self.build_search_url(keyword, current_page)
                
                print(f"🔍 Mengakses: {search_url}")
                
                self.driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                # Langkah 3: Scroll otomatis untuk memuat konten
                self.auto_scroll_page()
                
                # Langkah 4: Ekstrak data produk
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                products = self.extract_product_data_improved(soup)
                
                if products:
                    # Filter produk berdasarkan keyword
                    filtered_products = self.filter_products_by_keyword(products, keyword)
                    
                    if filtered_products:
                        all_products.extend(filtered_products)
                        consecutive_empty_pages = 0
                        print(f"✅ Halaman {current_page}: {len(filtered_products)} produk valid ditemukan")
                        print(f"📊 Total produk: {len(all_products)}/{target_count}")
                    else:
                        print(f"⚠️  Halaman {current_page}: Semua produk tidak mengandung keyword")
                        consecutive_empty_pages += 1
                else:
                    print(f"⚠️  Halaman {current_page}: Tidak ada produk ditemukan")
                    consecutive_empty_pages += 1
                
                # Cek apakah terlalu banyak halaman kosong berturut-turut
                if consecutive_empty_pages >= max_consecutive_empty:
                    print(f"⚠️  {max_consecutive_empty} halaman kosong berturut-turut, berhenti scraping")
                    break
                
                current_page += 1
                
                # Delay antar halaman
                time.sleep(random.uniform(3, 6))
            
            # Jika belum mencapai target, coba halaman berikutnya
            if len(all_products) < target_count:
                print(f"⚠️  Hanya berhasil mendapatkan {len(all_products)} produk dari {target_count} yang diinginkan")
            
            return all_products[:target_count]  # Batasi sesuai target
            
        except Exception as e:
            print(f"❌ Error dalam scraping: {e}")
            return all_products[:target_count]

    def filter_products_by_keyword(self, products, keyword):
        """
        Filter produk berdasarkan keyword dalam nama produk
        """
        filtered_products = []
        keyword_lower = keyword.lower()
        
        for product in products:
            product_name = product.get('nama_produk', '').lower()
            
            # Cek apakah keyword ada dalam nama produk
            if keyword_lower in product_name:
                filtered_products.append(product)
            else:
                print(f"❌ Produk dihapus: '{product.get('nama_produk', '')[:50]}...' (tidak mengandung keyword)")
        
        return filtered_products

    def scrape_until_target_fallback(self, keyword, target_count, max_pages=50):
        """
        Metode fallback menggunakan requests jika Selenium gagal
        """
        print("🔄 Menggunakan metode fallback dengan requests...")
        
        all_products = []
        current_page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        while len(all_products) < target_count and current_page <= max_pages:
            try:
                search_url = self.build_search_url(keyword, current_page)
                print(f"🔍 Mengakses: {search_url}")
                
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                products = self.extract_product_data_improved(soup)
                
                if products:
                    # Filter produk berdasarkan keyword
                    filtered_products = self.filter_products_by_keyword(products, keyword)
                    
                    if filtered_products:
                        all_products.extend(filtered_products)
                        consecutive_empty_pages = 0
                        print(f"✅ Halaman {current_page}: {len(filtered_products)} produk valid ditemukan")
                        print(f"📊 Total produk: {len(all_products)}/{target_count}")
                    else:
                        print(f"⚠️  Halaman {current_page}: Semua produk tidak mengandung keyword")
                        consecutive_empty_pages += 1
                else:
                    print(f"⚠️  Halaman {current_page}: Tidak ada produk ditemukan")
                    consecutive_empty_pages += 1
                
                # Cek apakah terlalu banyak halaman kosong berturut-turut
                if consecutive_empty_pages >= max_consecutive_empty:
                    print(f"⚠️  {max_consecutive_empty} halaman kosong berturut-turut, berhenti scraping")
                    break
                
                current_page += 1
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"❌ Error halaman {current_page}: {e}")
                consecutive_empty_pages += 1
                current_page += 1
        
        return all_products[:target_count]

    def auto_scroll_page(self):
        """
        Scroll otomatis untuk memuat konten yang lazy-loaded
        """
        print("📜 Melakukan scrolling otomatis...")
        
        try:
            # Scroll bertahap untuk simulasi user behavior
            scroll_pause_time = random.uniform(1, 2)
            
            # Scroll ke bawah secara bertahap
            for i in range(5):
                # Scroll ke bawah
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                
                # Scroll ke atas sedikit
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
                time.sleep(scroll_pause_time)
                
                # Cek apakah ada konten baru yang dimuat
                current_height = self.driver.execute_script("return document.body.scrollHeight")
                
                print(f"   📍 Scroll {i+1}/5 - Height: {current_height}")
            
            # Scroll ke atas untuk memulai ekstraksi
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            print("✅ Scrolling selesai")
            
        except Exception as e:
            print(f"⚠️  Error dalam scrolling: {e}")

    def build_search_url(self, keyword, page=1):
        """
        Membangun URL pencarian yang akurat
        """
        encoded_keyword = quote(keyword)
        
        if page == 1:
            search_url = f"https://www.tokopedia.com/search?st=&q={encoded_keyword}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource="
        else:
            search_url = f"https://www.tokopedia.com/search?st=&q={encoded_keyword}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource=&page={page}"
        
        return search_url

    def extract_product_data_improved(self, soup):
        """
        Ekstrak data produk dengan pendekatan yang lebih robust untuk SPA
        """
        products = []
        
        print("🔍 Menganalisis struktur halaman...")
        
        # Cari container produk dengan berbagai strategi
        product_containers = self.find_product_containers_improved(soup)
        
        if not product_containers:
            print("❌ Tidak ditemukan container produk")
            return products
        
        print(f"✅ Ditemukan {len(product_containers)} container produk")
        
        for idx, container in enumerate(product_containers):
            try:
                product_data = self.extract_single_product_improved(container, idx + 1)
                if product_data and self.validate_product_data(product_data):
                    products.append(product_data)
                    print(f"📦 Produk {len(products)}: {product_data['nama_produk'][:50]}... | {product_data['harga']}")
            except Exception as e:
                print(f"❌ Error ekstrak produk {idx + 1}: {e}")
                continue
        
        return products

    def find_product_containers_improved(self, soup):
        """
        Mencari container produk dengan strategi yang diperbaiki untuk SPA
        """
        containers = []
        
        # Strategi 1: Cari berdasarkan data-testid yang umum di Tokopedia
        container_selectors = [
            '[data-testid="master-product-card"]',
            '[data-testid*="product-card"]',
            '[data-testid*="product"]',
            'div[class*="css-"]',  # Tokopedia menggunakan CSS modules
            'div[class*="product"]',
            'div[class*="card"]',
            'div[class*="item"]'
        ]
        
        for selector in container_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"🎯 Ditemukan {len(elements)} container dengan selector: {selector}")
                containers = elements
                break
        
        # Strategi 2: Cari berdasarkan pola link produk
        if not containers:
            print("🔄 Menggunakan strategi berbasis link produk...")
            product_links = soup.find_all('a', href=re.compile(r'/p/'))
            
            for link in product_links:
                # Cari parent container
                parent = link.parent
                for _ in range(5):  # Naik maksimal 5 level
                    if parent and parent.name == 'div':
                        # Cek apakah parent ini memiliki konten yang cukup
                        text_content = parent.get_text()
                        if len(text_content) > 50 and ('Rp' in text_content or 'terjual' in text_content.lower()):
                            containers.append(parent)
                            break
                    parent = parent.parent if parent else None
        
        # Strategi 3: Cari berdasarkan harga
        if not containers:
            print("🔄 Menggunakan strategi berbasis harga...")
            price_elements = soup.find_all(text=re.compile(r'Rp[\d,.\s]+'))
            
            for price_element in price_elements:
                parent = price_element.parent
                for _ in range(5):
                    if parent and parent.name == 'div':
                        text_content = parent.get_text()
                        if len(text_content) > 50:
                            containers.append(parent)
                            break
                    parent = parent.parent if parent else None
        
        # Hapus duplikat dan batasi jumlah
        unique_containers = []
        seen_texts = set()
        
        for container in containers:
            text_content = container.get_text()[:100]  # Ambil 100 karakter pertama
            if text_content not in seen_texts:
                unique_containers.append(container)
                seen_texts.add(text_content)
        
        print(f"📊 Total container unik ditemukan: {len(unique_containers)}")
        return unique_containers[:50]  # Batasi maksimal 50 produk

    def extract_single_product_improved(self, element, product_number):
        """
        Ekstrak data produk dengan pendekatan yang lebih robust
        """
        product_data = {
            'nama_produk': '',
            'harga': '',
            'rating': '',
            'jumlah_terjual': '',
            'nama_toko': '',
            'link_produk': '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Ekstrak nama produk
            product_data['nama_produk'] = self.extract_product_name_improved(element)
            
            # Ekstrak harga
            product_data['harga'] = self.extract_price_improved(element)
            
            # Ekstrak rating
            product_data['rating'] = self.extract_rating_improved(element)
            
            # Ekstrak jumlah terjual
            product_data['jumlah_terjual'] = self.extract_sold_count_improved(element)
            
            # Ekstrak nama toko
            product_data['nama_toko'] = self.extract_shop_name_improved(element)
            
            # Ekstrak link produk
            product_data['link_produk'] = self.extract_product_link_improved(element)
            
            return product_data
            
        except Exception as e:
            print(f"❌ Error ekstrak produk {product_number}: {e}")
            return None

    def extract_product_name_improved(self, element):
        """Ekstrak nama produk dengan strategi yang diperbaiki"""
        name = ""
        
        # Strategi 1: Cari berdasarkan link produk
        links = element.find_all('a', href=re.compile(r'/p/'))
        for link in links:
            text = link.get_text(strip=True)
            if len(text) > 10 and 'Rp' not in text and not re.match(r'^[\d.,]+$', text):
                name = text
                break
        
        # Strategi 2: Cari teks terpanjang yang masuk akal
        if not name:
            all_texts = []
            for tag in element.find_all(['span', 'p', 'h1', 'h2', 'h3', 'a', 'div']):
                text = tag.get_text(strip=True)
                if (10 < len(text) < 200 and 
                    'Rp' not in text and 
                    not re.match(r'^[\d.,]+$', text) and
                    not re.match(r'^[1-5]\.[0-9]$', text) and
                    'terjual' not in text.lower()):
                    all_texts.append(text)
            
            if all_texts:
                # Ambil yang terpanjang
                name = max(all_texts, key=len)
        
        return name or "Nama tidak ditemukan"

    def extract_price_improved(self, element):
        """Ekstrak harga dengan strategi yang diperbaiki"""
        price = ""
        
        # Pattern untuk harga
        price_pattern = re.compile(r'Rp[\s]*[\d,.\s]+')
        
        # Cari di semua text nodes
        all_text = element.get_text()
        price_matches = price_pattern.findall(all_text)
        
        if price_matches:
            # Ambil harga pertama yang ditemukan
            price = price_matches[0].strip()
        
        return price or "Harga tidak ditemukan"

    def extract_rating_improved(self, element):
        """Ekstrak rating produk"""
        rating = ""
        
        # Pattern untuk rating
        rating_pattern = re.compile(r'\b([1-5]\.[0-9])\b')
        all_text = element.get_text()
        rating_matches = rating_pattern.findall(all_text)
        
        if rating_matches:
            rating = rating_matches[0]
        
        return rating

    def extract_sold_count_improved(self, element):
        """Ekstrak jumlah terjual"""
        sold = ""
        
        # Pattern untuk jumlah terjual
        sold_patterns = [
            r'(\d+)\s*terjual',
            r'(\d+)\s*sold',
            r'terjual\s*(\d+)',
            r'sold\s*(\d+)',
            r'(\d+[kK]?)\s*terjual'
        ]
        
        all_text = element.get_text().lower()
        
        for pattern in sold_patterns:
            match = re.search(pattern, all_text)
            if match:
                sold = match.group(1) + " terjual"
                break
        
        return sold

    def extract_shop_name_improved(self, element):
        """Ekstrak nama toko"""
        shop_name = ""
        
        # Cari teks yang mungkin nama toko
        spans = element.find_all('span')
        texts = [span.get_text(strip=True) for span in spans]
        
        # Filter teks yang mungkin nama toko
        possible_shop_names = []
        for text in texts:
            if (len(text) > 3 and len(text) < 100 and
                not re.search(r'Rp|terjual|\d+\.\d+|rating', text, re.IGNORECASE) and
                not re.match(r'^[\d.,]+$', text)):
                possible_shop_names.append(text)
        
        # Ambil yang terakhir (biasanya nama toko di bagian bawah)
        if possible_shop_names:
            shop_name = possible_shop_names[-1]
        
        return shop_name

    def extract_product_link_improved(self, element):
        """Ekstrak link produk"""
        link = ""
        
        # Cari link yang mengarah ke halaman produk
        links = element.find_all('a', href=True)
        for a_tag in links:
            href = a_tag.get('href', '')
            if '/p/' in href:
                if href.startswith('/'):
                    link = 'https://www.tokopedia.com' + href
                else:
                    link = href
                break
        
        return link

    def validate_product_data(self, product_data):
        """Validasi data produk minimal"""
        if not product_data:
            return False
        
        # Minimal harus ada nama atau harga
        has_name = product_data.get('nama_produk') and product_data['nama_produk'] != "Nama tidak ditemukan"
        has_price = product_data.get('harga') and product_data['harga'] != "Harga tidak ditemukan"
        
        return has_name or has_price

    def save_to_csv_auto(self, products, keyword, target_count):
        """Menyimpan data ke file CSV secara otomatis dengan format nama yang ditentukan"""
        if not products:
            print("⚠️  Tidak ada data untuk disimpan")
            return False
        
        # Format nama file: Tokopedia_keywordproduk_jumlahproduk.csv
        safe_keyword = re.sub(r'[^\w\s-]', '', keyword).strip().replace(' ', '_')
        filename = f"Tokopedia_{safe_keyword}_{len(products)}.csv"
        
        try:
            df = pd.DataFrame(products)
            
            # Bersihkan data
            for col in df.columns:
                if col != 'timestamp':
                    df[col] = df[col].astype(str).str.strip()
            
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"\n💾 Data berhasil disimpan otomatis ke: {filename}")
            print(f"📊 Jumlah baris: {len(df)}")
            print(f"📁 Path file: {os.path.abspath(filename)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error menyimpan ke CSV: {e}")
            return False

    def close_driver(self):
        """Tutup browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Browser driver ditutup")
            except Exception as e:
                print(f"⚠️  Error menutup driver: {e}")

    def display_summary(self, products, keyword, target_count):
        """Tampilkan ringkasan data"""
        if not products:
            print("⚠️  Tidak ada data untuk ditampilkan")
            return
        
        print("\n" + "="*80)
        print("📊 RINGKASAN HASIL SCRAPING")
        print("="*80)
        
        print(f"🎯 Target Produk: {target_count}")
        print(f"✅ Produk Berhasil: {len(products)}")
        print(f"🔍 Keyword: '{keyword}'")
        print(f"📈 Persentase Pencapaian: {(len(products)/target_count)*100:.1f}%")
        
        # Tampilkan sample data
        print(f"\n📋 SAMPLE DATA (3 produk pertama):")
        print("-" * 80)
        
        for i, product in enumerate(products[:3]):
            print(f"\nPRODUK {i+1}:")
            print(f"  📦 Nama: {product['nama_produk']}")
            print(f"  💰 Harga: {product['harga']}")
            print(f"  ⭐ Rating: {product['rating'] if product['rating'] else 'Tidak ada'}")
            print(f"  📈 Terjual: {product['jumlah_terjual'] if product['jumlah_terjual'] else 'Tidak ada'}")
            print(f"  🏪 Toko: {product['nama_toko'] if product['nama_toko'] else 'Tidak ada'}")
            print(f"  🔗 Link: {product['link_produk'][:60]}{'...' if len(product['link_produk']) > 60 else ''}")

def main():
    """
    Fungsi utama yang diperbaiki dengan fitur otomatis
    """
    print("="*80)
    print("🤖 TOKOPEDIA SCRAPER - VERSI ADVANCED")
    print("👨‍💻 Dikembangkan oleh: Pradipta Deska Pryanda")
    print("🔧 Diperbaiki oleh: Dosen Data Mining (30 tahun pengalaman)")
    print("="*80)
    print("✨ FITUR BARU:")
    print("   • Scraping otomatis hingga target tercapai")
    print("   • Validasi keyword dalam nama produk")
    print("   • Auto-save CSV tanpa konfirmasi")
    print("   • Format nama file: Tokopedia_keyword_jumlah.csv")
    print("   • Anti-detection mechanism")
    print("="*80)
    
    scraper = None
    
    try:
        # Input dari user
        keyword = input("\n🔍 Masukkan keyword pencarian: ").strip()
        if not keyword or len(keyword) < 2:
            print("❌ Keyword harus minimal 2 karakter!")
            return
        
        target_count_input = input("🎯 Jumlah produk yang diinginkan (1-1000): ").strip()
        try:
            target_count = int(target_count_input)
            if target_count < 1 or target_count > 1000:
                print("❌ Jumlah produk harus antara 1-1000!")
                return
        except ValueError:
            print("❌ Input jumlah produk tidak valid!")
            return
        
        headless_input = input("🖥️  Mode headless? (y/n, default=n): ").strip().lower()
        headless = headless_input in ['y', 'yes', 'ya']
        
        # Inisialisasi scraper
        scraper = TokopediaScraperAdvanced(headless=headless)
        
        # Konfirmasi
        print(f"\n📋 KONFIGURASI:")
        print(f"   🔍 Keyword: '{keyword}'")
        print(f"   🎯 Target Produk: {target_count}")
        print(f"   🖥️  Headless: {headless}")
        print(f"   💾 Auto-save: Ya (format: Tokopedia_{keyword}_{target_count}.csv)")
        
        print(f"\n🚀 MEMULAI SCRAPING OTOMATIS...")
        print("⚠️  Proses akan berjalan hingga target tercapai atau tidak ada data lagi")
        
        # Jalankan scraping otomatis
        start_time = datetime.now()
        
        products = scraper.scrape_until_target_reached(keyword, target_count)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if products:
            print(f"\n🎉 SCRAPING BERHASIL!")
            print(f"⏱️  Waktu eksekusi: {duration}")
            
            # Tampilkan ringkasan
            scraper.display_summary(products, keyword, target_count)
            
            # Simpan ke file secara otomatis
            print(f"\n💾 MENYIMPAN KE CSV OTOMATIS...")
            if scraper.save_to_csv_auto(products, keyword, target_count):
                print("✅ File berhasil disimpan otomatis!")
            else:
                print("❌ Gagal menyimpan file!")
        else:
            print(f"\n❌ TIDAK ADA PRODUK YANG BERHASIL DI-SCRAPE")
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  SCRAPING DIHENTIKAN OLEH USER")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    finally:
        if scraper:
            scraper.close_driver()
        print(f"\n👋 Terima kasih telah menggunakan Tokopedia Scraper Advanced!")

if __name__ == "__main__":
    main()