import os
import requests
import base64
import urllib.parse

def get_ebay_access_token():
    app_id = os.environ.get('APP_ID')
    cert_id = os.environ.get('CERT_ID')
    if not app_id or not cert_id:
        print("Error: APP_ID or CERT_ID not set in environment.")
        return None
    credentials = f"{app_id}:{cert_id}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {encoded_credentials}"}
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def get_active_ebay_inventory():
    token = get_ebay_access_token()
    if not token:
        return []
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=5339141674"
    }
    
    # Split into batches to avoid "Too Large" errors
    batches = [
        "lego minifig brickheadz",
        "diecast hot wheels pop race mini gt tarmac",
        "pc gaming electronics gpu motherboard nintendo sega"
    ]
    
    all_items = []
    seen_ids = set()
    
    for batch_query in batches:
        print(f"Fetching batch: {batch_query}")
        params = {
            "q": batch_query,
            "filter": "sellers:{reedpb},buyingOptions:{FIXED_PRICE|AUCTION}",
            "limit": "100"
        }
        response = requests.get("https://api.ebay.com/buy/browse/v1/item_summary/search", headers=headers, params=params)
        
        if response.status_code == 200:
            batch_items = response.json().get('itemSummaries', [])
            for item in batch_items:
                if item['itemId'] not in seen_ids:
                    all_items.append(item)
                    seen_ids.add(item['itemId'])
        else:
            print(f"API Error on batch {batch_query}: {response.text}")

    # Fetch descriptions for all items collected
    print(f"Fetching descriptions for {len(all_items)} unique items...")
    for item in all_items:
        encoded_id = urllib.parse.quote(item.get('itemId'))
        item_url = f"https://api.ebay.com/buy/browse/v1/item/{encoded_id}"
        resp = requests.get(item_url, headers=headers)
        if resp.status_code == 200:
            item['fullHtmlDescription'] = resp.json().get('description', '<p>No description.</p>')
        else:
            item['fullHtmlDescription'] = '<p>Description unavailable.</p>'
            
    return all_items
