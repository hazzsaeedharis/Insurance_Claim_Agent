"""
Insurance Claim Processing API

A clean, unified FastAPI application following SOLID principles and clean code practices.
All endpoints are organized logically with clear separation of concerns.
"""

import os
import tempfile
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Internal imports
from config import get_settings, validate_api_keys
from models import (
    PolicyIndexRequest, PolicyIndexResponse,
    DocumentExtractRequest, DocumentExtractResponse,
    ClaimAnalysisRequest, ClaimAnalysisResponse,
    PolicyRenameRequest,
    CustomerData
)
from processors.document import DocumentProcessor
from processors.policy import PolicyIndexer
from processors.claim import ClaimAnalyzer
from database import get_db, init_db, check_db_connection
from routers.auth import router as auth_router, get_current_user
from db_models.user import User as DBUser


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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.frontend_url,
        "http://localhost:8000",  # For serving frontend from same origin
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Include authentication router
app.include_router(auth_router)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")
    logger.info(f"Frontend static files mounted from: {frontend_path}")

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
    policy_id: Optional[str] = Form(None),
    policy_name: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    current_user: DBUser = Depends(get_current_user)
):
    """
    Index insurance policy documents (supports multiple files).
    
    Features:
    - Auto-generates policy_name from first file if not provided
    - Auto-generates policy_id from policy_name if not provided
    - Supports batch upload of multiple PDFs per policy
    
    Args:
        policy_id: Optional unique identifier (auto-generated if not provided)
        policy_name: Optional human-readable name (extracted from filename if not provided)
        files: One or more PDF files containing policy terms
    
    Returns:
        PolicyIndexResponse with indexing results
    """
    import re
    
    # Validate at least one file
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF file is required")
    
    # Validate all files are PDFs
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are supported. '{file.filename}' is not a PDF."
            )
    
    # Auto-generate policy_name if not provided
    if not policy_name:
        if len(files) == 1:
            # Single file: use its name
            first_filename = files[0].filename
            policy_name = first_filename.replace('.pdf', '').replace('_', ' ')
            policy_name = ' '.join(word.capitalize() for word in policy_name.split())
        else:
            # Multiple files: create combined name
            # Extract base name from first file
            first_filename = files[0].filename.replace('.pdf', '').replace('_', ' ')
            first_name = ' '.join(word.capitalize() for word in first_filename.split())
            # Add count
            policy_name = f"{first_name} ({len(files)} documents)"
        logger.info(f"Auto-generated policy name: {policy_name}")
    
    # Auto-generate policy_id if not provided
    if not policy_id:
        # Generate from policy_name
        # Replace non-alphanumeric with underscore, convert to uppercase
        policy_id = re.sub(r'[^A-Za-z0-9]+', '_', policy_name.upper())
        # Remove leading/trailing underscores
        policy_id = policy_id.strip('_')
        # Add year to make it unique
        policy_id = f"{policy_id}_{datetime.now().year}"
        logger.info(f"Auto-generated policy ID: {policy_id}")
    
    logger.info(f"Indexing policy {policy_id}: {policy_name} with {len(files)} file(s)")
    
    try:
        total_chunks = 0
        temp_files = []
        
        # Save all files temporarily with streaming to avoid memory issues
        for i, file in enumerate(files):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                # Stream file content in chunks to avoid loading entire file in memory
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    tmp_file.write(chunk)
                temp_files.append(tmp_file.name)
                logger.info(f"Saved file {i+1}/{len(files)}: {file.filename}")
        
        try:
            # Index each file
            for i, tmp_path in enumerate(temp_files):
                logger.info(f"Indexing file {i+1}/{len(files)} for policy {policy_id}")
                
                result = policy_indexer.index_policy_document(
                    pdf_path=tmp_path,
                    policy_id=policy_id,
                    policy_name=policy_name
                )
                
                total_chunks += result.get('total_chunks', 0)
            
            message = f"Successfully indexed {len(files)} file(s) with {total_chunks} total chunks"
            
            return PolicyIndexResponse(
                success=True,
                policy_id=policy_id,
                message=message,
                details={
                    "policy_name": policy_name,
                    "files_processed": len(files),
                    "total_chunks": total_chunks
                }
            )
            
        finally:
            # Clean up temporary files
            for tmp_path in temp_files:
                try:
                    os.unlink(tmp_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {tmp_path}: {e}")
    
    except Exception as e:
        logger.error(f"Error indexing policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policies")
async def list_policies(current_user: DBUser = Depends(get_current_user)):
    """
    List all indexed policies.
    
    Returns:
        List of policy IDs and names
    """
    try:
        # Query Pinecone to get unique policy IDs
        # This is a simple implementation - in production you'd want a separate metadata store
        from collections import defaultdict
        
        # Get some vectors to extract policy metadata
        index = policy_indexer.index
        
        # Query with a generic search to get policy metadata
        results = index.query(
            vector=[0.0] * 384,  # Dummy vector
            top_k=1000,
            include_metadata=True
        )
        
        # Extract unique policies
        policies_dict = {}
        for match in results.matches:
            if 'policy_id' in match.metadata:
                policy_id = match.metadata['policy_id']
                if policy_id not in policies_dict:
                    policies_dict[policy_id] = {
                        "policy_id": policy_id,
                        "policy_name": match.metadata.get('policy_name', policy_id),
                        "indexed_at": match.metadata.get('indexed_at', 'Unknown')
                    }
        
        return {
            "policies": list(policies_dict.values()),
            "count": len(policies_dict)
        }
        
    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/policies/{policy_id}")
async def delete_policy(policy_id: str, current_user: DBUser = Depends(get_current_user)):
    """
    Delete a policy from the index.
    
    Args:
        policy_id: Policy to delete
        
    Returns:
        Success message
    """
    try:
        index = policy_indexer.index
        
        # Delete all vectors with this policy_id
        # First, find all vector IDs with this policy_id
        results = index.query(
            vector=[0.0] * 384,
            top_k=10000,
            include_metadata=True,
            filter={"policy_id": policy_id}
        )
        
        # Extract IDs to delete
        ids_to_delete = [match.id for match in results.matches]
        
        if ids_to_delete:
            index.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} vectors for policy {policy_id}")
            return {
                "success": True,
                "message": f"Deleted policy {policy_id}",
                "vectors_deleted": len(ids_to_delete)
            }
        else:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policies/{policy_id}/search")
