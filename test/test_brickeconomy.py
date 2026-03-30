import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# Target Sets for Triangulation
TEST_SETS = ["75274", "31167", "71738"]

def get_brickeconomy_data(set_id):
    url = f"https://www.brickeconomy.com/set/{set_id}-1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"id": set_id, "error": f"Access Denied: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            "id": set_id,
            "market_value": "N/A",
            "retail_price": "N/A",
            "status": "Unknown",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # STRATEGY 1: Targeted Table Cell Selection
        # BrickEconomy often wraps key stats in a specific summary table
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if "Market Value" in label:
                    data["market_value"] = val
                elif "Retail Price" in label:
                    data["retail_price"] = val

        # STRATEGY 2: Precise Status Selection
        # The '6' came from a generic badge; we need the one specifically for availability
        status_container = soup.find('div', class_='mb-2', string=lambda t: t and 'Status' in t)
        if status_container:
            status_badge = status_container.find('span', class_='badge')
            if status_badge:
                data["status"] = status_badge.get_text(strip=True)
        else:
            # Fallback for status
            for badge in soup.find_all('span', class_='badge'):
                text = badge.get_text(strip=True)
                if text in ['Retired', 'Available', 'Retiring Soon']:
                    data["status"] = text
                    break

        return data
    except Exception as e:
        return {"id": set_id, "error": str(e)}

if __name__ == "__main__":
    print(f"--- BRICKECONOMY NPW TEST: {datetime.datetime.now()} ---")
    results = [get_brickeconomy_data(s) for s in TEST_SETS]
    
    # Save results ONLY to the 'test' directory
    os.makedirs('test/results', exist_ok=True)
    with open('test/results/brickeconomy_test.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print("--- TEST COMPLETE. CHECK test/results/brickeconomy_test.json ---")
