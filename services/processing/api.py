"""Document Processing Service for extraction and classification."""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

# Initialize FastAPI
app = FastAPI(
    title="Document Processing Service",
    description="Document extraction and classification service",
    version="1.0.0"
)

# Service URLs
OCR_SERVICE_URL = "http://localhost:8003"
DOCUMENT_SERVICE_URL = "http://localhost:8002"


class DocumentType(str, Enum):
    """Document classification types."""
    INVOICE = "invoice"
    PRESCRIPTION = "prescription"
    MEDICAL_REPORT = "medical_report"
    LAB_RESULTS = "lab_results"
    DENTAL_RECORD = "dental_record"
    INSURANCE_CARD = "insurance_card"
    CLAIM_FORM = "claim_form"
    RECEIPT = "receipt"
    REFERRAL = "referral"
    OTHER = "other"


class ExtractedData(BaseModel):
    """Extracted data model."""
    document_id: str
    document_type: DocumentType
    extracted_fields: Dict[str, Any]
    confidence: float
    extraction_timestamp: datetime


class ClassificationResult(BaseModel):
    """Classification result model."""
    document_id: str
    document_type: DocumentType
    confidence: float
    alternative_types: List[Dict[str, float]]


class FieldExtractor:
    """Extract specific fields from text based on patterns."""
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """Extract dates from text."""
        # Common date patterns
        patterns = [
            r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}',  # DD.MM.YYYY or MM/DD/YYYY
            r'\d{4}[./-]\d{1,2}[./-]\d{1,2}',      # YYYY-MM-DD
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates
    
    @staticmethod
    def extract_amounts(text: str) -> List[Dict[str, Any]]:
        """Extract monetary amounts from text."""
        patterns = [
            r'€\s*(\d+[.,]\d{2})',
            r'EUR\s*(\d+[.,]\d{2})',
            r'(\d+[.,]\d{2})\s*€',
            r'(\d+[.,]\d{2})\s*EUR',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = float(match.replace(',', '.'))
                amounts.append({
                    "value": amount,
                    "currency": "EUR",
                    "raw": match
                })
        
        return amounts
    
    @staticmethod
    def extract_policy_number(text: str) -> Optional[str]:
        """Extract policy number from text."""
        patterns = [
            r'Policy\s*#?\s*:?\s*([A-Z0-9-]+)',
            r'Versicherungsnummer\s*:?\s*([A-Z0-9-]+)',
            r'HK-\d{4}-\d{6}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        
        return None
    
    @staticmethod
    def extract_patient_info(text: str) -> Dict[str, str]:
        """Extract patient information from text."""
        info = {}
        
        # Name patterns
        name_patterns = [
            r'Patient\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Name\s*:?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                info['name'] = match.group(1)
                break
        
        # Date of birth
        dob_patterns = [
            r'DOB\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
            r'Geburtsdatum\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['date_of_birth'] = match.group(1)
                break
        
        return info
    
    @staticmethod
    def extract_provider_info(text: str) -> Dict[str, str]:
        """Extract healthcare provider information."""
        info = {}
        
        # Doctor/Provider name
        provider_patterns = [
            r'Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Physician\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Arzt\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in provider_patterns:
            match = re.search(pattern, text)
            if match:
                info['provider_name'] = match.group(1)
                break
        
        # Clinic/Hospital
        clinic_patterns = [
            r'(Hospital|Clinic|Krankenhaus|Klinik)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in clinic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['facility'] = match.group(0)
                break
        
        return info
    
    @staticmethod
    def extract_diagnosis_codes(text: str) -> List[str]:
        """Extract ICD-10 diagnosis codes."""
        # ICD-10 pattern
        pattern = r'[A-Z]\d{2}(?:\.\d{1,2})?'
        matches = re.findall(pattern, text)
        return matches
    
    @staticmethod
    def extract_prescription_info(text: str) -> List[Dict[str, str]]:
        """Extract prescription medication information."""
        medications = []
        
        # Common medication patterns
        med_patterns = [
            r'(\w+)\s+(\d+)\s*mg',
            r'(\w+)\s+(\d+)\s*ml',
        ]
        
        for pattern in med_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                medications.append({
                    "name": match[0],
                    "dosage": f"{match[1]}mg" if 'mg' in pattern else f"{match[1]}ml"
                })
        
        return medications


class DocumentClassifier:
    """Classify documents based on content."""
    
    @staticmethod
    def classify(text: str) -> ClassificationResult:
        """Classify document type based on text content."""
        scores = {}
        text_lower = text.lower()
        
        # Keywords for each document type
        keywords = {
            DocumentType.INVOICE: [
                "invoice", "rechnung", "total", "subtotal", "tax", "mwst", "bill"
            ],
            DocumentType.PRESCRIPTION: [
                "prescription", "rezept", "medication", "dosage", "mg", "ml", "tablets"
            ],
            DocumentType.MEDICAL_REPORT: [
                "diagnosis", "diagnose", "examination", "untersuchung", "medical report"
            ],
            DocumentType.LAB_RESULTS: [
                "lab", "laboratory", "blood", "urine", "test results", "laborwerte"
            ],
            DocumentType.DENTAL_RECORD: [
                "dental", "zahnarzt", "tooth", "teeth", "orthodontic"
            ],
            DocumentType.INSURANCE_CARD: [
                "insurance card", "versicherungskarte", "policy number", "member id"
            ],
            DocumentType.CLAIM_FORM: [
                "claim form", "antragsformular", "reimbursement", "erstattung"
            ],
            DocumentType.RECEIPT: [
                "receipt", "quittung", "payment", "zahlung", "paid"
            ],
            DocumentType.REFERRAL: [
                "referral", "überweisung", "specialist", "facharzt"
            ]
        }
        
        # Calculate scores for each type
        for doc_type, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            if score > 0:
                scores[doc_type] = score
        
        # Normalize scores
        total_score = sum(scores.values()) if scores else 1
        normalized_scores = {
            doc_type: score / total_score 
            for doc_type, score in scores.items()
        }
        
        # Get best match
        if normalized_scores:
            best_type = max(normalized_scores, key=normalized_scores.get)
            confidence = normalized_scores[best_type]
        else:
            best_type = DocumentType.OTHER
            confidence = 0.1
        
        # Get alternative types
        alternatives = [
            {"type": doc_type.value, "confidence": score}
            for doc_type, score in sorted(
                normalized_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[1:4]  # Top 3 alternatives
        ]
        
        return ClassificationResult(
            document_id="",
            document_type=best_type,
            confidence=confidence,
            alternative_types=alternatives
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "document-processing-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/process/extract/{document_id}", response_model=ExtractedData)
async def extract_document_data(document_id: str):
    """Extract structured data from a document."""
    try:
        # Get OCR text from document
        ocr_response = requests.post(
            f"{OCR_SERVICE_URL}/ocr/process/{document_id}",
            json={"document_id": document_id}
        )
        
        if ocr_response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f"Could not process document {document_id}"
            )
        
        ocr_data = ocr_response.json()
        text = ocr_data.get("extracted_text", "")
        
        # Extract fields
        extractor = FieldExtractor()
        extracted_fields = {
            "dates": extractor.extract_dates(text),
            "amounts": extractor.extract_amounts(text),
            "policy_number": extractor.extract_policy_number(text),
            "patient_info": extractor.extract_patient_info(text),
            "provider_info": extractor.extract_provider_info(text),
            "diagnosis_codes": extractor.extract_diagnosis_codes(text),
            "prescriptions": extractor.extract_prescription_info(text),
        }
        
        # Classify document
        classifier = DocumentClassifier()
        classification = classifier.classify(text)
        
        # Calculate overall confidence
        field_count = sum(
            1 for v in extracted_fields.values() 
            if v and (not isinstance(v, list) or len(v) > 0)
        )
        confidence = min(0.95, field_count * 0.15)
        
        result = ExtractedData(
            document_id=document_id,
            document_type=classification.document_type,
            extracted_fields=extracted_fields,
            confidence=confidence,
            extraction_timestamp=datetime.utcnow()
        )
        
        # Update document status
        requests.put(
            f"{DOCUMENT_SERVICE_URL}/documents/{document_id}/status",
            params={
                "status": "processed",
                "classification": classification.document_type.value
            }
        )
        
        return result
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service communication error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@app.post("/process/classify", response_model=ClassificationResult)
async def classify_text(text: str, document_id: Optional[str] = None):
    """Classify document based on text content."""
    classifier = DocumentClassifier()
    result = classifier.classify(text)
    
    if document_id:
        result.document_id = document_id
    
    return result


@app.post("/process/validate/{document_id}")
async def validate_document(document_id: str, document_type: DocumentType):
    """Validate if a document has required fields for its type."""
    try:
        # Get extracted data
        extraction = await extract_document_data(document_id)
        
        # Define required fields per document type
        required_fields = {
            DocumentType.INVOICE: ["amounts", "dates"],
            DocumentType.PRESCRIPTION: ["prescriptions", "provider_info"],
            DocumentType.MEDICAL_REPORT: ["diagnosis_codes", "patient_info", "provider_info"],
            DocumentType.LAB_RESULTS: ["patient_info", "dates"],
            DocumentType.CLAIM_FORM: ["policy_number", "amounts", "patient_info"],
        }
        
        # Check required fields
        required = required_fields.get(document_type, [])
        missing_fields = []
        
        for field in required:
            value = extraction.extracted_fields.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        completeness = 1 - (len(missing_fields) / len(required)) if required else 1
        
        return {
            "document_id": document_id,
            "document_type": document_type,
            "is_valid": is_valid,
            "completeness": completeness,
            "missing_fields": missing_fields,
            "extracted_fields": list(extraction.extracted_fields.keys())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@app.post("/process/batch")
async def batch_process(document_ids: List[str]):
    """Process multiple documents in batch."""
    results = []
    
    for doc_id in document_ids:
        try:
            result = await extract_document_data(doc_id)
            results.append({
                "document_id": doc_id,
                "status": "success",
                "data": result.dict()
            })
        except Exception as e:
            results.append({
                "document_id": doc_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "processed": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


@app.get("/process/supported-types")
async def get_supported_document_types():
    """Get list of supported document types."""
    return {
        "types": [
            {
                "value": doc_type.value,
                "name": doc_type.value.replace("_", " ").title()
            }
            for doc_type in DocumentType
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)