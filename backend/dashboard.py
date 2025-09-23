"""
Dashboard API Router
Handles dashboard and analytics endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime, timedelta

from schemas import (
    DashboardStats, ProcessingMetrics, APIResponse
)
from claim_orchestrator import claim_orchestrator

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # In a real implementation, this would query the database
        stats = DashboardStats(
            total_claims=1247,
            pending_claims=23,
            approved_claims=1156,
            rejected_claims=68,
            average_processing_time=2.3,
            fraud_detection_rate=0.94,
            ai_accuracy=0.95
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.get("/metrics", response_model=ProcessingMetrics)
async def get_processing_metrics():
    """Get processing metrics"""
    try:
        metrics = await claim_orchestrator.get_processing_metrics()
        
        return ProcessingMetrics(
            claims_processed_today=metrics.get("total_claims_processed", 0),
            average_processing_time=f"{metrics.get('average_processing_time', '2.3')} seconds",
            ai_accuracy_rate=metrics.get("ai_accuracy", 0.95),
            fraud_detection_rate=metrics.get("fraud_detection_rate", 0.94),
            system_uptime="99.97%",
            last_updated=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing metrics: {str(e)}"
        )

@router.get("/recent-claims")
async def get_recent_claims(limit: int = 10):
    """Get recent claims for dashboard"""
    try:
        # Demo data for recent claims
        recent_claims = [
            {
                "id": "claim-001",
                "claimant_name": "John Smith",
                "claim_amount": 2500.00,
                "status": "approved",
                "processed_at": datetime.now() - timedelta(hours=2),
                "processing_time": "2.3 seconds",
                "ai_confidence": 0.92
            },
            {
                "id": "claim-002",
                "claimant_name": "Jane Doe",
                "claim_amount": 1500.00,
                "status": "under_review",
                "processed_at": datetime.now() - timedelta(hours=4),
                "processing_time": "1.8 seconds",
                "ai_confidence": 0.89
            },
            {
                "id": "claim-003",
                "claimant_name": "Mike Johnson",
                "claim_amount": 5000.00,
                "status": "rejected",
                "processed_at": datetime.now() - timedelta(hours=6),
                "processing_time": "3.1 seconds",
                "ai_confidence": 0.95
            }
        ]
        
        return {
            "recent_claims": recent_claims[:limit],
            "total_count": len(recent_claims)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent claims: {str(e)}"
        )

@router.get("/analytics/trends")
async def get_analytics_trends(days: int = 30):
    """Get analytics trends for specified period"""
    try:
        # Demo analytics data
        trends = {
            "claims_by_status": {
                "approved": 1156,
                "pending": 23,
                "rejected": 68
            },
            "claims_by_type": {
                "Vehicle Collision": 456,
                "Property Damage": 234,
                "Medical Emergency": 189,
                "Theft": 123,
                "Other": 245
            },
            "processing_times": {
                "average": 2.3,
                "fastest": 0.8,
                "slowest": 5.2
            },
            "fraud_detection": {
                "total_analyzed": 1247,
                "fraud_detected": 23,
                "false_positives": 2,
                "accuracy": 0.94
            },
            "ai_performance": {
                "total_processed": 1247,
                "ai_decisions": 1156,
                "human_reviews": 91,
                "accuracy": 0.95
            }
        }
        
        return trends
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics trends: {str(e)}"
        )

@router.get("/performance")
async def get_system_performance():
    """Get system performance metrics"""
    try:
        performance = {
            "api_response_time": "120ms",
            "database_query_time": "45ms",
            "ai_processing_time": "2.3s",
            "system_uptime": "99.97%",
            "memory_usage": "67%",
            "cpu_usage": "23%",
            "active_connections": 156,
            "queue_size": 3
        }
        
        return performance
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system performance: {str(e)}"
        )

@router.get("/alerts")
async def get_system_alerts():
    """Get system alerts and notifications"""
    try:
        alerts = [
            {
                "id": "alert-001",
                "type": "info",
                "message": "AI processing queue is running smoothly",
                "timestamp": datetime.now() - timedelta(minutes=30),
                "resolved": True
            },
            {
                "id": "alert-002", 
                "type": "warning",
                "message": "High-value claim requires manual review",
                "timestamp": datetime.now() - timedelta(hours=2),
                "resolved": False
            },
            {
                "id": "alert-003",
                "type": "success",
                "message": "Fraud detection model updated successfully",
                "timestamp": datetime.now() - timedelta(hours=4),
                "resolved": True
            }
        ]
        
        return {
            "alerts": alerts,
            "unresolved_count": len([a for a in alerts if not a["resolved"]])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system alerts: {str(e)}"
        )
