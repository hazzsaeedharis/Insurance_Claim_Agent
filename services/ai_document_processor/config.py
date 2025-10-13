"""Configuration for AI Document Processing"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    """AI and API configuration settings"""
    
    # API Keys (set via environment variables)
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    
    # Model Configuration
    embedding_model: str = "text-embedding-3-small"  # Best for multilingual
    llm_model: str = "gpt-4"  # Best accuracy
    groq_model: str = "mixtral-8x7b-32768"  # Fast alternative
    
    # Processing Configuration
    chunk_size: int = 500  # Characters per chunk
    chunk_overlap: int = 50
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Vector DB Configuration
    vector_db_type: str = "chromadb"  # "chromadb" or "pinecone"
    collection_name: str = "insurance_policies"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
ai_config = AIConfig()


# Document type definitions
DOCUMENT_TYPES = {
    "medical_invoice": {
        "keywords": ["rechnung", "invoice", "arztrechnung", "medical bill"],
        "required_fields": ["provider", "date", "amount", "services"]
    },
    "prescription": {
        "keywords": ["rezept", "prescription", "verordnung", "rx"],
        "required_fields": ["medication", "dosage", "prescriber", "date"]
    },
    "hospital_bill": {
        "keywords": ["krankenhaus", "hospital", "klinik", "stationär"],
        "required_fields": ["admission_date", "discharge_date", "procedures", "total"]
    },
    "lab_report": {
        "keywords": ["labor", "laboratory", "befund", "test results"],
        "required_fields": ["test_date", "tests_performed", "results"]
    },
    "pharmacy_receipt": {
        "keywords": ["apotheke", "pharmacy", "medikament"],
        "required_fields": ["medications", "quantities", "prices", "date"]
    }
}


# Extraction prompts for different document types
EXTRACTION_PROMPTS = {
    "medical_invoice": """
Extract the following information from this medical invoice:

1. Provider Information:
   - Name
   - Address
   - Tax ID / Provider number

2. Patient Information:
   - Name
   - Insurance number
   - Date of birth (if present)

3. Services Rendered:
   For each service line item:
   - Date of service
   - Service description (in German and/or English)
   - Procedure code (GOÄ/EBM code if present)
   - Quantity
   - Unit price
   - Total price

4. Summary:
   - Subtotal
   - Tax amount (if applicable)
   - Total amount
   - Payment due date

Return the extracted data as a JSON object with clear field names.
""",
    
    "prescription": """
Extract the following information from this prescription:

1. Prescriber:
   - Doctor name
   - Practice name
   - Address
   - Prescription date

2. Patient:
   - Name
   - Date of birth
   - Insurance information

3. Medications:
   For each medication:
   - Name (brand and generic if both present)
   - Strength/dosage
   - Quantity prescribed
   - Dosing instructions
   - PZN (Pharmazentralnummer) if present

4. Additional Information:
   - Valid until date
   - Refills allowed
   - Special instructions

Return as structured JSON.
""",
    
    "hospital_bill": """
Extract the following from this hospital bill:

1. Hospital Information:
   - Name
   - Department
   - Case/invoice number

2. Patient Stay:
   - Admission date
   - Discharge date
   - Room type/class

3. Services and Procedures:
   - Main diagnosis (ICD code if present)
   - Procedures performed (OPS codes if present)
   - Daily rates
   - Special services

4. Costs:
   - Base rate (Basispflegesatz)
   - Department costs
   - Additional services
   - Total amount

Return as structured JSON with German terms preserved where relevant.
"""
}


# Medical code validation patterns
MEDICAL_CODE_PATTERNS = {
    "icd10": r"[A-Z]\d{2}\.?\d*",  # ICD-10 codes
    "ops": r"\d-\d{3}(?:\.\d+)?",  # OPS codes (German procedure codes)
    "goa": r"\d{1,4}[a-zA-Z]?",  # GOÄ codes (German medical fee schedule)
    "ebm": r"\d{5}[A-Z]?",  # EBM codes (German uniform assessment standard)
    "pzn": r"\d{7,8}",  # Pharmazentralnummer (German pharmaceutical number)
}


# Policy section identifiers (German and English)
POLICY_SECTIONS = {
    "coverage": ["leistungen", "coverage", "erstattung", "benefits"],
    "exclusions": ["ausschlüsse", "exclusions", "nicht erstattungsfähig"],
    "deductibles": ["selbstbehalt", "eigenanteil", "deductible"],
    "limits": ["höchstbeträge", "limits", "jahreshöchst", "maximum"],
    "waiting_periods": ["wartezeiten", "waiting period", "karenzzeit"],
    "pre_authorization": ["genehmigung", "vorherige", "pre-authorization"],
}
