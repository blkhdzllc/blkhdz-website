import os
import json
import datetime
from services.market_intel import get_aggregated_valuation


# --- 2. RAW INVENTORY DATA ---
# LEGO DATA: Standardized with your specific shipping dimensions and weights
LEGO_DATA = [
    {"id": "75274", "name": "Star Wars Helmet Collection (Variation)", "w": 3.2, "b": "14x10x6", "url": "https://www.ebay.com/itm/116951073772", "feat": True, "img": "75274.jpg"},
    {"id": "31167", "name": "Haunted Mansion 3-in-1 Seasonal Set", "w": 3.5, "b": "15x14x3", "url": "https://www.ebay.com/itm/117037598121", "feat": True, "img": "31167.jpg"},
    {"id": "31020", "name": "LEGO Creator Twinblade Adventures", "w": 0.7, "b": "10x7x2", "url": "https://www.ebay.com/itm/117004206278", "feat": False, "img": "31020.jpg"},
    {"id": "71738", "name": "Ninjago Zane's Titan Mech Battle", "w": 2.8, "b": "14x15x3", "url": "https://www.ebay.com/itm/117058462903", "feat": False, "img": "71738.jpg"},
    {"id": "31144", "name": "Creator 3-in-1 Exotic Pink Parrot", "w": 0.8, "b": "10x7x2", "url": "https://www.ebay.com/itm/116989698157", "feat": False, "img": "31144.jpg"},
    {"id": "76015", "name": "Marvel Doc Ock Truck Heist", "w": 0.9, "b": "11x7x2", "url": "https://www.ebay.com/itm/117029953980", "feat": False, "img": "76015.jpg"},
    {"id": "77247", "name": "Speed Champions Kicks Sauber F1", "w": 0.9, "b": "10x6x3", "url": "https://www.ebay.com/itm/117089969442", "feat": False, "img": "77247.jpg"},
    {"id": "76295", "name": "Marvel Avengers Helicarrier", "w": 1.9, "b": "15x10x3", "url": "https://www.ebay.com/itm/117007504223", "feat": False, "img": "76295.jpg"},
    {"id": "76232", "name": "The Marvels: Hoopty Spaceship", "w": 1.8, "b": "15x10x3", "url": "https://www.ebay.com/itm/117038961595", "feat": False, "img": "76232.jpg"},
    {"id": "60449", "name": "City Off-Road Police Car Chase", "w": 1.6, "b": "11x10x3", "url": "https://www.ebay.com/itm/117070479765", "feat": False, "img": "60449.jpg"},
    {"id": "30726", "name": "Batman: Bruce Wayne and the Batsuit", "w": 0.6, "b": "7x5x3", "url": "https://www.ebay.com/itm/117076682926", "feat": False, "img": "30726.jpg"},
    {"id": "41619", "name": "Brickheadz Darth Vader", "w": 0.4, "b": "5x4x3", "url": "https://www.ebay.com/itm/116928952963", "feat": False, "img": "41619.jpg"}
]

# DIECAST DATA: Reflects your cleaned MGT00716 and MGT01046 filenames
DIECAST_DATA = [
    {"id": "MGT00773-C", "name": "Mazda RX-7 LB-Silhouette #41 [CHASE SET]", "p": 95.00, "stat": "LIMITED CHASE SET", "url": "https://www.ebay.com/itm/117098917766", "feat": True, "img": "MGT00773-C.jpg"},
    {"id": "43SGT25016", "name": "1/43 Spark Honda Civic Type R-GT #16 2025", "p": 134.95, "stat": "PREMIUM 2025 RELEASE", "url": "https://www.ebay.com/itm/117055371825", "feat": True, "img": "43SGT25016.jpg"},
    {"id": "MGT00773-R", "name": "Mazda RX-7 LB-Silhouette #41 [White]", "p": 14.99, "stat": "22 IN STOCK", "url": "https://www.ebay.com/itm/117080910055", "feat": False, "img": "MGT00773-MJ.jpg"},
    {"id": "PR640255", "name": "Pop Race Mazda RX-7 FD3S RE Amemiya", "p": 28.99, "stat": "POP RACE APPROVED", "url": "https://www.ebay.com/itm/117078677592", "feat": False, "img": "PR640255.jpg"},
    {"id": "PR640212", "name": "Pop Race Honda Civic EG6 Pandem", "p": 26.99, "stat": "IN STOCK", "url": "https://www.ebay.com/itm/117078703657", "feat": False, "img": "PR640212.jpg"},
    {"id": "MGT01046", "name": "Mazda RX-7 FD3S RE Amemiya 20B", "p": 14.99, "stat": "IN STOCK", "url": "https://www.ebay.com/itm/117078628407", "feat": False, "img": "MGT01046.jpg"},
    {"id": "MGT00716", "name": "Cadillac V-Series.R #2 Le Mans Blue", "p": 16.99, "stat": "LIMITED EDITION", "url": "https://www.ebay.com/itm/117081912634", "feat": False, "img": "MGT00716.jpg"},
    {"id": "TSMV0027", "name": "1/43 Mazda RX-7 LB Silhouette IMSA", "p": 32.00, "stat": "1/43 SCALE", "url": "https://www.ebay.com/itm/117078591872", "feat": False, "img": "TSMV0027.jpg"},
    {"id": "T64-070-51", "name": "Ferrari 488 GT3 Macau GT Cup #51", "p": 24.95, "stat": "LOW STOCK", "url": "https://www.ebay.com/itm/117056036936", "feat": False, "img": "T64-072-22MGP51.jpg"},
    {"id": "T64-062-04", "name": "Mercedes-AMG GT3 #4 Bilstein", "p": 22.95, "stat": "LAST ONE", "url": "https://www.ebay.com/itm/117057905289", "feat": False, "img": "T64-062-23NUR04.jpg"}
]

# --- 3. HARMONIZATION ENGINE ---
def run_harmonization():
    print(f"Starting BLKHDZ Market Update: {datetime.datetime.now()}")
    
    # Base structure for data.json
    output = {
        "last_updated": datetime.datetime.now().strftime("%B %d, %Y"),
        "lego": [],
        "diecast": []
    }

    # Affiliate Tracking Suffix
    ebay_affiliate = "?mkcid=1&mkrid=711-53200-19255-0&campid=5339141674&toolid=10001&mkevt=1"

    # Process LEGO
   for item in LEGO_DATA:
        price_val = get_aggregated_valuation(item['id']) # <--- ADD THIS LINE
        
        output["lego"].append({
            "id": item['id'],
            "name": item['name'],
            "img": item['img'],
            "price": str(price_val) if isinstance(price_val, str) else f"{price_val:.2f}",
            "url": item['url'] + ebay_affiliate,
            "featured": item['feat'],
            "shipping": f"BOX: {item['b']} | WT: {item['w']} LBS"
        })

    # Process Diecast
    for item in DIECAST_DATA:
        price_val = get_aggregated_valuation(item['id'])
        
        output["diecast"].append({
            "id": item['id'],
            "name": item['name'],
            "img": item['img'],
            "price": str(price_val) if isinstance(price_val, str) else f"{price_val:.2f}",
            "url": item['url'] + ebay_affiliate,
            "featured": item['feat'],
            "status": item['stat']
        })

    # Save to data.json
    try:
        with open('data.json', 'w') as f:
            json.dump(output, f, indent=4)
        print("Success: data.json has been synchronized.")
    except Exception as e:
        print(f"Error saving data.json: {e}")

if __name__ == "__main__":
    run_harmonization()
