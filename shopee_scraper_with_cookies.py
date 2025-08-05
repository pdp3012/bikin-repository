import os
import time
import json
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

# Direktori untuk menyimpan cookies
COOKIE_DIR = r"D:\PKL BPS Surabaya"
COOKIE_FILE = os.path.join(COOKIE_DIR, "shopee_cookies.json")

# Fungsi untuk memastikan direktori cookies ada
def ensure_cookie_dir():
    try:
        if not os.path.exists(COOKIE_DIR):
            os.makedirs(COOKIE_DIR)
            print(f"✅ Direktori cookies dibuat: {COOKIE_DIR}")
    except Exception as e:
        print(f"⚠️ Error membuat direktori cookies: {e}")

# Fungsi untuk menyimpan cookies ke dalam file JSON
def save_cookies(driver, filename):
    try:
        ensure_cookie_dir()
        filepath = os.path.join(COOKIE_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(driver.get_cookies(), f)
        print(f"✅ Cookies berhasil disimpan di {filepath}.")
    except Exception as e:
        print(f"⚠️ Error saat menyimpan cookies: {e}")

# Fungsi untuk memuat cookies dari file JSON
def load_cookies(driver, filename):
    try:
        filepath = os.path.join(COOKIE_DIR, filename)
        
        with open(filepath, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            try:
                cookie.pop("sameSite", None)  # Hapus sameSite untuk kompatibilitas
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ Gagal menambahkan cookie: {e}")
        print("✅ Cookie dimuat.")
    except FileNotFoundError:
        print(f"⚠️ File cookies tidak ditemukan di {filepath}.")
    except Exception as e:
        print(f"⚠️ Error saat memuat cookies: {e}")

# Fungsi untuk memeriksa apakah sudah login
def is_logged_in(driver):
    try:
        driver.get("https://shopee.co.id/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "shopee-searchbar-input__input"))
        )
        return True
    except Exception as e:
        print(f"❌ Cek login gagal: {e}")
        return False

# Fungsi untuk scroll lambat
def slow_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for y in range(0, last_height, 400):
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(0.3)
    time.sleep(2.5)

# Fungsi utama untuk login dan menangani CAPTCHA
def handle_login_and_captcha(keyword: str):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options, headless=False, use_subprocess=True)
        driver.get("https://shopee.co.id/")
        time.sleep(5)  # Tunggu halaman load

        # Cek dan muat cookie
        if os.path.exists(COOKIE_FILE):
            print("🍪 Memuat cookie login...")
            driver.get("https://shopee.co.id/")  # Pastikan sudah di domain sebelum set cookie
            time.sleep(2)
            load_cookies(driver, "shopee_cookies.json")
            driver.refresh()
            time.sleep(5)

        if not is_logged_in(driver):
            print("🔐 Belum login, silakan login manual.")
            driver.get("https://shopee.co.id/buyer/login")
            messagebox.showinfo("Login Manual", "Silakan login manual di browser.\nKlik OK jika sudah berhasil login.")

            # Buka halaman pencarian untuk trigger captcha
            search_url = f"https://shopee.co.id/search?keyword={keyword.replace(' ', '%20')}"
            driver.get(search_url)

            timeout = 180  # Maksimal 3 menit
            start_time = time.time()

            while not is_logged_in(driver) and time.time() - start_time < timeout:
                print("⚠ Belum login. Tunggu dan refresh...")
                time.sleep(6)
                driver.refresh()

            if is_logged_in(driver):
                print("✅ Login berhasil.")
                # Simpan cookies setelah login manual berhasil
                save_cookies(driver, "shopee_cookies.json")
                print("✅ Cookie disimpan.")
                messagebox.showinfo("Sukses", "Login dan CAPTCHA berhasil.\nCookie telah disimpan.")
            else:
                print("⛔ Timeout login.")
                messagebox.showerror("Gagal", "Login tidak berhasil dalam 3 menit.")
        else:
            print("✅ Sudah login (dari cookie).")
            messagebox.showinfo("Info", "Login aktif dari cookie tersimpan.")

        driver.quit()

    except Exception as e:
        print(f"🔥 ERROR: {e}")
        messagebox.showerror("Error", f"Terjadi kesalahan saat membuka browser: {e}")

# Fungsi untuk scraping dengan cookies
def scrape_shopee(keyword: str, max_page: int, output_file: str):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1200,800")
        driver = uc.Chrome(options=options)

        driver.get("https://shopee.co.id")
        time.sleep(3)

        # Masukkan cookie akun
        load_cookies(driver, "shopee_cookies.json")

        driver.refresh()
        time.sleep(5)

        # Buka halaman pencarian
        driver.get(f"https://shopee.co.id/search?keyword={keyword.replace(' ', '%20')}")
        time.sleep(5)

        products = []
        page = 1

        while page <= max_page:
            print(f"\n📄 Scraping halaman {page}...")

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "shopee-search-item-result__item"))
                )
            except:
                print("❗ Produk tidak muncul, halaman mungkin gagal dimuat.")
                break

            slow_scroll(driver)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            product_cards = soup.select(".shopee-search-item-result__item")
            print(f"🔎 {len(product_cards)} produk ditemukan")

            for card in product_cards:
                try:
                    name_tag = card.select_one("div.line-clamp-2")
                    price_tag = card.select_one("span.font-medium.text-base\\/5.truncate")
                    if not name_tag or not price_tag:
                        continue

                    name = name_tag.text.strip()
                    price = price_tag.text.strip()

                    sold_tag = card.select_one("div.truncate.text-shopee-black87.text-xs.min-h-4")
                    sold = sold_tag.text.strip() if sold_tag else "Tidak ditemukan"

                    location_tag = card.select_one("div.flex-shrink.min-w-0.truncate.text-shopee-black54")
                    location = location_tag.text.strip() if location_tag else "Tidak ditemukan"

                    rating_tag = card.select_one("div.text-shopee-black87.text-xs\\/sp14.flex-none")
                    rating = rating_tag.text.strip() if rating_tag else "Tidak ditemukan"

                    products.append({
                        "product_name": name,
                        "price": price,
                        "sold": sold,
                        "location": location,
                        "rating": rating,
                        "kategori": keyword
                    })
                except:
                    continue

            page += 1
            if page > max_page:
                break

            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//a[@class="shopee-button-no-outline" and text()="{page}"]'))
                )
                next_button.click()
                time.sleep(4)
            except:
                print("🚫 Gagal klik halaman berikutnya.")
                break

        df = pd.DataFrame(products)
        df.to_csv(output_file, index=False)
        print(f"\n✅ {len(products)} produk disimpan ke '{output_file}'")
        messagebox.showinfo("Selesai", f"Scraping selesai!\n{len(products)} produk disimpan ke '{output_file}'")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        driver.quit()

