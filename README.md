# Insurance Claim Processing System

AI-powered document processing and claim analysis system for insurance companies.

## Features

- 📄 **Document Extraction** - Extract data from PDFs and images using OCR + AI
- 🤖 **AI Analysis** - Intelligent claim processing using Groq/OpenAI/Gemini
- 📊 **Policy Matching** - RAG-based policy coverage verification
- 💰 **Auto Calculation** - Transparent reimbursement calculations
- 🌐 **Web Interface** - Clean, modern UI for easy interaction

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Keys

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_key_here
# Optional:
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
```

### 3. Run Application

```bash
# On Windows:
py run.py

# On Linux/Mac:
python run.py
```

### 4. Access

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: Open `frontend/index.html` in browser

> **Note**: The backend runs on port 8000 and the frontend connects to it automatically.

## Project Structure

```
insurance-claim-agent/
├── backend/
│   ├── api.py               # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Data models
│   └── processors/          # Core business logic
│       ├── document.py      # Document extraction
│       ├── policy.py        # Policy indexing
│       └── claim.py         # Claim analysis
├── frontend/
│   ├── index.html          # Web interface
│   ├── app.js              # Frontend logic
│   └── styles.css          # Styling
├── data/
│   └── samples/            # Sample documents
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── run.py                  # Entry point
```

## API Endpoints

### Health Check
- `GET /health` - System status

### Policy Management
- `POST /api/policies/index` - Index policy document
- `GET /api/policies/{id}/search` - Search policy

### Document Processing
- `POST /api/documents/extract` - Extract claim data

### Claim Analysis
- `POST /api/claims/analyze/{id}` - Analyze claim

## Clean Code Principles

This project follows:
- **Single Responsibility** - Each module has one clear purpose
- **DRY** - No code duplication
- **Clear Naming** - Self-documenting code
- **Minimal Dependencies** - Only essential packages
- **Simple Structure** - Maximum 3 levels deep

## Requirements

- Python 3.8+
- At least one AI API key (Groq/OpenAI/Gemini)
- Optional: Tesseract OCR for document processing
- Optional: Pinecone API key for policy indexing

## Troubleshooting

### Frontend shows "404 Not Found"
- Ensure the backend is running: `py run.py`
- Check the API is accessible: http://localhost:8000/health
- Verify frontend is using port 8000 (check browser console)

### "€0.00 claimed, €0.00 approved"
- This usually indicates the AI extraction format doesn't match expectations
- The system automatically normalizes Groq response keys (Title Case → snake_case)
- Check backend logs for extraction details

### Port Already in Use
- Stop any existing instances: `Ctrl+C` in the terminal
- Or change the port in `backend/config.py` (default: 8000)

### AI Service Not Responding
- Verify your API key is set in `.env`
- Check you have internet connectivity
- Groq/OpenAI/Gemini may have rate limits - wait a moment and retry

## Known Issues

- **Groq Response Format**: Groq sometimes returns inconsistent JSON key formats (Title Case vs snake_case). The system handles this automatically via key normalization.
- **OCR Dependencies**: Tesseract must be installed separately for image-based PDFs

## License

MIT
