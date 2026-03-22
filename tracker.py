import os, json, datetime

# YOUR MANUAL PRICES
MANUAL_PRICES = {
    "31020": 56.00, "71738": 104.85, "31144": 28.54,
    "76015": 64.95, "77247": 49.99, "76295": 69.95,
    "76232": 59.95, "60449": 49.95, "30726": 11.93,
    "41619": 42.95 
}

# FULL INVENTORY WITH AFFILIATE LINKS
LEGO_DATA_LIST = [
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

def run():
    lego_final = []
    for item in LEGO_DATA_LIST:
        set_id = item['id']
        price = MANUAL_PRICES.get(set_id, 0.00)
        lego_final.append({
            "set_num": set_id, 
            "name": item['name'], 
            "market_value": round(price, 2),
            "buy_link": item['url'],
            "shipping_details": {"weight_lbs": item['weight'], "box_dimensions": item['box']}
        })

    output = {"last_updated": datetime.datetime.now().strftime("%B %d, %Y"), "sets": lego_final, "diecast": []}
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    run()
