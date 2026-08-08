import json
import os
from datetime import datetime

def generate_sitemap():
    base_url = "https://blkhdzllc.github.io/blkhdz-website"
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Core pages and main categories
    pages = [
        {"url": "/", "priority": "1.0"},
        {"url": "/#/catalog", "priority": "0.9"},
        {"url": "/#/category/speed-champions", "priority": "0.8"},
        {"url": "/#/category/star-wars", "priority": "0.8"},
        {"url": "/#/category/brickheadz", "priority": "0.8"},
        {"url": "/#/category/creator", "priority": "0.8"},
        {"url": "/#/category/architecture", "priority": "0.8"},
        {"url": "/#/category/1-64-diecast", "priority": "0.8"},
        {"url": "/#/category/1-43-diecast", "priority": "0.8"},
    ]

    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Add core static pages
    for page in pages:
        sitemap_content += f'  <url>\n    <loc>{base_url}{page["url"]}</loc>\n'
        sitemap_content += f'    <lastmod>{today}</lastmod>\n'
        sitemap_content += f'    <priority>{page["priority"]}</priority>\n  </url>\n'

    # Dynamically load individual items from your JSON inventory
    inventory_path = os.path.join("data", "inventory.json")
    
    if os.path.exists(inventory_path):
        try:
            with open(inventory_path, "r", encoding="utf-8") as f:
                inventory = json.load(f)
                
            for item in inventory:
                # Assuming your items use "set_number" or "sku" or "id" as their identifier
                item_id = item.get("set_number") or item.get("sku") or item.get("id")
                
                if item_id:
                    sitemap_content += f'  <url>\n    <loc>{base_url}/#/item/{item_id}</loc>\n'
                    sitemap_content += f'    <lastmod>{today}</lastmod>\n'
                    sitemap_content += f'    <priority>0.8</priority>\n  </url>\n'
                    
            print(f"Successfully added {len(inventory)} items to the sitemap.")
            
        except Exception as e:
            print(f"Error reading inventory file: {e}")
    else:
        print(f"Warning: Inventory file not found at {inventory_path}")

    sitemap_content += '</urlset>'

    # Write the complete XML to the sitemap.xml file
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
        
    print("Sitemap.xml generated successfully.")

if __name__ == "__main__":
    generate_sitemap()
