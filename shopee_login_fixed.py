import os
import time
import json
import tkinter as tk
from tkinter import messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import requests
import urllib.parse

class ShopeeLoginManager:
    def __init__(self):
        self.COOKIE_FILE = "shopee_cookies.json"
        self.driver = None
        self.is_driver_initialized = False
        
    def setup_chrome_driver(self):
        """Setup Chrome driver dengan konfigurasi yang optimal untuk menghindari deteksi"""
        try:
            options = uc.ChromeOptions()
            
            # Konfigurasi dasar untuk menghindari deteksi
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-prompt-on-repost")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-translate")
            options.add_argument("--metrics-recording-only")
            options.add_argument("--no-first-run")
            options.add_argument("--safebrowsing-disable-auto-update")
            options.add_argument("--enable-automation")
            options.add_argument("--password-store=basic")
            options.add_argument("--use-mock-keychain")
            
            # User agent yang realistis
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Window size
            options.add_argument("--window-size=1366,768")
            options.add_argument("--start-maximized")
            
            # Experimental options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Prefs untuk menghindari deteksi
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.media_stream": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            # Inisialisasi driver dengan undetected_chromedriver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Execute script untuk menghilangkan webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set window size
            self.driver.set_window_size(1366, 768)
            
            self.is_driver_initialized = True
            print("✅ Chrome driver berhasil diinisialisasi")
            return True
            
        except Exception as e:
            print(f"❌ Error saat inisialisasi Chrome driver: {str(e)}")
            return False
    
    def save_cookies(self, filename):
        """Simpan cookies dengan error handling"""
        try:
            if self.driver and self.is_driver_initialized:
                cookies = self.driver.get_cookies()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, indent=2, ensure_ascii=False)
                print(f"✅ Cookies berhasil disimpan ke {filename}")
                return True
        except Exception as e:
            print(f"❌ Error saat menyimpan cookies: {str(e)}")
        return False

    def load_cookies(self, filename):
        """Muat cookies dengan error handling"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                # Pastikan driver sudah mengakses domain yang benar
                self.driver.get("https://shopee.co.id")
                time.sleep(2)
                
                for cookie in cookies:
                    try:
                        # Hapus atribut yang tidak valid
                        if 'expiry' in cookie:
                            del cookie['expiry']
                        if 'sameSite' in cookie:
                            del cookie['sameSite']
                        
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"⚠️ Warning: Gagal menambahkan cookie {cookie.get('name', 'unknown')}: {str(e)}")
                        continue
                
                print(f"✅ Cookies berhasil dimuat dari {filename}")
                return True
        except Exception as e:
            print(f"❌ Error saat memuat cookies: {str(e)}")
        return False

    def is_logged_in(self):
        """Cek status login dengan multiple indicators"""
        try:
            if not self.driver or not self.is_driver_initialized:
                return False
            
            # Coba akses halaman utama
            self.driver.get("https://shopee.co.id/")
            time.sleep(3)
            
            # Cek beberapa indikator login
            login_indicators = [
                "//div[contains(@class, 'navbar__username')]",  # Username di navbar
                "//div[contains(@class, 'navbar__link-text') and contains(text(), 'Akun')]",  # Menu Akun
                "//div[contains(@class, 'navbar__link-text') and contains(text(), 'Account')]",  # Menu Account
                "//a[contains(@href, '/buyer/order')]",  # Link ke order
                "//div[contains(@class, 'navbar__link') and contains(@href, '/buyer/')]"  # Link buyer
            ]
            
            for indicator in login_indicators:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    if element:
                        print("✅ Login terdeteksi melalui indikator")
                        return True
                except TimeoutException:
                    continue
            
            # Cek apakah ada tombol login (indikator belum login)
            try:
                login_button = self.driver.find_element(By.XPATH, "//a[contains(@href, '/buyer/login')]")
                if login_button:
                    print("❌ Belum login - tombol login ditemukan")
                    return False
            except NoSuchElementException:
                pass
            
            # Cek search bar sebagai fallback
            try:
                search_bar = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "shopee-searchbar-input__input"))
                )
                print("✅ Halaman utama berhasil dimuat")
                return True
            except TimeoutException:
                print("❌ Gagal memuat halaman utama")
                return False
                
        except Exception as e:
            print(f"❌ Error saat cek login status: {str(e)}")
            return False

    def handle_login_and_captcha(self, keyword: str):
        """Handle proses login dan CAPTCHA dengan error handling yang komprehensif"""
        try:
            # Setup driver
            if not self.setup_chrome_driver():
                messagebox.showerror("Error", "Gagal menginisialisasi Chrome driver")
                return
            
            print("🌐 Membuka Shopee...")
            self.driver.get("https://shopee.co.id/")
            time.sleep(3)
            
            # Coba muat cookies jika ada
            if os.path.exists(self.COOKIE_FILE):
                print("🍪 Memuat cookies yang tersimpan...")
                if self.load_cookies(self.COOKIE_FILE):
                    self.driver.refresh()
                    time.sleep(5)
            
            # Cek status login
            if self.is_logged_in():
                print("✅ Sudah login dari cookies")
                messagebox.showinfo("Info", "Login masih aktif dari cookies yang tersimpan.")
                return
            
            # Jika belum login, mulai proses login manual
            print("🔐 Memulai proses login manual...")
            self.driver.get("https://shopee.co.id/buyer/login")
            time.sleep(3)
            
            # Tampilkan pesan untuk login manual
            messagebox.showinfo("Login Manual", 
                              "Silakan login secara manual di browser yang muncul.\n"
                              "Setelah login berhasil, klik OK untuk melanjutkan.")
            
            # Tunggu user login dan cek status
            timeout = 300  # 5 menit
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.is_logged_in():
                    print("✅ Login berhasil!")
                    break
                time.sleep(10)
                print("⏳ Menunggu login selesai...")
            
            if not self.is_logged_in():
                messagebox.showerror("Timeout", "Login tidak berhasil dalam waktu yang ditentukan.")
                return
            
            # Setelah login berhasil, coba akses halaman pencarian untuk trigger CAPTCHA
            print("🔍 Mengakses halaman pencarian untuk trigger CAPTCHA...")
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://shopee.co.id/search?keyword={encoded_keyword}"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Tunggu dan handle CAPTCHA jika muncul
            captcha_timeout = 180  # 3 menit untuk CAPTCHA
            captcha_start_time = time.time()
            
            while time.time() - captcha_start_time < captcha_timeout:
                try:
                    # Cek apakah ada CAPTCHA
                    captcha_elements = self.driver.find_elements(By.XPATH, 
                        "//iframe[contains(@src, 'captcha')] | //div[contains(@class, 'captcha')] | //div[contains(@id, 'captcha')]")
                    
                    if captcha_elements:
                        print("🤖 CAPTCHA terdeteksi, menunggu penyelesaian manual...")
                        messagebox.showinfo("CAPTCHA", 
                                          "CAPTCHA terdeteksi. Silakan selesaikan CAPTCHA di browser.\n"
                                          "Klik OK setelah CAPTCHA selesai.")
                        time.sleep(5)
                    else:
                        # Cek apakah pencarian berhasil
                        try:
                            search_results = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'shopee-search-item-result')]"))
                            )
                            print("✅ Pencarian berhasil, tidak ada CAPTCHA")
                            break
                        except TimeoutException:
                            print("⏳ Menunggu hasil pencarian...")
                            time.sleep(10)
                            continue
                            
                except Exception as e:
                    print(f"⚠️ Error saat cek CAPTCHA: {str(e)}")
                    time.sleep(10)
                    continue
            
            # Simpan cookies setelah login berhasil
            if self.save_cookies(self.COOKIE_FILE):
                messagebox.showinfo("Berhasil", 
                                  "Login dan CAPTCHA berhasil diselesaikan!\n"
                                  "Cookies telah disimpan untuk penggunaan selanjutnya.")
            else:
                messagebox.showwarning("Warning", 
                                     "Login berhasil tetapi gagal menyimpan cookies.")
                
        except Exception as e:
            print(f"❌ Error dalam handle_login_and_captcha: {str(e)}")
            messagebox.showerror("Error", f"Terjadi error: {str(e)}")
        
        finally:
            # Cleanup
            if self.driver and self.is_driver_initialized:
                try:
                    self.driver.quit()
                    print("🔒 Browser ditutup")
                except:
                    pass
                self.is_driver_initialized = False

# ========== GUI ==========

class ShopeeLoginGUI:
    def __init__(self):
        self.login_manager = ShopeeLoginManager()
        self.setup_gui()
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🛒 Shopee Login & CAPTCHA Manager")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Shopee Login & CAPTCHA Manager", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Masukkan kata kunci pencarian untuk memicu CAPTCHA\n"
                                   "dan menyelesaikan proses login Shopee", 
                              font=("Arial", 10),
                              foreground="gray")
        desc_label.pack(pady=(0, 20))
        
        # Keyword input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_frame, text="Kata Kunci Pencarian:", font=("Arial", 11)).pack(anchor=tk.W)
        
        self.keyword_entry = ttk.Entry(input_frame, width=50, font=("Arial", 11))
        self.keyword_entry.pack(fill=tk.X, pady=(5, 0))
        self.keyword_entry.insert(0, "laptop")  # Default keyword
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, 
                                      text="🚀 Mulai Proses Login", 
                                      command=self.start_process,
                                      style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_cookies_button = ttk.Button(button_frame, 
                                              text="🗑️ Hapus Cookies", 
                                              command=self.clear_cookies)
        self.clear_cookies_button.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, font=("Consolas", 9), wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial status
        self.log_status("Sistem siap. Masukkan kata kunci dan klik 'Mulai Proses Login'")
        
        # Bind Enter key
        self.keyword_entry.bind('<Return>', lambda e: self.start_process())
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def log_status(self, message):
        """Log pesan ke status text"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_process(self):
        """Mulai proses login"""
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Input Kosong", "Masukkan kata kunci pencarian!")
            return
        
        self.log_status(f"Memulai proses login dengan keyword: {keyword}")
        self.start_button.config(state='disabled')
        
        # Run in separate thread to avoid GUI freeze
        import threading
        thread = threading.Thread(target=self.run_login_process, args=(keyword,))
        thread.daemon = True
        thread.start()
    
    def run_login_process(self, keyword):
        """Run login process in separate thread"""
        try:
            self.login_manager.handle_login_and_captcha(keyword)
        except Exception as e:
            self.log_status(f"Error: {str(e)}")
        finally:
            # Re-enable button in main thread
            self.root.after(0, lambda: self.start_button.config(state='normal'))
    
    def clear_cookies(self):
        """Hapus file cookies"""
        try:
            if os.path.exists(self.login_manager.COOKIE_FILE):
                os.remove(self.login_manager.COOKIE_FILE)
                self.log_status("✅ Cookies berhasil dihapus")
                messagebox.showinfo("Berhasil", "File cookies berhasil dihapus!")
            else:
                self.log_status("ℹ️ File cookies tidak ditemukan")
                messagebox.showinfo("Info", "File cookies tidak ditemukan.")
        except Exception as e:
            self.log_status(f"❌ Error saat menghapus cookies: {str(e)}")
            messagebox.showerror("Error", f"Gagal menghapus cookies: {str(e)}")
    
    def run(self):
        """Jalankan GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ShopeeLoginGUI()
    app.run()