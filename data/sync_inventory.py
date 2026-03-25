# sync_inventory.py (CORRECTED)
import os
import json
import requests

def get_ebay_inventory():
    # FIXED: Hardcoded seller ID to prevent global trending leak
    seller_id = "blkhdz"
    
    # eBay API Endpoint for Search
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?filter=sellers:{{{seller_id}}}&q=LEGO"
    
    # [Authentication and Request logic remains standard]
    # Ensure your EPN Campaign ID is active in your headers/params
    pass

# index.html (SECURE FILTER)
/* Replace your loadInventory function in index.html to ensure 
other sellers' data never renders, even if the JSON is corrupted.
*/

async function loadInventory() {
    try {
        const response = await fetch('data/test/inventory.json');
        const data = await response.json();
        
        // SECURITY GUARDRAIL: Strict filter for your username only
        const myItems = data.itemSummaries.filter(item => {
            return item.seller && item.seller.username === 'blkhdz';
        });

        if (myItems.length === 0) {
            document.getElementById('inventory-container').innerHTML = 
                '<p class="status-msg">Updating Inventory... Check back in 5 minutes.</p>';
            return;
        }
        
        displayItems(myItems); 
    } catch (error) {
        console.error("Inventory Load Error:", error);
    }
}
