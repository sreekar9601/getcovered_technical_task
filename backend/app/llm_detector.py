"""LLM-based authentication detection as final fallback using Google Gemini"""

import os
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

# Check if Gemini API key is available
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LLM_ENABLED = bool(GEMINI_API_KEY)

if LLM_ENABLED:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')  # Updated model name
        logger.info("Google Gemini LLM detector enabled (using gemini-2.5-flash)")
    except ImportError:
        LLM_ENABLED = False
        logger.warning("Google Generative AI package not installed, LLM detection disabled")
    except Exception as e:
        LLM_ENABLED = False
        logger.warning(f"Failed to initialize Gemini: {str(e)}")
else:
    logger.info("GEMINI_API_KEY not found, LLM detection disabled")


def _extract_relevant_html(html: str, max_length: int = 8000) -> str:
    """
    Extract relevant parts of HTML for LLM analysis
    Focus on parts that might contain login forms
    """
    from bs4 import BeautifulSoup
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style tags
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()
        
        # Get text content with some structure
        text_parts = []
        
        # Look for login-related sections
        login_keywords = ['login', 'signin', 'sign-in', 'auth', 'authentication']
        
        for keyword in login_keywords:
            # Find divs/sections with login-related classes or IDs
            sections = soup.find_all(['div', 'section', 'form'], 
                                    class_=lambda x: x and keyword in x.lower())
            sections += soup.find_all(['div', 'section', 'form'],
                                     id=lambda x: x and keyword in x.lower())
            
            for section in sections[:2]:  # Max 2 per keyword
                text_parts.append(str(section)[:2000])
        
        # If no specific sections found, get a sample of the body
        if not text_parts:
            body = soup.find('body')
            if body:
                text_parts.append(str(body)[:3000])
        
        combined = '\n'.join(text_parts)
        
        # Truncate if too long
        if len(combined) > max_length:
            combined = combined[:max_length] + "..."
        
        return combined
        
    except Exception as e:
        logger.error(f"Error extracting relevant HTML: {str(e)}")
        # Fallback: just truncate
        return html[:max_length]


def detect_with_llm(html: str, url: str) -> Optional[Dict[str, Any]]:
    """
    Use LLM to detect authentication components
    
    Args:
        html: HTML content to analyze
        url: URL being analyzed (for context)
        
    Returns:
        Dict with detection results or None if LLM unavailable
    """
    if not LLM_ENABLED:
        logger.debug("LLM detection not available")
        return None
    
    try:
        logger.info(f"Attempting LLM-based detection for {url}")
        
        # Extract relevant HTML snippet
        relevant_html = _extract_relevant_html(html)
        
        # Construct prompt
        prompt = f"""Analyze this HTML snippet from {url} and determine if it contains login/authentication components.

HTML snippet:
```html
{relevant_html}
```

Please analyze and respond with ONLY a valid JSON object (no markdown, no code blocks, just the JSON):
{{
  "has_login_form": true/false,
  "has_password_field": true/false,
  "has_email_username_field": true/false,
  "oauth_providers": ["google", "microsoft", "github", "facebook", "apple"],
  "confidence": "high"/"medium"/"low",
  "reasoning": "brief explanation"
}}

Rules:
- Only include OAuth providers you clearly see mentioned (like "Sign in with Google" or oauth URLs)
- Be conservative - only set has_login_form to true if you're confident
- Look for password input fields, email/username fields, login buttons
- Return ONLY the JSON object, nothing else"""

        # Call Gemini API
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 500,
            }
        )
        
        # Parse response
        response_text = response.text.strip()
        logger.debug(f"Raw LLM response: {response_text[:300]}")
        
        # Extract JSON from response (might be wrapped in ```json```)
        try:
            if "```json" in response_text:
                parts = response_text.split("```json")
                if len(parts) > 1:
                    response_text = parts[1].split("```")[0].strip()
            elif "```" in response_text:
                parts = response_text.split("```")
                if len(parts) >= 3:
                    response_text = parts[1].strip()
        except Exception as e:
            logger.warning(f"Error extracting JSON from markdown: {str(e)}, using raw response")
        
        result = json.loads(response_text)
        
        logger.info(f"LLM detection result: has_login={result.get('has_login_form')}, confidence={result.get('confidence')}")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
        try:
            logger.error(f"Response was: {response_text[:300]}")
        except:
            pass
        return None
    
    except Exception as e:
        logger.error(f"LLM detection failed: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


def convert_llm_to_auth_components(llm_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert LLM detection result to our standard AuthComponents format
    
    Args:
        llm_result: Result from detect_with_llm
        
    Returns:
        Dict compatible with AuthComponents
    """
    traditional_indicators = []
    oauth_providers = llm_result.get('oauth_providers', [])
    
    # Build indicators based on LLM findings
    if llm_result.get('has_password_field'):
        traditional_indicators.append('password_field_detected_by_llm')
    if llm_result.get('has_email_username_field'):
        traditional_indicators.append('email_username_field_detected_by_llm')
    
    return {
        'traditional_form': {
            'found': llm_result.get('has_login_form', False),
            'html_snippets': [f"LLM Analysis: {llm_result.get('reasoning', 'Login form detected')}"],
            'indicators': traditional_indicators
        },
        'oauth_buttons': {
            'found': bool(oauth_providers),
            'providers': oauth_providers,
            'html_snippets': [f"LLM detected OAuth providers: {', '.join(oauth_providers)}"] if oauth_providers else [],
            'indicators': [f"{provider}_detected_by_llm" for provider in oauth_providers]
        },
        'detection_method': 'llm',
        'confidence': llm_result.get('confidence', 'medium')
    }

