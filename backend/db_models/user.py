"""
User Model

Represents authenticated users in the system.
Supports both email/password and Google OAuth authentication.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        email: Unique email address
        hashed_password: Bcrypt hashed password (nullable for OAuth users)
        google_id: Google OAuth ID (nullable for email/password users)
        full_name: User's full name
        is_active: Whether the account is active
        is_superuser: Whether the user has admin privileges
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