# ========== GUI FUNCTIONS ========== #
def start_login():
    keyword = keyword_entry.get()
    if not keyword.strip():
        messagebox.showwarning("Input Kosong", "Masukkan kata kunci pencarian.")
        return
    handle_login_and_captcha(keyword)

def start_scraping():
    keyword = keyword_entry.get()
    pages = pages_entry.get()
    filename = filename_entry.get()

    if not keyword or not pages or not filename:
        messagebox.showwarning("Input Kosong", "Semua kolom harus diisi.")
        return

    try:
        pages = int(pages)
    except ValueError:
        messagebox.showerror("Input Salah", "Jumlah halaman harus berupa angka.")
        return

    if not filename.endswith(".csv"):
        filename += ".csv"

    scrape_shopee(keyword, pages, filename)

# ========== GUI SETUP ========== #
root = tk.Tk()
root.title("Shopee Login & Scraper (Auto Cookie)")
root.geometry("500x400")

# Tab control
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# Tab 1: Login
login_frame = ttk.Frame(notebook)
notebook.add(login_frame, text="🔐 Login & Cookie")

ttk.Label(login_frame, text="🛒 Masukkan Kata Kunci Pencarian (untuk trigger CAPTCHA):").pack(pady=(15, 0))
keyword_entry = ttk.Entry(login_frame, width=50)
keyword_entry.pack(pady=10)

ttk.Button(login_frame, text="🚀 Mulai Proses Login", command=start_login).pack(pady=20)

# Tab 2: Scraping
scraping_frame = ttk.Frame(notebook)
notebook.add(scraping_frame, text="🔍 Scraping")

ttk.Label(scraping_frame, text="🔍 Kata Kunci Pencarian:").pack(pady=(15, 0))
keyword_entry_scraping = ttk.Entry(scraping_frame, width=50)
keyword_entry_scraping.pack()

ttk.Label(scraping_frame, text="📄 Jumlah Halaman:").pack(pady=(10, 0))
pages_entry = ttk.Entry(scraping_frame, width=20)
pages_entry.pack()

ttk.Label(scraping_frame, text="💾 Nama File Output:").pack(pady=(10, 0))
filename_entry = ttk.Entry(scraping_frame, width=40)
filename_entry.pack()

ttk.Button(scraping_frame, text="🚀 Mulai Scraping", command=start_scraping).pack(pady=20)

# Sync entries between tabs
def sync_entries(*args):
    keyword_entry_scraping.delete(0, tk.END)
    keyword_entry_scraping.insert(0, keyword_entry.get())

keyword_entry.bind('<KeyRelease>', sync_entries)

root.mainloop()