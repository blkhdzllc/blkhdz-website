import os, requests, json, time, re, random

# 18 SETS TOTAL
LEGO_SETS = [
    "75354-1", "71036-1", "75356-1", "75274-1", "31167-1", "75345-1", "77247-1", "76015-1", "76286-1",
    "42224-1", "71858-1", "71847-1", "75349-1", "30726-1", "76332-1", "75435-1", "75337-1", "75389-1"
]

DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works 1:64 Porsche 911 GT3 R Nürburgring 24h 2023 #54", "img": "Porsche 54.jpg"},
    {"id": "TW-AMG-BIL", "name": "Tarmac Works 1:64 Mercedes-AMG GT3 #4 Nurburgring 2023 Team Bilstein", "img": "Mercedez 4.jpg"},
    {"id": "TW-AMG-BH", "name": "Tarmac Works HOBBY64 Mercedes-AMG GT3 2022 Bathurst 12hr", "img": "Mercedes 2.jpg"},
    {"id": "SPK-CIV-16", "name": "1:43 Spark Honda Civic Type R-GT #16 GT500 Super GT 2025", "img": "Honda 16.jpg", "fixed": 134.95},
    {"id": "TW-F488-51", "name": "Tarmac Works 1:64 Ferrari 488 GT3 Macau GT Cup Harmony #51", "img": "Ferrari 51.jpg"}
]

def get_price(query):
    """Simplified price scraper to prevent hang-ups"""
    try:
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        # Find prices using regex for speed
        found = re.findall(r'\$(\d+\.\d+)', r.text)
        if found:
            prices = [float(p) for p in found[:5] if float(p) > 5]
            return round(sum(prices) / len(prices), 2)
    except: pass
    return "TBD"

def run():
    lego_data = []
    for sn in LEGO_SETS:
        clean_id = sn.split('-')[0]
        # FORCE HERO IMAGES
        img = f"https://images.brickset.com/sets/images/{clean_id}.jpg"
        if "71036" in sn: img = "https://images.brickset.com/sets/AdditionalImages/71036-1/71036_Lifestyle_1.jpg"
        if "75349" in sn: img = "https://images.brickset.com/sets/images/75349-1.jpg"
        
        price = get_price(f"LEGO {clean_id} sealed")
        lego_data.append({"set_num": sn, "name": f"LEGO {clean_id}", "image_url": img, "ebay_avg_price": price})
        time.sleep(1) # Small delay to be safe

    with open('data.json', 'w') as f: json.dump(lego_data, f, indent=4)

    diecast_data = []
    for car in DIECAST_LIST:
        p = car.get('fixed', get_price(car['name']))
        diecast_data.append({"set_num": car['id'], "name": car['name'], "image_url": car['img'], "ebay_avg_price": p})

    with open('diecast.json', 'w') as f: json.dump(diecast_data, f, indent=4)

if __name__ == "__main__":
    run()
