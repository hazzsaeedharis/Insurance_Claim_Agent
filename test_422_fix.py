"""
Test script to identify and fix the 422 error in claim analysis
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any

# Add services to path
sys.path.append(os.path.dirname(__file__))

def test_request_body_validation():
    """Test the Pydantic model validation for ClaimAnalysisRequest"""
    from services.ai_processing.api import ClaimAnalysisRequest
    
    # Test different request body formats
    test_cases = [
        # Case 1: Correct format
        {
            "claim_id": "CLAIM-123",
            "policy_id": "POLICY-456",
            "customer_id": "CUST-789"
        },
        # Case 2: Missing field
        {
            "claim_id": "CLAIM-123",
            "policy_id": "POLICY-456"
        },
        # Case 3: Extra field
        {
            "claim_id": "CLAIM-123",
            "policy_id": "POLICY-456",
            "customer_id": "CUST-789",
            "extra_field": "should be ignored"
        }
    ]
    
    print("Testing ClaimAnalysisRequest validation:")
    print("=" * 60)
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_data}")
        try:
            request = ClaimAnalysisRequest(**test_data)
            print(f"✓ Valid: {request}")
        except Exception as e:
            print(f"✗ Invalid: {e}")


def check_endpoint_signature():
    """Check the endpoint signature and expected parameters"""
    print("\n" + "=" * 60)
    print("Checking endpoint signature:")
    print("=" * 60)
    
    # Read the actual endpoint code
    api_file = "services/ai_processing/api.py"
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Find the analyze_claim endpoint
    import re
    pattern = r'@app\.post\("/claims/analyze/\{claim_id\}".*?\n(.*?)(?=@app|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        endpoint_code = match.group(0)
        # Extract first 500 chars to see the function signature
        print("Endpoint definition found:")
        print("-" * 40)
        print(endpoint_code[:800])
    else:
        print("Could not find endpoint definition")


def test_actual_api_call():
    """Test what actually happens with the API call"""
    print("\n" + "=" * 60)
    print("Testing actual API behavior:")
    print("=" * 60)
    
    # Import the FastAPI app
    from services.ai_processing.api import app
    from fastapi.testclient import TestClient
    
    # Create test client
    client = TestClient(app)
    
    # First, extract a document to get data in cache
    print("\n1. Extracting document first...")
    
    # Create a simple test file
    test_file_content = b"Test invoice content"
    files = {
        'file': ('test_invoice.pdf', test_file_content, 'application/pdf')
    }
    data = {
        'claim_id': 'TEST-CLAIM-123',
        'document_type_hint': 'medical_invoice'
    }
    
    # Note: This might fail because document processor expects real PDFs
    # but it will show us the validation issues
    
    # Test the analyze endpoint
    print("\n2. Testing analyze endpoint...")
    claim_id = "TEST-CLAIM-123"
    
    # Test different request formats
    test_requests = [
        # Format 1: As path parameter only
        {
            "url": f"/claims/analyze/{claim_id}",
            "json": {
                "policy_id": "POLICY-123",
                "customer_id": "CUST-456"
            }
        },
        # Format 2: With claim_id in body too
        {
            "url": f"/claims/analyze/{claim_id}",
            "json": {
                "claim_id": claim_id,
                "policy_id": "POLICY-123",
                "customer_id": "CUST-456"
            }
        }
    ]
    
    for i, test_req in enumerate(test_requests, 1):
        print(f"\nTest Request {i}:")
        print(f"URL: {test_req['url']}")
        print(f"Body: {json.dumps(test_req['json'], indent=2)}")
        
        response = client.post(test_req["url"], json=test_req["json"])
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            print("Validation Error Details:")
            error_detail = response.json()
            if 'detail' in error_detail:
                for error in error_detail['detail']:
                    print(f"  - Location: {error.get('loc', [])}")
                    print(f"    Message: {error.get('msg')}")
                    print(f"    Type: {error.get('type')}")
        elif response.status_code == 404:
            print(f"Response: {response.json()}")
        else:
            print(f"Response: {response.text[:200]}")


def main():
    """Main test function"""
    print("=" * 60)
    print("422 ERROR INVESTIGATION")
    print("=" * 60)
    
    # Test 1: Check Pydantic model validation
    test_request_body_validation()
    
    # Test 2: Check endpoint signature
    check_endpoint_signature()
    
    # Test 3: Test actual API behavior
    try:
        test_actual_api_call()
    except ImportError as e:
        print(f"\nCannot test actual API: {e}")
        print("Install fastapi test client: pip install httpx")


if __name__ == "__main__":
    main()