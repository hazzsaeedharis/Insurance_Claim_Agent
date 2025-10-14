"""
Debug script to identify the 422 error in the AI analysis endpoint
"""

import os
import sys
import json
import requests
import tempfile
from typing import Dict, Any

# Add services to path
sys.path.append(os.path.dirname(__file__))

def test_extraction_endpoint(base_url: str = "http://localhost:8000"):
    """Test the document extraction endpoint"""
    print("\n" + "="*60)
    print("TESTING DOCUMENT EXTRACTION ENDPOINT")
    print("="*60)
    
    # Check if we have a sample file
    sample_file = "data/samples/documents/hallesche_valid_outpatient.pdf"
    if not os.path.exists(sample_file):
        print(f"[WARNING] Sample file not found: {sample_file}")
        # Create a dummy file for testing
        sample_file = "data/synthetic/claim_001.json"
        if not os.path.exists(sample_file):
            print("[ERROR] No test files available")
            return None, None
    
    claim_id = "CLAIM-1760443249413"
    
    # Test extraction
    with open(sample_file, 'rb') as f:
        files = {'file': ('claim.pdf', f, 'application/pdf')}
        data = {
            'claim_id': claim_id,
            'document_type_hint': 'medical_invoice'
        }
        
        url = f"{base_url}/documents/extract"
        print(f"\nPOST {url}")
        print(f"Data: {data}")
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("[OK] Document extracted successfully")
                print(f"Document type: {result.get('document_type')}")
                print(f"Extracted data keys: {list(result.get('extracted_data', {}).keys())}")
                
                # Show the extracted data structure
                print("\nExtracted Data Structure:")
                print(json.dumps(result.get('extracted_data'), indent=2)[:500] + "...")
                
                return claim_id, result.get('extracted_data')
            else:
                print(f"[ERROR] Extraction failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None, None


def test_analysis_endpoint(claim_id: str, base_url: str = "http://localhost:8000"):
    """Test the claim analysis endpoint"""
    print("\n" + "="*60)
    print("TESTING CLAIM ANALYSIS ENDPOINT")
    print("="*60)
    
    # Prepare the request data
    request_data = {
        "claim_id": claim_id,
        "policy_id": "HALLESCHE_NK_SELECT_S",
        "customer_id": "CUST-123456"
    }
    
    url = f"{base_url}/claims/analyze/{claim_id}"
    print(f"\nPOST {url}")
    print(f"Request Data: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 422:
            print("\n[ERROR] 422 Unprocessable Content")
            print("Response details:")
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
            
            # Analyze the validation error
            if 'detail' in error_data:
                print("\nValidation Error Details:")
                for error in error_data.get('detail', []):
                    if isinstance(error, dict):
                        print(f"  - Field: {error.get('loc', [])}")
                        print(f"    Message: {error.get('msg')}")
                        print(f"    Type: {error.get('type')}")
                    else:
                        print(f"  - {error}")
            
            return False
            
        elif response.status_code == 200:
            result = response.json()
            print("[OK] Claim analyzed successfully")
            print(f"Total claimed: €{result.get('total_claimed')}")
            print(f"Total approved: €{result.get('total_approved')}")
            print(f"Approval rate: {result.get('approval_rate')}%")
            return True
            
        else:
            print(f"[ERROR] Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return False


def check_extracted_data_in_cache():
    """Check what's stored in the extracted documents cache"""
    print("\n" + "="*60)
    print("CHECKING EXTRACTED DATA STRUCTURE")
    print("="*60)
    
    # Import the document processor to see what it outputs
    from services.ai_document_processor.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    
    # Process a sample document to see the structure
    sample_file = "data/samples/documents/hallesche_valid_outpatient.pdf"
    if not os.path.exists(sample_file):
        # Try with synthetic data
        sample_file = "data/synthetic/claim_001.json"
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                data = json.load(f)
                print("\nSynthetic data structure:")
                print(json.dumps(data, indent=2)[:1000])
        return
    
    try:
        result = processor.process_document(
            file_path=sample_file,
            hints={"document_type": "medical_invoice"}
        )
        
        print("\nDocument Processor Output Structure:")
        print(f"Keys in result: {list(result.keys())}")
        print(f"\nExtracted data keys: {list(result['extracted_data'].keys())}")
        
        # Check the structure of services/servicesRendered
        extracted_data = result['extracted_data']
        if 'servicesRendered' in extracted_data:
            print(f"\nFound 'servicesRendered' with {len(extracted_data['servicesRendered'])} items")
            if extracted_data['servicesRendered']:
                print("First service structure:")
                print(json.dumps(extracted_data['servicesRendered'][0], indent=2))
        
        if 'services' in extracted_data:
            print(f"\nFound 'services' with {len(extracted_data['services'])} items")
            if extracted_data['services']:
                print("First service structure:")
                print(json.dumps(extracted_data['services'][0], indent=2))
                
        # Check what the claim analyzer expects
        print("\n" + "-"*40)
        print("What ClaimAnalyzer._extract_claim_items expects:")
        print("- 'servicesRendered' (new structure)")
        print("- 'services' (old structure)")
        print("- 'medications' (prescription structure)")
        
    except Exception as e:
        print(f"[ERROR] Failed to process document: {e}")
        import traceback
        traceback.print_exc()


def diagnose_pydantic_model():
    """Check the Pydantic model definitions"""
    print("\n" + "="*60)
    print("CHECKING PYDANTIC MODEL DEFINITIONS")
    print("="*60)
    
    from services.ai_processing.api import ClaimAnalysisRequest, ClaimAnalysisResponse
    
    print("\nClaimAnalysisRequest model:")
    print(f"Fields: {ClaimAnalysisRequest.__fields__.keys()}")
    for field_name, field in ClaimAnalysisRequest.__fields__.items():
        print(f"  - {field_name}: {field.type_} (required={field.required})")
    
    print("\nClaimAnalysisResponse model:")
    print(f"Fields: {ClaimAnalysisResponse.__fields__.keys()}")
    for field_name, field in ClaimAnalysisResponse.__fields__.items():
        print(f"  - {field_name}: {field.type_} (required={field.required})")


def main():
    """Main test function"""
    print("AI PROCESSING 422 ERROR DEBUGGER")
    print("="*60)
    
    # Check if the service is running
    base_url = "http://localhost:8000"
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            print(f"[OK] Service is running at {base_url}")
            service_info = response.json()
            print(f"Service: {service_info.get('service')}")
            print(f"Version: {service_info.get('version')}")
        else:
            print(f"[WARNING] Service returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Service is not running at {base_url}")
        print("Please start the service with: python services/ai_processing/api.py")
        print("\nRunning offline diagnostics...")
        
        # Run offline checks
        check_extracted_data_in_cache()
        diagnose_pydantic_model()
        return
    
    # 1. Test extraction
    claim_id, extracted_data = test_extraction_endpoint(base_url)
    
    if claim_id and extracted_data:
        # 2. Test analysis with the extracted data
        success = test_analysis_endpoint(claim_id, base_url)
        
        if not success:
            print("\n" + "="*60)
            print("DEBUGGING 422 ERROR")
            print("="*60)
            
            # Check the model requirements
            diagnose_pydantic_model()
            
            # Check the actual extracted data structure
            print("\n" + "-"*40)
            print("Extracted data that was stored:")
            print(json.dumps(extracted_data, indent=2)[:1000])
    
    # Additional diagnostics
    check_extracted_data_in_cache()


if __name__ == "__main__":
    main()