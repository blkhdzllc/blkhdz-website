import os, requests, json, time, re

# 1. INVENTORY (Hardcoded Prices)
LEGO_INVENTORY = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "price": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 (Set of 6)", "price": 49.95},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "price": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "price": 325.00},
    {"id": "31167-1", "name": "Creative Animals 3-in-1", "price": 34.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "price": 19.99},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44", "price": 26.99},
    {"id": "76015-1", "name": "Doc Ock Truck Heist", "price": 45.00},
    {"id": "76286-1", "name": "Guardians Milano", "price": 179.99}
]

# 2. WATCHLIST (Scraped, Rex Fixed)
LEGO_WATCHLIST = [
    {"id": "75349-1", "name": "Captain Rex Helmet", "price": 60.00}, 
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"},
    {"id": "71858-1", "name": "Ninjago 2026 Set A"},
    {"id": "71847-1", "name": "Ninjago 2026 Set B"},
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
        if prices:
            valid = [float(p) for p in prices[:5] if float(p) > 10]
            if valid: return round(sum(valid) / len(valid), 2)
    except: pass
    return "Market TBD"

def run():
    lego_final = []
    # EPN Details
    campid = "5339141674"
    toolid = "10001"
    
    for item in (LEGO_INVENTORY + LEGO_WATCHLIST):
        clean_id = item['id'].split('-')[0]
        
        # Image Logic
        if "71036" in item['id']:
            img = "https://images.brickset.com/sets/AdditionalImages/71036-1/71036_Lifestyle_1.jpg"
        else:
            img = f"https://images.brickset.com/sets/images/{clean_id}-1.jpg"
        
        price = item.get('price', get_market_price(f"LEGO {clean_id} new sealed"))
        
        # NEW DIRECT LINK STRUCTURE
        search_query = f"LEGO {clean_id} new sealed".replace(' ', '%20')
        affiliate_link = f"https://www.ebay.com/sch/i.html?_nkw={search_query}&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid={campid}&toolid={toolid}&customid=BLKHDZ_WEB"
        
        lego_final.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": img,
            "ebay_avg_price": price,
            "ebay_link": affiliate_link
        })

    with open('data.json', 'w') as f:
        json.dump(lego_final, f, indent=4)

    diecast_final = []
    for car in DIECAST_LIST:
        search_car = car['name'].replace(' ', '%20')
        car_link = f"https://www.ebay.com/sch/i.html?_nkw={search_car}&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid={campid}&toolid={toolid}&customid=BLKHDZ_WEB"
        
        diecast_final.append({
            "set_num": car['id'],
            "name": car['name'],
            "image_url": car['img'],
            "ebay_avg_price": car['p'],
            "ebay_link": car_link
        })

    with open('diecast.json', 'w') as f:
        json.dump(diecast_final, f, indent=4)

if __name__ == "__main__":
    run()
