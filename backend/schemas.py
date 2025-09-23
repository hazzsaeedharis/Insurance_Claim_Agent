"""
Pydantic Schemas for ClaimAI Pro
Data validation and serialization models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ClaimStatus(str, Enum):
    """Claim processing status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    AI_PROCESSING = "ai_processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAYMENT_PENDING = "payment_pending"
    COMPLETED = "completed"

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    CLAIMS_PROCESSOR = "claims_processor"
    CLAIMANT = "claimant"
    REVIEWER = "reviewer"

class DocumentType(str, Enum):
    """Document types"""
    CLAIM_FORM = "claim_form"
    INCIDENT_REPORT = "incident_report"
    PHOTOGRAPH = "photograph"
    RECEIPT = "receipt"
    POLICE_REPORT = "police_report"
    MEDICAL_REPORT = "medical_report"
    OTHER = "other"

# User Models
class UserBase(BaseModel):
    """Base user model"""
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, description="User password")

class UserResponse(UserBase):
    """User response model"""
    id: str
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

# Claim Models
class ClaimBase(BaseModel):
    """Base claim model"""
    claimant_name: str = Field(..., description="Claimant full name")
    policy_number: str = Field(..., description="Insurance policy number")
    incident_date: datetime = Field(..., description="Date of incident")
    claim_amount: float = Field(..., gt=0, description="Claim amount")
    incident_type: str = Field(..., description="Type of incident")
    location: Optional[str] = Field(None, description="Incident location")
    description: Optional[str] = Field(None, description="Incident description")

class ClaimCreate(ClaimBase):
    """Claim creation model"""
    documents: List[Dict[str, Any]] = Field(default=[], description="Claim documents")

class ClaimUpdate(BaseModel):
    """Claim update model"""
    status: Optional[ClaimStatus] = None
    notes: Optional[str] = None
    reviewer_id: Optional[str] = None

class ClaimResponse(ClaimBase):
    """Claim response model"""
    id: str
    status: ClaimStatus
    created_at: datetime
    updated_at: datetime
    ai_analysis: Optional[Dict[str, Any]] = None
    fraud_assessment: Optional[Dict[str, Any]] = None
    decision: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Document Models
class DocumentBase(BaseModel):
    """Base document model"""
    filename: str = Field(..., description="Document filename")
    document_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")

class DocumentCreate(DocumentBase):
    """Document creation model"""
    content: bytes = Field(..., description="Document content")

class DocumentResponse(DocumentBase):
    """Document response model"""
    id: str
    claim_id: str
    uploaded_at: datetime
    processed: bool = False
    ai_analysis: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# AI Processing Models
class AIAnalysisRequest(BaseModel):
    """AI analysis request model"""
    claim_id: str = Field(..., description="Claim ID to analyze")
    document_text: Optional[str] = Field(None, description="Document text content")
    document_type: str = Field(default="claim", description="Type of document")

class AIAnalysisResponse(BaseModel):
    """AI analysis response model"""
    claim_id: str
    document_analysis: Dict[str, Any]
    fraud_detection: Dict[str, Any]
    ai_decision: Dict[str, Any]
    processing_metadata: Dict[str, Any]
    processing_time: float

class FraudDetectionRequest(BaseModel):
    """Fraud detection request model"""
    claim_id: str
    claim_data: Dict[str, Any]
    ai_analysis: Dict[str, Any]

class FraudDetectionResponse(BaseModel):
    """Fraud detection response model"""
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1)")
    risk_level: str = Field(..., description="Risk level")
    fraud_indicators: List[str] = Field(default=[], description="Fraud indicators")
    recommendation: str = Field(..., description="Processing recommendation")

# Dashboard Models
class DashboardStats(BaseModel):
    """Dashboard statistics model"""
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    average_processing_time: float
    fraud_detection_rate: float
    ai_accuracy: float

class ProcessingMetrics(BaseModel):
    """Processing metrics model"""
    claims_processed_today: int
    average_processing_time: str
    ai_accuracy_rate: float
    fraud_detection_rate: float
    system_uptime: str
    last_updated: datetime

# API Response Models
class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)

# Health Check Models
class HealthCheck(BaseModel):
    """Health check model"""
    status: str
    demo_mode: bool
    ai_providers_available: Dict[str, bool]
    database_connected: bool
    timestamp: datetime = Field(default_factory=datetime.now)

# Demo Data Models
class DemoClaimData(BaseModel):
    """Demo claim data model"""
    claim_id: str
    claimant_name: str
    policy_number: str
    incident_date: str
    claim_amount: float
    incident_type: str
    status: ClaimStatus
    processing_time: str
    ai_confidence: float

class DemoResponse(BaseModel):
    """Demo response model"""
    message: str
    demo_data: List[DemoClaimData]
    processing_metrics: ProcessingMetrics
    ai_providers: Dict[str, bool]

# Validation Methods
class ClaimValidator:
    """Claim validation utilities"""
    
    @staticmethod
    def validate_claim_amount(amount: float) -> bool:
        """Validate claim amount"""
        return 0 < amount <= 1000000  # Max $1M
    
    @staticmethod
    def validate_policy_number(policy_number: str) -> bool:
        """Validate policy number format"""
        return len(policy_number) >= 6 and policy_number.isalnum()
    
    @staticmethod
    def validate_incident_date(date: datetime) -> bool:
        """Validate incident date"""
        return date <= datetime.now()

# Custom Validators
def validate_claim_amount(cls, v):
    """Pydantic validator for claim amount"""
    if v <= 0:
        raise ValueError("Claim amount must be positive")
    if v > 1000000:
        raise ValueError("Claim amount exceeds maximum limit")
    return v

def validate_policy_number(cls, v):
    """Pydantic validator for policy number"""
    if len(v) < 6:
        raise ValueError("Policy number too short")
    if not v.isalnum():
        raise ValueError("Policy number must be alphanumeric")
    return v

# Add validators to models
ClaimBase.__validators__ = {
    'claim_amount': validator('claim_amount', allow_reuse=True)(validate_claim_amount),
    'policy_number': validator('policy_number', allow_reuse=True)(validate_policy_number)
}
