import os
import requests

def get_active_ebay_inventory():
    """
    Fetches active inventory from the eBay API.
    """
    app_id = os.environ.get('APP_ID')
    # Note: Using your app_id to authorize the request
    
    # This is the standard endpoint for pulling your active listings
    # Replace the query parameters as needed for your specific store/category
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    
    headers = {
        "X-EBAY-C-ENDUSERCTX": "affiliateCampaignId=<YOUR_ID>,affiliateReferenceId=<YOUR_ID>",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "Authorization": f"Bearer {app_id}" 
    }
    
    params = {
        "q": "lego", # Adjust this search query as needed
        "limit": "20"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # Adjust the key path (e.g., 'itemSummaries') based on your previous working structure
            return data.get('itemSummaries', [])
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"Request failed: {e}")
        return []
