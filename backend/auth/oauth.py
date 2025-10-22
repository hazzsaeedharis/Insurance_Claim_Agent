"""
Google OAuth2 Integration

Handles Google OAuth2 authentication flow.
"""

from typing import Optional, Dict, Any
import logging
import secrets

from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session

from config import get_settings
from db_models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize OAuth client
oauth = OAuth()

# Register Google OAuth provider
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def get_google_oauth_url(redirect_uri: str) -> tuple[str, str]:
    """
    Generate Google OAuth authorization URL.
    
    Args:
        redirect_uri: Callback URL after authentication
        
    Returns:
        tuple: (authorization_url, state) - state is used for CSRF protection
        
    Example:
        auth_url, state = get_google_oauth_url("http://localhost:8000/auth/google/callback")
        # Store state in session, redirect user to auth_url
    """
    state = secrets.token_urlsafe(32)
    
    # Build authorization URL
    authorization_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"state={state}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return authorization_url, state


async def exchange_google_code(code: str, redirect_uri: str) -> Dict[str, Any]:
    """
    Exchange authorization code for user information.
    
    Args:
        code: Authorization code from Google
        redirect_uri: Same redirect URI used in authorization request
        
    Returns:
        Dict: User information from Google
        
    Raises:
        Exception: If token exchange fails
        
    Example:
        user_info = await exchange_google_code(code, redirect_uri)
        email = user_info.get("email")
    """
    import httpx
    
    try:
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Get user info
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            
            userinfo_response = await client.get(userinfo_url, headers=headers)
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
            
            return user_info
            
    except Exception as e:
        logger.error(f"Error exchanging Google code: {e}")
        raise Exception("Failed to authenticate with Google")


def get_or_create_user_from_google(db: Session, user_info: Dict[str, Any]) -> User:
    """
    Get or create user from Google OAuth user info.
    
    Args:
        db: Database session
        user_info: User information from Google
        
    Returns:
        User: Existing or newly created user
        
    Example:
        user = get_or_create_user_from_google(db, google_user_info)
    """
    google_id = user_info.get("id")
    email = user_info.get("email")
    full_name = user_info.get("name")
    
    if not google_id or not email:
        raise ValueError("Invalid user info from Google")
    
    # Check if user exists by Google ID
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if user:
        # Update user info if changed
        if user.full_name != full_name:
            user.full_name = full_name
            db.commit()
            db.refresh(user)
        return user
    
    # Check if user exists by email (might have registered with email/password)
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Link Google account to existing user
        user.google_id = google_id
        if not user.full_name:
            user.full_name = full_name
        db.commit()
        db.refresh(user)
        return user
    
    # Create new user
    new_user = User(
        email=email,
        google_id=google_id,
        full_name=full_name,
        is_active=True,
        hashed_password=None  # No password for OAuth users
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Created new user from Google OAuth: {email}")
    return new_user

