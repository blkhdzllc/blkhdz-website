import requests
import json
import os
from datetime import datetime

# Set numbers you want to track
watch_list = ["75192", "75337", "10316"]
API_KEY = os.getenv('REBRICKABLE_KEY')

def get_lego_data():
    results = []
    for set_id in watch_list:
        url = f"https://rebrickable.com/api/v3/lego/sets/{set_id}-1/"
        response = requests.get(url, headers={'Authorization': f'key {API_KEY}'})
        
        if response.status_code == 200:
            data = response.json()
            results.append({
                "set_id": set_id,
                "name": data['name'],
                "year": data['year'],
                "parts": data['num_parts'],
                "msrp": data.get('retail_price'), # ADDED THIS LINE
                "img": data['set_img_url'],
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M") # Added time for 4x daily tracking
            })
    
    with open('data.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    get_lego_data()
