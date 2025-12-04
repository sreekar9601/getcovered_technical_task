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

# Import LLM detector (will be None if not available)
try:
    from app.llm_detector import detect_with_llm, convert_llm_to_auth_components, LLM_ENABLED
except ImportError:
    detect_with_llm = None
    convert_llm_to_auth_components = None
    LLM_ENABLED = False
    logger.warning("LLM detector not available")


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
        Main detection orchestrator with LLM fallback
        
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
            
            # If nothing found and LLM is available, try LLM detection
            if not traditional.found and not oauth.found and LLM_ENABLED and detect_with_llm:
                logger.info("Traditional detection found nothing, trying LLM fallback...")
                llm_result = detect_with_llm(html, url)
                
                if llm_result and llm_result.get('has_login_form'):
                    logger.info(f"LLM detected login components (confidence: {llm_result.get('confidence')})")
                    
                    # Convert LLM result to our format
                    llm_components = convert_llm_to_auth_components(llm_result)
                    
                    return AuthComponents(
                        traditional_form=TraditionalAuthComponent(**llm_components['traditional_form']),
                        oauth_buttons=OAuthAuthComponent(**llm_components['oauth_buttons'])
                    )
                else:
                    logger.info("LLM also found no login components")
            
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
        2. Also look for inputs with password-related attributes
        3. Search in surrounding text/labels for login indicators
        4. For each password input, find parent form or container
        5. Look for username/email inputs in same form
        6. Extract HTML snippet
        """
        indicators = []
        found_snippets = []
        
        # 1. Find password inputs - multiple strategies
        password_inputs = set()
        
        # Standard type="password"
        password_inputs.update(soup.find_all('input', {'type': 'password'}))
        
        # Sometimes type is set via JavaScript - look for password-related names/ids
        for input_tag in soup.find_all('input'):
            attrs_text = ' '.join([
                str(input_tag.get('name', '')),
                str(input_tag.get('id', '')),
                str(input_tag.get('placeholder', '')),
                str(input_tag.get('autocomplete', '')),
            ]).lower()
            
            # Also check associated label text
            input_id = input_tag.get('id')
            label_text = ''
            if input_id:
                label = soup.find('label', {'for': input_id})
                if label:
                    label_text = label.get_text(strip=True).lower()
            
            combined_text = attrs_text + ' ' + label_text
            
            if 'password' in combined_text or 'passwd' in combined_text or 'pwd' in combined_text:
                password_inputs.add(input_tag)
        
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
                # Look for any input that might be username/email
                text_inputs = form.find_all('input')
                
                # Filter for login-related inputs
                login_inputs = [
                    inp for inp in text_inputs
                    if inp != pwd_input and self._is_login_input(inp)
                ]
                
                if login_inputs:
                    indicators.append('email_input')
                    logger.debug(f"Found {len(login_inputs)} login-related input(s)")
                
                # Find submit button - look more broadly
                submit_btn = (
                    form.find('button', {'type': 'submit'}) or
                    form.find('input', {'type': 'submit'}) or
                    form.find('button', string=lambda s: s and ('log' in s.lower() or 'sign' in s.lower())) or
                    form.find('button')  # Any button in the form
                )
                if submit_btn:
                    indicators.append('submit_button')
                    logger.debug("Found submit button")
                
                # Extract clean HTML snippet
                html_snippet = clean_html_snippet(form)
                found_snippets.append(html_snippet)
            else:
                # No form - look for container (modern SPAs)
                logger.debug("No form found, checking for formless login section")
                container = self._find_login_container(pwd_input)
                if container:
                    # Check if container has other inputs
                    all_inputs = container.find_all('input')
                    has_other_inputs = len(all_inputs) > 1
                    
                    if has_other_inputs:
                        indicators.append('formless_login')
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
        
        Examines: name, id, placeholder, aria-label, autocomplete, type, label text
        """
        # Skip password inputs (handled separately)
        if input_tag.get('type') == 'password':
            return False
        
        # Skip hidden inputs, submit buttons, etc.
        input_type = input_tag.get('type', 'text').lower()
        if input_type in ['hidden', 'submit', 'button', 'checkbox', 'radio']:
            return False
        
        # Get all relevant attributes
        attrs = [
            str(input_tag.get('name', '')),
            str(input_tag.get('id', '')),
            str(input_tag.get('placeholder', '')),
            str(input_tag.get('aria-label', '')),
            str(input_tag.get('autocomplete', '')),
            str(input_tag.get('class', '')),
        ]
        
        # Also check associated label text (for sites like Instagram)
        label_text = ''
        input_id = input_tag.get('id')
        if input_id:
            # Find label with matching 'for' attribute
            parent_form = input_tag.find_parent(['form', 'div'])
            if parent_form:
                label = parent_form.find('label', {'for': input_id})
                if label:
                    label_text = label.get_text(strip=True)
        
        # If no explicit label, check for nearby label or preceding sibling
        if not label_text:
            # Check previous sibling
            prev_sibling = input_tag.find_previous_sibling(['label', 'span', 'div'])
            if prev_sibling and len(prev_sibling.get_text(strip=True)) < 50:
                label_text = prev_sibling.get_text(strip=True)
        
        combined = ' '.join(attrs + [label_text]).lower()
        
        # Expanded keywords for better detection
        extended_keywords = self.login_keywords + [
            'mail', 'identifier', 'phone', 'mobile',
            'user_id', 'userid', 'user-id',
            'customer', 'member', 'telephone', 'tel',
        ]
        
        # Check for login keywords
        return any(keyword in combined for keyword in extended_keywords)
    
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
        Detect OAuth/SSO buttons (improved to avoid duplicates)
        
        Strategy:
        1. Find buttons and links (prioritize these)
        2. Check for OAuth keywords ("Sign in with...")
        3. Identify provider (Google, Microsoft, etc.)
        4. Check for OAuth URLs in hrefs
        5. Deduplicate nested elements
        """
        found_providers_map = {}  # provider -> element (avoid nested duplicates)
        indicators = []
        
        # 1. Find clickable elements - prioritize buttons and links
        # First pass: buttons and links only (most reliable)
        primary_elements = soup.find_all(['button', 'a'])
        
        # Second pass: clickable divs (only if they have role or onclick)
        secondary_elements = []
        for div in soup.find_all('div', class_=True):
            if div.get('role') in ['button', 'link'] or div.get('onclick'):
                secondary_elements.append(div)
        
        all_elements = primary_elements + secondary_elements
        
        logger.debug(f"Checking {len(all_elements)} clickable elements for OAuth")
        
        # Track seen elements to avoid nested duplicates
        processed_elements = set()
        
        for element in all_elements:
            # Skip if this element is a child of already processed element
            if any(element in processed.descendants for processed in processed_elements):
                continue
            
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
                        # Only add if we haven't found this provider yet
                        if provider not in found_providers_map:
                            found_providers_map[provider] = element
                            indicators.append(f"{provider}_oauth")
                            processed_elements.add(element)
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
                        # Only add if we haven't found this provider yet
                        if provider not in found_providers_map:
                            found_providers_map[provider] = element
                            indicators.append(f"{provider}_sso_url")
                            processed_elements.add(element)
                            logger.debug(f"Found {provider} OAuth URL")
                        break
        
        # 5. Extract snippets (one per provider)
        providers = list(found_providers_map.keys())
        snippets = [clean_html_snippet(elem, max_length=300) for elem in found_providers_map.values()]
        
        return OAuthAuthComponent(
            found=bool(providers),
            providers=providers,
            html_snippets=snippets,
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

