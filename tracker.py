import os, requests, json, time, re, urllib.parse, datetime

# Get your Scrape.do token from GitHub Secrets
SCRAPE_API_TOKEN = os.getenv("SCRAPE_TOKEN")

# Your verified inventory with mandatory Box-Only shipping specs
LEGO_DATA_LIST = [
    {"id": "75354-1", "name": "Coruscant Guard Gunship", "msrp": 139.99, "weight_lbs": 3.5, "box_size": "18x11x3"},
    {"id": "75356-1", "name": "Executor Super Star Destroyer", "msrp": 69.99, "weight_lbs": 2.2, "box_size": "14x7x3"},
    {"id": "76286-1", "name": "Guardians Milano", "msrp": 179.99, "weight_lbs": 4.1, "box_size": "19x14x3"},
    {"id": "75389-1", "name": "The Dark Falcon", "msrp": 179.99, "weight_lbs": 4.5, "box_size": "22x15x4"},
    {"id": "75337-1", "name": "AT-TE Walker", "msrp": 139.99, "weight_lbs": 3.8, "box_size": "19x14x3"},
    {"id": "77244-1", "name": "Mercedes-AMG F1 W15 (2024)", "msrp": 26.99, "weight_lbs": 1.0, "box_size": "10x6x3"}
]

def get_market_price(set_id):
    clean_id = set_id.split('-')[0]
    query = f"LEGO {clean_id} new sealed"
    target_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(query)}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=1000"
    api_url = f"https://api.scrape.do/?token={SCRAPE_API_TOKEN}&url={urllib.parse.quote(target_url)}"
    
    try:
        r = requests.get(api_url, timeout=20)
        prices = re.findall(r's-item__price.*?\$([\d,]+\.\d{2})', r.text)
        
        if prices:
            float_prices = sorted([float(p.replace(',', '')) for p in prices[:10]])
            if len(float_prices) > 0:
                # Median calculation to prevent "fantasy prices"
                n = len(float_prices)
                if n % 2 == 1:
                    return float_prices[n//2]
                else:
                    return (float_prices[n//2 - 1] + float_prices[n//2]) / 2
    except Exception as e:
        print(f"Error fetching {set_id}: {e}")
    return None

def run():
    print(f"Starting BLKHDZ Market Sync...")
    lego_final = []
    
    for item in LEGO_DATA_LIST:
        market_val = get_market_price(item['id'])
        final_price = market_val if market_val else item.get('msrp', 0.00)
        
        # Standard Brickset image URL format
        set_num_only = item['id'].split('-')[0]
        img = f"https://images.brickset.com/sets/images/{set_num_only}-1.jpg"
        
        lego_final.append({
            "set_num": item['id'], 
            "name": item['name'], 
            "image_url": img,
            "market_value": round(final_price, 2), # Correct field name for index.html
            "shipping_details": { # Correct structure for index.html
                "method": "Box Only",
                "weight_lbs": item.get('weight_lbs'),
                "box_dimensions": item.get('box_size')
            }
        })
        time.sleep(2)

    output = {
        "last_updated": datetime.datetime.now().strftime("%B %d, %Y"), 
        "sets": lego_final
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    run()
