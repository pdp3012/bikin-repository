import json, requests, os, re, math, glob
import pandas as pd
from tqdm.notebook import tqdm

# INPUT USER - Masukkan nama barang yang ingin dicari
search_query = input("Masukkan nama barang yang ingin dicari: ")

# Konfigurasi URL dengan input user
base_url = 'https://www.tokopedia.com'
first_url = f'https://www.tokopedia.com/find/{search_query.replace(" ", "%20")}'

ROWS = 200 # jumlah maksimal data yang disediakan API Endpoint
PAGES = 0

S = requests.Session()

base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
}

print(f"Memulai scraping untuk: {search_query}")
print(f"URL: {first_url}")

r = S.get(first_url, headers=base_headers)

pattern = r'window\.__cache={(.*?)};'

matches = re.findall(pattern, r.text, re.DOTALL)
matches = '{' + matches[0] + '}'
m = json.loads(matches)

rollout_ = ''
iris_ = ''
params_ = ''
adparams_ = ''
for key, value in m['ROOT_QUERY'].items():
    if 'RolloutFeature' in key:
        rollout_ = key
        iris_ = rollout_.split('iris_session_id":"')[1].split('","')[0]

    if'searchProductV5' in key:
        params_ = key.replace('searchProductV5({"params":"', '').replace('"})', '')

    if 'displayAdsV3' in key:
        adparams_ = key.replace('displayAdsV3({"displayParams":"', '').replace('"})', '')

