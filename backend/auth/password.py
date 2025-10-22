"""
Password Hashing and Verification

Uses pwdlib with Argon2 for secure password hashing.
"""

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
import logging

logger = logging.getLogger(__name__)

# Initialize password hasher with Argon2 (recommended by OWASP)
# Argon2 is more secure than bcrypt for password hashing
password_hash = PasswordHash((
    Argon2Hasher(),
))


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
        
    Example:
        hashed = hash_password("my_secure_password")
    """
    try:
        return password_hash.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise ValueError("Could not hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        if verify_password(input_password, user.hashed_password):
            # Password is correct
    """
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
        
    Example:
        valid, message = validate_password_strength("MyPass123!")
        if not valid:
            raise ValueError(message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

