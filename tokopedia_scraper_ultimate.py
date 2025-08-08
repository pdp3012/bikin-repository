import json
import requests
import os
import re
import math
import glob
import time
import random
from urllib.parse import quote, urlencode
from tqdm import tqdm
import pandas as pd

class TokopediaScraperUltimate:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session dengan headers yang lebih realistis"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
    
    def random_delay(self, min_delay=1, max_delay=3):
        """Random delay untuk menghindari detection"""
        time.sleep(random.uniform(min_delay, max_delay))
    
    def get_search_page_content(self, keyword):
        """Mengambil konten halaman search dengan berbagai metode"""
        search_url = f'https://www.tokopedia.com/search?q={quote(keyword)}'
        
        try:
            print(f"Mengakses URL: {search_url}")
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error mengakses halaman search: {e}")
            return None
    
    def extract_apollo_state(self, html_content):
        """Extract Apollo state dari HTML content"""
        patterns = [
            r'window\.__APOLLO_STATE__\s*=\s*({.*?});',
            r'__APOLLO_STATE__"\s*:\s*({.*?}),',
            r'"apolloState"\s*:\s*({.*?}),',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'window\.__cache\s*=\s*({.*?});'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            if matches:
                try:
                    data = json.loads(matches[0])
                    print(f"Berhasil extract data dengan pattern: {pattern[:50]}...")
                    return data
                except json.JSONDecodeError:
                    continue
        return None
    
    def build_graphql_params(self, keyword, page=1, rows=60):
        """Build GraphQL parameters secara manual"""
        start = (page - 1) * rows
        
        # Parameter dasar yang biasanya digunakan Tokopedia
        params = {
            'device': 'desktop',
            'navsource': '',
            'ob': '23',
            'page': str(page),
            'q': keyword,
            'related': 'true',
            'rows': str(rows),
            'safe_search': 'false',
            'scheme': 'https',
            'shipping': '',
            'source': 'search',
            'srp_component_id': '02.01.00.00',
            'st': 'product',
            'start': str(start),
            'topads_bucket': 'true',
            'unique_id': f'{int(time.time())}{random.randint(1000, 9999)}'
        }
        
        # Convert ke query string
        param_string = urlencode(params)
        
        # Ad parameters
        ad_params = {
            'headline_product_count': '2',
            'item': '15',
            'page': str(page),
            'product_ads_count': '2',
            'qid': '',
            'sc': '24',
            'user_addressId': '',
            'user_cityId': '176',
            'user_districtId': '2274',
            'user_id': '',
            'user_lat': '',
            'user_long': '',
            'user_postCode': '',
            'user_warehouseId': '12210375'
        }
        
        ad_param_string = urlencode(ad_params)
        
        return param_string, ad_param_string
    
    def create_graphql_payload(self, keyword, page=1, rows=60):
        """Create GraphQL payload untuk API call"""
        params, ad_params = self.build_graphql_params(keyword, page, rows)
        
        query = """
        query SearchProductQueryV5($params: String!, $adParams: String!) {
          organic: searchProductV5(params: $params) {
            header {
              totalData
              responseCode
              keywordProcess
              keywordIntention
              componentID
              isQuerySafe
              additionalParams
              backendFilters
              __typename
            }
            data {
              totalDataText
              products {
                id
                name
                url
                applink
                mediaURL {
                  image
                  image300
                  __typename
                }
                shop {
                  id
                  name
                  url
                  city
                  tier
                  __typename
                }
                badge {
                  id
                  title
                  url
                  __typename
                }
                price {
                  text
                  number
                  range
                  original
                  discountPercentage
                  __typename
                }
                freeShipping {
                  url
                  __typename
                }
                labelGroups {
                  position
                  title
                  type
                  url
                  __typename
                }
                category {
                  id
                  name
                  breadcrumb
                  gaKey
                  __typename
                }
                rating
                wishlist
                meta {
                  countReview
                  parentID
                  warehouseID
                  isImageBlurred
                  isPortrait
                  __typename
                }
                __typename
              }
              __typename
            }
            __typename
          }
        }
        """
        
        payload = [{
            "operationName": "SearchProductQueryV5",
            "query": query.strip(),
            "variables": {
                "params": params,
                "adParams": ad_params
            }
        }]
        
        return payload
    
    def get_graphql_headers(self):
        """Headers untuk GraphQL request"""
        return {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Origin': 'https://www.tokopedia.com',
            'Referer': 'https://www.tokopedia.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Tkpd-UserId': '0',
            'X-Device': 'desktop-0.0',
            'X-Source': 'tokopedia-lite',
            'X-Tkpd-Lite-Service': 'zeus',
            'X-Version': 'ed69c5d'
        }
    
    def test_graphql_endpoint(self, keyword):
        """Test GraphQL endpoint dengan berbagai metode"""
        print("Testing GraphQL endpoint...")
        
        # Method 1: Direct API call dengan parameter yang dibuild manual
        payload = self.create_graphql_payload(keyword, page=1, rows=10)
        headers = self.get_graphql_headers()
        
        try:
            response = self.session.post(
                'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and 'data' in data[0]:
                    organic_data = data[0]['data'].get('organic', {})
                    if organic_data and 'header' in organic_data:
                        total_data = organic_data['header'].get('totalData', 0)
                        print(f"✅ GraphQL endpoint berhasil! Total data: {total_data}")
                        return True, payload, headers
                    
            print(f"❌ Response tidak sesuai ekspektasi")
            if response.text:
                print(f"Response sample: {response.text[:500]}...")
                
        except Exception as e:
            print(f"❌ Error pada GraphQL test: {e}")
            
        return False, None, None
    
    def scrape_products(self, keyword='samsung', max_pages=30, rows_per_page=60):
        """Main scraping function dengan multiple fallback"""
        print(f"🚀 Memulai scraping produk Tokopedia untuk keyword: '{keyword}'")
        print("=" * 60)
        
        # Setup direktori output
        output_dir = 'scrape_tokopedia_requests'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Direktori '{output_dir}' dibuat")
        
        # Bersihkan file lama
        old_files = glob.glob(os.path.join(output_dir, '*.json'))
        for file in old_files:
            try:
                os.remove(file)
            except:
                pass
        print(f"🧹 Membersihkan {len(old_files)} file lama")
        
        # Test GraphQL endpoint
        is_working, base_payload, headers = self.test_graphql_endpoint(keyword)
        
        if not is_working:
            print("❌ GraphQL endpoint tidak dapat diakses")
            return self.fallback_scraping(keyword, max_pages, output_dir)
        
        # Mulai scraping dengan GraphQL
        print(f"✅ Memulai scraping {max_pages} halaman...")
        successful_pages = 0
        failed_pages = []
        
        with tqdm(total=max_pages, desc="Scraping progress") as pbar:
            for page in range(1, max_pages + 1):
                try:
                    # Create payload untuk page ini
                    payload = self.create_graphql_payload(keyword, page, rows_per_page)
                    
                    # Make request
                    response = self.session.post(
                        'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Validasi data
                        if (data and len(data) > 0 and 'data' in data[0] and 
                            data[0]['data'].get('organic', {}).get('data', {}).get('products')):
                            
                            # Simpan data
                            filename = os.path.join(output_dir, f'page_{page}.json')
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            
                            successful_pages += 1
                            
                            # Log progress
                            products_count = len(data[0]['data']['organic']['data']['products'])
                            pbar.set_postfix({
                                'success': successful_pages,
                                'products': products_count
                            })
                        else:
                            failed_pages.append(page)
                            print(f"⚠️  Page {page}: Data tidak valid")
                    else:
                        failed_pages.append(page)
                        print(f"❌ Page {page}: HTTP {response.status_code}")
                        
                except Exception as e:
                    failed_pages.append(page)
                    print(f"❌ Page {page}: Error - {e}")
                
                pbar.update(1)
                
                # Random delay
                if page < max_pages:
                    self.random_delay(0.5, 2.0)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY SCRAPING:")
        print(f"✅ Berhasil: {successful_pages}/{max_pages} halaman")
        print(f"❌ Gagal: {len(failed_pages)} halaman")
        if failed_pages:
            print(f"   Halaman gagal: {failed_pages}")
        print(f"📁 File disimpan di: {output_dir}/")
        
        return successful_pages
    
    def fallback_scraping(self, keyword, max_pages, output_dir):
        """Fallback method jika GraphQL tidak bekerja"""
        print("🔄 Menggunakan metode fallback...")
        
        # Implementasi scraping alternatif (bisa menggunakan BeautifulSoup, Selenium, dll)
        print("⚠️  Untuk implementasi fallback yang lengkap, diperlukan:")
        print("   1. Selenium WebDriver untuk scraping dinamis")
        print("   2. BeautifulSoup untuk parsing HTML")
        print("   3. Proxy rotation untuk menghindari blocking")
        
        # Buat sample data untuk testing
        sample_data = {
            "message": "Fallback method - GraphQL endpoint tidak tersedia",
            "keyword": keyword,
            "timestamp": int(time.time()),
            "suggestion": "Gunakan Selenium WebDriver atau tools scraping lainnya"
        }
        
        filename = os.path.join(output_dir, 'fallback_info.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"ℹ️  Info fallback disimpan di: {filename}")
        return 0

# Usage dan Testing
if __name__ == "__main__":
    print("🔥 TOKOPEDIA SCRAPER ULTIMATE v2.0")
    print("Developed by: Data Mining Expert (30+ years experience)")
    print("=" * 60)
    
    scraper = TokopediaScraperUltimate()
    
    # Test dengan keyword yang berbeda
    test_keywords = ['samsung']  # Bisa ditambah: ['iphone', 'laptop', 'sepatu']
    
    for keyword in test_keywords:
        print(f"\n🎯 Testing keyword: {keyword}")
        result = scraper.scrape_products(
            keyword=keyword, 
            max_pages=5,  # Test dengan 5 halaman dulu
            rows_per_page=60
        )
        
        if result > 0:
            print(f"✅ Scraping berhasil untuk keyword '{keyword}'")
            break
        else:
            print(f"❌ Scraping gagal untuk keyword '{keyword}'")
    
    print("\n🏁 Testing selesai!")