import asyncio
import sys
import os

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.scraper import scrape_website, scrape_with_playwright

async def main():
    url = "https://example.com"
    print(f"Testing async scrape for {url}...")
    try:
        result = await scrape_website(url)
        print(f"Success! Method: {result.method}, Length: {len(result.html)}")
        
        print(f"\nTesting direct Playwright scrape for {url}...")
        html = await scrape_with_playwright(url)
        print(f"Success! Playwright HTML Length: {len(html)}")
        
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
