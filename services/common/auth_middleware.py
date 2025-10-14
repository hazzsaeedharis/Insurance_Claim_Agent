"""
JWT Authentication middleware for Insurance Claim Agent microservices.
Validates JWT tokens and enforces role-based access control.
"""

import json
import os
import time
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
import hashlib

# Mock imports for demo - replace with actual implementations
try:
    from fastapi import HTTPException, Security, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    HTTPException = Exception  # Fallback for testing

try:
    from logger import get_logger, set_correlation_id, set_user_context
    from metrics import increment, timer
except ImportError:
    from .logger import get_logger, set_correlation_id, set_user_context
    from .metrics import increment, timer

logger = get_logger(__name__)

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ISSUER = os.getenv('JWT_ISSUER', 'insurance-claims-api')
JWT_AUDIENCE = os.getenv('JWT_AUDIENCE', 'insurance-claims')
JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES', '60'))

# Load roles from auth/roles.json
ROLES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'auth', 'roles.json')


@dataclass
class User:
    """Represents an authenticated user."""
    id: str
    email: str
    name: str
    roles: List[str]
    permissions: List[str]
    attributes: Dict[str, Any]
    token_issued_at: datetime
    token_expires_at: datetime


class RoleManager:
    """Manages roles and permissions."""
    
    def __init__(self, roles_file: str = ROLES_FILE):
        self.roles = {}
        self.permissions = {}
        self.hierarchy = {}
        self._load_roles(roles_file)
    
    def _load_roles(self, roles_file: str):
        """Load roles from JSON file."""
        try:
            if os.path.exists(roles_file):
                with open(roles_file, 'r') as f:
                    data = json.load(f)
                    self.roles = data.get('roles', {})
                    self.hierarchy = data.get('role_hierarchy', {})
                    logger.info(f"Loaded {len(self.roles)} roles from {roles_file}")
            else:
                logger.warning(f"Roles file not found: {roles_file}, using defaults")
                self._load_default_roles()
        except Exception as e:
            logger.error(f"Error loading roles: {e}")
            self._load_default_roles()
    
    def _load_default_roles(self):
        """Load default roles if file not found."""
        self.roles = {
            'customer': {
                'permissions': ['claim:read:own', 'claim:create:own', 'document:upload:own']
            },
            'adjuster': {
                'permissions': ['claim:read:all', 'claim:update:all', 'claim:approve']
            },
            'admin': {
                'permissions': ['*:*:*']  # Full access
            },
            'system': {
                'permissions': ['*:*:*']  # Full access for system operations
            }
        }
    
    def get_permissions(self, roles: List[str]) -> List[str]:
        """Get all permissions for given roles."""
        permissions = set()
        for role in roles:
            if role in self.roles:
                role_perms = self.roles[role].get('permissions', [])
                permissions.update(role_perms)
                
                # Add inherited permissions from hierarchy
                if role in self.hierarchy:
                    for inherited_role in self.hierarchy[role]:
                        if inherited_role in self.roles:
                            inherited_perms = self.roles[inherited_role].get('permissions', [])
                            permissions.update(inherited_perms)
        
        return list(permissions)
    
    def has_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission."""
        # Check for wildcard permissions
        if '*:*:*' in user_permissions:
            return True
        
        # Check exact match
        if required_permission in user_permissions:
            return True
        
        # Check wildcard patterns
        parts = required_permission.split(':')
        for perm in user_permissions:
            perm_parts = perm.split(':')
            if len(perm_parts) == len(parts):
                match = True
                for i in range(len(parts)):
                    if perm_parts[i] != '*' and perm_parts[i] != parts[i]:
                        match = False
                        break
                if match:
                    return True
        
        return False


# Global role manager instance
role_manager = RoleManager()


class JWTAuthenticator:
    """Handles JWT token generation and validation."""
    
    @staticmethod
    def generate_token(
        user_id: str,
        email: str,
        name: str,
        roles: List[str],
        additional_claims: Dict[str, Any] = None
    ) -> str:
        """Generate a JWT token for a user."""
        with timer('auth.token.generate'):
            permissions = role_manager.get_permissions(roles)
            
            now = datetime.utcnow()
            expires = now + timedelta(minutes=JWT_EXPIRATION_MINUTES)
            
            payload = {
                'sub': user_id,  # Subject
                'email': email,
                'name': name,
                'roles': roles,
                'permissions': permissions,
                'iat': now,
                'exp': expires,
                'iss': JWT_ISSUER,
                'aud': JWT_AUDIENCE,
                'jti': hashlib.sha256(f"{user_id}{now.timestamp()}".encode()).hexdigest()[:16]
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            increment('auth.token.generated')
            logger.info(f"Generated token for user {user_id} with roles {roles}")
            
            return token
    
    @staticmethod
    def validate_token(token: str) -> Optional[User]:
        """Validate a JWT token and return user info."""
        with timer('auth.token.validate'):
            try:
                payload = jwt.decode(
                    token,
                    JWT_SECRET,
                    algorithms=[JWT_ALGORITHM],
                    audience=JWT_AUDIENCE,
                    issuer=JWT_ISSUER
                )
                
                user = User(
                    id=payload['sub'],
                    email=payload.get('email', ''),
                    name=payload.get('name', ''),
                    roles=payload.get('roles', []),
                    permissions=payload.get('permissions', []),
                    attributes=payload.get('attributes', {}),
                    token_issued_at=datetime.fromtimestamp(payload['iat']),
                    token_expires_at=datetime.fromtimestamp(payload['exp'])
                )
                
                # Set user context for logging
                set_user_context(user.id)
                
                increment('auth.token.validated')
                return user
                
            except jwt.ExpiredSignatureError:
                increment('auth.token.expired')
                logger.warning("Token has expired")
                return None
            except jwt.InvalidTokenError as e:
                increment('auth.token.invalid')
                logger.warning(f"Invalid token: {e}")
                return None
            except Exception as e:
                increment('auth.error')
                logger.error(f"Error validating token: {e}")
                return None


def require_auth(required_permission: Optional[str] = None):
    """
    Decorator to require authentication and optionally check permissions.
    
    Args:
        required_permission: Permission string required (e.g., 'claim:read:all')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract token from kwargs or context
            token = kwargs.get('token') or os.getenv('AUTH_TOKEN')
            
            if not token:
                increment('auth.missing_token')
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user = JWTAuthenticator.validate_token(token)
            if not user:
                increment('auth.invalid_token')
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            # Check permission if required
            if required_permission:
                if not role_manager.has_permission(user.permissions, required_permission):
                    increment('auth.permission_denied')
                    logger.warning(f"User {user.id} denied access to {required_permission}")
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user to kwargs
            kwargs['current_user'] = user
            
            increment('auth.success')
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# FastAPI specific implementations
if FASTAPI_AVAILABLE:
    security = HTTPBearer()
    
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
        """FastAPI dependency to get current user from JWT token."""
        token = credentials.credentials
        user = JWTAuthenticator.validate_token(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        return user
    
    def require_permission(permission: str):
        """FastAPI dependency to require specific permission."""
        async def permission_checker(current_user: User = Depends(get_current_user)):
            if not role_manager.has_permission(current_user.permissions, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission '{permission}' required"
                )
            return current_user
        return permission_checker


# Utility functions
def mock_login(email: str, password: str) -> Optional[str]:
    """
    Mock login function for testing.
    In production, this would validate against a database.
    """
    # Mock user database
    users = {
        'customer@example.com': {'id': 'usr-001', 'name': 'John Doe', 'roles': ['customer']},
        'adjuster@hallesche.de': {'id': 'usr-002', 'name': 'Jane Smith', 'roles': ['adjuster']},
        'admin@hallesche.de': {'id': 'usr-003', 'name': 'Admin User', 'roles': ['admin']},
        'system@internal': {'id': 'sys-001', 'name': 'System', 'roles': ['system']},
    }
    
    if email in users:
        user_data = users[email]
        token = JWTAuthenticator.generate_token(
            user_id=user_data['id'],
            email=email,
            name=user_data['name'],
            roles=user_data['roles']
        )
        logger.info(f"User {email} logged in successfully")
        return token
    
    logger.warning(f"Failed login attempt for {email}")
    return None


# Example usage and testing
if __name__ == '__main__':
    print("Testing JWT Authentication Middleware")
    print("=====================================\n")
    
    # Test token generation and validation
    print("1. Testing customer token:")
    customer_token = mock_login('customer@example.com', 'password')
    if customer_token:
        print(f"   Token generated: {customer_token[:50]}...")
        user = JWTAuthenticator.validate_token(customer_token)
        if user:
            print(f"   Validated user: {user.name} ({user.email})")
            print(f"   Roles: {user.roles}")
            print(f"   Permissions: {user.permissions[:3]}...")
    
    print("\n2. Testing adjuster token:")
    adjuster_token = mock_login('adjuster@hallesche.de', 'password')
    if adjuster_token:
        user = JWTAuthenticator.validate_token(adjuster_token)
        if user:
            print(f"   User: {user.name}")
            print(f"   Can approve claims: {role_manager.has_permission(user.permissions, 'claim:approve')}")
    
    print("\n3. Testing permission checks:")
    admin_token = mock_login('admin@hallesche.de', 'password')
    if admin_token:
        user = JWTAuthenticator.validate_token(admin_token)
        if user:
            print(f"   Admin user: {user.name}")
            print(f"   Has full access: {role_manager.has_permission(user.permissions, 'system:manage:all')}")
    
    print("\n4. Testing invalid token:")
    invalid_user = JWTAuthenticator.validate_token("invalid.token.here")
    print(f"   Invalid token result: {invalid_user}")
    
    print("\n✅ Auth middleware test complete!")