"""
Test different Groq models to find the best one for JSON extraction
"""
import os
import sys
import json
import re
sys.path.append(os.path.dirname(__file__))

from groq import Groq
from services.ai_document_processor.config import ai_config

client = Groq(api_key=ai_config.groq_api_key)

# Models to test (based on common Groq models)
MODELS_TO_TEST = [
    "llama-3.3-70b-versatile",      # Current model
    "llama-3.1-70b-versatile",      # Previous version
    "llama-3.1-8b-instant",         # Faster, smaller
    "gemma2-9b-it",                 # Google's Gemma
    "mixtral-8x7b-32768",           # Mixtral (might be deprecated)
]

# Test prompt
prompt = """
Analyze this insurance policy section and extract the following information:

Section Type: coverage
Section Text:
We reimburse 80% of outpatient treatment costs after a 500 EUR annual deductible. Maximum annual limit is 5000 EUR.

Extract:
1. Coverage percentage (if mentioned)
2. Deductible amounts (if mentioned)
3. Annual or per-case limits (if mentioned)

Return ONLY valid JSON with this exact structure:
{
    "coverage_percentage": 80,
    "deductible": {"amount": 500, "currency": "EUR", "per": "year"},
    "limits": {"amount": 5000, "currency": "EUR", "per": "year"}
}

IMPORTANT: Return ONLY the JSON object. No explanations, no markdown, no code fences.
"""

def test_model(model_name: str):
    """Test a single model"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an insurance policy analyst. Return ONLY valid JSON, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        print(f"\nRaw response length: {len(content)} chars")
        print(f"First 150 chars: {content[:150]}...")
        
        # Try to extract and parse JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                print(f"\n[SUCCESS] Valid JSON extracted!")
                print(f"Parsed data: {json.dumps(parsed, indent=2)}")
                
                # Check if it has the expected fields
                has_coverage = "coverage_percentage" in parsed
                has_deductible = "deductible" in parsed
                has_limits = "limits" in parsed
                
                print(f"\nField validation:")
                print(f"  - coverage_percentage: {'✓' if has_coverage else '✗'}")
                print(f"  - deductible: {'✓' if has_deductible else '✗'}")
                print(f"  - limits: {'✓' if has_limits else '✗'}")
                
                score = sum([has_coverage, has_deductible, has_limits])
                print(f"\nScore: {score}/3")
                return score, True, content
                
            except json.JSONDecodeError as e:
                print(f"\n[FAILED] JSON parsing error: {e}")
                return 0, False, content
        else:
            print(f"\n[FAILED] No JSON found in response")
            return 0, False, content
            
    except Exception as e:
        print(f"\n[ERROR] Model failed: {e}")
        return 0, False, str(e)

# Test all models
print("\n" + "="*60)
print("GROQ MODEL COMPARISON TEST")
print("="*60)

results = []
for model in MODELS_TO_TEST:
    score, success, response = test_model(model)
    results.append({
        "model": model,
        "score": score,
        "success": success
    })

# Summary
print("\n\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"\n{'Model':<35} {'Score':<10} {'Status'}")
print("-"*60)
for r in results:
    status = "✓ OK" if r["success"] else "✗ FAILED"
    print(f"{r['model']:<35} {r['score']}/3        {status}")

# Recommend best model
best = max(results, key=lambda x: x["score"])
print(f"\n{'='*60}")
print(f"RECOMMENDATION: {best['model']}")
print(f"Score: {best['score']}/3")
print(f"{'='*60}")

