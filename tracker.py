import os, requests, json, time, re

# 1. ELITE INVENTORY & VERIFIED WATCHLIST
# Your manual prices are 100% PROTECTED. The script only scrapes if 'price' is missing.
LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "price": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 (Set of 6)", "price": 49.95},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "price": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "price": 325.00},
    {"id": "31167-1", "name": "Creator Haunted Mansion", "price": 88.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "price": 19.99},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44", "price": 26.99},
    {"id": "76015-1", "name": "Doc Ock Truck Heist", "price": 45.00},
    {"id": "76286-1", "name": "Guardians Milano", "price": 179.99},
    # --- 2026 WATCHLIST ITEMS ---
    {"id": "42224-1", "name": "Rexy the Porsche (42224)", "price": 185.00}, 
    {"id": "75349-1", "name": "Captain Rex Helmet", "price": 64.50},
    {"id": "75337-1", "name": "AT-TE Walker"}, # These will now show real prices instead of TBD
    {"id": "75389-1", "name": "The Dark Falcon"}, 
    {"id": "71858-1", "name": "Ninjago 2026 Set A"}, 
    {"id": "71847-1", "name": "Ninjago 2026 Set B"},
    {"id": "30726-1", "name": "2026 Polybag"},
    {"id": "76332-1", "name": "Marvel 2026"},
    {"id": "75435-1", "name": "Star Wars 2026"}
]

DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works Porsche 911 #54", "img": "Porsche 54.jpg", "p": 39.99},
    {"id": "TW-AMG-BIL", "name": "Mercedes-AMG GT3 Team Bilstein", "img": "Mercedez 4.jpg", "p": 31.99},
    {"id": "TW-AMG-BH", "name": "Mercedes-AMG GT3 Bathurst", "img": "Mercedes 2.jpg", "p": 34.95},
    {"id": "SPK-CIV-16", "name": "Spark Honda Civic Type R-GT", "img": "Honda 16.jpg", "p": 134.95},
    {"id": "TW-F488-51", "name": "Ferrari 488 GT3 Macau #51", "img": "Ferrari 51.jpg", "p": 31.99}
]

def get_market_price(set_id):
    clean_id = set_id.split('-')[0]
    query = f"LEGO {clean_id} new sealed"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
    
    # UPGRADED HEADERS: This is the "Vision" fix.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }

    try:
        time.sleep(2) # Polite delay
        r = requests.get(url, headers=headers, timeout=15)
        # Improved regex to find green "Sold" prices
        prices = re.findall(r'POSITIVE">\$([\d,]+\.\d+)', r.text)
        
        if prices:
            clean_prices = [float(p.replace(',', '')) for p in prices[:10]]
            return round(sum(clean_prices) / len(clean_prices), 2)
    except: pass
    return "Market TBD"

def run():
    lego_final = []
    for item in LEGO_DATA_LIST:
        clean_id = item['id'].split('-')[0]
        # PRIORITY CHECK: Only scrapes if "price" key is missing.
        val_price = item.get('price', get_market_price(item['id']))
        
        img = f"https://images.brickset.com/sets/images/{clean_id}-1.jpg"
        if "71036" in item['id']:
            img = "https://images.brickset.com/sets/AdditionalImages/71036-1/71036_Lifestyle_1.jpg"

        aff_link = f"https://www.ebay.com/sch/i.html?_nkw=LEGO%20{clean_id}%20new%20sealed&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&customid=BLKHDZ_WEB"
        
        lego_final.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": img,
            "ebay_avg_price": val_price,
            "ebay_link": aff_link
        })

    with open('data.json', 'w') as f:
        json.dump(lego_final, f, indent=4)

    diecast_final = []
    for car in DIECAST_LIST:
        car_query = car['name'].replace(' ', '%20')
        diecast_final.append({
            "set_num": car['id'],
            "name": car['name'],
            "image_url": car['img'],
            "ebay_avg_price": car['p'],
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw={car_query}&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&customid=BLKHDZ_WEB"
        })

    with open('diecast.json', 'w') as f:
        json.dump(diecast_final, f, indent=4)

if __name__ == "__main__":
    run()
