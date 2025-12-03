"""Authentication component detection logic"""

from bs4 import BeautifulSoup, Tag
from typing import Optional, List
import logging

from app.models import (
    AuthComponents,
    TraditionalAuthComponent,
    OAuthAuthComponent
)
from app.utils import clean_html_snippet

logger = logging.getLogger(__name__)


class AuthDetector:
    """Detects authentication components in HTML"""
    
    def __init__(self):
        self.login_keywords = [
            'email', 'username', 'user', 'login', 'account',
            'userid', 'user_name', 'user-name', 'mail'
        ]
        
        self.oauth_providers = {
            'google': ['google', 'gmail'],
            'microsoft': ['microsoft', 'outlook', 'office365', 'azure'],
            'github': ['github'],
            'facebook': ['facebook', 'fb'],
            'apple': ['apple'],
            'linkedin': ['linkedin'],
            'twitter': ['twitter', 'x.com'],
            'amazon': ['amazon']
        }
    
    def detect(self, html: str, url: str) -> AuthComponents:
        """
        Main detection orchestrator
        
        Args:
            html: HTML content to analyze
            url: Original URL (for context)
            
        Returns:
            AuthComponents with detected authentication elements
        """
        logger.info(f"Starting authentication detection for {url}")
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            traditional = self._detect_traditional_form(soup)
            oauth = self._detect_oauth_buttons(soup, url)
            
            logger.info(
                f"Detection complete - Traditional: {traditional.found}, "
                f"OAuth: {oauth.found} ({len(oauth.providers)} providers)"
            )
            
            return AuthComponents(
                traditional_form=traditional,
                oauth_buttons=oauth
            )
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            # Return empty results on error
            return AuthComponents(
                traditional_form=TraditionalAuthComponent(found=False),
                oauth_buttons=OAuthAuthComponent(found=False)
            )
    
    def _detect_traditional_form(self, soup: BeautifulSoup) -> TraditionalAuthComponent:
        """
        Detect username/password forms
        
        Strategy:
        1. Find all password inputs (strongest signal)
        2. For each password input, find parent form
        3. Look for username/email inputs in same form
        4. Extract HTML snippet
        """
        indicators = []
        found_snippets = []
        
        # 1. Find password inputs (strongest signal)
        password_inputs = soup.find_all('input', {'type': 'password'})
        
        if not password_inputs:
            logger.debug("No password inputs found")
            return TraditionalAuthComponent(found=False)
        
        logger.debug(f"Found {len(password_inputs)} password input(s)")
        indicators.append('password_input')
        
        # 2. Process each password input
        for pwd_input in password_inputs:
            # Find parent form
            form = pwd_input.find_parent('form')
            
            if form:
                logger.debug("Found form containing password input")
                
                # 3. Look for email/username/text inputs in same form
                text_inputs = form.find_all('input', {'type': ['email', 'text', 'tel']})
                
                # Filter for login-related inputs
                login_inputs = [
                    inp for inp in text_inputs
                    if self._is_login_input(inp)
                ]
                
                if login_inputs:
                    indicators.append('email_input')
                    logger.debug(f"Found {len(login_inputs)} login-related input(s)")
                    
                    # Find submit button
                    submit_btn = form.find(['button', 'input'], {'type': 'submit'})
                    if submit_btn:
                        indicators.append('submit_button')
                        logger.debug("Found submit button")
                    
                    # Extract clean HTML snippet
                    html_snippet = clean_html_snippet(form)
                    found_snippets.append(html_snippet)
        
        # 4. Handle password inputs outside forms (modern SPAs)
        if not found_snippets:
            logger.debug("No forms found, checking for formless login sections")
            for pwd_input in password_inputs:
                container = self._find_login_container(pwd_input)
                if container:
                    html_snippet = clean_html_snippet(container)
                    found_snippets.append(html_snippet)
        
        # Deduplicate and limit snippets
        unique_snippets = list(dict.fromkeys(found_snippets))[:3]  # Max 3 snippets
        
        return TraditionalAuthComponent(
            found=bool(unique_snippets),
            html_snippets=unique_snippets,
            indicators=list(set(indicators))
        )
    
    def _is_login_input(self, input_tag: Tag) -> bool:
        """
        Check if input is likely for login credentials
        
        Examines: name, id, placeholder, aria-label, autocomplete
        """
        # Get all relevant attributes
        attrs = [
            input_tag.get('name', ''),
            input_tag.get('id', ''),
            input_tag.get('placeholder', ''),
            input_tag.get('aria-label', ''),
            input_tag.get('autocomplete', ''),
        ]
        
        combined = ' '.join(attrs).lower()
        
        # Check for login keywords
        return any(keyword in combined for keyword in self.login_keywords)
    
    def _find_login_container(self, element: Tag) -> Optional[Tag]:
        """
        Find parent container that looks like a login section
        
        Searches up to 5 levels up the DOM tree
        """
        login_keywords = ['login', 'signin', 'sign-in', 'auth', 'authentication']
        
        current = element.parent
        for _ in range(5):  # Check up to 5 levels up
            if not current:
                break
            
            # Check classes and ids
            classes = current.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            elem_id = current.get('id', '')
            
            combined = ' '.join(classes) + ' ' + elem_id
            combined = combined.lower()
            
            if any(keyword in combined for keyword in login_keywords):
                logger.debug(f"Found login container: {current.name}")
                return current
            
            current = current.parent
        
        # Fallback to direct parent
        return element.parent if element.parent else element
    
    def _detect_oauth_buttons(self, soup: BeautifulSoup, url: str) -> OAuthAuthComponent:
        """
        Detect OAuth/SSO buttons
        
        Strategy:
        1. Find buttons, links, and clickable divs
        2. Check for OAuth keywords ("Sign in with...")
        3. Identify provider (Google, Microsoft, etc.)
        4. Check for OAuth URLs in hrefs
        """
        found_providers = []
        found_snippets = []
        indicators = []
        
        # 1. Find clickable elements
        clickable_elements = soup.find_all(['button', 'a', 'div'], class_=True)
        
        logger.debug(f"Checking {len(clickable_elements)} clickable elements for OAuth")
        
        for element in clickable_elements:
            # Get all relevant attributes
            text = element.get_text(strip=True).lower()
            classes = element.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            classes_str = ' '.join(classes).lower()
            elem_id = element.get('id', '').lower()
            href = element.get('href', '').lower()
            onclick = element.get('onclick', '').lower()
            
            combined = f"{text} {classes_str} {elem_id} {href} {onclick}"
            
            # 2. Check for OAuth keywords
            oauth_keywords = [
                'sign in with', 'continue with', 'log in with', 
                'login with', 'signup with', 'sign up with'
            ]
            
            has_oauth_keyword = any(keyword in combined for keyword in oauth_keywords)
            
            if has_oauth_keyword:
                # 3. Identify provider
                for provider, keywords in self.oauth_providers.items():
                    if any(keyword in combined for keyword in keywords):
                        found_providers.append(provider)
                        indicators.append(f"{provider}_oauth")
                        
                        # Extract snippet
                        snippet = clean_html_snippet(element, max_length=300)
                        found_snippets.append(snippet)
                        
                        logger.debug(f"Found {provider} OAuth button")
                        break
            
            # 4. Check for OAuth URLs in hrefs
            elif href:
                oauth_urls = {
                    'accounts.google.com': 'google',
                    'login.microsoftonline.com': 'microsoft',
                    'github.com/login/oauth': 'github',
                    'facebook.com/dialog/oauth': 'facebook',
                    'appleid.apple.com/auth': 'apple'
                }
                
                for oauth_url, provider in oauth_urls.items():
                    if oauth_url in href:
                        found_providers.append(provider)
                        indicators.append(f"{provider}_sso_url")
                        snippet = clean_html_snippet(element, max_length=300)
                        found_snippets.append(snippet)
                        
                        logger.debug(f"Found {provider} OAuth URL")
                        break
        
        # 5. Deduplicate providers and limit snippets
        unique_providers = list(dict.fromkeys(found_providers))  # Preserve order
        unique_snippets = list(dict.fromkeys(found_snippets))[:5]  # Max 5 snippets
        
        return OAuthAuthComponent(
            found=bool(unique_providers),
            providers=unique_providers,
            html_snippets=unique_snippets,
            indicators=list(set(indicators))
        )


# Global detector instance
_detector = AuthDetector()


def detect_auth(html: str, url: str) -> AuthComponents:
    """
    Convenience function to detect authentication components
    
    Args:
        html: HTML content to analyze
        url: Original URL
        
    Returns:
        AuthComponents with detected elements
    """
    return _detector.detect(html, url)

