import json
import os
from datetime import datetime

def generate_sitemap():
    base_url = "https://blkhdz.com" 
    pages = [
        {"url": "/", "priority": "1.0"},
    ]

    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_content += f'  <url>\n    <loc>{base_url}{page["url"]}</loc>\n'
        sitemap_content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_content += f'    <priority>{page["priority"]}</priority>\n  </url>\n'

    sitemap_content += '</urlset>'

    with open("sitemap.xml", "w") as f:
        f.write(sitemap_content)
    print("Sitemap.xml generated successfully.")

if __name__ == "__main__":
    generate_sitemap()
