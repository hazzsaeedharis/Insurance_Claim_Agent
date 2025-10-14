"""OCR Service for document text extraction."""

import os
import io
import base64
from typing import Optional, Dict, Any
from datetime import datetime
import tempfile

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pytesseract
from PIL import Image
import pdf2image
import requests

# Initialize FastAPI
app = FastAPI(
    title="OCR Service",
    description="Optical Character Recognition service for document processing",
    version="1.0.0"
)

# OCR configuration
TESSERACT_LANGUAGES = ["eng", "deu"]  # English and German
DOCUMENT_SERVICE_URL = "http://localhost:8002"


class OCRRequest(BaseModel):
    """OCR processing request."""
    document_id: str
    language: str = "eng+deu"
    preprocess: bool = True
    output_format: str = "text"  # text, hocr, json


class OCRResponse(BaseModel):
    """OCR processing response."""
    document_id: str
    extracted_text: str
    confidence: float
    language: str
    word_count: int
    processing_time: float
    status: str


class ImagePreprocessor:
    """Image preprocessing for better OCR accuracy."""
    
    @staticmethod
    def enhance_image(image: Image.Image) -> Image.Image:
        """Enhance image for better OCR."""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    @staticmethod
    def deskew_image(image: Image.Image) -> Image.Image:
        """Deskew tilted images."""
        # Simple deskew - would use more advanced methods in production
        return image
    
    @staticmethod
    def remove_noise(image: Image.Image) -> Image.Image:
        """Remove noise from image."""
        # Simple noise removal - would use OpenCV in production
        return image


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if Tesseract is available
        version = pytesseract.get_tesseract_version()
        return {
            "status": "healthy",
            "service": "ocr-service",
            "tesseract_version": str(version),
            "supported_languages": TESSERACT_LANGUAGES,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.post("/ocr/extract", response_model=OCRResponse)
async def extract_text(file: UploadFile = File(...), language: str = "eng+deu"):
    """Extract text from uploaded file."""
    start_time = datetime.utcnow()
    
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type and process accordingly
        if file.filename.lower().endswith('.pdf'):
            text = await process_pdf(content, language)
        elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            text = await process_image(content, language)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )
        
        # Calculate metrics
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        word_count = len(text.split())
        
        # Calculate confidence (mock - would use actual OCR confidence)
        confidence = 0.95 if word_count > 10 else 0.85
        
        return OCRResponse(
            document_id=file.filename,
            extracted_text=text,
            confidence=confidence,
            language=language,
            word_count=word_count,
            processing_time=processing_time,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


@app.post("/ocr/process/{document_id}")
async def process_document(document_id: str, request: OCRRequest):
    """Process a document from the document service."""
    start_time = datetime.utcnow()
    
    try:
        # Fetch document from document service
        response = requests.get(f"{DOCUMENT_SERVICE_URL}/documents/{document_id}/download")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Process based on content type
        content_type = response.headers.get('content-type', '')
        
        if 'pdf' in content_type:
            text = await process_pdf(response.content, request.language)
        elif 'image' in content_type or any(img in content_type for img in ['png', 'jpg', 'jpeg']):
            text = await process_image(response.content, request.language)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported content type: {content_type}"
            )
        
        # Update document status with extracted text
        update_response = requests.put(
            f"{DOCUMENT_SERVICE_URL}/documents/{document_id}/status",
            params={
                "status": "ocr_completed",
                "extracted_text": text[:5000]  # Store first 5000 chars
            }
        )
        
        # Calculate metrics
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        word_count = len(text.split())
        confidence = 0.95 if word_count > 10 else 0.85
        
        return OCRResponse(
            document_id=document_id,
            extracted_text=text,
            confidence=confidence,
            language=request.language,
            word_count=word_count,
            processing_time=processing_time,
            status="success"
        )
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch document: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


async def process_pdf(content: bytes, language: str) -> str:
    """Process PDF file for text extraction."""
    extracted_text = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save PDF temporarily
        pdf_path = os.path.join(temp_dir, "temp.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(content)
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path, dpi=300)
            
            # Process each page
            for i, image in enumerate(images):
                # Preprocess image
                preprocessor = ImagePreprocessor()
                image = preprocessor.enhance_image(image)
                
                # Extract text using Tesseract
                try:
                    text = pytesseract.image_to_string(image, lang=language)
                    extracted_text.append(f"--- Page {i+1} ---\n{text}")
                except Exception as e:
                    extracted_text.append(f"--- Page {i+1} ---\n[OCR Error: {str(e)}]")
        
        except Exception as e:
            # If PDF to image fails, try direct text extraction
            import PyPDF2
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for i, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        extracted_text.append(f"--- Page {i+1} ---\n{text}")
            except:
                raise Exception(f"Failed to process PDF: {str(e)}")
    
    return "\n\n".join(extracted_text)


async def process_image(content: bytes, language: str) -> str:
    """Process image file for text extraction."""
    # Open image
    image = Image.open(io.BytesIO(content))
    
    # Preprocess image
    preprocessor = ImagePreprocessor()
    image = preprocessor.enhance_image(image)
    
    # Extract text using Tesseract
    try:
        text = pytesseract.image_to_string(image, lang=language)
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")


@app.post("/ocr/batch")
async def batch_process(document_ids: list[str]):
    """Process multiple documents in batch."""
    results = []
    
    for doc_id in document_ids:
        try:
            result = await process_document(
                doc_id,
                OCRRequest(document_id=doc_id)
            )
            results.append(result.dict())
        except Exception as e:
            results.append({
                "document_id": doc_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "processed": len(results),
        "successful": sum(1 for r in results if r.get("status") == "success"),
        "failed": sum(1 for r in results if r.get("status") == "failed"),
        "results": results
    }


@app.get("/ocr/languages")
async def get_supported_languages():
    """Get list of supported OCR languages."""
    return {
        "languages": [
            {"code": "eng", "name": "English"},
            {"code": "deu", "name": "German"},
            {"code": "eng+deu", "name": "English + German"}
        ],
        "default": "eng+deu"
    }


@app.post("/ocr/validate")
async def validate_extraction(text: str, expected_fields: list[str]):
    """Validate if extracted text contains expected fields."""
    found_fields = []
    missing_fields = []
    
    text_lower = text.lower()
    
    for field in expected_fields:
        if field.lower() in text_lower:
            found_fields.append(field)
        else:
            missing_fields.append(field)
    
    completeness = len(found_fields) / len(expected_fields) if expected_fields else 0
    
    return {
        "is_valid": completeness >= 0.8,
        "completeness": completeness,
        "found_fields": found_fields,
        "missing_fields": missing_fields
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)