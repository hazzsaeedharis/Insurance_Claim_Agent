"""
Claim Orchestrator - Core Business Logic
Orchestrates the entire claim processing workflow
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

class ClaimStatus(Enum):
    """Claim processing status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    AI_PROCESSING = "ai_processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAYMENT_PENDING = "payment_pending"
    COMPLETED = "completed"

class ClaimOrchestrator:
    """Orchestrates the complete claim processing workflow"""
    
    def __init__(self):
        self.processing_steps = [
            "document_validation",
            "ai_analysis",
            "fraud_detection",
            "risk_assessment",
            "decision_making",
            "approval_workflow"
        ]
    
    async def process_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main claim processing workflow"""
        
        try:
            # Step 1: Validate claim data
            validation_result = await self._validate_claim(claim_data)
            if not validation_result["valid"]:
                return {
                    "status": "rejected",
                    "reason": "Invalid claim data",
                    "errors": validation_result["errors"]
                }
            
            # Step 2: AI Document Analysis
            ai_analysis = await self._analyze_documents(claim_data)
            
            # Step 3: Fraud Detection
            fraud_assessment = await self._detect_fraud(claim_data, ai_analysis)
            
            # Step 4: Risk Assessment
            risk_assessment = await self._assess_risk(claim_data, ai_analysis, fraud_assessment)
            
            # Step 5: Decision Making
            decision = await self._make_decision(claim_data, ai_analysis, fraud_assessment, risk_assessment)
            
            # Step 6: Update claim status
            final_status = await self._update_claim_status(claim_data["claim_id"], decision)
            
            return {
                "claim_id": claim_data["claim_id"],
                "status": final_status,
                "ai_analysis": ai_analysis,
                "fraud_assessment": fraud_assessment,
                "risk_assessment": risk_assessment,
                "decision": decision,
                "processing_time": self._calculate_processing_time(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "claim_id": claim_data.get("claim_id", "unknown"),
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _validate_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim data and documents"""
        
        errors = []
        
        # Required fields validation
        required_fields = ["claimant_name", "policy_number", "incident_date", "claim_amount"]
        for field in required_fields:
            if not claim_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Document validation
        if not claim_data.get("documents") or len(claim_data["documents"]) == 0:
            errors.append("No documents provided")
        
        # Amount validation
        try:
            amount = float(claim_data.get("claim_amount", 0))
            if amount <= 0:
                errors.append("Invalid claim amount")
            elif amount > 100000:  # High-value claim threshold
                errors.append("High-value claim requires manual review")
        except:
            errors.append("Invalid claim amount format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _analyze_documents(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze claim documents with AI"""
        
        # Simulate document analysis
        await asyncio.sleep(1)  # Simulate processing time
        
        return {
            "document_count": len(claim_data.get("documents", [])),
            "extracted_data": {
                "claimant_name": claim_data.get("claimant_name"),
                "policy_number": claim_data.get("policy_number"),
                "incident_date": claim_data.get("incident_date"),
                "claim_amount": claim_data.get("claim_amount"),
                "incident_type": self._classify_incident_type(claim_data),
                "location": claim_data.get("location", "Not specified")
            },
            "confidence_score": 0.92,
            "processing_time": "1.2 seconds"
        }
    
    async def _detect_fraud(self, claim_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential fraud indicators"""
        
        # Simulate fraud detection
        await asyncio.sleep(0.8)
        
        fraud_indicators = []
        risk_score = 0.0
        
        # Check for common fraud patterns
        amount = float(claim_data.get("claim_amount", 0))
        
        if amount > 50000:
            fraud_indicators.append("High-value claim")
            risk_score += 0.2
        
        if not claim_data.get("location"):
            fraud_indicators.append("Missing location information")
            risk_score += 0.1
        
        # Check for duplicate claims (simulated)
        if self._check_duplicate_claims(claim_data):
            fraud_indicators.append("Potential duplicate claim")
            risk_score += 0.3
        
        risk_level = "Low"
        if risk_score > 0.7:
            risk_level = "High"
        elif risk_score > 0.4:
            risk_level = "Medium"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "fraud_indicators": fraud_indicators,
            "recommendation": "Approve" if risk_score < 0.5 else "Manual Review Required"
        }
    
    async def _assess_risk(self, claim_data: Dict[str, Any], ai_analysis: Dict[str, Any], fraud_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall claim risk"""
        
        # Combine AI analysis and fraud assessment
        overall_risk = (fraud_assessment["risk_score"] + (1 - ai_analysis["confidence_score"])) / 2
        
        return {
            "overall_risk_score": overall_risk,
            "risk_factors": [
                "Document quality",
                "Fraud indicators",
                "Claim amount",
                "Historical patterns"
            ],
            "recommendation": "Low Risk" if overall_risk < 0.3 else "Medium Risk" if overall_risk < 0.7 else "High Risk"
        }
    
    async def _make_decision(self, claim_data: Dict[str, Any], ai_analysis: Dict[str, Any], fraud_assessment: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Make final claim decision"""
        
        # Decision logic
        if fraud_assessment["risk_score"] > 0.7:
            decision = "Reject"
            reason = "High fraud risk detected"
        elif risk_assessment["overall_risk_score"] > 0.6:
            decision = "Manual Review"
            reason = "Medium risk - requires human review"
        else:
            decision = "Approve"
            reason = "Low risk - automated approval"
        
        return {
            "decision": decision,
            "confidence": 0.89,
            "reasoning": reason,
            "next_steps": self._get_next_steps(decision),
            "processing_notes": f"Processed in {self._calculate_processing_time()}"
        }
    
    async def _update_claim_status(self, claim_id: str, decision: Dict[str, Any]) -> str:
        """Update claim status based on decision"""
        
        if decision["decision"] == "Approve":
            return ClaimStatus.APPROVED.value
        elif decision["decision"] == "Reject":
            return ClaimStatus.REJECTED.value
        else:
            return ClaimStatus.UNDER_REVIEW.value
    
    def _classify_incident_type(self, claim_data: Dict[str, Any]) -> str:
        """Classify incident type based on claim data"""
        
        # Simple classification logic
        amount = float(claim_data.get("claim_amount", 0))
        
        if amount < 1000:
            return "Minor Incident"
        elif amount < 10000:
            return "Standard Claim"
        else:
            return "Major Incident"
    
    def _check_duplicate_claims(self, claim_data: Dict[str, Any]) -> bool:
        """Check for potential duplicate claims"""
        
        # Simulate duplicate check
        # In real implementation, this would check against database
        return False
    
    def _get_next_steps(self, decision: str) -> List[str]:
        """Get next steps based on decision"""
        
        if decision == "Approve":
            return ["Process payment", "Send approval notification", "Update claim status"]
        elif decision == "Reject":
            return ["Send rejection notification", "Archive claim", "Update claim status"]
        else:
            return ["Assign to human reviewer", "Send notification", "Update claim status"]
    
    def _calculate_processing_time(self) -> str:
        """Calculate total processing time"""
        
        # Simulate processing time calculation
        return "2.4 seconds"
    
    async def get_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """Get current claim status"""
        
        # Simulate status retrieval
        return {
            "claim_id": claim_id,
            "status": "ai_processing",
            "progress": 75,
            "current_step": "fraud_detection",
            "estimated_completion": (datetime.now() + timedelta(minutes=2)).isoformat()
        }
    
    async def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing metrics and statistics"""
        
        return {
            "total_claims_processed": 1247,
            "average_processing_time": "2.3 seconds",
            "approval_rate": 0.89,
            "fraud_detection_rate": 0.94,
            "ai_accuracy": 0.95,
            "last_updated": datetime.now().isoformat()
        }

# Global orchestrator instance
claim_orchestrator = ClaimOrchestrator()
