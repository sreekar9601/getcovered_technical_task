"""Configuration management for different environments"""
import os
from typing import List

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
            "https://*.vercel.app",  # All Vercel preview deployments
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

