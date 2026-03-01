import os, requests, json, time, re

# 18 SETS TOTAL - 1-9 are INVENTORY, 10-18 are TRACKER
LEGO_SETS = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "price": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 6-Pack", "price": 49.95},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "price": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "price": 325.00},
    {"id": "31167-1", "name": "Creative Animals 3-in-1", "price": 34.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "price": 19.99},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44", "price": 26.99},
    {"id": "76015-1", "name": "Doc Ock Truck Heist", "price": 45.00},
    {"id": "76286-1", "name": "Guardians Milano", "price": 179.99},
    # Tracker items (Scraped)
    {"id": "42224-1", "name": "Rexy the Porsche"},
    {"id": "71858-1", "name": "Ninjago 2026 Set A"},
    {"id": "71847-1", "name": "Ninjago 2026 Set B"},
    {"id": "75349-1", "name": "Captain Rex Helmet"},
    {"id": "30726-1", "name": "2026 Polybag"},
    {"id": "76332-1", "name": "Marvel 2026"},
    {"id": "75435-1", "name": "Star Wars 2026"},
    {"id": "75337-1", "name": "AT-TE Walker"},
    {"id": "75389-1", "name": "The Dark Falcon"}
]

DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works Porsche 911 #54", "img": "Porsche 54.jpg", "p": 39.99},
    {"id": "TW-AMG-BIL", "name": "Mercedes-AMG GT3 Team Bilstein", "img": "Mercedez 4.jpg", "p": 31.99},
    {"id": "TW-AMG-BH", "name": "Mercedes-AMG GT3 Bathurst", "img": "Mercedes 2.jpg", "p": 34.95},
    {"id": "SPK-CIV-16", "name": "Spark Honda Civic Type R-GT", "img": "Honda 16.jpg", "p": 134.95},
    {"id": "TW-F488-51", "name": "Ferrari 488 GT3 Macau #51", "img": "Ferrari 51.jpg", "p": 31.99}
]

def get_market_price(query):
    try:
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        prices = re.findall(r'\$(\d+\.\d+)', r.text)
        if prices: return round(sum([float(p) for p in prices[:3]]) / 3, 2)
    except: pass
    return "TBD"

def run():
    lego_data = []
    for item in LEGO_SETS:
        clean_id = item['id'].split('-')[0]
        # Forced Image Links
        img = f"https://images.brickset.com/sets/images/{clean_id}-1.jpg"
        if "71036" in item['id']: 
            img = "https://www.lego.com/cdn/cs/set/assets/bltf2874100236f6d50/71036.png"
        
        # Use hardcoded price if available, otherwise scrape
        price = item.get('price', get_market_price(f"LEGO {clean_id} new sealed"))
        
        lego_data.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": img,
            "ebay_avg_price": price
        })

    with open('data.json', 'w') as f: json.dump(lego_data, f, indent=4)

    diecast_data = []
    for car in DIECAST_LIST:
        diecast_data.append({
            "set_num": car['id'],
            "name": car['name'],
            "image_url": car['img'],
            "ebay_avg_price": car['p']
        })
    with open('diecast.json', 'w') as f: json.dump(diecast_data, f, indent=4)

if __name__ == "__main__":
    run()
