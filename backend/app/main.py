"""FastAPI main application"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import validators
import time
import asyncio
import logging
from datetime import datetime

from app.models import (
    ScrapeRequest,
    SuccessResponse,
    ErrorResponse,
    Metadata
)
from app.scraper import scrape_website, ScrapingError
from app.detector import detect_auth
from app.utils import extract_title, normalize_url
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # React default
        "http://localhost:8080",
        "*"  # Allow all for development (restrict in production)
    ],
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
        
        # 3. Scrape with timeout
        logger.info(f"Starting scrape for: {url}")
        result = await asyncio.wait_for(
            asyncio.to_thread(scrape_website, url),
            timeout=45.0  # Overall timeout
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
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        logger.error(f"HTTP error scraping {url}: {status_code}")
        
        if status_code == 403:
            error_msg = "Access denied. The website may be blocking automated requests."
            error_type = "blocked"
        elif status_code == 429:
            error_msg = "Rate limited. The website is blocking too many requests."
            error_type = "rate_limited"
        else:
            error_msg = f"HTTP error {status_code}"
            error_type = "http_error"
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                success=False,
                url=url,
                error=error_type,
                message=error_msg,
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

