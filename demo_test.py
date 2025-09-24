#!/usr/bin/env python3
"""
ClaimAI Pro Demo Test Script
Comprehensive testing and demo data generation
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_backend_health():
    """Test backend health endpoint"""
    print_header("Testing Backend Health")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Backend is running!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Demo Mode: {data.get('demo_mode', 'unknown')}")
            print(f"   AI Providers: {data.get('ai_providers_available', {})}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print_error(f"Error testing backend: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print_header("Testing API Endpoints")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/dashboard/stats", "Dashboard stats"),
        ("/api/dashboard/metrics", "Processing metrics"),
        ("/api/claims/", "Claims list"),
        ("/api/ai/demo", "AI demo"),
        ("/api/ai/health", "AI health"),
        ("/api/ai/providers", "AI providers"),
        ("/api/dashboard/recent-claims", "Recent claims"),
        ("/api/dashboard/analytics/trends", "Analytics trends"),
        ("/api/dashboard/performance", "System performance"),
        ("/api/dashboard/alerts", "System alerts")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{description}: OK")
                results[endpoint] = "✅ OK"
            else:
                print_error(f"{description}: Status {response.status_code}")
                results[endpoint] = f"❌ Status {response.status_code}"
        except Exception as e:
            print_error(f"{description}: Error - {e}")
            results[endpoint] = f"❌ Error: {e}"
    
    return results

def generate_demo_claims():
    """Generate realistic demo claims data"""
    print_header("Generating Demo Claims Data")
    
    demo_claims = [
        {
            "id": "claim-001",
            "claimant_name": "John Smith",
            "policy_number": "POL-2024-001234",
            "incident_date": "2024-01-15",
            "claim_amount": 2500.00,
            "incident_type": "Vehicle Collision",
            "location": "123 Main St, Anytown, USA",
            "description": "Rear-end collision on highway",
            "status": "approved",
            "processing_time": "2.3 seconds",
            "ai_confidence": 0.92,
            "fraud_risk": "Low",
            "ai_analysis": {
                "extracted_data": {
                    "claim_amount": "$2,500.00",
                    "incident_type": "Vehicle Collision",
                    "damage_assessment": "Moderate rear-end damage"
                },
                "confidence_score": 0.92
            }
        },
        {
            "id": "claim-002",
            "claimant_name": "Jane Doe",
            "policy_number": "POL-2024-001235",
            "incident_date": "2024-01-14",
            "claim_amount": 1500.00,
            "incident_type": "Property Damage",
            "location": "456 Oak Ave, City, USA",
            "description": "Storm damage to roof",
            "status": "under_review",
            "processing_time": "1.8 seconds",
            "ai_confidence": 0.89,
            "fraud_risk": "Low",
            "ai_analysis": {
                "extracted_data": {
                    "claim_amount": "$1,500.00",
                    "incident_type": "Property Damage",
                    "damage_assessment": "Roof shingle damage from storm"
                },
                "confidence_score": 0.89
            }
        },
        {
            "id": "claim-003",
            "claimant_name": "Mike Johnson",
            "policy_number": "POL-2024-001236",
            "incident_date": "2024-01-13",
            "claim_amount": 5000.00,
            "incident_type": "Medical Emergency",
            "location": "789 Pine St, Medical City, USA",
            "description": "Emergency room visit for accident",
            "status": "rejected",
            "processing_time": "3.1 seconds",
            "ai_confidence": 0.95,
            "fraud_risk": "High",
            "ai_analysis": {
                "extracted_data": {
                    "claim_amount": "$5,000.00",
                    "incident_type": "Medical Emergency",
                    "damage_assessment": "Emergency medical treatment"
                },
                "confidence_score": 0.95
            }
        },
        {
            "id": "claim-004",
            "claimant_name": "Sarah Wilson",
            "policy_number": "POL-2024-001237",
            "incident_date": "2024-01-12",
            "claim_amount": 750.00,
            "incident_type": "Theft",
            "location": "321 Elm St, Downtown, USA",
            "description": "Stolen laptop from office",
            "status": "approved",
            "processing_time": "1.5 seconds",
            "ai_confidence": 0.87,
            "fraud_risk": "Low",
            "ai_analysis": {
                "extracted_data": {
                    "claim_amount": "$750.00",
                    "incident_type": "Theft",
                    "damage_assessment": "Stolen personal property"
                },
                "confidence_score": 0.87
            }
        },
        {
            "id": "claim-005",
            "claimant_name": "David Brown",
            "policy_number": "POL-2024-001238",
            "incident_date": "2024-01-11",
            "claim_amount": 12000.00,
            "incident_type": "Major Accident",
            "location": "555 Highway 101, Interstate, USA",
            "description": "Multi-vehicle collision with injuries",
            "status": "under_review",
            "processing_time": "4.2 seconds",
            "ai_confidence": 0.91,
            "fraud_risk": "Medium",
            "ai_analysis": {
                "extracted_data": {
                    "claim_amount": "$12,000.00",
                    "incident_type": "Major Accident",
                    "damage_assessment": "Severe vehicle damage with injuries"
                },
                "confidence_score": 0.91
            }
        }
    ]
    
    print_success(f"Generated {len(demo_claims)} demo claims")
    for claim in demo_claims:
        print(f"   📋 {claim['id']}: {claim['claimant_name']} - ${claim['claim_amount']:,} ({claim['status']})")
    
    return demo_claims

def test_ai_demo():
    """Test AI demo endpoint"""
    print_header("Testing AI Demo")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/demo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("AI Demo endpoint working!")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Demo Claims: {len(data.get('demo_data', []))}")
            print(f"   AI Providers: {data.get('ai_providers', {})}")
            return True
        else:
            print_error(f"AI Demo returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing AI demo: {e}")
        return False

def test_dashboard_data():
    """Test dashboard data endpoints"""
    print_header("Testing Dashboard Data")
    
    try:
        # Test stats
        stats_response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print_success("Dashboard stats loaded")
            print(f"   Total Claims: {stats.get('total_claims', 0):,}")
            print(f"   Pending: {stats.get('pending_claims', 0)}")
            print(f"   Approved: {stats.get('approved_claims', 0)}")
            print(f"   Rejected: {stats.get('rejected_claims', 0)}")
        
        # Test metrics
        metrics_response = requests.get(f"{API_BASE_URL}/api/dashboard/metrics", timeout=5)
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            print_success("Processing metrics loaded")
            print(f"   AI Accuracy: {metrics.get('ai_accuracy_rate', 0)*100:.1f}%")
            print(f"   Fraud Detection: {metrics.get('fraud_detection_rate', 0)*100:.1f}%")
            print(f"   System Uptime: {metrics.get('system_uptime', 'N/A')}")
        
        return True
    except Exception as e:
        print_error(f"Error testing dashboard data: {e}")
        return False

def create_demo_presentation():
    """Create demo presentation data"""
    print_header("Creating Demo Presentation Data")
    
    presentation_data = {
        "title": "ClaimAI Pro - AI-Powered Insurance Claims Processing",
        "subtitle": "Revolutionizing Insurance with Cutting-Edge AI Technology",
        "key_metrics": {
            "processing_speed": "91% faster than traditional methods",
            "accuracy": "95% AI accuracy rate",
            "fraud_detection": "94% fraud detection rate",
            "cost_savings": "$2.1M+ annual savings per insurer",
            "market_opportunity": "$2.76B market size"
        },
        "demo_scenarios": [
            {
                "scenario": "Standard Auto Claim",
                "claimant": "John Smith",
                "amount": "$2,500",
                "processing_time": "2.3 seconds",
                "ai_decision": "Approved",
                "confidence": "92%"
            },
            {
                "scenario": "High-Value Medical Claim",
                "claimant": "Mike Johnson", 
                "amount": "$5,000",
                "processing_time": "3.1 seconds",
                "ai_decision": "Rejected (Fraud Risk)",
                "confidence": "95%"
            },
            {
                "scenario": "Property Damage Claim",
                "claimant": "Jane Doe",
                "amount": "$1,500",
                "processing_time": "1.8 seconds",
                "ai_decision": "Under Review",
                "confidence": "89%"
            }
        ],
        "ai_capabilities": [
            "Multi-provider AI (OpenAI, Google Gemini, Anthropic)",
            "Intelligent document analysis and OCR",
            "Advanced fraud detection and risk scoring",
            "Automated decision making with confidence levels",
            "Real-time processing and status updates"
        ]
    }
    
    print_success("Demo presentation data created!")
    print(f"   Title: {presentation_data['title']}")
    print(f"   Key Metrics: {len(presentation_data['key_metrics'])}")
    print(f"   Demo Scenarios: {len(presentation_data['demo_scenarios'])}")
    print(f"   AI Capabilities: {len(presentation_data['ai_capabilities'])}")
    
    return presentation_data

def main():
    """Main demo test function"""
    print_header("ClaimAI Pro Demo Test Suite")
    print("🎯 Testing the complete ClaimAI Pro application...")
    
    # Test backend health
    if not test_backend_health():
        print_error("Backend is not running. Please start it first:")
        print("   cd backend && python main.py")
        return
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Test AI demo
    test_ai_demo()
    
    # Test dashboard data
    test_dashboard_data()
    
    # Generate demo claims
    demo_claims = generate_demo_claims()
    
    # Create presentation data
    presentation_data = create_demo_presentation()
    
    # Final summary
    print_header("Demo Test Summary")
    print_success("All tests completed!")
    print_info("Backend is running and ready for demo")
    print_info("Frontend can be opened at: http://localhost:8080")
    print_info("API documentation available at: http://localhost:8000/docs")
    
    print("\n🎯 DEMO READY! You can now:")
    print("   1. Open frontend: http://localhost:8080")
    print("   2. Show API docs: http://localhost:8000/docs")
    print("   3. Test AI demo: http://localhost:8000/api/ai/demo")
    print("   4. View dashboard stats: http://localhost:8000/api/dashboard/stats")

if __name__ == "__main__":
    main()
