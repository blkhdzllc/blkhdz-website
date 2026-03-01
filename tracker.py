import os, requests, json, time, re

# Ensure the output keys match your HTML (set_num, name, image_url, ebay_avg_price)
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
    {"id": "75349-1", "name": "Captain Rex Helmet", "price": 69.99} # Hardcoded to be safe
]

# Adding tracker sets (without hardcoded prices)
TRACKER_IDS = ["42224-1", "71858-1", "71847-1", "30726-1", "76332-1", "75435-1", "75337-1", "75389-1"]

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
    return "Market TBD"

def run():
    lego_final = []
    # Process Inventory
    for item in LEGO_SETS:
        clean_id = item['id'].split('-')[0]
        img = f"https://images.brickset.com/sets/images/{clean_id}-1.jpg"
        if "71036" in item['id']: img = "https://www.lego.com/cdn/cs/set/assets/bltf2874100236f6d50/71036.png"
        
        lego_final.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": img,
            "ebay_avg_price": item['price'] # This is the hardcoded fix
        })

    # Process Tracker
    for tid in TRACKER_IDS:
        clean_id = tid.split('-')[0]
        lego_final.append({
            "set_num": tid,
            "name": f"LEGO {clean_id} Tracker",
            "image_url": f"https://images.brickset.com/sets/images/{clean_id}-1.jpg",
            "ebay_avg_price": get_market_price(f"LEGO {clean_id} sealed")
        })

    with open('data.json', 'w') as f: json.dump(lego_final, f, indent=4)

    diecast_final = []
    for car in DIECAST_LIST:
        diecast_final.append({
            "set_num": car['id'],
            "name": car['name'],
            "image_url": car['img'],
            "ebay_avg_price": car['p'] # Fixed variable name
        })
    with open('diecast.json', 'w') as f: json.dump(diecast_final, f, indent=4)

if __name__ == "__main__":
    run()
