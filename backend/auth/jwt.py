"""
JWT Token Management

Handles creation and verification of JWT access and refresh tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import logging

from jose import JWTError, jwt
from fastapi import HTTPException, status

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
        
    Example:
        token = create_access_token({"sub": user.email, "user_id": user.id})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT refresh token
        
    Example:
        token = create_refresh_token({"sub": user.email, "user_id": user.id})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid, expired, or wrong type
        
    Example:
        payload = verify_token(token, "access")
        user_email = payload.get("sub")
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            raise credentials_exception
        
        # Check expiration (jose library does this automatically, but we can add custom logic)
        exp = payload.get("exp")
        if exp is None:
            raise credentials_exception
            
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        raise credentials_exception


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a token without verifying signature (for debugging/inspection only).
    
    Args:
        token: JWT token string
        
    Returns:
        Dict or None: Decoded payload or None if invalid
        
    Warning:
        DO NOT use this for authentication! Only for debugging.
    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None

