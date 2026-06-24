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
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    data = {
        "grant_type": "client_credentials", 
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def get_active_ebay_inventory():
    """Fetches inventory in batches to avoid 'response too large' API errors."""
    token = get_ebay_access_token()
    if not token:
        return []

    search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=5339141674" 
    }
    
    # 1. Split your big query into smaller batches to avoid Error 12023
    query_batches = [
        "lego minifig brickheadz polybag",
        "diecast hot wheels matchbox pop race mini gt tarmac spark tsm looksmart",
        "pc gaming electronics gpu motherboard nintendo sega mattel"
    ]
    
    all_item_summaries = []
    seen_ids = set()

    # 2. Iterate through batches to collect summaries
    for q_string in query_batches:
        print(f"Fetching batch: {q_string}")
        params = {
            "q": q_string,
            "filter": "sellers:{reedpb},buyingOptions:{FIXED_PRICE|AUCTION}",
            "limit": "100"
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            batch_items = response.json().get('itemSummaries', [])
            for item in batch_items:
                if item['itemId'] not in seen_ids:
                    all_item_summaries.append(item)
                    seen_ids.add(item['itemId'])
        else:
            print(f"API Error {response.status_code} on batch '{q_string}': {response.text}")

    # 3. Proceed to fetch HTML descriptions for collected items
    print(f"Total unique items found: {len(all_item_summaries)}. Fetching HTML descriptions...")
    
    for item in all_item_summaries:
        item_id = item.get('itemId')
        if item_id:
            encoded_id = urllib.parse.quote(item_id)
            item_url = f"https://api.ebay.com/buy/browse/v1/item/{encoded_id}"
            
            item_response = requests.get(item_url, headers=headers)
            if item_response.status_code == 200:
                item_data = item_response.json()
                item['fullHtmlDescription'] = item_data.get('description', '')
            else:
                item['fullHtmlDescription'] = '<p>Description temporarily unavailable.</p>'
                    
    return all_item_summaries
