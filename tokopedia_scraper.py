import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

class TokopediaScraper:
    def __init__(self, headless=False):
        """
        Inisialisasi scraper Tokopedia
        Args:
            headless (bool): Jika True, browser akan berjalan tanpa GUI
        """
        self.driver = None
        self.headless = headless
        self.base_url = "https://www.tokopedia.com"
        self.search_url = "https://www.tokopedia.com/search"
        
    def setup_driver(self):
        """Setup Chrome WebDriver dengan konfigurasi optimal"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Konfigurasi untuk menghindari deteksi bot
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent yang realistis
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set window size
        self.driver.set_window_size(1920, 1080)
        
    def navigate_to_search_page(self, search_query):
        """
        Navigasi ke halaman pencarian Tokopedia
        Args:
            search_query (str): Kata kunci pencarian
        """
        try:
            # Encode query untuk URL
            encoded_query = urllib.parse.quote(search_query)
            
            # Buat URL pencarian
            search_url = f"{self.search_url}?st=&q={encoded_query}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource="
            
            print(f"Navigasi ke: {search_url}")
            self.driver.get(search_url)
            
            # Tunggu halaman dimuat
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='divSRPContentProducts']"))
            )
            
            print("Halaman pencarian berhasil dimuat")
            return True
            
        except TimeoutException:
            print("Timeout saat memuat halaman pencarian")
            return False
        except Exception as e:
            print(f"Error saat navigasi: {str(e)}")
            return False
    
    def auto_scroll(self, max_scrolls=10, scroll_pause_time=2):
        """
        Melakukan scrolling otomatis untuk memuat lebih banyak produk
        Args:
            max_scrolls (int): Jumlah maksimal scroll
            scroll_pause_time (int): Waktu jeda antar scroll (detik)
        """
        print("Memulai auto-scrolling...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            # Scroll ke bawah
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Tunggu konten baru dimuat
            time.sleep(scroll_pause_time)
            
            # Hitung tinggi baru
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Jika tinggi tidak berubah, berarti sudah di akhir halaman
            if new_height == last_height:
                print("Sudah mencapai akhir halaman")
                break
                
            last_height = new_height
            scroll_count += 1
            print(f"Scroll ke-{scroll_count} selesai")
            
        print(f"Auto-scrolling selesai. Total scroll: {scroll_count}")
    
    def extract_product_data(self, product_element):
        """
        Ekstrak data produk dari elemen HTML
        Args:
            product_element: Elemen HTML produk
        Returns:
            dict: Data produk yang sudah diekstrak
        """
        product_data = {
            'nama_produk': '',
            'harga_produk': '',
            'jumlah_terjual': '',
            'rating_produk': '',
            'lokasi_toko': ''
        }
        
        try:
            # Konversi elemen ke BeautifulSoup untuk parsing yang lebih mudah
            soup = BeautifulSoup(product_element.get_attribute('outerHTML'), 'html.parser')
            
            # 1. Scraping Nama Produk
            nama_produk_element = soup.select_one('div.SzILjt4fxHUFNVT48ZPhHA== span.+tnoqZhn89+NHUA43BpiJg==')
            if nama_produk_element:
                product_data['nama_produk'] = nama_produk_element.get_text(strip=True)
            
            # 2. Scraping Harga Produk
            harga_produk_element = soup.select_one('div.urMOIDHH7I0Iy1Dv2oFaNw==.HJhoi0tEIlowsgSNDNWVXg==')
            if harga_produk_element:
                product_data['harga_produk'] = harga_produk_element.get_text(strip=True)
            
            # 3. Scraping Jumlah Terjual
            jumlah_terjual_element = soup.select_one('span.u6SfjDD2WiBlNW7zHmzRhQ==')
            if jumlah_terjual_element:
                product_data['jumlah_terjual'] = jumlah_terjual_element.get_text(strip=True)
            
            # 4. Scraping Rating Produk
            rating_produk_element = soup.select_one('div._8BRsFZmjhjt-Zm-1rWcg2w== span._2NfJxPu4JC-55aCJ8bEsyw==')
            if rating_produk_element:
                product_data['rating_produk'] = rating_produk_element.get_text(strip=True)
            
            # 5. Scraping Lokasi Toko
            lokasi_toko_elements = soup.select('div.ljZNQLe6R-7wAWexijt7lA== div._1yoE8Ml3qwvn-r+EZ5hlbA== span')
            if lokasi_toko_elements:
                lokasi_parts = []
                for element in lokasi_toko_elements:
                    text = element.get_text(strip=True)
                    if text:
                        lokasi_parts.append(text)
                product_data['lokasi_toko'] = ' | '.join(lokasi_parts)
                
        except Exception as e:
            print(f"Error saat ekstraksi data produk: {str(e)}")
            
        return product_data
    
    def scrape_products(self, search_query, max_scrolls=10):
        """
        Scraping produk dari halaman pencarian Tokopedia
        Args:
            search_query (str): Kata kunci pencarian
            max_scrolls (int): Jumlah maksimal scroll
        Returns:
            list: List data produk
        """
        try:
            # Setup driver
            self.setup_driver()
            
            # Navigasi ke halaman pencarian
            if not self.navigate_to_search_page(search_query):
                return []
            
            # Lakukan auto-scrolling
            self.auto_scroll(max_scrolls=max_scrolls)
            
            # Tunggu sebentar untuk memastikan semua konten dimuat
            time.sleep(3)
            
            # Cari semua elemen produk
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='divSRPContentProducts'] > div")
            
            print(f"Ditemukan {len(product_elements)} elemen produk")
            
            products_data = []
            
            for i, product_element in enumerate(product_elements):
                try:
                    product_data = self.extract_product_data(product_element)
                    
                    # Hanya tambahkan jika ada data yang berhasil diekstrak
                    if any(product_data.values()):
                        product_data['search_query'] = search_query
                        products_data.append(product_data)
                        print(f"Produk {i+1}: {product_data['nama_produk'][:50]}...")
                    
                except Exception as e:
                    print(f"Error saat memproses produk {i+1}: {str(e)}")
                    continue
            
            print(f"Total {len(products_data)} produk berhasil diekstrak")
            return products_data
            
        except Exception as e:
            print(f"Error saat scraping: {str(e)}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_to_csv(self, data, filename):
        """
        Simpan data ke file CSV
        Args:
            data (list): Data produk
            filename (str): Nama file CSV
        """
        if not data:
            print("Tidak ada data untuk disimpan")
            return
            
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data berhasil disimpan ke {filename}")
        except Exception as e:
            print(f"Error saat menyimpan CSV: {str(e)}")
    
    def save_to_json(self, data, filename):
        """
        Simpan data ke file JSON
        Args:
            data (list): Data produk
            filename (str): Nama file JSON
        """
        if not data:
            print("Tidak ada data untuk disimpan")
            return
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Data berhasil disimpan ke {filename}")
        except Exception as e:
            print(f"Error saat menyimpan JSON: {str(e)}")

def main():
    """
    Fungsi utama untuk menjalankan scraper
    """
    print("=== Tokopedia Scraper ===")
    print("Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman")
    print("=" * 50)
    
    # Inisialisasi scraper
    scraper = TokopediaScraper(headless=False)  # Set True untuk headless mode
    
    # Input pencarian dari user
    search_query = input("Masukkan kata kunci pencarian (contoh: cabai, cabai rawit): ").strip()
    
    if not search_query:
        print("Kata kunci pencarian tidak boleh kosong!")
        return
    
    print(f"\nMemulai scraping untuk: '{search_query}'")
    print("=" * 50)
    
    # Lakukan scraping
    products_data = scraper.scrape_products(search_query, max_scrolls=5)
    
    if products_data:
        # Generate filename berdasarkan query
        safe_query = search_query.replace(' ', '_').replace('/', '_')
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        csv_filename = f"tokopedia_{safe_query}_{timestamp}.csv"
        json_filename = f"tokopedia_{safe_query}_{timestamp}.json"
        
        # Simpan data
        scraper.save_to_csv(products_data, csv_filename)
        scraper.save_to_json(products_data, json_filename)
        
        # Tampilkan ringkasan
        print("\n" + "=" * 50)
        print("RINGKASAN SCRAPING")
        print("=" * 50)
        print(f"Kata kunci: {search_query}")
        print(f"Total produk: {len(products_data)}")
        print(f"File CSV: {csv_filename}")
        print(f"File JSON: {json_filename}")
        
        # Tampilkan sample data
        if products_data:
            print("\nSAMPLE DATA (3 produk pertama):")
            print("-" * 50)
            for i, product in enumerate(products_data[:3]):
                print(f"Produk {i+1}:")
                for key, value in product.items():
                    print(f"  {key}: {value}")
                print()
        
    else:
        print("Tidak ada data yang berhasil di-scrape")

if __name__ == "__main__":
    main()