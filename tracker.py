import os, json, datetime

# Your specific prices as of March 22, 2026
MANUAL_PRICES = {
    "31020": 56.00,
    "71738": 104.85,
    "31144": 28.54,
    "76015": 64.95,
    "77247": 49.99,
    "76295": 69.95,
    "76232": 59.95,
    "60449": 49.95,
    "30726": 11.93
}

# Full inventory list with Box-specific shipping requirements
LEGO_DATA_LIST = [
    {"id": "31020", "name": "LEGO Creator Twinblade Adventures", "weight": 0.7, "box": "10x7x2", "asin": "B00GSPF9PU"},
    {"id": "71738", "name": "Ninjago Zane's Titan Mech Battle", "weight": 2.8, "box": "14x15x3", "asin": "B08NF9YF5R"},
    {"id": "31144", "name": "Creator 3-in-1 Exotic Pink Parrot", "weight": 0.8, "box": "10x7x2", "asin": "B0BBRYTCXG"},
    {"id": "76015", "name": "Marvel Doc Ock Truck Heist", "weight": 0.9, "box": "11x7x2", "asin": "B00I3P7HRC"},
    {"id": "77247", "name": "Speed Champions Kicks Sauber F1", "weight": 0.9, "box": "10x6x3", "asin": "B0CW9VRD3Y"},
    {"id": "76295", "name": "Marvel Avengers Helicarrier", "weight": 1.9, "box": "15x10x3", "asin": "B0CW9V1W1R"},
    {"id": "76232", "name": "The Marvels: Hoopty Spaceship", "weight": 1.8, "box": "15x10x3", "asin": "B0BXQ5Z9W7"},
    {"id": "60449", "name": "City Off-Road Police Car Chase", "weight": 1.6, "box": "11x10x3", "asin": "B0CW9V6K9F"},
    {"id": "30726", "name": "Batman: Bruce Wayne and the Batsuit", "weight": 0.6, "box": "7x5x3", "asin": "B0CXBB9L9X"}
]

def run():
    print("Starting BLKHDZ Manual Price Sync...")
    lego_final = []
    
    for item in LEGO_DATA_LIST:
        set_id = item['id']
        final_price = MANUAL_PRICES.get(set_id, 0.00)
        
        print(f"Processing: {item['name']} -> ${final_price}")
        
        lego_final.append({
            "set_num": set_id, 
            "name": item['name'], 
            "asin": item.get('asin', ""),
            "market_value": round(final_price, 2),
            "shipping_details": {
                "weight_lbs": item.get('weight'),
                "box_dimensions": item.get('box')
            }
        })

    output = {
        "last_updated": datetime.datetime.now().strftime("%B %d, %Y"), 
        "sets": lego_final,
        "diecast": [] 
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Sync Complete. {len(lego_final)} sets updated in data.json.")

if __name__ == "__main__":
    run()
