"""
Insurance Claim Processing API

A clean, unified FastAPI application following SOLID principles and clean code practices.
All endpoints are organized logically with clear separation of concerns.
"""

import os
import tempfile
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Internal imports
from config import get_settings, validate_api_keys
from models import (
    PolicyIndexRequest, PolicyIndexResponse,
    DocumentExtractRequest, DocumentExtractResponse,
    ClaimAnalysisRequest, ClaimAnalysisResponse,
    CustomerData
)
from processors.document import DocumentProcessor
from processors.policy import PolicyIndexer
from processors.claim import ClaimAnalyzer


# ============================================================================
# INITIALIZATION
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered insurance claim processing system",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
document_processor = DocumentProcessor()
policy_indexer = PolicyIndexer()
claim_analyzer = ClaimAnalyzer()

# In-memory cache for extracted documents (for demo/MVP)
# In production, this would be replaced with a database
extracted_documents_cache: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "Insurance Claim Processing API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns system status and configured services.
    """
    api_status = validate_api_keys()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "services": api_status,
        "cache_size": len(extracted_documents_cache)
    }


@app.get("/status")
async def get_status():
    """
    Detailed status endpoint.
    
    Returns configuration and capabilities.
    """
    return {
        "service": settings.app_name,
        "status": "operational",
        "version": settings.app_version,
        "capabilities": {
            "policy_indexing": True,
            "document_extraction": True,
            "claim_analysis": True,
            "supported_languages": ["en", "de"],
            "supported_formats": settings.supported_file_types
        },
        "configuration": validate_api_keys()
    }


# ============================================================================
# POLICY MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/policies/index", response_model=PolicyIndexResponse)
async def index_policy(
    policy_id: str = Form(...),
    policy_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Index a new insurance policy document for RAG retrieval.
    
    Args:
        policy_id: Unique identifier for the policy
        policy_name: Human-readable policy name
        file: PDF file containing policy terms
        
    Returns:
        PolicyIndexResponse: Result of indexing operation
        
    This endpoint processes policy PDFs and stores them in a vector database
    for later retrieval during claim analysis.
    """
    logger.info(f"Indexing policy {policy_id}: {policy_name}")
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported for policy documents"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Index the policy document
            result = policy_indexer.index_policy_document(
                pdf_path=tmp_path,
                policy_id=policy_id,
                policy_name=policy_name
            )
            
            return PolicyIndexResponse(
                success=True,
                policy_id=policy_id,
                message=f"Successfully indexed policy with {result['total_chunks']} chunks",
                details=result
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Error indexing policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policies/{policy_id}/search")
async def search_policy(
    policy_id: str,
    query: str,
    limit: int = 5
):
    """
    Search within a specific policy document.
    
    Args:
        policy_id: Policy to search within
        query: Search query
        limit: Maximum number of results
        
    Returns:
        Search results with relevant policy sections
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


# ============================================================================
# DOCUMENT EXTRACTION ENDPOINTS
# ============================================================================

@app.post("/api/documents/extract", response_model=DocumentExtractResponse)
async def extract_document(
    claim_id: str = Form(...),
    document_type_hint: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Extract structured data from a claim document using AI.
    
    Args:
        claim_id: Unique identifier for the claim
        document_type_hint: Optional hint about document type
        file: Document file (PDF, image)
        
    Returns:
        DocumentExtractResponse: Extracted data with confidence scores
        
    This endpoint uses OCR and AI to extract structured information
    from insurance claim documents.
    """
    start_time = datetime.now()
    logger.info(f"Extracting document for claim {claim_id}")
    
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.supported_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {settings.supported_file_types}"
            )
        
        # Check file size
        file_size = len(await file.read())
        await file.seek(0)  # Reset file pointer
        
        if file_size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Process the document
            hints = {"document_type": document_type_hint} if document_type_hint else None
            result = document_processor.process_document(tmp_path, hints)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Store in cache for later analysis
            extracted_documents_cache[claim_id] = {
                "document_type": result["document_type"],
                "extracted_data": result["extracted_data"],
                "upload_timestamp": datetime.now().isoformat(),
                "filename": file.filename
            }
            
            logger.info(f"Successfully extracted data for claim {claim_id}")
            
            return DocumentExtractResponse(
                success=True,
                document_type=result["document_type"],
                extracted_data=result["extracted_data"],
                confidence_scores=result["confidence_scores"],
                warnings=result["warnings"],
                processing_time_ms=processing_time
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CLAIM ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/claims/analyze/{claim_id}", response_model=ClaimAnalysisResponse)
async def analyze_claim(
    claim_id: str,
    request: ClaimAnalysisRequest
):
    """
    Analyze a claim against policy terms and calculate reimbursement.
    
    Args:
        claim_id: Claim identifier (from document extraction)
        request: Analysis parameters (policy_id, customer_id)
        
    Returns:
        ClaimAnalysisResponse: Detailed analysis with calculations
        
    This endpoint matches extracted claim data against policy terms
    and calculates the reimbursement amount with full transparency.
    """
    logger.info(f"Analyzing claim {claim_id} against policy {request.policy_id}")
    
    try:
        # Retrieve extracted data from cache
        if claim_id not in extracted_documents_cache:
            raise HTTPException(
                status_code=404,
                detail=f"No extracted data found for claim {claim_id}. "
                       f"Please extract a document first using /api/documents/extract"
            )
        
        cached_data = extracted_documents_cache[claim_id]
        extracted_data = cached_data["extracted_data"]
        
        # Prepare customer data (in production, fetch from database)
        customer_data = CustomerData(
            customer_id=request.customer_id,
            deductible_used_this_year=25.00,  # Mock data for demo
            claims_paid_this_year=500.00      # Mock data for demo
        )
        
        # Analyze the claim
        result = claim_analyzer.analyze_claim(
            extracted_data=extracted_data,
            policy_id=request.policy_id,
            customer_data=customer_data.dict()
        )
        
        logger.info(
            f"Claim {claim_id} analyzed: "
            f"€{result['total_claimed']:.2f} claimed, "
            f"€{result['total_approved']:.2f} approved"
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/claims/cache")
async def get_cached_claims():
    """
    Get all cached claim extractions (for debugging/demo).
    
    Returns:
        List of cached claim IDs and their metadata
    """
    return {
        "count": len(extracted_documents_cache),
        "claims": [
            {
                "claim_id": claim_id,
                "document_type": data["document_type"],
                "filename": data["filename"],
                "timestamp": data["upload_timestamp"]
            }
            for claim_id, data in extracted_documents_cache.items()
        ]
    }


@app.delete("/api/claims/cache/{claim_id}")
async def clear_claim_cache(claim_id: str):
    """
    Remove a claim from the cache.
    
    Args:
        claim_id: Claim to remove from cache
        
    Returns:
        Success message
    """
    if claim_id in extracted_documents_cache:
        del extracted_documents_cache[claim_id]
        return {"message": f"Cleared cache for claim {claim_id}"}
    else:
        raise HTTPException(status_code=404, detail="Claim not found in cache")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors with proper status codes."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."}
    )


# ============================================================================
# STARTUP EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Validate configuration
    api_status = validate_api_keys()
    logger.info(f"API Keys configured: {api_status}")
    
    if not any(api_status.values()):
        logger.warning(
            "No AI services configured! Please set at least one API key "
            "(GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY)"
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application")
    # Add any cleanup code here


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug_mode
    )