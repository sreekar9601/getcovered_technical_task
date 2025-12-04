import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _should_try_playwright(html: str, url: str) -> bool:
    # Check for signs this is a SPA that needs JavaScript
    spa_indicators = [
        '<div id="root"',
        '<div id="app"',
        'react', 'vue', 'angular',
        'bundle.js', 'app.js', 'main.js',
        '__NEXT_DATA__',  # Next.js
        'nuxt',  # Nuxt.js
        '<noscript>',
        'enable javascript',
        'javascript is required',
        'window.__',
    ]
    
    html_lower = html.lower()
    
    # Strong indication this needs JavaScript
    has_spa_signs = any(indicator in html_lower for indicator in spa_indicators)
    
    # Check if page has very little content (might be JS-rendered)
    visible_text_length = len(html.replace('<', ' ').replace('>', ' ').strip())
    is_minimal = visible_text_length < 2000
    
    # Check for login-related keywords
    login_keywords = ['login', 'sign in', 'signin', 'log in', 'authentication']
    has_login_keywords = any(keyword in url.lower() or keyword in html_lower for keyword in login_keywords)
    
    print(f"DEBUG: has_spa_signs={has_spa_signs}")
    print(f"DEBUG: visible_text_length={visible_text_length}")
    print(f"DEBUG: is_minimal={is_minimal}")
    print(f"DEBUG: has_login_keywords={has_login_keywords}")
    
    return (has_spa_signs and has_login_keywords) or (is_minimal and has_login_keywords)

def test_url(url):
    print(f"\nTesting {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        html = response.text
        print(f"HTML Length: {len(html)}")
        print(f"First 500 chars: {html[:500]}")
        
        has_password = 'type="password"' in html or "type='password'" in html
        print(f"Has password input: {has_password}")
        
        should_try = _should_try_playwright(html, url)
        print(f"Should try Playwright: {should_try}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_url("https://discord.com/login")
    test_url("https://www.twitch.tv/login")
