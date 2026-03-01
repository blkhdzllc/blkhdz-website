import os, requests, json, time, re, random
from bs4 import BeautifulSoup

API_KEY = os.environ.get('REBRICKABLE_KEY')

# YOUR STRATEGIC LIST: 9 Inventory First, then 9 Tracker
LEGO_SETS = [
    "75354-1", "71036-1", "75356-1", "75274-1", "31167-1", "75345-1", "77247-1", "76015-1", "76286-1", # Inventory
    "42224-1", "71858-1", "71847-1", "71813-1", "30726-1", "76332-1", "75435-1", "75337-1", "75389-1"  # Tracker
]

# YOUR DIECAST INVENTORY
DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works 1:64 Porsche 911 GT3 R #54 Nurburgring 2023", "img": "porsche-54.jpg"},
    {"id": "TW-AMG-BIL", "name": "Tarmac Works 1:64 Mercedes-AMG GT3 #4 Bilstein Nurburgring", "img": "mercedes-bilstein.jpg"},
    {"id": "TW-AMG-BH", "name": "Tarmac Works Hobby64 Mercedes-AMG GT3 2022 Bathurst 12hr", "img": "mercedes-bathurst.jpg"},
    {"id": "SPK-CIV-16", "name": "1:43 Spark Honda Civic Type R-GT #16 GT500 Super GT 2025", "img": "civic-spark-16.jpg"},
    {"id": "TW-F488-51", "name": "Tarmac Works 1:64 Ferrari 488 GT3 Macau Harmony #51", "img": "ferrari-macau.jpg"}
]

def get_ebay_avg(query):
    # Search specifically for Sold/Completed
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    try:
        time.sleep(random.uniform(3, 6)) # Vital for 2026 eBay scraping
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = []
        
        for tag in soup.find_all('span', class_='s-item__price'):
            price_text = tag.get_text().replace('$', '').replace(',', '')
            val = re.findall(r"\d+\.\d+", price_text)
            if val:
                price_float = float(val[0])
                if price_float > 5: # Filter out low-value noise
                    prices.append(price_float)
        
        if len(prices) > 1:
            subset = prices[:8] # Average of most recent 8 sales
            return round(sum(subset) / len(subset), 2)
    except Exception as e:
        print(f"Scrape Error for {query}: {e}")
    return "TBD"

def run():
    # --- PART 1: LEGO ---
    lego_results = []
    prefix = "key " if API_KEY and not API_KEY.startswith("key ") else ""
    auth_header = f"{prefix}{API_KEY}"
    
    for sn in LEGO_SETS:
        print(f"Tracking LEGO: {sn}...")
        try:
            r = requests.get(f"https://rebrickable.com/api/v3/lego/sets/{sn}/", headers={'Authorization': auth_header})
            data = r.json()
            clean_id = sn.split('-')[0]
            avg = get_ebay_avg(f"LEGO {clean_id} new sealed")
            
            lego_results.append({
                "set_num": sn,
                "name": data.get('name', 'Unknown LEGO Set'),
                "image_url": data.get('set_img_url', ''),
                "ebay_avg_price": avg
            })
        except Exception as e: print(f"Lego Error: {e}")

    with open('data.json', 'w') as f:
        json.dump(lego_results, f, indent=4)

    # --- PART 2: DIECAST ---
    diecast_results = []
    for car in DIECAST_LIST:
        print(f"Tracking Diecast: {car['name']}...")
        avg = get_ebay_avg(car['name'])
        
        diecast_results.append({
            "set_num": car['id'],
            "name": car['name'],
            "image_url": car['img'], # This uses your local JPG filename
            "ebay_avg_price": avg
        })

    with open('diecast.json', 'w') as f:
        json.dump(diecast_results, f, indent=4)

    print("Success: data.json and diecast.json updated.")

if __name__ == "__main__":
    run()
