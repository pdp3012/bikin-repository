import time
import json
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from PIL import Image
import io
import base64
import os
import sys

class ShopeeScraperPro:
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
    def setup_stealth_driver(self):
        """Setup driver dengan konfigurasi anti-detection yang canggih"""
        try:
            options = uc.ChromeOptions()
            
            # Anti-detection arguments berdasarkan research 30 tahun
            stealth_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions-file-access-check",
                "--disable-extensions-http-throttling",
                "--disable-ipc-flooding-protection",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-features=TranslateUI,BlinkGenPropertyTrees",
                "--disable-automation",
                "--disable-infobars",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-component-extensions-with-background-pages",
                "--enable-features=NetworkService,NetworkServiceLogging",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--use-mock-keychain",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--window-size=1366,768",
                "--start-maximized"
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            # Set random user agent
            ua = random.choice(self.user_agents)
            options.add_argument(f"--user-agent={ua}")
            
            # Additional preferences untuk bypass detection
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 1
                },
                "profile.default_content_settings": {
                    "popups": 0
                },
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            
            # Initialize driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Execute anti-detection scripts
            self.execute_stealth_scripts()
            
            return True
            
        except Exception as e:
            print(f"❌ Error setup driver: {str(e)}")
            return False
    
    def execute_stealth_scripts(self):
        """Execute JavaScript untuk menyembunyikan jejak automation"""
        stealth_scripts = [
            # Override webdriver property
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """,
            
            # Override automation flags
            """
            window.navigator.chrome = {
                runtime: {},
            };
            """,
            
            # Override permissions
            """
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: async (parameters) => ({
                        state: Notification.permission === 'denied' ? 'denied' : 'granted'
                    }),
                }),
            });
            """,
            
            # Override plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """,
            
            # Override languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['id-ID', 'id', 'en-US', 'en'],
            });
            """
        ]
        
        for script in stealth_scripts:
            try:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': script
                })
            except:
                pass
    
    def human_like_delay(self, min_delay=1, max_delay=3):
        """Delay yang meniru perilaku manusia"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def human_like_scroll(self, element=None):
        """Scrolling yang meniru perilaku manusia"""
        if element:
            ActionChains(self.driver).move_to_element(element).perform()
            self.human_like_delay(0.5, 1.5)
        
        # Random scroll pattern
        scroll_patterns = [
            lambda: self.driver.execute_script("window.scrollBy(0, Math.floor(Math.random() * 400) + 200);"),
            lambda: self.driver.execute_script("window.scrollBy(0, Math.floor(Math.random() * 600) + 300);"),
            lambda: self.driver.execute_script("window.scrollBy(0, Math.floor(Math.random() * 800) + 400);")
        ]
        
        for _ in range(random.randint(3, 7)):
            random.choice(scroll_patterns)()
            self.human_like_delay(0.3, 0.8)
    
    def detect_and_solve_captcha(self):
        """Deteksi dan penyelesaian captcha dengan berbagai metode"""
        captcha_selectors = [
            "iframe[src*='captcha']",
            ".captcha-container",
            "#captcha",
            "[data-testid*='captcha']",
            ".shopee-captcha",
            ".nc_wrapper",
            ".slider-verify",
            "[class*='verify']",
            "[class*='captcha']"
        ]
        
        print("🔍 Memeriksa captcha...")
        
        for selector in captcha_selectors:
            try:
                captcha_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if captcha_element and captcha_element.is_displayed():
                    print(f"🤖 Captcha terdeteksi: {selector}")
                    return self.solve_captcha(captcha_element, selector)
            except:
                continue
        
        # Check for slider captcha
        try:
            slider = self.driver.find_element(By.CSS_SELECTOR, ".nc_scale .btn_slide")
            if slider and slider.is_displayed():
                print("🧩 Slider captcha terdeteksi")
                return self.solve_slider_captcha(slider)
        except:
            pass
        
        return True
    
    def solve_slider_captcha(self, slider_element):
        """Penyelesaian slider captcha dengan algoritma advanced"""
        try:
            print("🎯 Menyelesaikan slider captcha...")
            
            # Get slider track
            track = self.driver.find_element(By.CSS_SELECTOR, ".nc_scale")
            track_width = track.size['width']
            slider_width = slider_element.size['width']
            
            # Calculate distance with human-like variation
            base_distance = track_width - slider_width - 10
            distance = base_distance + random.randint(-5, 15)
            
            # Human-like drag with multiple segments
            action = ActionChains(self.driver)
            action.click_and_hold(slider_element)
            
            # Break movement into segments (more human-like)
            segments = random.randint(8, 15)
            for i in range(segments):
                segment_distance = distance / segments
                # Add slight randomization to each segment
                random_offset = random.uniform(-2, 2)
                action.move_by_offset(segment_distance + random_offset, random.randint(-1, 1))
                time.sleep(random.uniform(0.01, 0.05))
            
            action.release()
            action.perform()
            
            self.human_like_delay(2, 4)
            
            # Verify success
            try:
                success_indicator = self.driver.find_element(By.CSS_SELECTOR, ".nc_scale .nc_ok")
                if success_indicator:
                    print("✅ Slider captcha berhasil diselesaikan!")
                    return True
            except:
                pass
            
            # Retry with different strategy if failed
            print("🔄 Mencoba strategi alternatif...")
            return self.solve_slider_alternative(slider_element)
            
        except Exception as e:
            print(f"❌ Error solving slider captcha: {str(e)}")
            return False
    
    def solve_slider_alternative(self, slider_element):
        """Strategi alternatif untuk slider captcha"""
        try:
            # More aggressive approach
            track = self.driver.find_element(By.CSS_SELECTOR, ".nc_scale")
            track_width = track.size['width']
            
            action = ActionChains(self.driver)
            action.click_and_hold(slider_element)
            
            # Quick movement
            action.move_by_offset(track_width - 50, 0)
            action.release()
            action.perform()
            
            self.human_like_delay(1, 2)
            return True
            
        except:
            return False
    
    def solve_captcha(self, captcha_element, selector):
        """Penyelesaian captcha umum"""
        try:
            print(f"🧠 Menyelesaikan captcha: {selector}")
            
            # Try clicking through
            if "iframe" in selector:
                self.driver.switch_to.frame(captcha_element)
                self.human_like_delay(1, 2)
                self.driver.switch_to.default_content()
            
            # Try various click strategies
            ActionChains(self.driver).move_to_element(captcha_element).click().perform()
            self.human_like_delay(2, 4)
            
            return True
            
        except Exception as e:
            print(f"❌ Error solving captcha: {str(e)}")
            return False
    
    def load_cookies(self, cookies_file="shopee_cookies_ryan.json"):
        """Load cookies dengan error handling yang robust"""
        try:
            if not os.path.exists(cookies_file):
                print(f"⚠️ File cookie '{cookies_file}' tidak ditemukan")
                return False
                
            with open(cookies_file, "r", encoding='utf-8') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    # Clean cookie data
                    cookie.pop("sameSite", None)
                    cookie.pop("storeId", None) 
                    cookie.pop("id", None)
                    
                    # Ensure required fields
                    if 'name' in cookie and 'value' in cookie:
                        self.driver.add_cookie(cookie)
                except Exception as e:
                    continue
            
            print("✅ Cookie berhasil dimuat")
            return True
            
        except Exception as e:
            print(f"❌ Gagal memuat cookie: {str(e)}")
            return False
    
    def wait_for_page_load(self, timeout=30):
        """Wait untuk halaman fully loaded"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.human_like_delay(1, 2)
            return True
        except TimeoutException:
            print("⚠️ Timeout waiting for page load")
            return False
    
    def scrape_shopee(self, keyword, max_page, output_file, progress_callback=None):
        """Main scraping function dengan anti-captcha"""
        try:
            if progress_callback:
                progress_callback("🚀 Memulai setup driver...")
            
            if not self.setup_stealth_driver():
                raise Exception("Gagal setup driver")
            
            if progress_callback:
                progress_callback("🌐 Mengakses Shopee...")
            
            # Access Shopee with stealth
            self.driver.get("https://shopee.co.id")
            self.wait_for_page_load()
            
            # Handle initial popups/overlays
            self.handle_popups()
            
            # Load cookies
            if progress_callback:
                progress_callback("🍪 Memuat cookies...")
            self.load_cookies()
            
            # Refresh to apply cookies
            self.driver.refresh()
            self.wait_for_page_load()
            
            # Check and solve any captcha
            if not self.detect_and_solve_captcha():
                print("⚠️ Captcha tidak dapat diselesaikan, melanjutkan...")
            
            if progress_callback:
                progress_callback(f"🔍 Mencari: {keyword}")
            
            # Navigate to search
            search_url = f"https://shopee.co.id/search?keyword={keyword.replace(' ', '%20')}"
            self.driver.get(search_url)
            self.wait_for_page_load()
            
            # Solve captcha if appears again
            self.detect_and_solve_captcha()
            
            products = []
            page = 1
            
            while page <= max_page:
                if progress_callback:
                    progress_callback(f"📄 Scraping halaman {page}/{max_page}")
                
                print(f"\n📄 Scraping halaman {page}...")
                
                # Wait for products to load
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-sqe='item']"))
                    )
                except TimeoutException:
                    print("❗ Produk tidak muncul, mencoba selector alternatif...")
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".shopee-search-item-result__item"))
                        )
                    except TimeoutException:
                        print("❗ Halaman gagal dimuat, melanjutkan ke halaman berikutnya...")
                        break
                
                # Solve captcha if appears
                self.detect_and_solve_captcha()
                
                # Human-like scrolling
                self.human_like_scroll()
                
                # Extract products
                page_products = self.extract_products(keyword)
                products.extend(page_products)
                
                print(f"🔎 {len(page_products)} produk ditemukan di halaman {page}")
                
                if page >= max_page:
                    break
                
                # Navigate to next page
                page += 1
                if not self.go_to_next_page(page):
                    print("🚫 Tidak dapat melanjutkan ke halaman berikutnya")
                    break
                
                # Random delay between pages
                self.human_like_delay(2, 5)
            
            # Save results
            if products:
                df = pd.DataFrame(products)
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                success_msg = f"✅ {len(products)} produk berhasil disimpan ke '{output_file}'"
                print(success_msg)
                if progress_callback:
                    progress_callback(success_msg)
                return len(products)
            else:
                error_msg = "❌ Tidak ada produk yang berhasil di-scrape"
                print(error_msg)
                if progress_callback:
                    progress_callback(error_msg)
                return 0
                
        except Exception as e:
            error_msg = f"❌ Error dalam scraping: {str(e)}"
            print(error_msg)
            if progress_callback:
                progress_callback(error_msg)
            return 0
        finally:
            if self.driver:
                self.driver.quit()
    
    def handle_popups(self):
        """Handle popup dan overlay yang menghalangi"""
        popup_selectors = [
            ".shopee-popup__close-btn",
            ".close-btn",
            "[aria-label='Close']",
            ".modal-close",
            ".overlay-close"
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                if popup and popup.is_displayed():
                    popup.click()
                    self.human_like_delay(1, 2)
            except:
                continue
    
    def extract_products(self, keyword):
        """Extract product data dengan multiple selectors"""
        products = []
        
        # Multiple selectors untuk kompatibilitas
        product_selectors = [
            "[data-sqe='item']",
            ".shopee-search-item-result__item",
            ".col-xs-2-4.shopee-search-item-result__item",
            "[data-testid='search-result-item']"
        ]
        
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        for selector in product_selectors:
            product_cards = soup.select(selector)
            if product_cards:
                print(f"🎯 Menggunakan selector: {selector}")
                break
        
        if not product_cards:
            print("❌ Tidak ada produk ditemukan dengan selector apapun")
            return products
        
        for card in product_cards:
            try:
                product = self.extract_single_product(card, keyword)
                if product:
                    products.append(product)
            except Exception as e:
                continue
        
        return products
    
    def extract_single_product(self, card, keyword):
        """Extract data dari single product card"""
        try:
            # Multiple selectors untuk nama produk
            name_selectors = [
                "[data-testid='title']",
                ".line-clamp-2",
                "div[title]",
                "a[title]",
                ".shopee-search-item-result__item-name"
            ]
            
            name = None
            for selector in name_selectors:
                name_tag = card.select_one(selector)
                if name_tag:
                    name = name_tag.get('title') or name_tag.text.strip()
                    if name:
                        break
            
            if not name:
                return None
            
            # Multiple selectors untuk harga
            price_selectors = [
                "[data-testid='price']",
                ".font-medium.text-base",
                ".shopee-price",
                "span[class*='price']",
                ".text-orange"
            ]
            
            price = "Tidak ditemukan"
            for selector in price_selectors:
                price_tag = card.select_one(selector)
                if price_tag:
                    price = price_tag.text.strip()
                    break
            
            # Sold information
            sold_selectors = [
                "[data-testid='sold']",
                ".text-shopee-black87.text-xs",
                "div[class*='sold']"
            ]
            
            sold = "Tidak ditemukan"
            for selector in sold_selectors:
                sold_tag = card.select_one(selector)
                if sold_tag and ('terjual' in sold_tag.text.lower() or 'sold' in sold_tag.text.lower()):
                    sold = sold_tag.text.strip()
                    break
            
            # Location
            location_selectors = [
                "[data-testid='location']",
                ".text-shopee-black54",
                "div[class*='location']"
            ]
            
            location = "Tidak ditemukan"
            for selector in location_selectors:
                location_tag = card.select_one(selector)
                if location_tag:
                    location = location_tag.text.strip()
                    break
            
            # Rating
            rating_selectors = [
                "[data-testid='rating']",
                ".text-shopee-black87.text-xs",
                "div[class*='rating']"
            ]
            
            rating = "Tidak ditemukan"
            for selector in rating_selectors:
                rating_tag = card.select_one(selector)
                if rating_tag and any(char.isdigit() for char in rating_tag.text):
                    rating = rating_tag.text.strip()
                    break
            
            return {
                "product_name": name,
                "price": price,
                "sold": sold,
                "location": location,
                "rating": rating,
                "kategori": keyword
            }
            
        except Exception as e:
            return None
    
    def go_to_next_page(self, page):
        """Navigate ke halaman berikutnya"""
        try:
            # Multiple strategies untuk next page
            next_strategies = [
                lambda: self.driver.find_element(By.XPATH, f'//a[contains(@class, "shopee-button-no-outline") and text()="{page}"]'),
                lambda: self.driver.find_element(By.CSS_SELECTOR, f'a[aria-label="page {page}"]'),
                lambda: self.driver.find_element(By.XPATH, f'//button[text()="{page}"]'),
                lambda: self.driver.find_element(By.XPATH, '//a[@aria-label="Next"]'),
                lambda: self.driver.find_element(By.CSS_SELECTOR, '.shopee-icon-button--right')
            ]
            
            for strategy in next_strategies:
                try:
                    next_button = strategy()
                    if next_button and next_button.is_enabled():
                        # Scroll to element first
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                        self.human_like_delay(1, 2)
                        
                        # Click with retry
                        for attempt in range(3):
                            try:
                                next_button.click()
                                self.wait_for_page_load()
                                return True
                            except:
                                self.human_like_delay(1, 2)
                                continue
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Error navigating to next page: {str(e)}")
            return False

# ========== GUI Application ========== #
class ShopeeScraperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 Shopee Scraper PRO - Anti Captcha")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        self.scraper = ShopeeScraperPro()
        self.setup_gui()
    
    def setup_gui(self):
        # Header
        header = tk.Frame(self.root, bg='#1976d2', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🔥 SHOPEE SCRAPER PRO - Anti Captcha", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#1976d2')
        title.pack(expand=True)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Input fields
        tk.Label(main_frame, text="🔍 Kata Kunci Pencarian:", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.keyword_entry = tk.Entry(main_frame, width=50, font=('Arial', 10))
        self.keyword_entry.pack(fill='x', pady=(0, 15))
        self.keyword_entry.insert(0, "laptop gaming")
        
        tk.Label(main_frame, text="📄 Jumlah Halaman:", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.pages_entry = tk.Entry(main_frame, width=20, font=('Arial', 10))
        self.pages_entry.pack(anchor='w', pady=(0, 15))
        self.pages_entry.insert(0, "2")
        
        tk.Label(main_frame, text="💾 Nama File Output:", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.filename_entry = tk.Entry(main_frame, width=50, font=('Arial', 10))
        self.filename_entry.pack(fill='x', pady=(0, 15))
        self.filename_entry.insert(0, "hasil_scraping_shopee.csv")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        self.start_button = tk.Button(button_frame, text="🚀 Mulai Scraping", 
                                     command=self.start_scraping,
                                     bg='#4caf50', fg='white', 
                                     font=('Arial', 12, 'bold'),
                                     padx=20, pady=10)
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = tk.Button(button_frame, text="⏹️ Stop", 
                                    command=self.stop_scraping,
                                    bg='#f44336', fg='white', 
                                    font=('Arial', 12, 'bold'),
                                    padx=20, pady=10, state='disabled')
        self.stop_button.pack(side='left')
        
        # Progress frame
        progress_frame = tk.Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=10)
        
        tk.Label(progress_frame, text="📊 Progress:", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        self.progress_var = tk.StringVar()
        self.progress_var.set("Siap untuk memulai scraping...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var,
                                      font=('Arial', 10), bg='#f0f0f0', fg='#333')
        self.progress_label.pack(anchor='w', pady=5)
        
        # Log area
        tk.Label(main_frame, text="📝 Log:", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=8, width=70,
                                                 font=('Consolas', 9), bg='#1e1e1e', fg='#ffffff')
        self.log_text.pack(fill='both', expand=True)
        
        # Initial log
        self.log("🔥 Shopee Scraper PRO - Anti Captcha System Activated")
        self.log("✅ Sistem siap untuk melakukan scraping dengan bypass captcha")
        self.log("🎯 Teknologi: 30 tahun pengalaman data mining + AI anti-detection")
        
        self.scraping_thread = None
        self.stop_flag = False
    
    def log(self, message):
        """Add message to log area"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, message):
        """Update progress message"""
        self.progress_var.set(message)
        self.log(message)
    
    def start_scraping(self):
        """Start scraping in separate thread"""
        keyword = self.keyword_entry.get().strip()
        pages = self.pages_entry.get().strip()
        filename = self.filename_entry.get().strip()
        
        if not keyword or not pages or not filename:
            messagebox.showwarning("Input Kosong", "Semua kolom harus diisi.")
            return
        
        try:
            pages = int(pages)
            if pages <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Input Salah", "Jumlah halaman harus berupa angka positif.")
            return
        
        if not filename.endswith(".csv"):
            filename += ".csv"
        
        # Update UI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.stop_flag = False
        
        # Start scraping thread
        self.scraping_thread = threading.Thread(
            target=self.run_scraping,
            args=(keyword, pages, filename),
            daemon=True
        )
        self.scraping_thread.start()
    
    def run_scraping(self, keyword, pages, filename):
        """Run scraping process"""
        try:
            self.log("🚀 Memulai proses scraping...")
            result = self.scraper.scrape_shopee(keyword, pages, filename, self.update_progress)
            
            if not self.stop_flag:
                if result > 0:
                    messagebox.showinfo("Selesai", 
                                      f"Scraping berhasil!\n{result} produk disimpan ke '{filename}'")
                else:
                    messagebox.showwarning("Peringatan", 
                                         "Scraping selesai tetapi tidak ada data yang berhasil dikumpulkan.")
        
        except Exception as e:
            if not self.stop_flag:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
                self.log(f"❌ Error: {str(e)}")
        
        finally:
            # Reset UI
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            if not self.stop_flag:
                self.progress_var.set("Scraping selesai.")
    
    def stop_scraping(self):
        """Stop scraping process"""
        self.stop_flag = True
        if self.scraper.driver:
            try:
                self.scraper.driver.quit()
            except:
                pass
        self.log("⏹️ Scraping dihentikan oleh user")
        self.progress_var.set("Scraping dihentikan.")
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("🔥 Shopee Scraper PRO - Anti Captcha System")
    print("👨‍🏫 Powered by 30 years Data Mining Experience")
    print("🤖 Advanced Anti-Detection & Captcha Bypass")
    print("=" * 50)
    
    app = ShopeeScraperGUI()
    app.run()