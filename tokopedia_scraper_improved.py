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

class TokopediaScraperImproved:
    def __init__(self, headless=False):
        """
        Inisialisasi scraper dengan Selenium untuk simulasi browser yang lebih realistis
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

    def search_products_with_scrolling(self, keyword, max_pages=3):
        """
        Mencari produk dengan scrolling otomatis dan navigasi yang benar
        """
        all_products = []
        
        try:
            # Langkah 1: Akses halaman utama terlebih dahulu
            if not self.navigate_to_tokopedia_home():
                print("⚠️  Gagal mengakses halaman utama, menggunakan metode alternatif")
                return self.search_products_fallback(keyword, max_pages)
            
            # Langkah 2: Navigasi ke halaman pencarian
            search_url = self.build_search_url(keyword)
            print(f"🔍 Mengakses halaman pencarian: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            # Langkah 3: Scroll otomatis untuk memuat konten
            self.auto_scroll_page()
            
            # Langkah 4: Ekstrak data produk
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            products = self.extract_product_data_improved(soup)
            all_products.extend(products)
            
            print(f"✅ Halaman 1: {len(products)} produk ditemukan")
            
            # Langkah 5: Navigasi ke halaman berikutnya jika diperlukan
            for page in range(2, max_pages + 1):
                if self.navigate_to_next_page(page):
                    # Scroll lagi di halaman baru
                    self.auto_scroll_page()
                    
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    products = self.extract_product_data_improved(soup)
                    if products:
                        all_products.extend(products)
                        print(f"✅ Halaman {page}: {len(products)} produk ditemukan")
                    else:
                        print(f"⚠️  Halaman {page}: Tidak ada produk ditemukan")
                        break
                else:
                    print(f"⚠️  Tidak dapat mengakses halaman {page}")
                    break
                
                # Delay antar halaman
                time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            print(f"❌ Error dalam pencarian produk: {e}")
            
        return all_products

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

    def navigate_to_next_page(self, page_number):
        """
        Navigasi ke halaman berikutnya
        """
        try:
            # Cari tombol next page
            next_selectors = [
                f'a[data-testid="btn-page-{page_number}"]',
                f'a[aria-label="Page {page_number}"]',
                f'a[href*="page={page_number}"]',
                f'button[data-testid="btn-page-{page_number}"]'
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    next_button.click()
                    time.sleep(random.uniform(2, 4))
                    print(f"✅ Berhasil navigasi ke halaman {page_number}")
                    return True
                except TimeoutException:
                    continue
            
            # Jika tidak ditemukan, coba dengan URL langsung
            current_url = self.driver.current_url
            if "page=" in current_url:
                new_url = re.sub(r'page=\d+', f'page={page_number}', current_url)
            else:
                new_url = current_url + f'&page={page_number}'
            
            self.driver.get(new_url)
            time.sleep(random.uniform(3, 5))
            print(f"✅ Berhasil navigasi ke halaman {page_number} via URL")
            return True
            
        except Exception as e:
            print(f"❌ Error navigasi ke halaman {page_number}: {e}")
            return False

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

    def search_products_fallback(self, keyword, max_pages=3):
        """
        Metode fallback menggunakan requests jika Selenium gagal
        """
        print("🔄 Menggunakan metode fallback dengan requests...")
        
        all_products = []
        
        for page in range(1, max_pages + 1):
            try:
                search_url = self.build_search_url(keyword, page)
                print(f"🔍 Mengakses: {search_url}")
                
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                products = self.extract_product_data_improved(soup)
                
                if products:
                    all_products.extend(products)
                    print(f"✅ Halaman {page}: {len(products)} produk ditemukan")
                else:
                    print(f"⚠️  Halaman {page}: Tidak ada produk ditemukan")
                    break
                
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"❌ Error halaman {page}: {e}")
                break
        
        return all_products

    def save_to_csv(self, products, filename=None):
        """Menyimpan data ke file CSV"""
        if not products:
            print("⚠️  Tidak ada data untuk disimpan")
            return False
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tokopedia_scraping_improved_{timestamp}.csv'
        
        try:
            df = pd.DataFrame(products)
            
            # Bersihkan data
            for col in df.columns:
                if col != 'timestamp':
                    df[col] = df[col].astype(str).str.strip()
            
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"\n💾 Data berhasil disimpan ke: {filename}")
            print(f"📊 Jumlah baris: {len(df)}")
            
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

    def display_summary(self, products):
        """Tampilkan ringkasan data"""
        if not products:
            print("⚠️  Tidak ada data untuk ditampilkan")
            return
        
        print("\n" + "="*80)
        print("📊 RINGKASAN HASIL SCRAPING")
        print("="*80)
        
        print(f"🎯 Total Produk: {len(products)}")
        
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
    Fungsi utama yang diperbaiki
    """
    print("="*80)
    print("🤖 TOKOPEDIA SCRAPER - VERSI DIPERBAIKI")
    print("👨‍💻 Dikembangkan oleh: Pradipta Deska Pryanda")
    print("🔧 Diperbaiki oleh: Dosen Data Mining (30 tahun pengalaman)")
    print("="*80)
    print("✨ FITUR BARU:")
    print("   • Navigasi melalui halaman utama Tokopedia")
    print("   • Scrolling otomatis untuk memuat konten")
    print("   • Simulasi browser dengan Selenium")
    print("   • Anti-detection mechanism")
    print("="*80)
    
    scraper = None
    
    try:
        # Input dari user
        keyword = input("\n🔍 Masukkan keyword pencarian: ").strip()
        if not keyword or len(keyword) < 2:
            print("❌ Keyword harus minimal 2 karakter!")
            return
        
        max_pages_input = input("📄 Jumlah halaman (1-10, default=3): ").strip()
        max_pages = int(max_pages_input) if max_pages_input.isdigit() and 1 <= int(max_pages_input) <= 10 else 3
        
        headless_input = input("🖥️  Mode headless? (y/n, default=n): ").strip().lower()
        headless = headless_input in ['y', 'yes', 'ya']
        
        # Inisialisasi scraper
        scraper = TokopediaScraperImproved(headless=headless)
        
        # Konfirmasi
        print(f"\n📋 KONFIGURASI:")
        print(f"   🔍 Keyword: '{keyword}'")
        print(f"   📄 Halaman: {max_pages}")
        print(f"   🖥️  Headless: {headless}")
        
        confirm = input("\n🚀 Lanjutkan scraping? (y/n): ").lower()
        if confirm not in ['y', 'yes', 'ya']:
            print("❌ Scraping dibatalkan")
            return
        
        # Jalankan scraping
        print(f"\n🎬 MEMULAI SCRAPING...")
        start_time = datetime.now()
        
        products = scraper.search_products_with_scrolling(keyword, max_pages)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if products:
            print(f"\n🎉 SCRAPING BERHASIL!")
            print(f"⏱️  Waktu eksekusi: {duration}")
            
            # Tampilkan ringkasan
            scraper.display_summary(products)
            
            # Simpan ke file
            save_option = input("\n💾 Simpan ke file CSV? (y/n): ").lower()
            if save_option in ['y', 'yes', 'ya']:
                custom_filename = input("📁 Nama file (kosongkan untuk auto): ").strip()
                filename = custom_filename if custom_filename else None
                
                if scraper.save_to_csv(products, filename):
                    print("✅ File berhasil disimpan!")
        else:
            print(f"\n❌ TIDAK ADA PRODUK YANG BERHASIL DI-SCRAPE")
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  SCRAPING DIHENTIKAN OLEH USER")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    finally:
        if scraper:
            scraper.close_driver()
        print(f"\n👋 Terima kasih telah menggunakan Tokopedia Scraper!")

if __name__ == "__main__":
    main()