"""Web scraping functionality"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging

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


def scrape_website(url: str) -> ScrapeResult:
    """
    Main scraping function with dual-path strategy
    Currently implements static scraping only (Phase 1)
    
    Args:
        url: Website URL to scrape
        
    Returns:
        ScrapeResult object with HTML and metadata
        
    Raises:
        ScrapingError: For scraping failures
    """
    # Phase 1: Static scraping only
    try:
        html = scrape_static(url)
        return ScrapeResult(
            html=html,
            method="static",
            redirected=False
        )
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {str(e)}")
        raise ScrapingError(f"Failed to scrape website: {str(e)}")

