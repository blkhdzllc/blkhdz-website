import os, requests, json, time, re, urllib.parse, datetime

SCRAPE_API_TOKEN = os.getenv("SCRAPE_TOKEN")

# Corrected List with the 2024 Season Mercedes W15
LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "msrp": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 (6-Pack)", "msrp": 29.99},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "msrp": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "msrp": 425.00},
    {"id": "31167-1", "name": "Creator Haunted Mansion", "msrp": 88.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "msrp": 19.99},
    {"id": "76286-1", "name": "Guardians Milano", "msrp": 179.99},
    {"id": "75389-1", "name": "The Dark Falcon", "msrp": 179.99},
    {"id": "76332-1", "name": "The Batman Batmobile (2026)", "msrp": 29.99},
    {"id": "75435-1", "name": "Battle of Felucia Separatist MTT", "msrp": 159.99},
    {"id": "42224-1", "name": "Rexy the Porsche (42224)", "msrp": 149.99},
    {"id": "71858-1", "name": "Ninjago 15th Anniv. Blacksmith", "msrp": 129.99},
    {"id": "71847-1", "name": "Ninjago The Guardian Dragon", "msrp": 19.99},
    {"id": "30726-1", "name": "Bruce Wayne & Batsuit Polybag", "msrp": 4.99},
    {"id": "75349-1", "name": "Captain Rex Helmet", "msrp": 69.99},
    {"id": "75337-1", "name": "AT-TE Walker", "msrp": 139.99},
    {"id": "77244-1", "name": "Mercedes-AMG F1 W15 (2024)", "msrp": 26.99}
]

def get_market_price(set_id):
    clean_id = set_id.split('-')[0]
    query = f"LEGO {clean_id} new sealed"
    target_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(query)}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=1000"
    api_url = f"https://api.scrape.do/?token={SCRAPE_API_TOKEN}&url={urllib.parse.quote(target_url)}"
    
    try:
        r = requests.get(api_url, timeout=20)
        prices = re.findall(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2}))', r.text)
        if prices:
            float_prices = sorted([float(p.replace(',', '')) for p in prices])
            if len(float_prices) > 3:
                float_prices = float_prices[1:-1]
            return round(sum(float_prices) / len(float_prices), 2)
    except:
        return None
    return None

def run():
    print(f"Syncing BLKHDZ Inventory...")
    lego_final = []
    for item in LEGO_DATA_LIST:
        market_val = get_market_price(item['id'])
        # Fallback to MSRP so the site never looks "broke"
        final_price = market_val if market_val else item.get('msrp', "TBD")
        
        # This link format is the most stable for images
        img = f"https://images.brickset.com/sets/images/{item['id'].split('-')[0]}-1.jpg"
        
        lego_final.append({
            "set_num": item['id'], 
            "name": item['name'], 
            "image_url": img,
            "ebay_avg_price": final_price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO%20{item['id'].split('-')[0]}%20new%20sealed&mkcid=1&mkrid=711-53200-19255-0&campid=5339141674&customid=BLKHDZ_WEB"
        })
        time.sleep(1)

    output = {"last_updated": datetime.datetime.now().strftime("%B %d, %Y"), "sets": lego_final}
    with open('data.json', 'w') as f: json.dump(output, f, indent=4)
    print("Market Sync Complete.")

if __name__ == "__main__":
    run()
