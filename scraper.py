import requests
import csv
import time
import json

SERPER_API_KEY = "1afdf1789171e412bb4cf9f3507efd86e0203f4c"

queries = [
    'site:myshopify.com "clothing"',
    'site:myshopify.com "jewelry"',
    'site:myshopify.com "beauty"',
    'site:myshopify.com "supplements"',
    'site:myshopify.com "home decor"',
    'site:myshopify.com "electronics"',
    'site:myshopify.com "shoes"',
    'site:myshopify.com "watches"',
    'site:myshopify.com "skincare"',
    'site:myshopify.com "fitness"',
    'site:myshopify.com "yoga"',
    'site:myshopify.com "pet supplies"',
    'site:myshopify.com "baby"',
    'site:myshopify.com "toys"',
    'site:myshopify.com "candles"',
    'site:myshopify.com "furniture"',
    'site:myshopify.com "kitchen"',
    'site:myshopify.com "bags"',
    'site:myshopify.com "sunglasses"',
    'site:myshopify.com "sports"',
    'site:myshopify.com "outdoor"',
    'site:myshopify.com "camping"',
    'site:myshopify.com "hair care"',
    'site:myshopify.com "makeup"',
    'site:myshopify.com "vitamins"',
    'site:myshopify.com "coffee"',
    'site:myshopify.com "tea"',
    'site:myshopify.com "food"',
    'site:myshopify.com "wine"',
    'site:myshopify.com "art"',
    'site:myshopify.com "books"',
    'site:myshopify.com "music"',
    'site:myshopify.com "games"',
    'site:myshopify.com "phone cases"',
    'site:myshopify.com "laptop"',
    'site:myshopify.com "headphones"',
    'site:myshopify.com "camera"',
    'site:myshopify.com "garden"',
    'site:myshopify.com "plants"',
    'site:myshopify.com "tools"',
    'site:myshopify.com "automotive"',
    'site:myshopify.com "motorcycle"',
    'site:myshopify.com "cycling"',
    'site:myshopify.com "swimming"',
    'site:myshopify.com "hunting"',
    'site:myshopify.com "fishing"',
    'site:myshopify.com "golf"',
    'site:myshopify.com "kids"',
    'site:myshopify.com "maternity"',
    'site:myshopify.com "wedding"',
    'site:myshopify.com "gifts"',
]

def search_serper(query, page=0):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": 10,
        "start": page * 10
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        results = data.get("organic", [])
        urls = [r["link"] for r in results if "myshopify.com" in r.get("link", "")]
        return urls
    except Exception as e:
        print(f"Error: {e}")
        return []

def verify_store(url):
    try:
        # extract base domain
        base = url.split("/")[0] + "//" + url.split("/")[2]
        check = requests.get(base + "/products.json", timeout=5)
        if check.status_code == 200:
            data = check.json()
            products = data.get("products", [])
            if len(products) > 0:
                return True
    except:
        pass
    return False

def main():
    all_urls = set()
    verified = []
    credits_used = 0

    print("Starting scrape...")

    for query in queries:
        for page in range(5):  # 5 pages per query = 50 results per niche
            if credits_used >= 2400:  # leave small buffer
                print("Credits almost used up, stopping")
                break

            urls = search_serper(query, page)
            new_urls = [u for u in urls if u not in all_urls]
            all_urls.update(new_urls)
            credits_used += 1

            print(f"Query: '{query}' Page {page+1} → {len(new_urls)} new URLs | Total: {len(all_urls)} | Credits: {credits_used}")

            time.sleep(1)  # be gentle with API

        if credits_used >= 2400:
            break

    print(f"\nTotal raw URLs: {len(all_urls)}")
    print("Now verifying stores...")

    for url in all_urls:
        is_live = verify_store(url)
        if is_live:
            verified.append(url)
            print(f"✅ Live: {url}")
        else:
            print(f"❌ Dead: {url}")
        time.sleep(0.5)

    # Save to CSV
    with open("shopify_stores.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["store_url"])
        for url in verified:
            writer.writerow([url])

    print(f"\nDone! {len(verified)} verified live stores saved to shopify_stores.csv")

if __name__ == "__main__":
    main()
