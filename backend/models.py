"""
Data Models for Insurance Claim Processing System

This module contains all Pydantic models used throughout the application.
Following clean code principles: Single Responsibility, Clear Naming, No Duplication.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# REQUEST MODELS - What clients send to our API
# ============================================================================

class PolicyIndexRequest(BaseModel):
    """Request to index a new insurance policy document."""
    policy_id: str = Field(..., description="Unique policy identifier")
    policy_name: str = Field(..., description="Human-readable policy name")
    

class DocumentExtractRequest(BaseModel):
    """Request to extract data from a claim document."""
    claim_id: str = Field(..., description="Associated claim ID")
    document_type_hint: Optional[str] = Field(None, description="Optional document type hint")


class ClaimAnalysisRequest(BaseModel):
    """Request to analyze a claim against policy terms."""
    policy_id: str = Field(..., description="Policy ID to match against")
    customer_id: str = Field(..., description="Customer ID for deductible tracking")


class PolicyRenameRequest(BaseModel):
    """Request to rename a policy."""
    policy_name: str = Field(..., description="New policy name", min_length=1, max_length=200)


# ============================================================================
# RESPONSE MODELS - What our API returns to clients
# ============================================================================

class PolicyIndexResponse(BaseModel):
    """Response after indexing a policy document."""
    success: bool
    policy_id: str
    message: str
    details: Optional[Dict[str, Any]] = None


class DocumentExtractResponse(BaseModel):
    """Response after extracting data from a document."""
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_scores: Dict[str, float]
    warnings: List[str]
    processing_time_ms: int


class ClaimAnalysisResponse(BaseModel):
    """Response after analyzing a claim."""
    success: bool
    claim_id: str
    total_claimed: float
    total_approved: float
    approval_rate: float
    justification: str
    calculations: List[Dict[str, Any]]
    warnings: List[str]


# ============================================================================
# INTERNAL MODELS - Used within the application
# ============================================================================

class ExtractedService(BaseModel):
    """A medical service extracted from a claim document."""
    service_description: str
    procedure_code: Optional[str] = None
    date_of_service: str
    quantity: int = 1
    unit_price: float
    total_price: float
    

class ExtractedDocument(BaseModel):
    """Complete extracted data from a claim document."""
    document_type: str
    provider_information: Dict[str, Any]
    patient_information: Dict[str, Any]
    services_rendered: List[ExtractedService]
    total_amount: float
    currency: str = "EUR"
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)


class PolicyMatch(BaseModel):
    """Result of matching a service against policy terms."""
    coverage_percentage: float
    deductible: Optional[float]
    covered: bool
    reason: str
    policy_reference: str
    annual_limit: Optional[float] = None


class ReimbursementCalculation(BaseModel):
    """Detailed calculation for a single claim item."""
    service_description: str
    claimed_amount: float
    coverage_rate: float
    covered_amount: float
    deductible_applied: float
    final_amount: float
    calculation_notes: List[str]


class CustomerData(BaseModel):
    """Customer information for claim processing."""
    customer_id: str
    deductible_used_this_year: float = 0.0
    claims_paid_this_year: float = 0.0
    
    
# ============================================================================
# CONFIGURATION MODELS - For app configuration
# ============================================================================

class AIConfig(BaseModel):
    """Configuration for AI services."""
    groq_api_key: Optional[str] = Field(None, description="Groq API key for LLM")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    gemini_api_key: Optional[str] = Field(None, description="Google Gemini API key")
    pinecone_api_key: Optional[str] = Field(None, description="Pinecone API key for vector DB")
    
    class Config:
        env_prefix = ""  # Read directly from environment variables