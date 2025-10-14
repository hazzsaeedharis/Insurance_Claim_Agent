"""
AI Processing API Service
Main API for document processing and claim analysis
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel, Field
import aiofiles
import tempfile

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.common.base_service import BaseService
from services.common.config import get_settings
from services.ai_document_processor.policy_indexer import PolicyIndexer
from services.ai_document_processor.document_processor import DocumentProcessor
from services.ai_document_processor.claim_analyzer import ClaimAnalyzer

# Get settings
settings = get_settings()

# Initialize service
service = BaseService(
    service_name="ai-processing-service",
    version="1.0.0",
    description="AI-powered document processing and claim analysis"
)

app = service.app
logger = logging.getLogger(__name__)

# Initialize processors
policy_indexer = PolicyIndexer()
document_processor = DocumentProcessor()
claim_analyzer = ClaimAnalyzer()

# In-memory storage for extracted documents (for demo purposes)
# In production, this would be stored in a database
extracted_documents_cache: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class PolicyIndexRequest(BaseModel):
    """Request model for policy indexing"""
    policy_id: str = Field(..., description="Unique policy identifier")
    policy_name: str = Field(..., description="Human-readable policy name")
    file_path: Optional[str] = Field(None, description="Path to policy PDF file")


class DocumentProcessRequest(BaseModel):
    """Request model for document processing"""
    claim_id: str = Field(..., description="Associated claim ID")
    document_type_hint: Optional[str] = Field(None, description="Optional document type hint")


class ClaimAnalysisRequest(BaseModel):
    """Request model for claim analysis"""
    policy_id: str = Field(..., description="Policy ID to match against")
    customer_id: str = Field(..., description="Customer ID for deductible tracking")
    
    
class PolicyIndexResponse(BaseModel):
    """Response model for policy indexing"""
    success: bool
    policy_id: str
    message: str
    details: Optional[Dict[str, Any]] = None


class DocumentProcessResponse(BaseModel):
    """Response model for document processing"""
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_scores: Dict[str, float]
    warnings: list[str]
    processing_time_ms: int


class ClaimAnalysisResponse(BaseModel):
    """Response model for claim analysis"""
    success: bool
    claim_id: str
    total_claimed: float
    total_approved: float
    approval_rate: float
    justification: str
    calculations: list[Dict[str, Any]]
    warnings: list[str]


# API Endpoints

@app.post("/policies/index", response_model=PolicyIndexResponse)
async def index_policy(
    policy_id: str = Form(...),
    policy_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Index a new policy document for RAG retrieval
    
    This endpoint processes a policy PDF and indexes it for future claim matching.
    """
    start_time = datetime.now()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Index the policy
        logger.info(f"Indexing policy {policy_id}: {policy_name}")
        result = policy_indexer.index_policy_document(
            pdf_path=tmp_path,
            policy_id=policy_id,
            policy_name=policy_name
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return PolicyIndexResponse(
            success=True,
            policy_id=policy_id,
            message=f"Successfully indexed policy with {result['total_chunks']} chunks",
            details=result
        )
        
    except Exception as e:
        logger.error(f"Error indexing policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/extract", response_model=DocumentProcessResponse)
async def extract_document(
    claim_id: str = Form(...),
    document_type_hint: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Extract information from an uploaded document
    
    This endpoint uses AI to extract structured data from insurance documents.
    """
    start_time = datetime.now()
    
    try:
        # Validate file type
        allowed_types = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed types: {allowed_types}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process the document
        hints = {"document_type": document_type_hint} if document_type_hint else None
        result = document_processor.process_document(tmp_path, hints)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Store extracted data in cache
        extracted_documents_cache[claim_id] = {
            "document_type": result["document_type"],
            "extracted_data": result["extracted_data"],
            "upload_timestamp": datetime.now().isoformat(),
            "filename": file.filename
        }
        logger.info(f"Stored extracted data for claim {claim_id}: {result['document_type']}")
        
        return DocumentProcessResponse(
            success=True,
            document_type=result["document_type"],
            extracted_data=result["extracted_data"],
            confidence_scores=result["confidence_scores"],
            warnings=result["warnings"],
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/claims/analyze/{claim_id}", response_model=ClaimAnalysisResponse)
async def analyze_claim(
    claim_id: str,
    request: ClaimAnalysisRequest
):
    """
    Analyze a claim against policy terms and calculate reimbursement
    
    This endpoint matches claim items against policy coverage and calculates
    the reimbursement amount with detailed justification.
    """
    try:
        # Get the actual extracted data from cache
        if claim_id not in extracted_documents_cache:
            logger.error(f"No extracted data found for claim {claim_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"No extracted document found for claim {claim_id}. Please upload and extract a document first."
            )
        
        # Use the real extracted data
        cached_data = extracted_documents_cache[claim_id]
        extracted_data = cached_data["extracted_data"]
        
        logger.info(f"Retrieved extracted data for claim {claim_id}: {cached_data['document_type']}")
        
        # Get customer data (mock)
        customer_data = {
            "customer_id": request.customer_id,
            "deductible_used_this_year": 25.00,
            "claims_paid_this_year": 500.00
        }
        
        # Analyze the claim
        result = claim_analyzer.analyze_claim(
            extracted_data=extracted_data,
            policy_id=request.policy_id,
            customer_data=customer_data
        )
        
        return ClaimAnalysisResponse(
            success=True,
            claim_id=claim_id,
            total_claimed=result["total_claimed"],
            total_approved=result["total_approved"],
            approval_rate=result["approval_rate"],
            justification=result["justification"],
            calculations=result["calculations"],
            warnings=result["warnings"]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policies/{policy_id}/search")
async def search_policy(
    policy_id: str,
    query: str,
    limit: int = 5
):
    """
    Search within a specific policy document
    
    This endpoint allows searching for specific terms or conditions within a policy.
    """
    try:
        results = policy_indexer.search_policy(
            query=query,
            policy_id=policy_id,
            top_k=limit
        )
        
        return {
            "policy_id": policy_id,
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get service status and configuration"""
    return {
        "service": "ai-processing-service",
        "status": "operational",
        "version": "1.0.0",
        "capabilities": {
            "policy_indexing": True,
            "document_extraction": True,
            "claim_analysis": True,
            "supported_languages": ["en", "de"],
            "supported_formats": [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
        },
        "models": {
            "llm": "groq/mixtral-8x7b-32768",
            "embeddings": "text-embedding-3-small",
            "ocr": "tesseract"
        }
    }


# Health check is inherited from BaseService

if __name__ == "__main__":
    # Run the service
    service.run(port=settings.services.processing_service_port)
