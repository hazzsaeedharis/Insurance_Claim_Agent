"""
Test script for AI Document Processing
Run this to test the document processing pipeline
"""

import os
import sys
import asyncio
import json

# Add services to path
sys.path.append(os.path.dirname(__file__))

from services.ai_document_processor.config import ai_config
from services.ai_document_processor.policy_indexer import PolicyIndexer
from services.ai_document_processor.document_processor import DocumentProcessor
from services.ai_document_processor.claim_analyzer import ClaimAnalyzer


async def test_pipeline():
    """Test the complete document processing pipeline"""
    
    print("Testing AI Document Processing Pipeline")
    print("=" * 50)
    
    # Initialize components
    print("\n1. Initializing components...")
    policy_indexer = PolicyIndexer()
    document_processor = DocumentProcessor()
    claim_analyzer = ClaimAnalyzer()
    print("[OK] Components initialized")
    
    # Test 1: Index a policy document
    print("\n2. Testing Policy Indexing...")
    print("   (This will create a vector database of policy terms)")
    
    policy_path = "data/policies/hallesche/pm255u-e-0922.pdf"
    if os.path.exists(policy_path):
        try:
            result = policy_indexer.index_policy_document(
                pdf_path=policy_path,
                policy_id="HALLESCHE_NK_SELECT_S",
                policy_name="Hallesche NK.select S"
            )
            print(f"[OK] Policy indexed successfully!")
            print(f"   - Total sections: {result['total_sections']}")
            print(f"   - Total chunks: {result['total_chunks']}")
            print(f"   - Section types: {', '.join(result['section_types'])}")
        except Exception as e:
            print(f"[ERROR] Error indexing policy: {e}")
            print("   Note: You need to set OPENAI_API_KEY for embeddings or the system will use placeholders")
    else:
        print(f"[WARNING] Policy file not found: {policy_path}")
    
    # Test 2: Process a claim document
    print("\n3. Testing Document Processing...")
    print("   (This extracts data from claim documents)")
    
    claim_path = "data/samples/documents/hallesche_valid_outpatient.pdf"
    if os.path.exists(claim_path):
        try:
            result = document_processor.process_document(
                file_path=claim_path,
                hints={"document_type": "medical_invoice"}
            )
            print(f"[OK] Document processed successfully!")
            print(f"   - Document type: {result['document_type']}")
            print(f"   - Confidence: {result['confidence_scores'].get('overall', 0):.2%}")
            print(f"   - Extracted fields: {len(result['extracted_data'])} items")
            
            # Save extracted data for next step
            extracted_data = result['extracted_data']
            
            # Print some extracted data
            if 'services' in extracted_data:
                print(f"   - Services found: {len(extracted_data['services'])}")
                for service in extracted_data['services'][:2]:
                    print(f"     • {service.get('description', 'Unknown')}: €{service.get('total_price', 0)}")
            
        except Exception as e:
            print(f"[ERROR] Error processing document: {e}")
            print("   Note: Make sure Tesseract OCR is installed")
            # Create mock data for testing
            extracted_data = {
                "provider": {"name": "Dr. Schmidt Medical Center"},
                "services": [
                    {
                        "description": "General consultation",
                        "code": "01010",
                        "total_price": 85.00,
                        "date": "2024-01-15"
                    }
                ]
            }
    else:
        print(f"[WARNING] Claim file not found: {claim_path}")
        # Create mock data
        extracted_data = {
            "provider": {"name": "Dr. Schmidt Medical Center"},
            "services": [
                {
                    "description": "General consultation",
                    "code": "01010",
                    "total_price": 85.00,
                    "date": "2024-01-15"
                }
            ]
        }
    
    # Test 3: Analyze claim against policy
    print("\n4. Testing Claim Analysis...")
    print("   (This matches claims against policy and calculates reimbursement)")
    
    customer_data = {
        "customer_id": "DEMO-001",
        "deductible_used_this_year": 25.00,
        "claims_paid_this_year": 500.00
    }
    
    try:
        result = claim_analyzer.analyze_claim(
            extracted_data=extracted_data,
            policy_id="HALLESCHE_NK_SELECT_S",
            customer_data=customer_data
        )
        
        print(f"[OK] Claim analyzed successfully!")
        print(f"   - Total claimed: €{result['total_claimed']:.2f}")
        print(f"   - Total approved: €{result['total_approved']:.2f}")
        print(f"   - Approval rate: {result['approval_rate']:.1f}%")
        print(f"\n   Justification Preview:")
        print("   " + "-" * 40)
        justification_lines = result['justification'].split('\n')[:10]
        for line in justification_lines:
            print(f"   {line}")
        print("   ...")
        
    except Exception as e:
        print(f"[ERROR] Error analyzing claim: {e}")
    
    # Test 4: Search policy
    print("\n5. Testing Policy Search...")
    print("   (This demonstrates RAG-based policy retrieval)")
    
    try:
        search_results = policy_indexer.search_policy(
            query="outpatient treatment coverage percentage",
            policy_id="HALLESCHE_NK_SELECT_S",
            top_k=2
        )
        
        if search_results:
            print(f"[OK] Found {len(search_results)} relevant policy sections")
            for i, result in enumerate(search_results[:2], 1):
                print(f"\n   Result {i}:")
                print(f"   {result['text'][:150]}...")
                if result['metadata']:
                    print(f"   Section: {result['metadata'].get('section_type', 'Unknown')}")
        else:
            print("[WARNING] No search results found (vector DB might be empty)")
            
    except Exception as e:
        print(f"[ERROR] Error searching policy: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("\nNotes:")
    print("- For production use, add your OPENAI_API_KEY to get better embeddings")
    print("- Make sure to set GROQ_API_KEY environment variable")
    print("- Install Tesseract OCR for document processing: https://github.com/tesseract-ocr/tesseract")


if __name__ == "__main__":
    # Check API keys
    print("\nAPI Key Status:")
    print(f"   - Groq API Key: {'[OK] Set' if ai_config.groq_api_key else '[ERROR] Missing'}")
    print(f"   - Gemini API Key: {'[OK] Set' if ai_config.gemini_api_key else '[WARNING] Not set'}")
    print(f"   - OpenAI API Key: {'[OK] Set' if ai_config.openai_api_key else '[WARNING] Not set'}")
    
    if not ai_config.groq_api_key:
        print("\n[WARNING] Groq API key is required!")
        print("   Please set the GROQ_API_KEY environment variable:")
        print("   export GROQ_API_KEY='your_groq_api_key_here'")
        print("\n   Get your API key from: https://console.groq.com/keys")
        print("   See services/ai_document_processor/API_KEYS.md for details")
        exit(1)
    
    # Run tests
    asyncio.run(test_pipeline())
