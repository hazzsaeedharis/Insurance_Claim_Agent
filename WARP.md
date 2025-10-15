# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Development
- **Start server**: `py run.py` (main entry point with startup checks and banner)
- **Start with auto-open**: `py run.py --open` (opens API docs in browser)
- **Direct FastAPI**: `uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload`

### Dependencies
- **Install**: `pip install -r requirements.txt`
- **Test basic import**: `py test.py` (imports backend.api module)

### API Endpoints
- **Health check**: `GET /health` 
- **API docs**: `GET /docs`
- **Frontend**: Open `frontend/index.html` in browser

### Environment Setup
Create `.env` file with at least one AI service:
```
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # optional
GEMINI_API_KEY=your_key_here  # optional  
PINECONE_API_KEY=your_key_here  # optional for policy indexing
```

## Architecture

### Core Processing Pipeline
The system follows a 3-stage AI processing pipeline:

1. **Document Extraction** (`backend/processors/document.py`)
   - OCR + AI extraction of medical invoices, prescriptions, reports
   - Uses Tesseract OCR with German+English support
   - AI models prioritize: Gemini > OpenAI > Groq
   - Returns structured JSON with confidence scores

2. **Policy Matching** (`backend/processors/policy.py`) 
   - RAG-based policy document indexing with Pinecone vector DB
   - Chunks policy PDFs into searchable sections
   - Local embeddings (sentence-transformers) as default (free)
   - Supports Gemini/OpenAI embeddings for premium accuracy

3. **Claim Analysis** (`backend/processors/claim.py`)
   - Matches extracted claims against policy coverage
   - Calculates reimbursements with deductibles and limits
   - Generates detailed justifications and warnings

### AI Service Configuration
Services are prioritized by quality and cost:
- **Primary**: Gemini (gemini-1.5-flash) - best multilingual support
- **Fallback**: OpenAI (gpt-4) - premium accuracy 
- **Default**: Groq (llama-3.3-70b-versatile) - fast and free

### Data Models (`backend/models.py`)
All request/response models use Pydantic with clear field validation:
- PolicyIndexRequest/Response
- DocumentExtractRequest/Response  
- ClaimAnalysisRequest/Response
- Internal models: ExtractedService, PolicyMatch, ReimbursementCalculation

### Configuration (`backend/config.py`)
Centralized settings with environment variable loading:
- AI model selection and API keys
- Document processing limits and file types
- Vector DB configuration (Pinecone settings)
- Medical code patterns (GOÄ, ICD, PZN, OPS)

### Frontend Integration
JavaScript frontend (`frontend/app.js`) connects to FastAPI backend:
- Real-time claim processing with pipeline visualization
- Detailed justification display with confidence scores
- System health monitoring via `/health` endpoint

## File Processing
- **Supported formats**: PDF, PNG, JPG, JPEG, TIFF
- **Max file size**: 10MB (configurable)
- **OCR languages**: German + English
- **Medical codes**: Automatic detection of GOÄ, ICD-10, PZN codes

## Vector Database
- **Default**: Pinecone with cosine similarity
- **Index**: insurance-policies (384-dim for sentence transformers)
- **Chunking**: 1000 chars with 200 char overlap
- **Local fallback**: sentence-transformers (all-MiniLM-L6-v2)

## Testing
The system includes basic module import testing. For claim processing:
1. Start server: `python run.py`
2. Upload test document via frontend or API
3. Check `/health` endpoint for service status
4. Use `/docs` for interactive API testing

## Error Handling
- Graceful fallbacks when AI services are unavailable
- Comprehensive validation with helpful error messages
- Default coverage rules when policy matching fails
- File cleanup for temporary document uploads

## Development Notes
- Clean code principles: single responsibility, clear naming, no duplication
- All processors can work with any of the three AI services
- In-memory cache for demo (would use database in production)
- CORS enabled for frontend development
- Comprehensive logging throughout the system