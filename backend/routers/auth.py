"""
Authentication Router

Handles user registration, login, logout, token refresh, and Google OAuth.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from database import get_db
from db_models.user import User
from db_models.refresh_token import RefreshToken
from auth.jwt import create_access_token, create_refresh_token, verify_token
from auth.password import hash_password, verify_password, validate_password_strength
from auth.oauth import get_google_oauth_url, exchange_google_code, get_or_create_user_from_google
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User information response."""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(token, "access")
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
            
    except HTTPException:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check).
    
    Args:
        current_user: Current user from token
        
    Returns:
        User: Current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If email already exists or password is weak
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email}")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        created_at=new_user.created_at.isoformat()
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    Args:
        response: FastAPI response object (for setting cookies)
        form_data: OAuth2 form data (username=email, password)
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token_str = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Store refresh token in database
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    refresh_token_obj = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(refresh_token_obj)
    db.commit()
    
    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_str,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        token_data: Refresh token
        db: Database session
        
    Returns:
        TokenResponse: New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    # Try to get refresh token from request body or cookie
    refresh_token_str = token_data.refresh_token or request.cookies.get("refresh_token")
    
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    # Verify token
    try:
        payload = verify_token(refresh_token_str, "refresh")
        user_id: int = payload.get("user_id")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists in database and is valid
    token_obj = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_str,
        RefreshToken.user_id == user_id
    ).first()
    
    if not token_obj or not token_obj.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Revoke old refresh token
    token_obj.is_revoked = True
    db.commit()
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Store new refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    new_token_obj = RefreshToken(
        token=new_refresh_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(new_token_obj)
    db.commit()
    
    # Set new refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    # Get refresh token from cookie
    refresh_token_str = request.cookies.get("refresh_token")
    
    if refresh_token_str:
        # Revoke refresh token
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.user_id == current_user.id
        ).first()
        
        if token_obj:
            token_obj.is_revoked = True
            db.commit()
    
    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at.isoformat()
    )


# ============================================================================
# GOOGLE OAUTH ENDPOINTS
# ============================================================================

@router.get("/google/login")
async def google_login(request: Request):
    """
    Redirect to Google OAuth login page.
    
    Args:
        request: FastAPI request object
        
    Returns:
        RedirectResponse: Redirect to Google OAuth
    """
    redirect_uri = settings.google_redirect_uri
    auth_url, state = get_google_oauth_url(redirect_uri)
    
    # Store state in session/cookie for CSRF protection
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="lax",
        max_age=600  # 10 minutes
    )
    
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        code: Authorization code from Google
        state: State parameter for CSRF protection
        db: Database session
        
    Returns:
        RedirectResponse: Redirect to frontend with tokens
    """
    # Verify state for CSRF protection
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    try:
        # Exchange code for user info
        user_info = await exchange_google_code(code, settings.google_redirect_uri)
        
        # Get or create user
        user = get_or_create_user_from_google(db, user_info)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        refresh_token_str = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Store refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        refresh_token_obj = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(refresh_token_obj)
        db.commit()
        
        # Clear oauth_state cookie
        response.delete_cookie(key="oauth_state")
        
        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_str,
            httponly=True,
            secure=False,  # Set to True in production
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )
        
        logger.info(f"User logged in via Google: {user.email}")
        
        # Redirect to frontend with access token
        frontend_url = f"{settings.frontend_url}/auth-callback.html?access_token={access_token}&refresh_token={refresh_token_str}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google"
        )

