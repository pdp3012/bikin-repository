import json, requests, os, re, math, glob
import pandas as pd
from tqdm import tqdm
import time

class TokopediaScraper:
    def __init__(self):
        self.base_url = 'https://www.tokopedia.com'
        self.session = requests.Session()
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def extract_search_params(self, search_url):
        """Extract search parameters from Tokopedia search page"""
        try:
            r = self.session.get(search_url, headers=self.base_headers)
            r.raise_for_status()
            
            # Cari berbagai pattern yang mungkin ada
            patterns = [
                r'window\.__cache\s*=\s*({.*?});',
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__APOLLO_STATE__\s*=\s*({.*?});'
            ]
            
            cache_data = None
            for pattern in patterns:
                matches = re.findall(pattern, r.text, re.DOTALL)
                if matches:
                    try:
                        cache_data = json.loads(matches[0])
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not cache_data:
                raise ValueError("Tidak dapat menemukan data cache di halaman")
            
            # Extract parameters dengan berbagai kemungkinan struktur
            params = self._extract_params_from_cache(cache_data)
            return params
            
        except Exception as e:
            print(f"Error saat extract params: {e}")
            # Fallback ke parameters default
            return self._get_default_params()
    
    def _extract_params_from_cache(self, cache_data):
        """Extract parameters dari cache data dengan berbagai struktur"""
        params = {
            'iris_session_id': '',
            'search_params': '',
            'ad_params': ''
        }
        
        # Cari di berbagai lokasi yang mungkin
        search_locations = [
            cache_data.get('ROOT_QUERY', {}),
            cache_data.get('data', {}),
            cache_data.get('apolloState', {}),
            cache_data
        ]
        
        for location in search_locations:
            if not isinstance(location, dict):
                continue
                
            for key, value in location.items():
                if isinstance(key, str):
                    # Extract iris session ID
                    if 'iris_session_id' in key or 'iris-session' in key:
                        if 'iris_session_id":"' in key:
                            params['iris_session_id'] = key.split('iris_session_id":"')[1].split('","')[0]
                    
                    # Extract search parameters
                    if 'searchProductV5' in key and 'params":"' in key:
                        params['search_params'] = key.replace('searchProductV5({"params":"', '').replace('"})', '')
                    
                    # Extract ad parameters
                    if 'displayAdsV3' in key and 'displayParams":"' in key:
                        params['ad_params'] = key.replace('displayAdsV3({"displayParams":"', '').replace('"})', '')
        
        # Jika tidak ada params yang ditemukan, gunakan default
        if not params['search_params']:
            params = self._get_default_params()
            
        return params
    
    def _get_default_params(self):
        """Default parameters jika extraction gagal"""
        return {
            'iris_session_id': f'session_{int(time.time())}',
            'search_params': 'device=desktop&navsource=&ob=23&page=1&q=samsung&related=true&rows=60&safe_search=false&scheme=https&shipping=&source=search&srp_component_id=02.01.00.00&st=product&start=0&topads_bucket=true&unique_id=',
            'ad_params': 'headline_product_count=2&item=15&page=1&product_ads_count=2&qid=&sc=24&user_addressId=&user_cityId=176&user_districtId=2274&user_id=&user_lat=&user_long=&user_postCode=&user_warehouseId=12210375'
        }
    
    def create_graphql_query(self):
        """Create GraphQL query untuk search"""
        return """query SearchProductQueryV5($params: String!, $adParams: String!) {
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
                  videoCustom
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
                  styles {
                    key
                    value
                    __typename
                  }
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
                ads {
                  id
                  productClickURL
                  productViewURL
                  productWishlistURL
                  tag
                  __typename
                }
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
        }"""
    
    def scrape_products(self, search_keyword='samsung', max_pages=30, rows_per_page=60):
        """Main scraping function"""
        print(f"Memulai scraping untuk keyword: {search_keyword}")
        
        # Setup directory
        dir_path = 'scrape_tokopedia_requests'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Clean existing files
        files = glob.glob(os.path.join(dir_path, '*'))
        for file in files:
            try:
                os.remove(file)
            except:
                pass
        
        # Get search parameters
        search_url = f'https://www.tokopedia.com/find/{search_keyword}'
        params = self.extract_search_params(search_url)
        
        # Create GraphQL headers
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'content-type': 'application/json',
            'Tkpd-UserId': '0',
            'x-device': 'desktop-0.0',
            'x-dark-mode': 'false',
            'X-Source': 'tokopedia-lite',
            'X-Version': 'ed69c5d',
            'X-Tkpd-Lite-Service': 'zeus',
            'iris-session_id': params['iris_session_id'],
            'Priority': 'u=4',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # GraphQL query
        query_data = [{
            "operationName": "SearchProductQueryV5",
            "query": self.create_graphql_query(),
            "variables": {
                "params": params['search_params'],
                "adParams": params['ad_params']
            }
        }]
        
        # Test first request
        try:
            test_response = self.session.post(
                'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                headers=headers,
                json=query_data
            )
            test_response.raise_for_status()
            test_data = test_response.json()
            
            if test_data and len(test_data) > 0 and 'data' in test_data[0]:
                total_data = test_data[0]['data']['organic']['header']['totalData']
                print(f"Total data tersedia: {total_data}")
            else:
                raise ValueError("Response tidak valid")
                
        except Exception as e:
            print(f"Error pada test request: {e}")
            print("Menggunakan mode scraping sederhana...")
            return self._simple_scrape(search_keyword, max_pages)
        
        # Start scraping
        pbar = tqdm(total=max_pages, desc="Scraping pages")
        successful_pages = 0
        
        for page in range(1, max_pages + 1):
            try:
                start = (page - 1) * rows_per_page
                
                # Update parameters untuk page ini
                current_params = params['search_params']
                current_params = re.sub(r'page=\d+', f'page={page}', current_params)
                current_params = re.sub(r'start=\d+', f'start={start}', current_params)
                current_params = re.sub(r'rows=\d+', f'rows={rows_per_page}', current_params)
                
                current_ad_params = params['ad_params']
                current_ad_params = re.sub(r'page=\d+', f'page={page}', current_ad_params)
                
                # Update query data
                page_query_data = [{
                    "operationName": "SearchProductQueryV5",
                    "query": self.create_graphql_query(),
                    "variables": {
                        "params": current_params,
                        "adParams": current_ad_params
                    }
                }]
                
                # Make request
                response = self.session.post(
                    'https://gql.tokopedia.com/graphql/SearchProductQueryV5',
                    headers=headers,
                    json=page_query_data
                )
                
                if response.status_code == 200:
                    filename = f'{dir_path}/page_{page}.json'
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(response.json(), f, indent=4, ensure_ascii=False)
                    successful_pages += 1
                else:
                    print(f"Error pada page {page}: HTTP {response.status_code}")
                
                # Delay untuk menghindari rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error pada page {page}: {e}")
                
            pbar.update(1)
        
        pbar.close()
        print(f"Scraping selesai. {successful_pages} dari {max_pages} halaman berhasil disimpan.")
        return successful_pages
    
    def _simple_scrape(self, search_keyword, max_pages):
        """Fallback simple scraping method"""
        print("Menggunakan metode scraping alternatif...")
        # Implementasi scraping sederhana jika GraphQL gagal
        return 0

# Usage
if __name__ == "__main__":
    scraper = TokopediaScraper()
    scraper.scrape_products(search_keyword='samsung', max_pages=30, rows_per_page=60)