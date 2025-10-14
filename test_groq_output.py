"""
Quick test to see what Groq is actually returning
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from groq import Groq
from services.ai_document_processor.config import ai_config

client = Groq(api_key=ai_config.groq_api_key)

# Test the exact prompt we're using
prompt = """
You are an insurance policy analyst. Extract information precisely.

Analyze this insurance policy section and extract the following information:

Section Type: coverage
Section Text:
We reimburse 100% of the costs of general hospital treatment.

Extract:
1. Coverage percentage (if mentioned)
2. Deductible amounts (if mentioned)
3. Annual or per-case limits (if mentioned)
4. Waiting periods (if mentioned)
5. Key conditions or requirements
6. Excluded items (if this is an exclusions section)

Return as JSON with the following structure:
{
    "coverage_percentage": null or number (e.g., 80),
    "deductible": null or {"amount": number, "currency": "EUR", "per": "year|case"},
    "limits": null or {"amount": number, "currency": "EUR", "per": "year|case|lifetime"},
    "waiting_period_days": null or number,
    "conditions": [],
    "exclusions": []
}

Be precise and only include information explicitly stated in the text.
"""

response = client.chat.completions.create(
    model=ai_config.groq_model,
    messages=[
        {"role": "system", "content": "You are an insurance policy analyst. Extract information precisely as JSON."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    max_tokens=1000
)

print("=" * 60)
print("GROQ MODEL:", ai_config.groq_model)
print("=" * 60)
print("\nRaw Response:")
print("-" * 60)
print(response.choices[0].message.content)
print("-" * 60)
print("\nResponse Type:", type(response.choices[0].message.content))
print("Response Length:", len(response.choices[0].message.content))
print("\nFirst 100 chars:", repr(response.choices[0].message.content[:100]))

