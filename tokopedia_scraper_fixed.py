import tempfile
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

def setup_driver():
    """
    Setup Chrome driver dengan options yang sesuai untuk scraping
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent yang realistis
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Mode headless untuk stability
    chrome_options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_window_size(1920, 1080)
        return driver
    except Exception as e:
        print(f"Error creating Chrome driver: {e}")
        # Fallback dengan options minimal
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

def scroll_to_load_content(driver, scroll_pause_time=2, max_scrolls=10):
    """
    Fungsi untuk scrolling otomatis agar konten tambahan dimuat
    """
    print("Memulai auto-scrolling...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    
    while scrolls < max_scrolls:
        # Scroll ke bagian paling bawah
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Tunggu konten baru dimuat
        time.sleep(scroll_pause_time)
        
        # Hitung tinggi baru
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Jika tidak ada konten baru, hentikan scrolling
        if new_height == last_height:
            print("Sudah mencapai akhir halaman")
            break
            
        last_height = new_height
        scrolls += 1
        print(f"Scroll ke-{scrolls} selesai")
    
    print(f"Auto-scrolling selesai. Total scroll: {scrolls}")

def scrape_tokopedia_search(keyword, max_products=50):
    """
    Fungsi utama untuk scraping data produk dari hasil pencarian Tokopedia
    """
    # Encode keyword untuk URL
    encoded_keyword = urllib.parse.quote(keyword)
    
    # Buat URL pencarian
    search_url = f"https://www.tokopedia.com/search?st=&q={encoded_keyword}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource="
    
    # Setup driver
    driver = setup_driver()
    products_data = []
    
    try:
        print(f"Membuka halaman pencarian untuk: {keyword}")
        print(f"URL: {search_url}")
        driver.get(search_url)
        
        # Tunggu halaman dimuat dengan explicit wait
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='divSRPContentProducts']"))
            )
            print("Halaman pencarian berhasil dimuat")
        except TimeoutException:
            print("Timeout saat memuat halaman, mencoba lanjutkan...")
        
        # Tunggu beberapa detik untuk memastikan halaman dimuat
        time.sleep(5)
        
        # Scroll untuk memuat lebih banyak konten
        print("Melakukan scrolling otomatis...")
        scroll_to_load_content(driver, max_scrolls=5)
        
        # Tunggu sebentar setelah scrolling
        time.sleep(3)
        
        # Dapatkan konten HTML setelah JavaScript dieksekusi
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Cari kontainer produk menggunakan selector yang benar untuk Tokopedia
        product_containers = []
        
        # Selector utama untuk Tokopedia
        main_selectors = [
            "div[data-testid='divSRPContentProducts'] > div",
            "div[data-testid='divSRPContentProducts'] div[data-testid*='product']",
            "div[data-testid='divSRPContentProducts'] div[class*='ProductCard']",
            "div[data-testid='divSRPContentProducts'] div[class*='product']"
        ]
        
        for selector in main_selectors:
            try:
                containers = soup.select(selector)
                if containers:
                    product_containers = containers
                    print(f"Menemukan {len(containers)} kontainer produk dengan selector: {selector}")
                    break
            except Exception as e:
                print(f"Selector {selector} error: {e}")
                continue
        
        # Fallback: cari semua div dalam container utama
        if not product_containers:
            print("Menggunakan pendekatan fallback...")
            main_container = soup.select_one("div[data-testid='divSRPContentProducts']")
            if main_container:
                # Cari semua div yang kemungkinan adalah produk
                all_divs = main_container.find_all('div', recursive=True)
                # Filter div yang memiliki konten yang cukup
                product_containers = [div for div in all_divs if len(div.get_text(strip=True)) > 20]
                print(f"Fallback menemukan {len(product_containers)} elemen potensial")
        
        print(f"Total kontainer produk yang ditemukan: {len(product_containers)}")
        
        # Counter untuk jumlah produk yang berhasil di-scrape
        product_count = 0
        
        # Iterasi setiap kontainer produk
        for container in product_containers:
            if product_count >= max_products:
                break
                
            try:
                # Inisialisasi dictionary untuk menyimpan data produk
                product_data = {
                    'nama_produk': '',
                    'harga_produk': '',
                    'jumlah_terjual': '',
                    'rating_produk': '',
                    'lokasi_toko': ''
                }
                
                # Ekstrak data menggunakan selector yang diberikan
                try:
                    # 1. Scraping Nama Produk
                    nama_element = container.select_one('div.SzILjt4fxHUFNVT48ZPhHA== span.+tnoqZhn89+NHUA43BpiJg==')
                    if nama_element:
                        product_data['nama_produk'] = nama_element.get_text(strip=True)
                    else:
                        # Fallback: cari elemen dengan teks yang panjang
                        text_elements = container.find_all(['div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
                        for elem in text_elements:
                            text = elem.get_text(strip=True)
                            if (len(text) > 10 and 
                                not text.startswith('Rp') and 
                                'terjual' not in text.lower() and 
                                not text.replace('.', '', 1).replace(',', '', 1).isdigit() and
                                len(text.split()) > 2):
                                product_data['nama_produk'] = text
                                break
                    
                    # 2. Scraping Harga Produk
                    harga_element = container.select_one('div.urMOIDHH7I0Iy1Dv2oFaNw==.HJhoi0tEIlowsgSNDNWVXg==')
                    if harga_element:
                        product_data['harga_produk'] = harga_element.get_text(strip=True)
                    else:
                        # Fallback: cari elemen dengan prefix 'Rp'
                        for elem in container.find_all(['div', 'span']):
                            text = elem.get_text(strip=True)
                            if text.startswith('Rp') and any(c.isdigit() for c in text):
                                product_data['harga_produk'] = text
                                break
                    
                    # 3. Scraping Jumlah Terjual
                    terjual_element = container.select_one('span.u6SfjDD2WiBlNW7zHmzRhQ==')
                    if terjual_element:
                        product_data['jumlah_terjual'] = terjual_element.get_text(strip=True)
                    else:
                        # Fallback: cari elemen dengan kata 'terjual'
                        for elem in container.find_all(['div', 'span']):
                            text = elem.get_text(strip=True)
                            if 'terjual' in text.lower() and any(c.isdigit() for c in text):
                                product_data['jumlah_terjual'] = text
                                break
                    
                    # 4. Scraping Rating Produk
                    rating_element = container.select_one('div._8BRsFZmjhjt-Zm-1rWcg2w== span._2NfJxPu4JC-55aCJ8bEsyw==')
                    if rating_element:
                        product_data['rating_produk'] = rating_element.get_text(strip=True)
                    else:
                        # Fallback: cari angka desimal
                        for elem in container.find_all(['div', 'span']):
                            text = elem.get_text(strip=True)
                            if ('.' in text and len(text) <= 4 and 
                                text.replace('.', '').isdigit()):
                                try:
                                    rating_val = float(text)
                                    if 0 <= rating_val <= 5:
                                        product_data['rating_produk'] = text
                                        break
                                except ValueError:
                                    continue
                    
                    # 5. Scraping Lokasi Toko
                    lokasi_elements = container.select('div.ljZNQLe6R-7wAWexijt7lA== div._1yoE8Ml3qwvn-r+EZ5hlbA== span')
                    if lokasi_elements:
                        lokasi_parts = []
                        for element in lokasi_elements:
                            text = element.get_text(strip=True)
                            if text:
                                lokasi_parts.append(text)
                        product_data['lokasi_toko'] = ' | '.join(lokasi_parts)
                    else:
                        # Fallback: cari lokasi berdasarkan pola
                        lokasi_parts = []
                        for elem in container.find_all(['div', 'span']):
                            text = elem.get_text(strip=True)
                            if (any(kata in text.lower() for kata in ['kab.', 'kota', 'toko', 'shop', 'jakarta', 'bandung', 'surabaya']) and 
                                len(text) > 3 and len(text) < 50):
                                lokasi_parts.append(text)
                        
                        if lokasi_parts:
                            product_data['lokasi_toko'] = ' | '.join(lokasi_parts[:2])
                
                except Exception as e:
                    print(f"Error saat ekstraksi data: {str(e)}")
                    continue
                
                # Validasi apakah produk memiliki data minimal
                if any(product_data.values()):
                    # Tambahkan keyword pencarian
                    product_data['search_query'] = keyword
                    products_data.append(product_data)
                    product_count += 1
                    print(f"Produk #{product_count} berhasil di-scrape: {product_data['nama_produk'][:50]}...")
                
            except Exception as e:
                print(f"Error saat memproses kontainer produk: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error utama: {str(e)}")
        
    finally:
        driver.quit()
    
    return products_data

def save_to_csv(products_data, filename="tokopedia_products.csv"):
    """
    Simpan data produk ke file CSV
    """
    if products_data:
        df = pd.DataFrame(products_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Data berhasil disimpan ke {filename}")
        print(f"Total produk yang di-scrape: {len(products_data)}")
    else:
        print("Tidak ada data yang berhasil di-scrape")

def save_to_json(products_data, filename="tokopedia_products.json"):
    """
    Simpan data produk ke file JSON
    """
    if products_data:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
        print(f"Data berhasil disimpan ke {filename}")
    else:
        print("Tidak ada data yang berhasil di-scrape")

def main():
    """
    Fungsi utama untuk menjalankan scraping
    """
    print("=== Scraping Data Produk Tokopedia ===")
    print("Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman")
    print("="*50)
    
    # Input keyword pencarian dari user
    keyword = input("Masukkan keyword pencarian (contoh: cabai, cabai rawit): ").strip()
    
    if not keyword:
        print("Keyword tidak boleh kosong!")
        return
    
    print(f"Memulai scraping untuk keyword: '{keyword}'")
    print("="*50)
    
    # Lakukan scraping
    products = scrape_tokopedia_search(keyword, max_products=30)
    
    # Tampilkan hasil
    if products:
        print("\n=== HASIL SCRAPING ===")
        print(f"Total produk yang berhasil di-scrape: {len(products)}")
        
        # Tampilkan 5 produk pertama sebagai contoh
        for i, product in enumerate(products[:5], 1):
            print(f"\nProduk #{i}:")
            for key, value in product.items():
                if value:  # Hanya tampilkan yang ada datanya
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Simpan ke file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_keyword = keyword.replace(' ', '_').replace('/', '_')
        
        csv_filename = f"tokopedia_{safe_keyword}_{timestamp}.csv"
        json_filename = f"tokopedia_{safe_keyword}_{timestamp}.json"
        
        save_to_csv(products, csv_filename)
        save_to_json(products, json_filename)
        
        print(f"\n✅ File output:")
        print(f"  📄 CSV: {csv_filename}")
        print(f"  📄 JSON: {json_filename}")
        
    else:
        print("❌ Tidak ada data produk yang berhasil di-scrape.")
        print("Tips:")
        print("1. Pastikan koneksi internet stabil")
        print("2. Coba keyword yang berbeda")
        print("3. Pastikan Chrome browser terinstall")

# Fungsi tambahan untuk scraping multiple keywords
def scrape_multiple_keywords(keywords_list):
    """
    Scraping untuk multiple keywords
    """
    all_products = []
    
    for keyword in keywords_list:
        print(f"\n--- Scraping keyword: {keyword} ---")
        products = scrape_tokopedia_search(keyword, max_products=20)
        all_products.extend(products)
        time.sleep(5)  # Delay antar pencarian
    
    return all_products

if __name__ == "__main__":
    main()