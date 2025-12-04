"""FastAPI main application"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import validators
import time
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.models import (
    ScrapeRequest,
    SuccessResponse,
    ErrorResponse,
    Metadata
)
from app.scraper import scrape_website, ScrapingError
from app.detector import detect_auth
from app.utils import extract_title, normalize_url
from app.config import get_cors_origins
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Login Form Detector API",
    description="API for detecting authentication components on websites",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS based on environment
cors_origins = get_cors_origins()
logger.info(f"CORS origins configured for {os.getenv('ENVIRONMENT', 'development')}: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Login Form Detector API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }


@app.post("/api/scrape")
async def scrape_endpoint(request: ScrapeRequest):
    """
    Scrape a website and detect authentication components
    
    Args:
        request: ScrapeRequest with URL
        
    Returns:
        SuccessResponse or ErrorResponse
    """
    url = request.url.strip()
    logger.info(f"Received scrape request for: {url}")
    
    # 1. Normalize URL (add protocol if missing)
    url = normalize_url(url)
    
    # 2. Validate URL format
    if not validators.url(url):
        logger.warning(f"Invalid URL format: {url}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                url=url,
                error="invalid_url",
                message="Please provide a valid URL (e.g., https://example.com)",
                auth_found=False
            ).model_dump()
        )
    
    try:
        start_time = time.time()
        
        # 3. Scrape with timeout (increased to allow Playwright + fallback)
        logger.info(f"Starting scrape for: {url}")
        result = await asyncio.wait_for(
            scrape_website(url),
            timeout=60.0  # 60 second timeout to allow Playwright (30s) + fallback
        )
        
        scrape_time = int((time.time() - start_time) * 1000)
        logger.info(f"Scraping completed in {scrape_time}ms")
        
        # 4. Detect auth components
        logger.info("Starting authentication detection")
        auth_components = detect_auth(result.html, url)
        
        # 5. Extract metadata
        page_title = extract_title(result.html)
        
        # 6. Build response
        response = SuccessResponse(
            success=True,
            url=url,
            auth_found=auth_components.has_auth(),
            scraping_method=result.method,
            components=auth_components.to_dict(),
            metadata=Metadata(
                scrape_time_ms=scrape_time,
                page_title=page_title,
                redirect_detected=result.redirected
            )
        )
        
        logger.info(
            f"Success - Auth found: {response.auth_found}, "
            f"Method: {response.scraping_method}, "
            f"Time: {scrape_time}ms"
        )
        
        return response
    
    except asyncio.TimeoutError:
        logger.error(f"Timeout scraping {url}")
        return JSONResponse(
            status_code=408,
            content=ErrorResponse(
                success=False,
                url=url,
                error="timeout",
                message="Request timed out. The website took too long to respond.",
                auth_found=False
            ).model_dump()
        )
    
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error scraping {url}: {str(e)}")
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                success=False,
                url=url,
                error="connection_error",
                message="Could not connect to the website. Please check the URL.",
                auth_found=False
            ).model_dump()
        )
    
    except ScrapingError as e:
        logger.error(f"Scraping error for {url}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                url=url,
                error="scraping_error",
                message=str(e),
                auth_found=False
            ).model_dump()
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error scraping {url}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                url=url,
                error="unknown",
                message="An unexpected error occurred. Please try again.",
                auth_found=False
            ).model_dump()
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

