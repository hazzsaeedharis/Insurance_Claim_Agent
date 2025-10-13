"""
Test what data is being extracted from claim documents
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from services.ai_document_processor.document_processor import DocumentProcessor

processor = DocumentProcessor()

claim_path = "data/samples/documents/hallesche_valid_outpatient.pdf"

if os.path.exists(claim_path):
    result = processor.process_document(
        file_path=claim_path,
        hints={"document_type": "medical_invoice"}
    )
    
    print("=" * 60)
    print("DOCUMENT EXTRACTION RESULTS")
    print("=" * 60)
    print(f"\nDocument type: {result['document_type']}")
    print(f"Status: {result.get('status', 'unknown')}")
    
    print(f"\n\nExtracted Data:")
    print("-" * 60)
    import json
    print(json.dumps(result['extracted_data'], indent=2))
    
else:
    print(f"File not found: {claim_path}")

