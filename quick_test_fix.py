"""Quick test to verify the document extraction fix is working"""
import requests
import json

# Test extraction only
API_URL = "http://localhost:8005"

print("Testing Document Extraction Fix")
print("==============================\n")

# Test with the ambiguous dental claim
with open("data/samples/documents/hallesche_ambiguous_claim.pdf", "rb") as f:
    files = {'file': ('test.pdf', f, 'application/pdf')}
    data = {'claim_id': 'TEST-123', 'document_type_hint': 'dental'}
    
    response = requests.post(f"{API_URL}/documents/extract", files=files, data=data)

if response.status_code == 200:
    result = response.json()
    extracted = result['extracted_data']
    
    print("[SUCCESS] Document extracted!")
    print(f"Document Type: {result['document_type']}")
    
    # Count services
    if 'servicesRendered' in extracted:
        total = sum(float(s.get('totalPrice', 0)) for s in extracted['servicesRendered'])
        print(f"\nExtracted Services:")
        for s in extracted['servicesRendered']:
            print(f"  - {s.get('serviceDescription')}: €{s.get('totalPrice')}")
        print(f"\nTotal: €{total}")
        
        if total == 625.0:
            print("\n✓ CORRECT! Extracted actual €625 dental claim")
            print("✓ NOT the hardcoded €130.50 consultation + blood test")
        else:
            print(f"\n✗ ERROR: Expected €625, got €{total}")
    else:
        print("\nRaw extracted data:")
        print(json.dumps(extracted, indent=2))
else:
    print(f"[ERROR] Extraction failed: {response.status_code}")
    print(response.text)
