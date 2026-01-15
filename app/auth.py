"""
Simple API key authentication.
This protects our POST endpoints from unauthorized access.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "default_dev_key_change_in_production")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Validates that the provided API key matches our secret key.
    
    This function is used as a dependency in routes that need protection.
    If the key is invalid or missing, it raises a 403 Forbidden error.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key is missing. Please provide X-API-Key in headers."
        )
    
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key