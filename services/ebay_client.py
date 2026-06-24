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
    """Fetches ALL active inventory using an expanded keyword catch-all."""
    token = get_ebay_access_token()
    if not token:
        return []

    search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=5339141674" 
    }
    
    # The 'q' parameter is restored with an expanded OR list matching your specific inventory
    params = {
        "q": "(lego,diecast,hot wheels,matchbox,car,truck,vehicle,pop race,mini gt,tarmac,spark,tsm,looksmart,pc,gaming,electronics,gpu,motherboard,nintendo,sega,mattel,minifig,polybag,brickheadz)",
        "filter": "sellers:{reedpb},buyingOptions:{FIXED_PRICE|AUCTION}",
        "limit": "100"
    }

    print("Fetching item summaries...")
    response = requests.get(search_url, headers=headers, params=params)
    
    if response.status_code == 200:
        item_summaries = response.json().get('itemSummaries', [])
        print(f"Found {len(item_summaries)} items. Fetching HTML descriptions...")
        
        for item in item_summaries:
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
                    
        return item_summaries
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return []
