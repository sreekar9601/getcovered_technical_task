import requests
import json
import time
import subprocess
import sys

API_URL = "http://localhost:8000/api/scrape"

# Comprehensive test sites across categories
TEST_SITES = [
    # Social Media / Communication
    {"url": "https://github.com/login", "category": "Social/Dev", "expected": True},
    {"url": "https://discord.com/login", "category": "Social/Chat", "expected": True},
    {"url": "https://www.reddit.com/login/", "category": "Social", "expected": True},
    {"url": "https://twitter.com/i/flow/login", "category": "Social", "expected": True},
    
    # SaaS / Productivity
    {"url": "https://www.notion.so/login", "category": "SaaS", "expected": True},
    {"url": "https://trello.com/login", "category": "SaaS", "expected": True},
    
    # E-commerce
    {"url": "https://www.amazon.com/ap/signin", "category": "E-commerce", "expected": True},
    {"url": "https://www.etsy.com/signin", "category": "E-commerce", "expected": True},
    
    # News / Media
    {"url": "https://www.nytimes.com/", "category": "News", "expected": False},
    {"url": "https://www.bbc.com/", "category": "News", "expected": False},
    
    # Tech / Dev
    {"url": "https://stackoverflow.com/users/login", "category": "Tech/Dev", "expected": True},
    {"url": "https://news.ycombinator.com/login", "category": "Tech/Dev", "expected": True},
    
    # Streaming
    {"url": "https://www.twitch.tv/login", "category": "Streaming", "expected": True},
    {"url": "https://www.netflix.com/login", "category": "Streaming", "expected": True},
]

def run_tests():
    try:
        from tabulate import tabulate
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        from tabulate import tabulate
    
    results = []
    stats = {"total": 0, "passed": 0, "failed": 0, "static": 0, "dynamic": 0}
    
    print(f"Running comprehensive detection tests...\n")
    
    for site in TEST_SITES:
        url = site["url"]
        print(f"Testing {site['category']:15} {url[:50]:50}...", end="", flush=True)
        
        start_time = time.time()
        try:
            response = requests.post(API_URL, json={"url": url}, timeout=90)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                auth_found = data.get("auth_found", False)
                method = data.get("scraping_method", "unknown")
                
                passed = auth_found == site["expected"]
                stats["total"] += 1
                if passed:
                    stats["passed"] += 1
                else:
                    stats["failed"] += 1
                
                if method == "static":
                    stats["static"] += 1
                elif method == "dynamic":
                    stats["dynamic"] += 1
                
                results.append({
                    "Category": site["category"],
                    "URL": url[:40] + "..." if len(url) > 40 else url,
                    "Auth": "✅" if auth_found else "❌",
                    "Method": method[:8],
                    "Time": f"{duration:.1f}s",
                    "Status": "✅" if passed else "❌"
                })
                print(f" {duration:.1f}s [{method}] {'✅' if passed else '❌'}")
            else:
                stats["total"] += 1
                stats["failed"] += 1
                results.append({
                    "Category": site["category"],
                    "URL": url[:40] + "..." if len(url) > 40 else url,
                    "Auth": "ERR",
                    "Method": "N/A",
                    "Time": f"{duration:.1f}s",
                    "Status": "❌"
                })
                print(f" HTTP {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            stats["total"] += 1
            stats["failed"] += 1
            results.append({
                "Category": site["category"],
                "URL": url[:40] + "..." if len(url) > 40 else url,
                "Auth": "ERR",
                "Method": "N/A",
                "Time": f"{duration:.1f}s",
                "Status": "❌"
            })
            print(f" Error: {str(e)[:30]}")

    print("\n" + "="*80)
    print(tabulate(results, headers="keys", tablefmt="simple"))
    print("="*80)
    print(f"\n📊 SUMMARY:")
    print(f"   Total: {stats['total']}")
    print(f"   Passed: {stats['passed']} ({stats['passed']/stats['total']*100:.0f}%)")
    print(f"   Failed: {stats['failed']}")
    print(f"   Static: {stats['static']}")
    print(f"   Dynamic (Playwright): {stats['dynamic']}")

if __name__ == "__main__":
    run_tests()
