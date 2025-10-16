# 🏥 Insurance Claim Agent

> AI-powered insurance claim processing system with automated document extraction, policy matching, and settlement calculation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🚀 Core Capabilities
- **📄 Intelligent Document Processing** - Extract claim data from PDFs using AI (Groq/Gemini/OpenAI)
- **🔍 Policy Management** - Upload and index multiple policy documents with auto-generation
- **🤖 RAG-Based Analysis** - Match claims against policy terms using vector search (Pinecone)
- **💰 Automated Calculations** - Calculate reimbursements with deductibles, coverage rates, and limits
- **⚡ Real-Time Processing** - Watch your claim flow through the pipeline with live animations
- **🌐 Modern Web UI** - Clean, responsive interface for seamless interaction

### 🎯 Smart Features
- **Batch Upload**: Upload multiple PDFs per policy (e.g., base contract + supplements)
- **Auto-Generation**: Policy ID and name auto-generated from filenames if not provided
- **Multi-File Support**: Merge multiple policy documents under single policy ID
- **Memory-Safe**: Streaming file uploads (1MB chunks) to handle large documents
- **Free-Tier Friendly**: Works with free APIs (Groq, Gemini) and local embeddings

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API Keys (at least one):
  - [Groq](https://console.groq.com/) (Recommended - Fast & Free)
  - [Gemini](https://ai.google.dev/) (Alternative - Free tier)
  - [OpenAI](https://platform.openai.com/) (Premium option)
  - [Pinecone](https://www.pinecone.io/) (For vector storage)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/insurance-claim-agent.git
cd insurance-claim-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**

Create a `.env` file in the root directory:

```env
# Required: At least one LLM API
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
# Or
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxx
# Or
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Required: Vector database
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=insurance-policies

# Optional: Embedding strategy
EMBEDDING_STRATEGY=local  # or 'gemini', 'openai'
```

4. **Run the application**

```bash
# Windows
py run.py

# Linux/Mac
python3 run.py
```

5. **Access the application**

- 🌐 **Frontend**: Open `frontend/index.html` in your browser
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
insurance-claim-agent/
├── backend/
│   ├── api.py                    # 🚀 FastAPI endpoints
│   ├── config.py                 # ⚙️ Configuration & environment
│   ├── models.py                 # 📋 Pydantic models
│   └── processors/
│       ├── document.py           # 📄 PDF extraction & OCR
│       ├── policy.py             # 🔍 Policy indexing (RAG)
│       └── claim.py              # 💰 Claim analysis & calculation
├── frontend/
│   ├── index.html               # 🌐 Main UI
│   ├── app.js                   # ⚡ Frontend logic
│   └── styles.css               # 🎨 Styling
├── data/
│   └── samples/                 # 📑 Sample documents
├── .env                         # 🔐 API keys (create this)
├── requirements.txt             # 📦 Dependencies
├── run.py                       # ▶️ Application entry point
└── README.md                    # 📖 You are here
```

## 🔧 How It Works

### The Processing Pipeline

```mermaid
graph LR
    A[Upload Claim PDF] --> B[Extract Data AI]
    B --> C[Match Policy RAG]
    C --> D[Calculate Settlement]
    D --> E[Return Result]
```

### Policy Indexing Flow

1. **Upload PDFs** → Multiple files supported per policy
2. **Extract Text** → Parse PDF pages with PyPDF2
3. **Segment Sections** → Identify coverage, exclusions, terms
4. **Chunk Text** → Split into 512-char chunks with overlap
5. **Generate Embeddings** → Convert to 384-dim vectors (free local model)
6. **Store in Pinecone** → Vector database for semantic search

### Claim Analysis Flow

1. **Document Upload** → User submits claim PDF
2. **AI Extraction** → Groq/Gemini extracts structured data
3. **Policy Search** → RAG retrieves relevant policy sections
4. **Coverage Analysis** → LLM interprets policy terms
5. **Calculation** → Apply coverage rate, deductible, limits
6. **Result** → Detailed justification with line-by-line breakdown

## 📡 API Endpoints

### System
- `GET /` - Welcome message
- `GET /health` - Health check with service status
- `GET /status` - Detailed system capabilities

### Policy Management
- `POST /api/policies/index` - Upload & index policy documents
  - Supports multiple files
  - Auto-generates policy_id and policy_name
  - Streaming file upload
- `GET /api/policies` - List all indexed policies
- `DELETE /api/policies/{policy_id}` - Delete policy from index

### Document Processing
- `POST /api/documents/extract` - Extract claim data from PDF
  - Returns structured JSON with claim items
  - Confidence scores included

### Claim Analysis
- `POST /api/claims/analyze/{claim_id}` - Analyze claim against policy
  - Returns approval status and settlement amount
  - Detailed justification with policy references
  - Handles deductibles and coverage limits

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Pinecone** - Vector database for semantic search
- **Sentence Transformers** - Free local embeddings
- **PyPDF2** - PDF text extraction
- **Pydantic** - Data validation

### AI/LLM
- **Groq** - Fast inference (Mixtral/Llama)
- **Google Gemini** - Multimodal AI with generous free tier
- **OpenAI** - GPT-4 (premium option)

### Frontend
- **Vanilla JavaScript** - No framework bloat
- **Modern CSS** - Responsive design with animations
- **Font Awesome** - Icon library

## 💡 Key Features Explained

### 1. Batch Policy Upload
Upload multiple PDFs (e.g., base contract + supplements) under one policy:
```
Input: ["contract.pdf", "supplement.pdf", "schedule.pdf"]
Output: All indexed under "MEDICARE_PREMIUM_2025"
Benefit: Search across all documents at once
```

### 2. Auto-Generation
No manual data entry needed:
```
File: "dental_perplexity.pdf"
→ Policy Name: "Dental Perplexity" (auto-extracted)
→ Policy ID: "DENTAL_PERPLEXITY_2025" (auto-generated)
```

### 3. Memory-Safe Upload
Handles large files without crashes:
```python
while chunk := await file.read(1024 * 1024):  # 1MB chunks
    tmp_file.write(chunk)
```

### 4. Free-Tier Optimization
- **Embeddings**: Local Sentence Transformers (100% free)
- **LLM**: Groq free tier (fast Mixtral model)
- **Vector DB**: Pinecone free tier (100K vectors)
- **Cost**: $0/month for moderate usage

## 🎬 Usage Example

### 1. Upload a Policy
1. Navigate to "Policies" section
2. Select one or more PDF files
3. Optionally provide policy name/ID (or leave empty for auto-generation)
4. Click "Upload & Index Policy"
5. Watch the processing animation

### 2. Submit a Claim
1. Go to "Live Demo" section
2. Select the policy to analyze against
3. Choose claim type (outpatient, inpatient, dental, pharmacy)
4. Enter amount
5. Upload claim document (receipt, invoice, etc.)
6. Watch AI process in real-time:
   - Document Received ✓
   - OCR Processing ✓
   - AI Analysis ✓
   - Settlement ✓
7. View detailed results with justification

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Connection refused"** | Start backend: `py run.py` |
| **"[object Object]" error** | Clear browser cache, refresh page |
| **Port already in use** | Kill process on port 8000 or change port in config |
| **Slow processing** | Switch to Groq (fastest) in `.env` |
| **No policies showing** | Check Pinecone API key and index name |

## 🚀 Deployment

### Docker (Recommended)
```bash
docker build -t insurance-claim-agent .
docker run -p 8000:8000 --env-file .env insurance-claim-agent
```

### Cloud Platforms
- **Railway**: `railway up`
- **Heroku**: `git push heroku main`
- **Vercel**: Deploy via GitHub integration

### Production Considerations
- Add authentication (JWT/OAuth)
- Use PostgreSQL for claim history
- Add Redis for caching
- Enable HTTPS
- Set up monitoring (Prometheus/Grafana)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Built for Hallesche Insurance demonstration
- Powered by Groq, Gemini, and Pinecone
- Inspired by modern claims processing workflows

---

**Made with ❤️ for intelligent insurance processing**