data_pre = [{"operationName":"SearchProductQueryV5","query":"query SearchProductQueryV5($params: String!, $adParams: String!) {\n  organic: searchProductV5(params: $params) {\n    header {\n      totalData\n      responseCode\n      keywordProcess\n      keywordIntention\n      componentID\n      isQuerySafe\n      additionalParams\n      backendFilters\n      __typename\n    }\n    data {\n      totalDataText\n      related {\n        relatedKeyword\n        position\n        trackingOption\n        otherRelated {\n          keyword\n          url\n          componentID\n          products {\n            id\n            name\n            url\n            applink\n            mediaURL {\n              image\n              __typename\n            }\n            shop {\n              id\n              name\n              city\n              tier\n              __typename\n            }\n            badge {\n              id\n              title\n              url\n              __typename\n            }\n            price {\n              text\n              number\n              __typename\n            }\n            freeShipping {\n              url\n              __typename\n            }\n            labelGroups {\n              position\n              title\n              type\n              url\n              styles {\n                key\n                value\n                __typename\n              }\n              __typename\n            }\n            rating\n            wishlist\n            ads {\n              id\n              productClickURL\n              productViewURL\n              productWishlistURL\n              tag\n              __typename\n            }\n            meta {\n              warehouseID\n              componentID\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      suggestion {\n        currentKeyword\n        suggestion\n        query\n        text\n        componentID\n        trackingOption\n        __typename\n      }\n      products {\n        id\n        name\n        url\n        applink\n        mediaURL {\n          image\n          image300\n          videoCustom\n          __typename\n        }\n        shop {\n          id\n          name\n          url\n          city\n          tier\n          __typename\n        }\n        badge {\n          id\n          title\n          url\n          __typename\n        }\n        price {\n          text\n          number\n          range\n          original\n          discountPercentage\n          __typename\n        }\n        freeShipping {\n          url\n          __typename\n        }\n        labelGroups {\n          position\n          title\n          type\n          url\n          styles {\n            key\n            value\n            __typename\n          }\n          __typename\n        }\n        category {\n          id\n          name\n          breadcrumb\n          gaKey\n          __typename\n        }\n        rating\n        wishlist\n        ads {\n          id\n          productClickURL\n          productViewURL\n          productWishlistURL\n          tag\n          __typename\n        }\n        meta {\n          countReview\n          parentID\n          warehouseID\n          isImageBlurred\n          isPortrait\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  topads: displayAdsV3(displayParams: $adParams) {\n    data {\n      id\n      productClickURL: product_click_url\n      product {\n        id\n        name\n        wishlist\n        image {\n          imageURL: s_ecs\n          viewTrackURL: s_url\n          __typename\n        }\n        url: uri\n        price: price_format\n        rating: product_rating\n        ratingAverage: product_rating_format\n        countReview: count_review_format\n        labelGroups: label_group {\n          position\n          title\n          type\n          url\n          style {\n            key\n            value\n            __typename\n          }\n          __typename\n        }\n        campaign {\n          discountPercentage: discount_percentage\n          originalPrice: original_price\n          __typename\n        }\n        category_breadcrumb\n        __typename\n      }\n      shop {\n        id\n        name\n        uri\n        location\n        goldmerchant: gold_shop\n        official: shop_is_official\n        badges {\n          title\n          imageURL: image_url\n          show\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]

data = data_pre.copy()
data[0]['variables'] = {"params":params_,"adParams":adparams_}

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
    'iris-session_id': iris_,
    'Priority': 'u=4',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

r = S.post('https://gql.tokopedia.com/graphql/SearchProductQueryV5', headers=headers, json=data)

total_data = r.json()[0]['data']['organic']['header']['totalData']

products = r.json()[0]['data']['organic']['data']['products']

PAGES = math.ceil(total_data // ROWS)

print(f"Total data ditemukan: {total_data}")
print(f"Total halaman yang akan di-scrape: {PAGES}")

# Menggunakan nama search query untuk folder
dir_path = f'scrape_tokopedia_{search_query.replace(" ", "_").lower()}'

if not os.path.exists(dir_path): 
    os.makedirs(dir_path)

files = glob.glob(os.path.join(dir_path, '*'))
for file in files:
    try:
        os.remove(file)
    except: 
        pass

rows = ROWS
start_page = 1
last_page = 30

print(f"Memulai scraping dari halaman {start_page} sampai {last_page}")

pbar = tqdm(total=last_page-start_page+1, desc="Scraping halaman")

for page in range(start_page, last_page+1):
    start = (page-1) * rows
    data = data_pre.copy()
    data[0]['variables'] = {
        "params":params_.\
            replace('page=1', 'page=' + str(page)).\
            replace('start=0', 'start=' + str(start)).\
            replace('rows=60', 'rows=' + str(rows)),
        "adParams":adparams_.replace('page=1', 'page=' + str(page))
    }

    r = S.post('https://gql.tokopedia.com/graphql/SearchProductQueryV5', headers=headers, json=data)

    filename = f'{dir_path}/page_{page}.json'
    with open(filename, 'w') as f:
        json.dump(r.json(), f, indent=4)

    pbar.update(1)

pbar.close()

print("Mengolah data hasil scraping...")

all_files = os.listdir(dir_path)
json_files = [file for file in all_files if file.endswith('.json')] 

li = []
pbar = tqdm(total=len(json_files), desc="Memproses file JSON")

for json_file in json_files:
    file_path = os.path.join(dir_path, json_file)
    with open(file_path) as f:
        data = json.load(f)[0]['data']['organic']['data']['products']

        for datum in data:
            li.append({
            'id': datum['id'],
            'name': datum['name'],
            'price': datum['price']['number'],
            'url': datum['url'],
            'shop_id': datum['shop']['id'],
            'shop_name': datum['shop']['name'],
            'shop_city': datum['shop']['city'],
            'shop_url': datum['shop']['url'],
            'category_id': datum['category']['id'],
            'category_name': datum['category']['name'],
            'category_url': base_url + '/p/' + datum['category']['breadcrumb'],
            })

    pbar.update(1)

df = pd.DataFrame(li)
pbar.close()

# Simpan hasil dengan nama file yang mengandung search query
excel_filename = f'hasil_scrape_{search_query.replace(" ", "_").lower()}.xlsx'
df.to_excel(os.path.join(dir_path, excel_filename), index=False)

print(f"\nScraping selesai!")
print(f"Total produk yang berhasil di-scrape: {len(df)}")
print(f"File Excel disimpan di: {dir_path}/{excel_filename}")
print(f"Preview 5 data teratas:")
print(df.head())

# Tampilkan statistik dasar
print(f"\nStatistik Harga:")
print(f"Harga termurah: Rp {df['price'].min():,.0f}")
print(f"Harga termahal: Rp {df['price'].max():,.0f}")
print(f"Harga rata-rata: Rp {df['price'].mean():,.0f}")
print(f"Total toko yang berbeda: {df['shop_name'].nunique()}")
print(f"Total kategori yang berbeda: {df['category_name'].nunique()}")