"""Pydantic models for request/response validation"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


class ScrapeRequest(BaseModel):
    """Request model for scraping endpoint"""
    url: str = Field(..., description="Website URL to scrape")
    force_playwright: bool = Field(default=False, description="Force browser automation (slower but more reliable)")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        return v


class TraditionalAuthComponent(BaseModel):
    """Traditional username/password form component"""
    found: bool
    html_snippets: List[str] = Field(default_factory=list)
    indicators: List[str] = Field(default_factory=list)


class OAuthAuthComponent(BaseModel):
    """OAuth/SSO button component"""
    found: bool
    providers: List[str] = Field(default_factory=list)
    html_snippets: List[str] = Field(default_factory=list)
    indicators: List[str] = Field(default_factory=list)


class AuthComponents(BaseModel):
    """Container for all authentication components"""
    traditional_form: TraditionalAuthComponent
    oauth_buttons: OAuthAuthComponent
    
    def has_auth(self) -> bool:
        """Check if any authentication component was found"""
        return self.traditional_form.found or self.oauth_buttons.found
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON response"""
        return {
            "traditional_form": self.traditional_form.model_dump(),
            "oauth_buttons": self.oauth_buttons.model_dump()
        }


class Metadata(BaseModel):
    """Scraping metadata"""
    scrape_time_ms: int
    page_title: Optional[str] = None
    redirect_detected: bool = False


class SuccessResponse(BaseModel):
    """Successful scraping response"""
    success: bool = True
    url: str
    auth_found: bool
    scraping_method: Literal["static", "dynamic"]
    components: dict
    metadata: Metadata


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    url: str
    error: str
    message: str
    auth_found: bool = False

