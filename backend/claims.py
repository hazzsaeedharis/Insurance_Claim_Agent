"""
Claims API Router
Handles all claim-related endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime

from schemas import (
    ClaimCreate, ClaimResponse, ClaimUpdate, 
    APIResponse, ErrorResponse
)
from claim_orchestrator import claim_orchestrator

router = APIRouter()

@router.post("/", response_model=APIResponse)
async def create_claim(claim_data: ClaimCreate):
    """Create a new claim"""
    try:
        # Process claim through orchestrator
        result = await claim_orchestrator.process_claim(claim_data.dict())
        
        return APIResponse(
            success=True,
            message="Claim created successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create claim: {str(e)}"
        )

@router.get("/", response_model=List[ClaimResponse])
async def get_claims(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get claims with optional filtering"""
    try:
        # In a real implementation, this would query the database
        # For now, return demo data
        demo_claims = [
            {
                "id": "claim-001",
                "claimant_name": "John Smith",
                "policy_number": "POL-2024-001234",
                "incident_date": datetime.now(),
                "claim_amount": 2500.00,
                "incident_type": "Vehicle Collision",
                "location": "123 Main St, Anytown, USA",
                "description": "Rear-end collision on highway",
                "status": "under_review",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "claim-002", 
                "claimant_name": "Jane Doe",
                "policy_number": "POL-2024-001235",
                "incident_date": datetime.now(),
                "claim_amount": 1500.00,
                "incident_type": "Property Damage",
                "location": "456 Oak Ave, City, USA",
                "description": "Storm damage to roof",
                "status": "approved",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        return demo_claims
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve claims: {str(e)}"
        )

@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: str):
    """Get a specific claim by ID"""
    try:
        # In a real implementation, this would query the database
        demo_claim = {
            "id": claim_id,
            "claimant_name": "John Smith",
            "policy_number": "POL-2024-001234",
            "incident_date": datetime.now(),
            "claim_amount": 2500.00,
            "incident_type": "Vehicle Collision",
            "location": "123 Main St, Anytown, USA",
            "description": "Rear-end collision on highway",
            "status": "under_review",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "ai_analysis": {
                "confidence_score": 0.92,
                "extracted_data": {
                    "claim_amount": "$2,500.00",
                    "incident_type": "Vehicle Collision"
                }
            },
            "fraud_assessment": {
                "risk_score": 0.15,
                "risk_level": "Low",
                "fraud_indicators": []
            },
            "decision": {
                "recommendation": "Approve",
                "confidence": 0.89,
                "reasoning": "Standard claim with low fraud risk"
            }
        }
        
        return demo_claim
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim not found: {str(e)}"
        )

@router.put("/{claim_id}", response_model=APIResponse)
async def update_claim(claim_id: str, claim_update: ClaimUpdate):
    """Update a claim"""
    try:
        # In a real implementation, this would update the database
        return APIResponse(
            success=True,
            message=f"Claim {claim_id} updated successfully",
            data={"claim_id": claim_id, "updated_fields": claim_update.dict()}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claim: {str(e)}"
        )

@router.delete("/{claim_id}", response_model=APIResponse)
async def delete_claim(claim_id: str):
    """Delete a claim"""
    try:
        # In a real implementation, this would delete from database
        return APIResponse(
            success=True,
            message=f"Claim {claim_id} deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete claim: {str(e)}"
        )

@router.get("/{claim_id}/status")
async def get_claim_status(claim_id: str):
    """Get claim processing status"""
    try:
        status_info = await claim_orchestrator.get_claim_status(claim_id)
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get claim status: {str(e)}"
        )

@router.post("/{claim_id}/documents")
async def upload_document(claim_id: str, file_data: dict):
    """Upload document to a claim"""
    try:
        # In a real implementation, this would handle file upload
        return APIResponse(
            success=True,
            message="Document uploaded successfully",
            data={"claim_id": claim_id, "document_id": "doc-001"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )
