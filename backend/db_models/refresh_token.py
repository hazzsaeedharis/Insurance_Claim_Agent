"""
Refresh Token Model

Stores refresh tokens for secure session management.
Allows token revocation and tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class RefreshToken(Base):
    """
    Refresh token model for JWT token refresh mechanism.
    
    Attributes:
        id: Primary key
        token: Unique refresh token string
        user_id: Foreign key to users table
        expires_at: Token expiration timestamp
        is_revoked: Whether the token has been revoked
        created_at: Token creation timestamp
    """
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
    
    def is_valid(self) -> bool:
        """Check if token is still valid (not expired and not revoked)."""
        return not self.is_revoked and self.expires_at > datetime.utcnow()

