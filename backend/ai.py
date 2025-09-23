"""
AI Processing API Router
Handles AI-related endpoints for claim processing
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from schemas import (
    AIAnalysisRequest, AIAnalysisResponse, 
    FraudDetectionRequest, FraudDetectionResponse,
    APIResponse, DemoResponse, DemoClaimData, ProcessingMetrics
)
from ai_service import ai_service
from claim_orchestrator import claim_orchestrator

router = APIRouter()

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_document(request: AIAnalysisRequest):
    """Analyze claim document with AI"""
    try:
        # Process document with AI service
        result = await ai_service.process_claim_document(
            document_text=request.document_text or "",
            document_type=request.document_type
        )
        
        return AIAnalysisResponse(
            claim_id=request.claim_id,
            document_analysis=result.get("document_analysis", {}),
            fraud_detection=result.get("fraud_detection", {}),
            ai_decision=result.get("ai_decision", {}),
            processing_metadata=result.get("processing_metadata", {}),
            processing_time=result.get("processing_metadata", {}).get("processing_time", 0.0)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )

@router.post("/fraud-detection", response_model=FraudDetectionResponse)
async def detect_fraud(request: FraudDetectionRequest):
    """Detect potential fraud in claim"""
    try:
        # Use AI service for fraud detection
        result = await ai_service.process_claim_document(
            document_text=str(request.claim_data),
            document_type="claim"
        )
        
        fraud_data = result.get("fraud_detection", {})
        
        return FraudDetectionResponse(
            risk_score=fraud_data.get("risk_score", 0.0),
            risk_level=fraud_data.get("risk_level", "Unknown"),
            fraud_indicators=fraud_data.get("fraud_indicators", []),
            recommendation=fraud_data.get("recommendation", "Manual Review Required")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection failed: {str(e)}"
        )

@router.get("/demo", response_model=DemoResponse)
async def ai_demo():
    """AI processing demo with sample data"""
    try:
        # Generate demo data
        demo_claims = [
            DemoClaimData(
                claim_id="demo-001",
                claimant_name="John Smith",
                policy_number="POL-2024-001234",
                incident_date="2024-01-15",
                claim_amount=2500.00,
                incident_type="Vehicle Collision",
                status="approved",
                processing_time="2.3 seconds",
                ai_confidence=0.92
            ),
            DemoClaimData(
                claim_id="demo-002",
                claimant_name="Jane Doe", 
                policy_number="POL-2024-001235",
                incident_date="2024-01-14",
                claim_amount=1500.00,
                incident_type="Property Damage",
                status="under_review",
                processing_time="1.8 seconds",
                ai_confidence=0.89
            ),
            DemoClaimData(
                claim_id="demo-003",
                claimant_name="Mike Johnson",
                policy_number="POL-2024-001236", 
                incident_date="2024-01-13",
                claim_amount=5000.00,
                incident_type="Medical Emergency",
                status="rejected",
                processing_time="3.1 seconds",
                ai_confidence=0.95
            )
        ]
        
        # Get processing metrics
        metrics = await claim_orchestrator.get_processing_metrics()
        
        # Get available AI providers
        providers = ai_service.get_available_providers()
        
        return DemoResponse(
            message="🚀 AI Processing Demo - ClaimAI Pro",
            demo_data=demo_claims,
            processing_metrics=ProcessingMetrics(
                claims_processed_today=metrics.get("total_claims_processed", 0),
                average_processing_time=f"{metrics.get('average_processing_time', '2.3')} seconds",
                ai_accuracy_rate=metrics.get("ai_accuracy", 0.95),
                fraud_detection_rate=metrics.get("fraud_detection_rate", 0.94),
                system_uptime="99.97%",
                last_updated=datetime.now()
            ),
            ai_providers=providers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo failed: {str(e)}"
        )

@router.get("/health")
async def ai_health_check():
    """Check AI service health"""
    try:
        health_status = await ai_service.health_check()
        return {
            "status": "healthy",
            "ai_services": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/providers")
async def get_ai_providers():
    """Get available AI providers"""
    try:
        providers = ai_service.get_available_providers()
        return {
            "available_providers": providers,
            "default_provider": "google",
            "demo_mode": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get providers: {str(e)}"
        )

@router.post("/process-claim/{claim_id}")
async def process_claim_with_ai(claim_id: str, claim_data: Dict[str, Any]):
    """Process a complete claim with AI"""
    try:
        # Process claim through orchestrator
        result = await claim_orchestrator.process_claim(claim_data)
        
        return APIResponse(
            success=True,
            message=f"Claim {claim_id} processed successfully",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Claim processing failed: {str(e)}"
        )
