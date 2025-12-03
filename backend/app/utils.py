"""Utility functions"""

from bs4 import BeautifulSoup
from typing import Optional
import re


def extract_title(html: str) -> Optional[str]:
    """Extract page title from HTML"""
    try:
        soup = BeautifulSoup(html, 'lxml')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        return None
    except Exception:
        return None


def clean_html_snippet(element, max_length: int = 500) -> str:
    """Extract and prettify HTML snippet"""
    try:
        # Remove script and style tags
        for tag in element.find_all(['script', 'style']):
            tag.decompose()
        
        html = str(element)
        
        # Prettify
        try:
            soup = BeautifulSoup(html, 'lxml')
            pretty = soup.prettify()
            
            # Limit length
            if len(pretty) > max_length:
                pretty = pretty[:max_length - 3] + "..."
            
            return pretty
        except Exception:
            # Fallback to raw HTML with length limit
            if len(html) > max_length:
                html = html[:max_length - 3] + "..."
            return html
    except Exception:
        return str(element)[:max_length]


def is_valid_url_format(url: str) -> bool:
    """Basic URL format validation"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return url_pattern.match(url) is not None


def normalize_url(url: str) -> str:
    """Normalize URL by adding protocol if missing"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

