"""
Configuration Management for Insurance Claim Processing System

Centralizes all configuration in one place following the Single Responsibility Principle.
Uses environment variables for sensitive data (12-factor app methodology).
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Following clean code principles:
    - Single source of truth for configuration
    - Clear, descriptive names
    - Sensible defaults for development
    """
    
    # ========================================================================
    # API CONFIGURATION
    # ========================================================================
    app_name: str = "Insurance Claim Processor"
    app_version: str = "1.0.0"
    debug_mode: bool = True
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    
    # ========================================================================
    # AI SERVICE KEYS (Set via environment variables)
    # ========================================================================
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  
    gemini_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east-1"
    
    # ========================================================================
    # AI MODEL SELECTION
    # ========================================================================
    # LLM Models (in order of preference)
    groq_model: str = "llama-3.3-70b-versatile"  # Updated to current model
    gemini_llm_model: str = "gemini-1.5-flash"
    gemini_model: str = "gemini-1.5-flash"  # Backward compatibility
    openai_model: str = "gpt-4"
    
    # Embedding Models
    embedding_strategy: str = "local"  # local, openai, or gemini
    local_embedding_model: str = "all-MiniLM-L6-v2"
    openai_embedding_model: str = "text-embedding-3-small"
    gemini_embedding_model: str = "models/text-embedding-004"
    embedding_model: str = "text-embedding-3-small"  # Backward compatibility
    embedding_dimension: int = 384  # For local model (all-MiniLM-L6-v2)
    
    # ========================================================================
    # DOCUMENT PROCESSING
    # ========================================================================
    max_file_size_mb: int = 10
    supported_file_types: list = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
    ocr_language: str = "deu+eng"  # German + English
    
    # ========================================================================
    # VECTOR DATABASE
    # ========================================================================
    vector_db_type: str = "pinecone"  # or "chroma"
    pinecone_index_name: str = "insurance-policies"
    collection_name: str = "insurance-policies"  # For backward compatibility
    pinecone_metric: str = "cosine"
    vector_search_top_k: int = 5
    chunk_size: int = 1000  # Characters per chunk
    chunk_overlap: int = 200  # Overlap between chunks
    
    # ========================================================================
    # CLAIM PROCESSING
    # ========================================================================
    default_currency: str = "EUR"
    default_deductible: float = 50.0
    default_coverage_rate: float = 0.80  # 80% coverage
    
    # ========================================================================
    # AUTHENTICATION & SECURITY
    # ========================================================================
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/insurance_claims"
    
    # JWT Configuration
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Change in production!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Google OAuth2
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    
    # Frontend URL (for CORS and redirects)
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings singleton.
    
    Returns:
        Settings: Application configuration instance
        
    This ensures we only load configuration once (Singleton pattern).
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_api_keys() -> dict:
    """
    Check which AI services are configured.
    
    Returns:
        dict: Status of each AI service configuration
    """
    settings = get_settings()
    
    return {
        "groq": bool(settings.groq_api_key),
        "openai": bool(settings.openai_api_key),
        "gemini": bool(settings.gemini_api_key),
        "pinecone": bool(settings.pinecone_api_key),
    }


def get_active_llm() -> tuple[str, str]:
    """
    Determine which LLM to use based on available API keys.
    
    Returns:
        tuple: (service_name, model_name)
        
    Priority order: Gemini > OpenAI > Groq
    """
    settings = get_settings()
    
    if settings.gemini_api_key:
        return ("gemini", settings.gemini_model)
    elif settings.openai_api_key:
        return ("openai", settings.openai_model)
    elif settings.groq_api_key:
        return ("groq", settings.groq_model)
    else:
        raise ValueError(
            "No AI service configured. Please set at least one API key: "
            "GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY"
        )


# ============================================================================
# DOCUMENT PROCESSING CONSTANTS
# ============================================================================

DOCUMENT_TYPES = {
    "medical_invoice": {
        "keywords": ["rechnung", "invoice", "arztrechnung", "behandlung", "doctor", "medical"],
        "required_fields": ["patient_name", "total_amount", "service_date", "provider"]
    },
    "prescription": {
        "keywords": ["rezept", "prescription", "medikament", "medication", "pharmacy", "apotheke"],
        "required_fields": ["patient_name", "medication", "prescription_date", "doctor"]
    },
    "medical_report": {
        "keywords": ["befund", "report", "diagnose", "diagnosis", "arztbericht"],
        "required_fields": ["patient_name", "diagnosis", "report_date", "doctor"]
    },
    "lab_results": {
        "keywords": ["labor", "lab", "testergebnis", "test result", "blut", "blood"],
        "required_fields": ["patient_name", "test_type", "result_date"]
    }
}

EXTRACTION_PROMPTS = {
    "medical_invoice": """
    Extract the following information from this medical invoice/receipt:
    
    1. Patient Information:
       - patient_name
       - patient_dob (date of birth)
       - policy_number (if mentioned)
    
    2. Provider Information:
       - provider_name
       - provider_address
       - provider_id (if mentioned)
    
    3. Service Information:
       - service_date
       - services (array of):
         * service_description
         * procedure_code (if available)
         * quantity
         * unit_price
         * total_price
    
    4. Financial Information:
       - subtotal
       - tax (if applicable)
       - total_amount
       - currency (usually EUR)
    
    Return as a structured JSON object with these exact field names.
    """,
    
    "prescription": """
    Extract the following information from this prescription:
    
    1. Patient Information:
       - patient_name
       - patient_dob
    
    2. Doctor Information:
       - doctor_name
       - doctor_address
    
    3. Prescription Information:
       - prescription_date
       - medications (array of):
         * medication_name
         * dosage
         * quantity
         * instructions
         * pzn (pharmaceutical number if available)
    
    4. Pharmacy Information (if filled):
       - pharmacy_name
       - fill_date
       - total_cost
    
    Return as a structured JSON object with these exact field names.
    """,
    
    "medical_report": """
    Extract the following information from this medical report:
    
    1. Patient Information:
       - patient_name
       - patient_dob
    
    2. Doctor Information:
       - doctor_name
       - specialty
       - facility_name
    
    3. Report Information:
       - report_date
       - diagnosis
       - symptoms
       - examination_findings
       - recommended_treatment
       - icd_codes (if mentioned)
    
    Return as a structured JSON object with these exact field names.
    """
}

MEDICAL_CODE_PATTERNS = {
    "GOÄ": r"\d{4,5}[A-Z]?",  # German medical fee schedule
    "ICD": r"[A-Z]\d{2}\.\d{1,2}",  # ICD-10 codes
    "PZN": r"\d{7,8}",  # Pharmaceutical number (Germany)
    "OPS": r"\d-\d{3}\.\d{1,2}"  # German procedure codes
}

POLICY_SECTIONS = {
    "coverage": ["leistungen", "coverage", "erstattung", "reimbursement", "versicherungsschutz"],
    "exclusions": ["ausschlüsse", "exclusions", "nicht versichert", "not covered"],
    "limitations": ["begrenzungen", "limitations", "limits", "höchstbeträge"],
    "waiting_period": ["wartezeit", "waiting period", "karenzzeit"],
    "deductible": ["selbstbehalt", "deductible", "eigenanteil"],
    "general": ["allgemeine bedingungen", "general terms", "definitions"]
}