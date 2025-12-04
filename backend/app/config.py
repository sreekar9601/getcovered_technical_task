"""Configuration management for different environments"""
import os
import re
from typing import List, Optional

# Detect environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# CORS origins based on environment
def get_cors_origins() -> List[str]:
    """Get CORS allowed origins based on environment"""
    
    # Base origins (always allowed)
    origins = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",
    ]
    
    # Production origins (only in production)
    if ENVIRONMENT == "production":
        origins.extend([
            "https://getcovered-technical-task.vercel.app",
        ])
    
    # Docker/local origins (development or docker)
    if ENVIRONMENT in ["development", "docker"]:
        origins.extend([
            "http://localhost",  # Docker frontend (port 80)
        ])
    
    # Allow custom origins from environment variable
    custom_origins = os.getenv("CORS_ORIGINS", "")
    if custom_origins:
        origins.extend([origin.strip() for origin in custom_origins.split(",")])
    
    return origins


def get_cors_origin_regex() -> Optional[str]:
    """Get regex pattern for CORS origins (for wildcard support)"""
    
    # In production, allow all Vercel preview deployments
    if ENVIRONMENT == "production":
        return r"https://.*\.vercel\.app"
    
    return None

