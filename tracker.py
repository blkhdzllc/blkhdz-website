import os, requests, json, time, re, urllib.parse, datetime

# ==========================================================
# CONFIGURATION
# ==========================================================
SCRAPE_API_TOKEN = os.getenv("SCRAPE_TOKEN")

# LEGO DATA: Added MSRP where applicable for fallback accuracy
LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "msrp": 139.99},
    {"id": "71036-1", "name": "Minifigures Series 23 (6-Pack)", "msrp": 29.99},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "msrp": 69.99},
    {"id": "75274-1", "name": "TIE Fighter Pilot Helmet", "msrp": 59.99},
    {"id": "31167-1", "name": "Creator Haunted Mansion", "msrp": 88.99},
    {"id": "75345-1", "name": "501st Clone Troopers Battle Pack", "msrp": 19.99},
    {"id": "77247-1", "name": "KICK Sauber F1 Team C44", "msrp": 26.99},
    {"id": "76286-1", "name": "Guardians Milano", "msrp": 179.99},
    {"id": "75389-1", "name": "The Dark Falcon", "msrp": 179.99},
    {"id": "76332-1", "name": "The Batman Batmobile (2026)"},
    {"id": "75435-1", "name": "Battle of Felucia Separatist MTT"},
    {"id": "42224-1", "name": "Rexy the Porsche (42224)"},
    {"id": "71858-1", "name": "Ninjago 15th Anniv. Blacksmith"},
    {"id": "71847-1", "name": "Ninjago The Guardian Dragon"},
    {"id": "30726-1", "name": "Bruce Wayne & Batsuit Polybag"},
    {"id": "75349-1", "name": "Captain Rex Helmet", "msrp": 69.99},
    {"id": "75337-1", "name": "AT-TE Walker", "msrp": 139.99}
]

DIECAST_LIST = [
    {"id": "TW-911-54", "name": "Tarmac Works Porsche 911 #54", "img": "Porsche 54.jpg", "p": 39.99},
    {"id": "TW-AMG-BIL", "name": "Mercedes-AMG GT3 Team Bilstein", "img": "Mercedez 4.jpg", "p": 31.99},
    {"id": "TW-AMG-BH", "name": "Mercedes-AMG GT3 Bathurst", "img": "Mercedes 2.jpg", "p": 34.95},
    {"id": "SPK-CIV-16", "name": "Spark Honda Civic Type R-GT", "img": "Honda 16.jpg", "p": 134.95},
    {"id": "TW-F488-51", "name": "Ferrari 488 GT3 Macau #51", "img": "Ferrari 51.jpg", "p": 31.99}
]

# ==========================================================
# SCRAPING LOGIC
# ==========================================================
def get_market_price(set_id):
    clean_id = set_id.split('-')[0]
    query = f"LEGO {clean_id} new sealed"
    
    # NEW FILTERS: LH_ItemCondition=1000 (New), LH_Sold=1 (Sold items only)
    target_ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(query)}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=1000&rt=nc&LH_BIN=1"
    api_url = f"https://api.scrape.do/?token={SCRAPE_API_TOKEN}&url={urllib.parse.quote(target_ebay_url)}"
    
    try:
        r = requests.get(api_url, timeout=30)
        # Regex to find prices like $149.99
        prices = re.findall(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2}))', r.text)
        
        if prices:
            float_prices = [float(p.replace(',', '')) for p in prices]
            # Remove extreme outliers (lower than 40% of the max price) to filter out "Stickers" or "Instructions Only"
            max_p = max(float_prices)
            clean_prices = [p for p in float_prices if p > (max_p * 0.4)]
            
            if clean_prices:
                # Average the most recent 6 valid sales
                return round(sum(clean_prices[:6]) / len(clean_prices[:6]), 2)
    except Exception as e:
        print(f"Error scraping {clean_id}: {e}")
    return None

def run():
    print(f"--- BLKHDZ UPDATE START: {datetime.datetime.now()} ---")
    lego_final = []
    
    for item in LEGO_DATA_LIST:
        clean_id = item['id'].split('-')[0]
        print(f"Processing: {item['name']}...")
        
        market_val = get_market_price(item['id'])
        
        # Determine Final Price: Scraped Value > MSRP > TBD
        final_price = market_val if market_val else item.get('msrp', "TBD")

        # Set Image Logic
        img = f"https://images.brickset.com/sets/images/{clean_id}-1.jpg"
        if "71036" in item['id']:
            img = "https://images.brickset.com/sets/AdditionalImages/71036-1/71036_Lifestyle_1.jpg"

        lego_final.append({
            "set_num": item['id'], 
            "name": item['name'], 
            "image_url": img,
            "ebay_avg_price": final_price,
            "ebay_link": f"https://www.ebay.com/sch/i.html?_nkw=LEGO%20{clean_id}%20new%20sealed&LH_ItemCondition=1000"
        })
        time.sleep(1.5) # Compliance delay

    output_data = {
        "last_updated": datetime.datetime.now().strftime("%B %d, %Y"),
        "sets": lego_final
    }

    with open('data.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    
    with open('diecast.json', 'w') as f:
        json.dump(DIECAST_LIST, f, indent=4)
    
    print("--- UPDATE COMPLETE ---")

if __name__ == "__main__":
    run()
