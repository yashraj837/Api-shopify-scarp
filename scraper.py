import requests
import csv
import time
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Force unbuffered output for GitHub Actions
sys.stdout.reconfigure(line_buffering=True)

SERPER_API_KEY = "1afdf1789171e412bb4cf9f3507efd86e0203f4c"
MAX_THREADS = 200

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
    'site:myshopify.com "accessories"',
    'site:myshopify.com "lingerie"',
    'site:myshopify.com "streetwear"',
    'site:myshopify.com "sneakers"',
    'site:myshopify.com "luxury"',
    'site:myshopify.com "handmade"',
    'site:myshopify.com "vintage"',
    'site:myshopify.com "organic"',
    'site:myshopify.com "vegan"',
    'site:myshopify.com "CBD"',
    'site:myshopify.com "protein"',
    'site:myshopify.com "keto"',
    'site:myshopify.com "gluten free"',
    'site:myshopify.com "matcha"',
    'site:myshopify.com "stationery"',
    'site:myshopify.com "wallpaper"',
    'site:myshopify.com "rugs"',
    'site:myshopify.com "curtains"',
    'site:myshopify.com "bedding"',
    'site:myshopify.com "bathroom"',
    'site:myshopify.com "storage"',
    'site:myshopify.com "cleaning"',
    'site:myshopify.com "lighting"',
    'site:myshopify.com "perfume"',
    'site:myshopify.com "cologne"',
    'site:myshopify.com "beard"',
    'site:myshopify.com "mens"',
    'site:myshopify.com "womens"',
    'site:myshopify.com "plus size"',
    'site:myshopify.com "swimwear"',
    'site:myshopify.com "activewear"',
    'site:myshopify.com "leggings"',
    'site:myshopify.com "hoodie"',
    'site:myshopify.com "t-shirt"',
    'site:myshopify.com "dress"',
    'site:myshopify.com "socks"',
    'site:myshopify.com "underwear"',
    'site:myshopify.com "hat"',
    'site:myshopify.com "wallet"',
    'site:myshopify.com "belt"',
    'site:myshopify.com "sunscreen"',
    'site:myshopify.com "serum"',
    'site:myshopify.com "moisturizer"',
    'site:myshopify.com "shampoo"',
    'site:myshopify.com "conditioner"',
    'site:myshopify.com "essential oils"',
    'site:myshopify.com "diffuser"',
    'site:myshopify.com "crystals"',
    'site:myshopify.com "meditation"',
]

lock = Lock()
verified_stores = []
all_urls = set()

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
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        results = data.get("organic", [])
        urls = [r["link"] for r in results if "myshopify.com" in r.get("link", "")]
        return urls
    except Exception as e:
        print(f"Search error: {e}", flush=True)
        return []

def verify_store(url):
    try:
        base = url.split("/")[0] + "//" + url.split("/")[2]
        response = requests.get(
            base + "/products.json",
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            if len(products) > 0:
                with lock:
                    verified_stores.append({
                        "url": base,
                        "product_count": len(products)
                    })
                print(f"✅ LIVE [{len(products)} products] {base}", flush=True)
                return True
            else:
                print(f"⚠️  EMPTY {base}", flush=True)
        elif response.status_code == 401:
            print(f"🔒 LOCKED {base}", flush=True)
        elif response.status_code == 404:
            print(f"❌ DEAD {base}", flush=True)
        else:
            print(f"❓ STATUS {response.status_code} {base}", flush=True)
    except requests.exceptions.Timeout:
        print(f"⏱️  TIMEOUT {url}", flush=True)
    except Exception as e:
        print(f"⚠️  ERROR {url} → {e}", flush=True)
    return False

def main():
    global all_urls
    credits_used = 0

    print("=" * 60, flush=True)
    print("🚀 SHOPIFY STORE SCRAPER STARTED", flush=True)
    print(f"📋 Total queries: {len(queries)}", flush=True)
    print(f"🧵 Threads: {MAX_THREADS}", flush=True)
    print("=" * 60, flush=True)

    print("\n📡 PHASE 1 — Scraping URLs from Serper\n", flush=True)

    for query in queries:
        for page in range(5):
            if credits_used >= 2400:
                print("⛔ Credits limit reached — stopping scrape", flush=True)
                break

            urls = search_serper(query, page)
            new_urls = [u for u in urls if u not in all_urls]
            all_urls.update(new_urls)
            credits_used += 1

            print(f"[{credits_used}/2400] '{query}' p{page+1} → +{len(new_urls)} new | Total: {len(all_urls)}", flush=True)
            time.sleep(0.5)

        if credits_used >= 2400:
            break

    print(f"\n✅ Phase 1 Done — {len(all_urls)} raw URLs collected", flush=True)

    print("\n" + "=" * 60, flush=True)
    print(f"🔍 PHASE 2 — Verifying {len(all_urls)} stores with {MAX_THREADS} threads\n", flush=True)

    url_list = list(all_urls)
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(verify_store, url): url for url in url_list}
        for future in as_completed(futures):
            future.result()
            completed += 1
            if completed % 100 == 0:
                print(f"⏳ Progress: {completed}/{len(url_list)} checked | {len(verified_stores)} live so far", flush=True)

    print(f"\n✅ Phase 2 Done — {len(verified_stores)} live stores found", flush=True)

    # Save CSV
    with open("shopify_stores.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "product_count"])
        writer.writeheader()
        writer.writerows(verified_stores)

    print("\n" + "=" * 60, flush=True)
    print(f"🎉 DONE!", flush=True)
    print(f"📊 Raw URLs scraped: {len(all_urls)}", flush=True)
    print(f"✅ Verified live stores: {len(verified_stores)}", flush=True)
    print(f"💾 Saved to: shopify_stores.csv", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
