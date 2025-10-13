"""
Document Processor for Claims
Extracts information from uploaded claim documents using AI
"""

import os
import re
import json
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from groq import Groq
import openai
import google.generativeai as genai
import pytesseract
from PIL import Image
import pdf2image
import io

from services.ai_document_processor.config import (
    ai_config, 
    DOCUMENT_TYPES, 
    EXTRACTION_PROMPTS,
    MEDICAL_CODE_PATTERNS
)

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes claim documents to extract structured information"""
    
    def __init__(self):
        """Initialize the document processor"""
        # Initialize Groq client
        self.groq_client = Groq(api_key=ai_config.groq_api_key) if ai_config.groq_api_key else None
        
        # Initialize Gemini if available (priority)
        if ai_config.gemini_api_key:
            genai.configure(api_key=ai_config.gemini_api_key)
            self.use_gemini = True
            self.use_openai = False
            logger.info("Using Gemini API for document processing")
        # Initialize OpenAI if available
        elif ai_config.openai_api_key:
            openai.api_key = ai_config.openai_api_key
            self.use_openai = True
            self.use_gemini = False
            logger.info("Using OpenAI API for document processing")
        else:
            self.use_openai = False
            self.use_gemini = False
            logger.info("Using Groq for document processing")
    
    def process_document(self, file_path: str, hints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for document processing
        
        Args:
            file_path: Path to the document file
            hints: Optional hints about document type or expected content
            
        Returns:
            Extracted and validated information
        """
        logger.info(f"Processing document: {file_path}")
        
        # Extract text from document
        text, images = self._extract_text_from_document(file_path)
        
        if not text and not images:
            raise ValueError("No text or images could be extracted from document")
        
        # Classify document type
        doc_type = self._classify_document(text, hints)
        logger.info(f"Document classified as: {doc_type}")
        
        # Extract information based on document type
        extracted_data = self._extract_information(text, doc_type, images)
        
        # Validate and enrich extracted data
        validated_data = self._validate_and_enrich(extracted_data, doc_type)
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(extracted_data, validated_data)
        
        return {
            "document_type": doc_type,
            "extracted_data": validated_data,
            "confidence_scores": confidence_scores,
            "raw_text_length": len(text),
            "processing_timestamp": datetime.utcnow().isoformat(),
            "warnings": self._generate_warnings(validated_data, doc_type)
        }
    
    def _extract_text_from_document(self, file_path: str) -> Tuple[str, List[Image.Image]]:
        """Extract text and images from various document formats"""
        text = ""
        images = []
        
        if file_path.lower().endswith('.pdf'):
            # Convert PDF to images first
            try:
                pdf_images = pdf2image.convert_from_path(file_path)
                images.extend(pdf_images)
                
                # Extract text from each page
                for img in pdf_images:
                    page_text = pytesseract.image_to_string(img, lang='deu+eng')
                    text += page_text + "\n\n"
                    
            except Exception as e:
                logger.error(f"Error processing PDF: {e}")
                raise
                
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            # Direct image processing
            try:
                img = Image.open(file_path)
                images.append(img)
                text = pytesseract.image_to_string(img, lang='deu+eng')
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                raise
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        return text.strip(), images
    
    def _classify_document(self, text: str, hints: Optional[Dict[str, Any]] = None) -> str:
        """Classify document type using AI or rules"""
        
        # If hint provided, validate it
        if hints and "document_type" in hints:
            if hints["document_type"] in DOCUMENT_TYPES:
                return hints["document_type"]
        
        # First try rule-based classification
        text_lower = text.lower()
        for doc_type, config in DOCUMENT_TYPES.items():
            keyword_matches = sum(1 for keyword in config["keywords"] if keyword in text_lower)
            if keyword_matches >= 2:  # At least 2 keyword matches
                return doc_type
        
        # Use AI for classification if rules don't work
        prompt = f"""
        Classify this document into one of these categories:
        {', '.join(DOCUMENT_TYPES.keys())}
        
        Document text (first 1000 characters):
        {text[:1000]}
        
        Return only the category name, nothing else.
        """
        
        try:
            if self.use_gemini:
                model = genai.GenerativeModel('gemini-1.5-flash')  # Fast model for classification
                response = model.generate_content(
                    f"You are a document classifier. Return only the document type.\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(temperature=0)
                )
                doc_type = response.text.strip().lower().replace(" ", "_")
            elif self.use_openai:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Cheaper model for classification
                    messages=[
                        {"role": "system", "content": "You are a document classifier. Return only the document type."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    max_tokens=50
                )
                doc_type = response.choices[0].message.content.strip().lower().replace(" ", "_")
            else:
                response = self.groq_client.chat.completions.create(
                    model=ai_config.groq_model,
                    messages=[
                        {"role": "system", "content": "You are a document classifier. Return only the document type."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    max_tokens=50
                )
                doc_type = response.choices[0].message.content.strip().lower().replace(" ", "_")
            
            # Validate response
            if doc_type in DOCUMENT_TYPES:
                return doc_type
            else:
                logger.warning(f"AI returned invalid document type: {doc_type}")
                return "medical_invoice"  # Default fallback
                
        except Exception as e:
            logger.error(f"Error in AI classification: {e}")
            return "medical_invoice"  # Default fallback
    
    def _extract_information(self, text: str, doc_type: str, images: List[Image.Image]) -> Dict[str, Any]:
        """Extract structured information from document"""
        
        # Get appropriate prompt for document type
        extraction_prompt = EXTRACTION_PROMPTS.get(doc_type, EXTRACTION_PROMPTS["medical_invoice"])
        
        # Add the actual document text to prompt
        full_prompt = f"""
        {extraction_prompt}
        
        Document text:
        {text[:3000]}  # Limit to prevent token overflow
        
        Important: Return valid JSON only. Include all amounts in EUR.
        """
        
        try:
            if self.use_gemini:
                # Use Gemini Pro for best extraction accuracy
                model = genai.GenerativeModel(ai_config.gemini_llm_model)
                response = model.generate_content(
                    f"You are a medical document data extractor. Extract information precisely and return valid JSON only.\n\n{full_prompt}",
                    generation_config=genai.types.GenerationConfig(temperature=0.1)
                )
                # Extract JSON from response
                content = response.text
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    extracted = json.loads(json_match.group())
                else:
                    extracted = json.loads(content)
            elif self.use_openai:
                # Use GPT-4 for best extraction accuracy
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a medical document data extractor. Extract information precisely and return valid JSON."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                extracted = json.loads(response.choices[0].message.content)
            else:
                # Use Groq as fallback
                response = self.groq_client.chat.completions.create(
                    model=ai_config.groq_model,
                    messages=[
                        {"role": "system", "content": "You are a medical document data extractor. Extract information precisely and return valid JSON only."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                # Groq might return markdown, so extract JSON
                content = response.choices[0].message.content
                # Try to extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    extracted = json.loads(json_match.group())
                else:
                    extracted = json.loads(content)
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            # Return minimal structure
            return {
                "error": str(e),
                "partial_extraction": self._fallback_extraction(text, doc_type)
            }
    
    def _fallback_extraction(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Fallback extraction using regex patterns"""
        extracted = {}
        
        # Extract amounts
        amount_pattern = r'€\s*(\d+[.,]\d{2})'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            extracted["amounts_found"] = [float(a.replace(',', '.')) for a in amounts]
            extracted["total_amount"] = max(extracted["amounts_found"])
        
        # Extract dates
        date_pattern = r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})'
        dates = re.findall(date_pattern, text)
        if dates:
            extracted["dates_found"] = dates
        
        # Extract medical codes
        for code_type, pattern in MEDICAL_CODE_PATTERNS.items():
            codes = re.findall(pattern, text)
            if codes:
                extracted[f"{code_type}_codes"] = codes
        
        return extracted
    
    def _validate_and_enrich(self, extracted_data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Validate extracted data and enrich with additional information"""
        validated = extracted_data.copy()
        
        # Validate required fields
        required_fields = DOCUMENT_TYPES[doc_type]["required_fields"]
        validated["missing_fields"] = []
        
        for field in required_fields:
            if field not in validated or not validated.get(field):
                validated["missing_fields"].append(field)
        
        # Validate and standardize medical codes
        if "services" in validated:
            for service in validated.get("services", []):
                if "code" in service:
                    service["code_type"] = self._identify_code_type(service["code"])
                    service["code_valid"] = self._validate_medical_code(
                        service["code"], 
                        service.get("code_type")
                    )
        
        # Standardize dates
        validated = self._standardize_dates(validated)
        
        # Calculate totals if line items exist
        if "services" in validated and isinstance(validated["services"], list):
            calculated_total = sum(
                float(item.get("total_price", 0)) 
                for item in validated["services"]
            )
            validated["calculated_total"] = round(calculated_total, 2)
        
        return validated
    
    def _identify_code_type(self, code: str) -> Optional[str]:
        """Identify medical code type"""
        for code_type, pattern in MEDICAL_CODE_PATTERNS.items():
            if re.match(pattern, code):
                return code_type
        return None
    
    def _validate_medical_code(self, code: str, code_type: Optional[str]) -> bool:
        """Validate medical code format"""
        if not code_type:
            return False
        
        pattern = MEDICAL_CODE_PATTERNS.get(code_type)
        if pattern:
            return bool(re.match(f"^{pattern}$", code))
        
        return False
    
    def _standardize_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize date formats to ISO format"""
        date_pattern = r'(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})'
        
        def convert_date(date_str: str) -> str:
            match = re.match(date_pattern, date_str)
            if match:
                day, month, year = match.groups()
                if len(year) == 2:
                    year = "20" + year
                try:
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime("%Y-%m-%d")
                except:
                    pass
            return date_str
        
        # Recursively process the data structure
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and re.match(date_pattern, value):
                    data[key] = convert_date(value)
                elif isinstance(value, (dict, list)):
                    data[key] = self._standardize_dates(value)
        elif isinstance(data, list):
            return [self._standardize_dates(item) for item in data]
        
        return data
    
    def _calculate_confidence_scores(self, extracted: Dict[str, Any], validated: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for extracted data"""
        scores = {}
        
        # Overall extraction confidence
        if "error" in extracted:
            scores["overall"] = 0.3
        else:
            # Base score on field completeness
            total_fields = len(validated.keys())
            missing_fields = len(validated.get("missing_fields", []))
            scores["overall"] = max(0.5, 1.0 - (missing_fields / max(total_fields, 1)))
        
        # Document type confidence
        scores["document_type"] = 0.9 if not extracted.get("error") else 0.5
        
        # Amount confidence (if amounts match)
        if "total_amount" in validated and "calculated_total" in validated:
            if abs(validated["total_amount"] - validated["calculated_total"]) < 0.01:
                scores["amount"] = 1.0
            else:
                scores["amount"] = 0.7
        else:
            scores["amount"] = 0.5
        
        # Code validation confidence
        if "services" in validated:
            valid_codes = sum(
                1 for s in validated["services"] 
                if s.get("code_valid", False)
            )
            total_codes = len(validated["services"])
            scores["medical_codes"] = valid_codes / max(total_codes, 1)
        
        return scores
    
    def _generate_warnings(self, data: Dict[str, Any], doc_type: str) -> List[str]:
        """Generate warnings for potential issues"""
        warnings = []
        
        # Check for missing required fields
        if data.get("missing_fields"):
            warnings.append(f"Missing required fields: {', '.join(data['missing_fields'])}")
        
        # Check for amount mismatches
        if "total_amount" in data and "calculated_total" in data:
            diff = abs(data["total_amount"] - data["calculated_total"])
            if diff > 0.01:
                warnings.append(f"Amount mismatch: stated €{data['total_amount']}, calculated €{data['calculated_total']}")
        
        # Check for invalid medical codes
        if "services" in data:
            invalid_codes = [
                s.get("code", "unknown") 
                for s in data["services"] 
                if not s.get("code_valid", True)
            ]
            if invalid_codes:
                warnings.append(f"Invalid medical codes found: {', '.join(invalid_codes[:3])}")
        
        # Check for future dates
        today = datetime.now().date()
        for key, value in data.items():
            if isinstance(value, str) and re.match(r'\d{4}-\d{2}-\d{2}', value):
                try:
                    date_obj = datetime.strptime(value, "%Y-%m-%d").date()
                    if date_obj > today:
                        warnings.append(f"Future date found in {key}: {value}")
                except:
                    pass
        
        return warnings


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = DocumentProcessor()
    
    # Process a sample document
    result = processor.process_document(
        file_path="data/samples/documents/hallesche_valid_outpatient.pdf",
        hints={"document_type": "medical_invoice"}
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
