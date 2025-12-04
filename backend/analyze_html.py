"""Analyze HTML from Discord, Twitch, and GitLab to improve detection"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.scraper import scrape_static, scrape_with_playwright

async def analyze_site(url, name):
    print(f"\n{'='*80}")
    print(f"Analyzing {name}: {url}")
    print('='*80)
    
    # Get static HTML
    try:
        static_html = scrape_static(url)
        print(f"\n[STATIC] Length: {len(static_html)}")
        has_password = 'type="password"' in static_html or "type='password'" in static_html
        print(f"[STATIC] Has password field: {has_password}")
        print(f"[STATIC] First 300 chars:\n{static_html[:300]}")
        
        # Check for common SPA patterns
        html_lower = static_html.lower()
        has_root = '<div id="root"' in html_lower or "<div id='root'" in html_lower
        has_app = '<div id="app"' in html_lower or "<div id='app'" in html_lower
        has_react = 'react' in html_lower
        has_noscript = '<noscript>' in html_lower
        
        print(f"\n[STATIC] Has <div id='root'>: {has_root}")
        print(f"[STATIC] Has <div id='app'>: {has_app}")
        print(f"[STATIC] Has 'react': {has_react}")
        print(f"[STATIC] Has <noscript>: {has_noscript}")
        
    except Exception as e:
        print(f"[STATIC] Error: {e}")
    
    # Get Playwright HTML
    try:
        playwright_html = await scrape_with_playwright(url)
        print(f"\n[PLAYWRIGHT] Length: {len(playwright_html)}")
        has_password_pw = 'type="password"' in playwright_html or "type='password'" in playwright_html
        print(f"[PLAYWRIGHT] Has password field: {has_password_pw}")
        print(f"[PLAYWRIGHT] First 300 chars:\n{playwright_html[:300]}")
    except Exception as e:
        print(f"[PLAYWRIGHT] Error: {e}")

async def main():
    await analyze_site("https://discord.com/login", "Discord")
    await analyze_site("https://www.twitch.tv/login", "Twitch")
    await analyze_site("https://gitlab.com/users/sign_in", "GitLab")

if __name__ == "__main__":
    asyncio.run(main())