async def search_policy(
    policy_id: str,
    query: str,
    limit: int = 5,
    current_user: DBUser = Depends(get_current_user)
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


@app.patch("/api/policies/{policy_id}/rename")
async def rename_policy(
    policy_id: str,
    request: PolicyRenameRequest,
    current_user: DBUser = Depends(get_current_user)
):
    """
    Rename a policy by updating metadata in Pinecone.
    
    Args:
        policy_id: Policy to rename
        request: PolicyRenameRequest with new policy name
        
    Returns:
        Success message with update details
    """
    try:
        new_name = request.policy_name.strip()
        
        # Check for XSS patterns
        xss_patterns = ['<script', '</script', 'javascript:', 'onload=', 'onerror=']
        if any(pattern in new_name.lower() for pattern in xss_patterns):
            raise HTTPException(status_code=400, detail="Invalid characters in policy name")
        
        index = policy_indexer.index
        
        # Find all vectors with this policy_id
        results = index.query(
            vector=[0.0] * 384,
            top_k=10000,
            include_metadata=True,
            filter={"policy_id": policy_id}
        )
        
        if not results.matches:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        
        # Update metadata for all vectors (metadata-only update)
        # We only need to update metadata, not the vector values
        vectors_updated = 0
        for match in results.matches:
            updated_metadata = match.metadata.copy()
            updated_metadata['policy_name'] = new_name
            
            # Update metadata only - Pinecone requires the full vector to upsert
            # So we need to fetch and re-upsert with updated metadata
            index.update(
                id=match.id,
                set_metadata=updated_metadata
            )
            vectors_updated += 1
        
        logger.info(f"Renamed policy {policy_id} to '{new_name}' ({vectors_updated} vectors updated)")
        
        return {
            "success": True,
            "message": f"Policy renamed to '{new_name}'",
            "policy_id": policy_id,
            "new_name": new_name,
            "vectors_updated": vectors_updated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renaming policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT EXTRACTION ENDPOINTS
# ============================================================================

@app.post("/api/documents/extract", response_model=DocumentExtractResponse)
async def extract_document(
    claim_id: str = Form(...),
    document_type_hint: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: DBUser = Depends(get_current_user)
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
    request: ClaimAnalysisRequest,
    current_user: DBUser = Depends(get_current_user)
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
async def get_cached_claims(current_user: DBUser = Depends(get_current_user)):
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
async def clear_claim_cache(claim_id: str, current_user: DBUser = Depends(get_current_user)):
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
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        init_db()
        if check_db_connection():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed - authentication features may not work")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        logger.warning("Continuing without database - authentication features will not work")
    
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