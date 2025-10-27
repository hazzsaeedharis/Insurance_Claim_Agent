# 🏥 Insurance Claim Agent

> AI-powered insurance claim processing system with automated document extraction, policy matching, and settlement calculation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🚀 Core Capabilities
- **🔐 Secure Authentication** - JWT tokens with Google OAuth2 and email/password login
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
- PostgreSQL 12+ (for user authentication)
- API Keys (at least one):
  - [Groq](https://console.groq.com/) (Recommended - Fast & Free)
  - [Gemini](https://ai.google.dev/) (Alternative - Free tier)
  - [OpenAI](https://platform.openai.com/) (Premium option)
  - [Pinecone](https://www.pinecone.io/) (For vector storage)
- Google OAuth2 Credentials (optional, for Google login):
  - [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

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

3. **Setup PostgreSQL Database**

```bash
# Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
psql -U postgres
CREATE DATABASE insurance_claims;
\q
```

4. **Configure environment**

Copy `env.example` to `.env` and fill in your values:

```bash
cp env.example .env
```

Edit `.env` with your API keys:

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

# Required: Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/insurance_claims

# Required: JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your_generated_secret_key_here

# Optional: Google OAuth2 (for Google login)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Optional: Embedding strategy
EMBEDDING_STRATEGY=local  # or 'gemini', 'openai'
```

**Setting up Google OAuth2 (Optional):**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
7. Copy Client ID and Client Secret to `.env`

5. **Run the application**

```bash
# Windows
py run.py

# Linux/Mac
python3 run.py
```

The application will:
- Initialize the PostgreSQL database (create tables automatically)
- Start the FastAPI server on port 8000
- Display API status and configuration

6. **Access the application**

- 🌐 **Frontend**: Open `frontend/index.html` in your browser
- 🔐 **Login**: http://localhost:8000/frontend/auth.html (or click "Login" in nav)
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health

7. **Create your first account**

- Click "Login" in the navigation bar
- Switch to "Register" tab
- Fill in your details (or use Google OAuth)
- Login and start processing claims!

## 📁 Project Structure

```
insurance-claim-agent/
├── backend/
│   ├── api.py                    # 🚀 FastAPI endpoints
│   ├── config.py                 # ⚙️ Configuration & environment
│   ├── models.py                 # 📋 Pydantic request/response models
│   ├── database.py               # 🗄️ Database connection & session
│   ├── auth/                     # 🔐 Authentication
│   │   ├── jwt.py                # JWT token management
│   │   ├── password.py           # Password hashing
│   │   └── oauth.py              # Google OAuth2
│   ├── models/                   # 📊 Database models
│   │   ├── user.py               # User model
│   │   └── refresh_token.py     # Refresh token model
│   ├── routers/                  # 🛣️ API routers
│   │   └── auth.py               # Authentication endpoints
│   └── processors/
│       ├── document.py           # 📄 PDF extraction & OCR
│       ├── policy.py             # 🔍 Policy indexing (RAG)
│       └── claim.py              # 💰 Claim analysis & calculation
├── frontend/
│   ├── index.html               # 🌐 Main UI
│   ├── auth.html                # 🔐 Login/Register page
│   ├── auth-callback.html       # 🔄 OAuth callback handler
│   ├── app.js                   # ⚡ Frontend logic
│   ├── auth.js                  # 🔑 Authentication logic
│   └── styles.css               # 🎨 Styling
├── data/
│   └── samples/                 # 📑 Sample documents
├── .env                         # 🔐 API keys (create this)
├── env.example                  # 📝 Environment template
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

### Authentication 🔐
- `POST /auth/register` - Register new user with email/password
- `POST /auth/login` - Login with email/password (returns JWT tokens)
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke refresh token
- `GET /auth/me` - Get current user information (protected)
- `GET /auth/google/login` - Redirect to Google OAuth
- `GET /auth/google/callback` - Handle Google OAuth callback

### System (Public)
- `GET /` - Welcome message
- `GET /health` - Health check with service status
- `GET /status` - Detailed system capabilities

### Policy Management (Protected 🔒)
- `POST /api/policies/index` - Upload & index policy documents
  - Supports multiple files
  - Auto-generates policy_id and policy_name
  - Streaming file upload
  - **Requires authentication**
- `GET /api/policies` - List all indexed policies **🔒**
- `DELETE /api/policies/{policy_id}` - Delete policy from index **🔒**
- `PATCH /api/policies/{policy_id}/rename` - Rename policy **🔒**
- `GET /api/policies/{policy_id}/search` - Search within policy **🔒**

### Document Processing (Protected 🔒)
- `POST /api/documents/extract` - Extract claim data from PDF **🔒**
  - Returns structured JSON with claim items
  - Confidence scores included

### Claim Analysis (Protected 🔒)
- `POST /api/claims/analyze/{claim_id}` - Analyze claim against policy **🔒**
  - Returns approval status and settlement amount
  - Detailed justification with policy references
  - Handles deductibles and coverage limits
- `GET /api/claims/cache` - Get cached claim extractions **🔒**
- `DELETE /api/claims/cache/{claim_id}` - Clear claim cache **🔒**

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **PostgreSQL** - Relational database for user management
- **SQLAlchemy** - ORM for database operations
- **Pinecone** - Vector database for semantic search
- **Sentence Transformers** - Free local embeddings
- **PyPDF2** - PDF text extraction
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **pwdlib** - Password hashing with Argon2
- **authlib** - OAuth2 client library

### AI/LLM
- **Groq** - Fast inference (Mixtral/Llama)
- **Google Gemini** - Multimodal AI with generous free tier
- **OpenAI** - GPT-4 (premium option)

### Frontend
- **Vanilla JavaScript** - No framework bloat
- **Modern CSS** - Responsive design with animations
- **Font Awesome** - Icon library

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure access tokens with 15-minute expiry
- **Refresh Tokens**: Long-lived tokens (7 days) stored in httpOnly cookies
- **Password Security**: Argon2 hashing (OWASP recommended)
- **Google OAuth2**: Single sign-on with Google accounts
- **Token Refresh**: Automatic token renewal before expiry
- **Session Management**: Database-backed refresh token storage with revocation

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### API Security
- All claim processing endpoints require authentication
- CORS configured for specific origins only
- Rate limiting on authentication endpoints (planned)
- XSS prevention in user inputs
- CSRF protection in OAuth flow

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
