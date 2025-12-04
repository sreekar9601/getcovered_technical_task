import requests
import json
import time
import sys
import subprocess

API_URL = "http://localhost:8000/api/scrape"

TEST_SITES = [
    # Static / Traditional
    {"url": "https://github.com/login", "type": "Static", "expected": True},
    {"url": "https://gitlab.com/users/sign_in", "type": "Static", "expected": True},
    {"url": "https://news.ycombinator.com/login", "type": "Static", "expected": True},
    {"url": "https://stackoverflow.com/users/login", "type": "Static", "expected": True},
    
    # SPA / JavaScript Heavy
    {"url": "https://discord.com/login", "type": "SPA/JS", "expected": True},
    {"url": "https://www.twitch.tv/login", "type": "SPA/JS", "expected": True},
    {"url": "https://www.reddit.com/login/", "type": "SPA/JS", "expected": True},
    {"url": "https://app.slack.com/login", "type": "SPA/JS", "expected": True},
    
    # Likely to fail (Bot protection / Complex)
    {"url": "https://www.linkedin.com/login", "type": "Bot Protected", "expected": True},
    {"url": "https://twitter.com/i/flow/login", "type": "Bot Protected", "expected": True},
]

def install_tabulate():
    try:
        import tabulate
    except ImportError:
        print("Installing tabulate...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])

def run_tests():
    install_tabulate()
    from tabulate import tabulate
    
    results = []
    print(f"Starting detection test suite against {API_URL}...\n")
    
    for site in TEST_SITES:
        url = site["url"]
        print(f"Testing {url} ({site['type']})...", end="", flush=True)
        
        start_time = time.time()
        try:
            response = requests.post(API_URL, json={"url": url}, timeout=90)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                auth_found = data.get("auth_found", False)
                method = data.get("scraping_method", "unknown")
                
                # Determine if pass/fail based on expectation
                passed = auth_found == site["expected"]
                
                results.append({
                    "URL": url,
                    "Type": site["type"],
                    "Status": "OK" if success else "Error",
                    "Auth Found": "✅ YES" if auth_found else "❌ NO",
                    "Method": method,
                    "Time (s)": f"{duration:.2f}",
                    "Result": "✅ PASS" if passed else "❌ FAIL"
                })
                print(f" Done ({duration:.2f}s) - Auth: {auth_found}, Method: {method}")
            else:
                results.append({
                    "URL": url,
                    "Type": site["type"],
                    "Status": f"HTTP {response.status_code}",
                    "Auth Found": "N/A",
                    "Method": "N/A",
                    "Time (s)": f"{duration:.2f}",
                    "Result": "❌ FAIL"
                })
                print(f" Failed (HTTP {response.status_code})")
                
        except Exception as e:
            duration = time.time() - start_time
            results.append({
                "URL": url,
                "Type": site["type"],
                "Status": "Exception",
                "Auth Found": "N/A",
                "Method": "N/A",
                "Time (s)": f"{duration:.2f}",
                "Result": "❌ ERROR"
            })
            print(f" Error: {str(e)}")

    print("\n" + "="*80 + "\n")
    print(tabulate(results, headers="keys", tablefmt="grid"))
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results if "PASS" in r["Result"])
    print(f"\nSummary: {passed}/{total} passed")

if __name__ == "__main__":
    run_tests()
