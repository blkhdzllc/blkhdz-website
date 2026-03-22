import os, json, datetime

# --- 1. LEGO MANUAL PRICES & RANGES ---
LEGO_PRICES = {
    "31020": 56.00, "71738": 104.85, "31144": 28.54,
    "76015": 64.95, "77247": 49.99, "76295": 69.95,
    "76232": 59.95, "60449": 49.95, "30726": 11.93,
    "41619": 42.95, 
    "75274": "84.95 - 425.00", 
    "31167": "14.99 - 145.00"
}

# --- 2. LEGO INVENTORY DATA ---
LEGO_INVENTORY = [
    {"id": "75274", "name": "Star Wars Helmet Collection (Variation)", "weight": 3.2, "box": "14x10x6", "url": "https://www.ebay.com/itm/116951073772?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1", "featured": True},
    {"id": "31167", "name": "Haunted Mansion 3-in-1 Seasonal Bundle", "weight": 3.5, "box": "15x14x3", "url": "https://www.ebay.com/itm/117037598121?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1", "featured": True},
    {"id": "31020", "name": "LEGO Creator Twinblade Adventures", "weight": 0.7, "box": "10x7x2", "url": "https://www.ebay.com/itm/117004206278?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "71738", "name": "Ninjago Zane's Titan Mech Battle", "weight": 2.8, "box": "14x15x3", "url": "https://www.ebay.com/itm/117058462903?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "31144", "name": "Creator 3-in-1 Exotic Pink Parrot", "weight": 0.8, "box": "10x7x2", "url": "https://www.ebay.com/itm/116989698157?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "76015", "name": "Marvel Doc Ock Truck Heist", "weight": 0.9, "box": "11x7x2", "url": "https://www.ebay.com/itm/117029953980?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "77247", "name": "Speed Champions Kicks Sauber F1", "weight": 0.9, "box": "10x6x3", "url": "https://www.ebay.com/itm/117089969442?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "76295", "name": "Marvel Avengers Helicarrier", "weight": 1.9, "box": "15x10x3", "url": "https://www.ebay.com/itm/117007504223?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "76232", "name": "The Marvels: Hoopty Spaceship", "weight": 1.8, "box": "15x10x3", "url": "https://www.ebay.com/itm/117038961595?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "60449", "name": "City Off-Road Police Car Chase", "weight": 1.6, "box": "11x10x3", "url": "https://www.ebay.com/itm/117070479765?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "30726", "name": "Batman: Bruce Wayne and the Batsuit", "weight": 0.6, "box": "7x5x3", "url": "https://www.ebay.com/itm/117076682926?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "41619", "name": "Brickheadz Darth Vader", "weight": 0.4, "box": "5x4x3", "url": "https://www.ebay.com/itm/116928952963?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"}
]

# --- 3. DIECAST INVENTORY DATA ---
DIECAST_INVENTORY = [
    {"id": "MGT00773-C", "name": "Mazda RX-7 LB-Super Silhouette #41 [CHASE BUNDLE]", "img": "MGT00773.jpg", "price": 95.00, "status": "LIMITED CHASE BUNDLE", "url": "https://www.ebay.com/itm/117098917766?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1", "featured": True},
    {"id": "43SGT25016", "name": "1/43 Spark Honda Civic Type R-GT #16 GT500 2025", "img": "43SGT25016.jpg", "price": 134.95, "status": "PREMIUM 2025 RELEASE", "url": "https://www.ebay.com/itm/117055371825?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1", "featured": True},
    {"id": "MGT00773-R", "name": "Mazda RX-7 LB-Super Silhouette #41 [Numero White]", "img": "MGT00773.jpg", "price": 14.99, "status": "22 IN STOCK", "url": "https://www.ebay.com/itm/117080910055?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "PR640255", "name": "Pop Race Mazda RX-7 FD3S RE Amemiya Gunmetal", "img": "PR640255.jpg", "price": 28.99, "status": "POP RACE APPROVED", "url": "https://www.ebay.com/itm/117078677592?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "PR640212", "name": "Pop Race Honda Civic EG6 Pandem Idemitsu", "img": "PR640212.jpg", "price": 26.99, "status": "IN STOCK", "url": "https://www.ebay.com/itm/117078703657?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "MGT01046", "name": "Mazda RX-7 FD3S RE Amemiya 20B Ama-San Go", "img": "MGT01046.jpg", "price": 14.99, "status": "IN STOCK", "url": "https://www.ebay.com/itm/117078628407?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "MGT00716", "name": "Cadillac V-Series.R #2 Le Mans 3rd Blue", "img": "MGT00716.jpg", "price": 16.99, "status": "LIMITED EDITION", "url": "https://www.ebay.com/itm/117081912634?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "TSMV0027", "name": "1/43 Mazda RX-7 LB Silhouette IMSA Liberty Walk", "img": "TSMV0027.jpg", "price": 32.00, "status": "1/43 SCALE", "url": "https://www.ebay.com/itm/117078591872?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "T64-070-51", "name": "Ferrari 488 GT3 Macau GT Cup #51", "img": "T64-070-51.jpg", "price": 24.95, "status": "LOW STOCK", "url": "https://www.ebay.com/itm/117056036936?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"},
    {"id": "T64-062-04", "name": "Mercedes-AMG GT3 #4 Nurburgring Team Bilstein", "img": "T64-062-04.jpg", "price": 22.95, "status": "LAST ONE", "url": "https://www.ebay.com/itm/117057905289?mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339141674&toolid=10001&mkevt=1"}
]

# --- 4. DATA PROCESSING ---
def run():
    lego_final = []
    for item in LEGO_INVENTORY:
        price = LEGO_PRICES.get(item['id'], 0.00)
        display_price = price if isinstance(price, str) else f"{price:.2f}"
        lego_final.append({
            "set_num": item['id'], 
            "name": item['name'], 
            "market_value": display_price,
            "buy_link": item['url'],
            "is_featured": item.get("featured", False),
            "shipping": {"weight": item['weight'], "box": item['box']}
        })

    output = {
        "last_updated": datetime.datetime.now().strftime("%B %d, %Y"),
        "sets": lego_final,
        "diecast": DIECAST_INVENTORY
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("Successfully updated data.json with LEGO and Diecast inventory.")

if __name__ == "__main__":
    run()
