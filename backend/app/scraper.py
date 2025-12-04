"""Web scraping functionality"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class ScrapeResult:
    """Result of a scraping operation"""
    def __init__(self, html: str, method: str, redirected: bool = False):
        self.html = html
        self.method = method
        self.redirected = redirected


class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass


def scrape_static(url: str, timeout: int = 10) -> str:
    """
    Fast HTTP request + BeautifulSoup for static content
    
    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        HTML content as string
        
    Raises:
        requests.RequestException: For network/HTTP errors
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    logger.info(f"Starting static scrape for: {url}")
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            timeout=timeout, 
            allow_redirects=True,
            verify=True
        )
        response.raise_for_status()
        
        # Check if response is HTML
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            raise ScrapingError(f"Response is not HTML (Content-Type: {content_type})")
        
        logger.info(f"Successfully scraped {url} (status: {response.status_code})")
        return response.text
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout scraping {url}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error scraping {url}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error scraping {url}: {e.response.status_code}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {str(e)}")
        raise


async def scrape_with_playwright(url: str, timeout: int = 30) -> str:
    """
    Browser automation for JavaScript-rendered sites
    
    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        HTML content as string
        
    Raises:
        PlaywrightTimeout: For timeout errors
        Exception: For other Playwright errors
    """
    logger.info(f"Starting Playwright scrape for: {url}")
    
    try:
        logger.info("Initializing Playwright async API...")
        async with async_playwright() as p:
            logger.info("Playwright API initialized, launching Firefox...")
            # Use Firefox (Chromium crashes on this macOS system)
            browser = await p.firefox.launch(headless=True)
            logger.info("Firefox browser launched successfully")
            
            logger.info("Creating browser context...")
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                java_script_enabled=True
            )
            logger.info("Browser context created")
            
            logger.info("Creating new page...")
            page = await context.new_page()
            logger.info("New page created, navigating...")
            
            # Navigate with strict timeout
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=10000)  # 10 second max
                logger.info("Page loaded via domcontentloaded")
            except Exception as e:
                logger.warning(f"domcontentloaded failed: {str(e)[:50]}")
                # Don't retry, just raise to trigger fallback
                raise
            
            # Smart waiting: Try to wait for password input, but don't fail if not found
            try:
                await page.wait_for_selector('input[type="password"], input[name*="password"], input[id*="password"]', timeout=8000)
                logger.info("Found password input via Playwright")
            except:
                # No password input found immediately, wait a bit for JavaScript
                logger.debug("No password input found immediately, waiting for JavaScript...")
                await page.wait_for_timeout(2000)
            
            # Scroll to trigger lazy loading
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
            except:
                pass
            
            # Get the fully rendered HTML
            html = await page.content()
            
            await browser.close()
            
            logger.info(f"Successfully scraped {url} with Playwright (length: {len(html)})")
            return html
            
    except PlaywrightTimeout:
        logger.error(f"Playwright timeout for {url}")
        raise
    except Exception as e:
        logger.error(f"Playwright error for {url}: {str(e)}")
        raise


def _should_try_playwright(html: str, url: str) -> bool:
    """
    Determine if we should try Playwright based on static HTML content
    
    Args:
        html: Static HTML content
        url: URL being scraped
        
    Returns:
        True if Playwright should be tried
    """
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
    # Increased threshold to catch more SPAs like Discord/Twitch
    visible_text_length = len(html.replace('<', ' ').replace('>', ' ').strip())
    is_minimal = visible_text_length < 10000
    
    # Check for login-related keywords
    login_keywords = ['login', 'sign in', 'signin', 'log in', 'authentication']
    has_login_keywords = any(keyword in url.lower() or keyword in html_lower for keyword in login_keywords)
    
    result = (has_spa_signs and has_login_keywords) or (is_minimal and has_login_keywords)
    
    logger.info(f"SPA Detection for {url}: Signs={has_spa_signs}, Minimal={is_minimal}, Keywords={has_login_keywords}, Result={result}")
    if not result:
        logger.debug(f"HTML snippet: {html[:200]}...")
        
    return result


async def scrape_website(url: str) -> ScrapeResult:
    """
    Main scraping function with intelligent dual-path strategy
    
    Strategy:
    1. Try fast static scraping first
    2. Analyze if content looks like it needs JavaScript
    3. Use Playwright if needed
    
    Args:
        url: Website URL to scrape
        
    Returns:
        ScrapeResult object with HTML and metadata
        
    Raises:
        ScrapingError: For scraping failures
    """
    static_error = None
    static_html = None
    
    # Path 1: Try fast static scraping first
    try:
        logger.info(f"Attempting static scrape for {url}")
        static_html = scrape_static(url)
        
        # Check if content is sufficient
        if len(static_html) > 500:
            logger.info(f"Static scrape successful for {url} (length: {len(static_html)})")
            
            # Quick check: Does it have password input already?
            if 'type="password"' in static_html or "type='password'" in static_html:
                logger.info("Password input found in static HTML, using static result")
                return ScrapeResult(
                    html=static_html,
                    method="static",
                    redirected=False
                )
            
            # Check if we should try Playwright (now using Firefox)
            if _should_try_playwright(static_html, url):
                logger.info("Static HTML suggests JavaScript rendering, trying Playwright with Firefox")
                static_error = "javascript_detected"
            else:
                # Use static result if no JavaScript indicators
                logger.info("Static HTML looks complete, using without Playwright")
                return ScrapeResult(
                    html=static_html,
                    method="static",
                    redirected=False
                )
        else:
            logger.warning(f"Static scrape returned minimal content ({len(static_html)} chars)")
            static_error = "insufficient_content"
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        if status_code in [403, 429, 503]:
            logger.warning(f"Static scrape blocked ({status_code}), trying Playwright")
            static_error = f"HTTP {status_code}"
        else:
            # Don't retry on 404, etc.
            raise ScrapingError(f"HTTP error {status_code}")
    
    except requests.exceptions.Timeout:
        logger.warning(f"Static scrape timed out, trying Playwright")
        static_error = "timeout"
    
    except requests.exceptions.ConnectionError:
        logger.warning(f"Static scrape connection error, trying Playwright")
        static_error = "connection_error"
    
    except Exception as e:
        logger.warning(f"Static scrape failed ({type(e).__name__}), trying Playwright")
        static_error = str(e)
    
    # Path 2: Fallback to browser automation
    try:
        logger.info(f"Attempting Playwright scrape for {url} (reason: {static_error})")
        html = await scrape_with_playwright(url, timeout=20)  # 20 second timeout for Playwright
        
        return ScrapeResult(
            html=html,
            method="dynamic",
            redirected=False
        )
    
    except PlaywrightTimeout:
        logger.error(f"Playwright timeout for {url}")
        # If we have static HTML, use it as fallback (LLM can analyze it)
        if static_html and len(static_html) > 500:
            logger.warning("Playwright timed out, using static HTML as fallback (LLM will try to detect)")
            return ScrapeResult(
                html=static_html,
                method="static_with_playwright_timeout",
                redirected=False
            )
        raise ScrapingError("Request timed out while loading the page")
    
    except Exception as e:
        logger.error(f"Both scraping methods failed for {url}. Static: {static_error}, Playwright: {str(e)}")
        # If we have static HTML, use it as last resort (LLM can still analyze it)
        if static_html and len(static_html) > 500:
            logger.warning("Playwright failed, using static HTML as last resort (LLM will try to detect)")
            return ScrapeResult(
                html=static_html,
                method="static_after_playwright_failure",
                redirected=False
            )
        raise ScrapingError(f"Failed to scrape website: both static and dynamic methods failed")

