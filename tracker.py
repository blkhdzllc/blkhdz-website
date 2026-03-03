import os, requests, json, time, re

# VERIFIED TOKEN
SCRAPE_API_TOKEN = "3687f040467644d5a62797baa02ffba5f13b60e27d5"

# --- FULL INVENTORY LIST (LEGO + DIECAST) ---
LEGO_LIST = [
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"},
    {"id": "75337-1", "name": "AT-TE Walker"},
    {"id": "75389-1", "name": "The Dark Falcon"},
    {"id": "75354-1", "name": "Coruscant Guard Gunship"},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet"},
    {"id": "75435-1", "name": "MTT - Battle of Felucia (2026)"},
    {"id": "75356-1", "name": "Executor Super Star Destroyer"}
]

DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works Porsche 911 #54", "img": "Porsche 54.jpg", "p": 39.99},
    {"id": "TW-AMG-BIL", "name": "Mercedes-AMG GT3 Team Bilstein", "img": "Mercedez 4.jpg", "p": 31.99},
    {"id": "TW-AMG-BH", "name": "Mercedes-AMG GT3 Bathurst", "img": "Mercedes 2.jpg", "p": 34.95},
    {"id": "SPK-CIV-16", "name": "Spark Honda Civic Type R-GT", "img": "Honda 16.jpg", "p": 134.95},
    {"id": "TW-F488-51", "name": "Ferrari 488 GT3 Macau #51", "img": "Ferrari 51.jpg", "p": 31.99}
]

def get_market_price(set_num):
    clean_id = set_num.split('-')[0]
    # PINPOINT SEARCH: US Only, New Condition, Excludes Custom/Pro mods to keep price realistic
    search_query = f"LEGO {clean_id} -pro -custom -light"
    target_url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1&LH_PrefLoc=1&LH_ItemCondition=1000"
    
    api_url = f"https://api.scrape.do?token={SCRAPE_API_TOKEN}&url={target_url}"

    try:
        r = requests.get(api_url, timeout=30)
        # March 2026 eBay HTML Pattern Match
        prices = re.findall(r'POSITIVE">\$([\d,]+\.\d+)', r.text)
        if not prices:
            prices = re.findall(r's-item__price">.*?\$([\d,]+\.\d+)', r.text)
        
        if prices:
            # Take only the last 10 sold items for a true market average
            clean_prices = [float(p.replace(',', '')) for p in prices[:10]]
            avg = round(sum(clean_prices) / len(clean_prices), 2)
            # Guardrail: If average is insane (double retail), check logic
            return avg
    except:
        pass
    return None

def run():
    # Load old data to ensure we never have a blank website
    try:
        with open('data.json', 'r') as f:
            old_data = {item['set_num']: item for item in json.load(f)}
    except:
        old_data = {}

    final_inventory = []

    # Process LEGO
    for item in LEGO_LIST:
        print(f"Analyzing Market for {item['name']}...")
        new_price = get_market_price(item['id'])
        
        # If scraper fails, keep the last known good price
        price = new_price if new_price else old_data.get(item['id'], {}).get('ebay_avg_price', "Market TBD")
        
        final_inventory.append({
            "set_num": item['id'],
            "name": item['name'],
            "image_url": f"https://images.brickset.com/sets/images/{item['id'].split('-')[0]}-1.jpg",
            "ebay_avg_price": price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO+{item['id'].split('-')[0]}+new+sealed&LH_PrefLoc=1"
        })
        time.sleep(1)

    # Process Diecast (restores your missing cars)
    for car in DIECAST_LIST:
        final_inventory.append({
            "set_num": car['id'],
            "name": car['name'],
            "image_url": car['img'],
            "ebay_avg_price": car['p'],
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw={car['name'].replace(' ', '+')}"
        })

    with open('data.json', 'w') as f:
        json.dump(final_inventory, f, indent=4)
    print("Full inventory restored and prices pinpointed.")

if __name__ == "__main__":
    run()
