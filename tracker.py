import os, requests, json, time, re, random
from bs4 import BeautifulSoup

API_KEY = os.environ.get('REBRICKABLE_KEY')

# 9 IN-STOCK ITEMS FIRST, THEN 9 WATCHLIST ITEMS
LEGO_SETS = [
    "75354-1", "71036-1", "75356-1", "75274-1", "31167-1", "75345-1", "77247-1", "76015-1", "76286-1",
    "42224-1", "71858-1", "71847-1", "71813-1", "30726-1", "76332-1", "75435-1", "75337-1", "75389-1"
]

# DIECAST WITH UPDATED FILENAMES
DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works 1:64 Porsche 911 GT3 R Nürburgring 24h 2023 #54", "img": "Porsche 54.jpg"},
    {"id": "TW-AMG-BIL", "name": "Tarmac Works 1:64 Mercedes-AMG GT3 #4 Nurburgring 2023 Team Bilstein", "img": "Mercedez 4.jpg"},
    {"id": "TW-AMG-BH", "name": "Tarmac Works HOBBY64 Mercedes-AMG GT3 2022 Bathurst 12hr", "img": "Mercedes 2.jpg"},
    {"id": "SPK-CIV-16", "name": "1:43 Spark Honda Civic Type R-GT #16 GT500 Super GT 2025", "img": "Honda 16.jpg"},
    {"id": "TW-F488-51", "name": "Tarmac Works 1:64 Ferrari 488 GT3 Macau GT Cup Harmony #51", "img": "Ferrari 51.jpg"}
]

def get_ebay_avg(query):
    search_query = query.replace(' ', '+')
    url = f"https://www.ebay.com/sch/i.html?_nkw={search_query}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=3"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    try:
        time.sleep(random.uniform(4, 7)) 
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = []
        for tag in soup.find_all('span', class_='s-item__price'):
            price_text = tag.get_text().replace('$', '').replace(',', '')
            val = re.findall(r"\d+\.\d+", price_text)
            if val:
                price_float = float(val[0])
                if price_float > 5: prices.append(price_float)
        if len(prices) > 1:
            subset = prices[:10]
            return round(sum(subset) / len(subset), 2)
    except: pass
    return "TBD"

def run():
    lego_results = []
    prefix = "key " if API_KEY and not API_KEY.startswith("key ") else ""
    auth_header = f"{prefix}{API_KEY}"
    for sn in LEGO_SETS:
        try:
            r = requests.get(f"https://rebrickable.com/api/v3/lego/sets/{sn}/", headers={'Authorization': auth_header})
            data = r.json()
            avg = get_ebay_avg(f"LEGO {sn.split('-')[0]} new sealed")
            lego_results.append({"set_num": sn, "name": data.get('name', 'Unknown'), "image_url": data.get('set_img_url', ''), "ebay_avg_price": avg})
        except: pass
    with open('data.json', 'w') as f: json.dump(lego_results, f, indent=4)

    diecast_results = []
    for car in DIECAST_LIST:
        avg = get_ebay_avg(car['name'])
        diecast_results.append({"set_num": car['id'], "name": car['name'], "image_url": car['img'], "ebay_avg_price": avg})
    with open('diecast.json', 'w') as f: json.dump(diecast_results, f, indent=4)

if __name__ == "__main__":
    run()
