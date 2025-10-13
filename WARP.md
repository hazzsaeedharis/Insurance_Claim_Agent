# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

InsureClaim AI is a production-ready, AI-powered insurance claims processing platform built with microservices architecture. It reduces claim processing time by 85% through automated document processing, AI-powered validation, and intelligent settlement calculations.

## Common Development Commands

### Environment Setup
```powershell
# Initial setup (creates virtual environment, installs dependencies)
.\setup.ps1

# Load environment variables from .env file
. .\load-env.ps1

# Setup API keys interactively
.\setup-api-keys.ps1
```

### Testing & Development
```powershell
# Test AI processing pipeline with Groq API
python test_ai_processing.py

# Test specific Groq models
.\check-groq-models.ps1

# Run all unit tests
.\test_all.ps1

# Test system integration
.\test_system.ps1

# Test individual components
python test_document_extraction.py
python test_pinecone.py
```

### Running Services

#### Individual Service Development
```powershell
# Start individual components for development
.\run-components.ps1

# Run specific service (example)
python services/ai_processing/api.py
python services/claims/api.py
```

#### Full Infrastructure
```powershell
# Start complete Docker infrastructure
.\run-docker.ps1

# Start with rebuild
.\run-docker.ps1 -Build

# Start in background
.\run-docker.ps1 -Detached

# Stop all services
.\run-docker.ps1 -Action down

# View service status
.\run-docker.ps1 -Action status

# View logs
.\run-docker.ps1 -Action logs
```

### Docker Services Access Points
When running full infrastructure, services are available at:
- **Keycloak Admin**: http://localhost:8080 (admin/admin123)
- **PostgreSQL**: localhost:5432 (insurance_admin/dev_password_123)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)
- **Redis**: localhost:6379
- **RabbitMQ Management**: http://localhost:15672 (rabbitmq/rabbitmq123)
- **Health Check**: http://localhost:8000/health
- **AI Processing API**: http://localhost:8005/docs

## High-Level Architecture

### Multi-Agent System Design
The system implements a sophisticated multi-agent architecture with specialized AI agents:

1. **Document Intake Agent**: Classifies documents and routes to specialists
2. **Medical Invoice Agent**: Extracts medical entities with specialized NER
3. **Policy Validation Agent**: Uses RAG system to validate claims against policies
4. **Fraud Detection Agent**: ML-powered fraud detection with explainable AI
5. **Settlement Calculation Agent**: Multi-step reasoning for settlement amounts

### Microservices Architecture
```
Insurance_Claim_Agent/
├── services/
│   ├── ai_processing/       # Main AI processing service (FastAPI)
│   ├── claims/             # Claims management API
│   ├── documents/          # Document storage service (MinIO)
│   ├── ocr/               # OCR processing service (Tesseract)
│   ├── processing/        # Document classification & extraction
│   └── common/            # Shared utilities (auth, logging, metrics)
├── services/ai_document_processor/  # Core AI components
│   ├── policy_indexer.py   # RAG system for policy documents
│   ├── document_processor.py # AI-powered document extraction
│   └── claim_analyzer.py   # Claim validation and settlement calculation
├── infra/                  # Infrastructure & deployment
│   ├── docker-compose.yml  # Full stack infrastructure
│   └── k8s/               # Kubernetes manifests
└── data/                   # Policy documents and samples
```

### AI/ML Stack Integration
- **LLM APIs**: Groq (primary), OpenAI, Gemini (configurable)
- **Embeddings**: Local Sentence Transformers (free) or OpenAI API
- **Vector Database**: Pinecone for policy document RAG
- **OCR**: Tesseract with PyTesseract integration
- **Document Processing**: Multi-format support (PDF, images)

### Key Design Patterns

#### RAG (Retrieval Augmented Generation)
The `PolicyIndexer` implements semantic search over policy documents:
- Chunks policy PDFs into sections
- Creates embeddings for semantic similarity
- Supports contextual claim validation

#### Agent Orchestration
The `ClaimProcessingWorkflow` coordinates multiple agents:
- State machine-based workflow management
- Parallel processing where possible
- Memory and context management between agents

#### Multi-Modal Processing
Handles various document types:
- PDF processing with pdfplumber
- Image OCR with Tesseract
- Structured data extraction with AI

## Environment Configuration

### Required Environment Variables
```env
# Core AI API (required for main functionality)
GROQ_API_KEY=your_groq_key_here

# Embedding strategy
EMBEDDING_STRATEGY=local  # or 'openai' if you have OPENAI_API_KEY

# Optional AI providers
OPENAI_API_KEY=your_openai_key  # For better embeddings
GEMINI_API_KEY=your_gemini_key  # Alternative LLM

# Vector Database (for policy RAG)
PINECONE_API_KEY=your_pinecone_key  # Optional, can use local ChromaDB
```

### Free Setup (No Credit Card Required)
The system can run completely free using:
- Groq API (free tier: 100 requests/minute)
- Local Sentence Transformers for embeddings
- Local ChromaDB instead of Pinecone
- Tesseract OCR (local processing)

## Key Components Deep Dive

### AI Document Processor (`services/ai_document_processor/`)
The core AI functionality is centralized here:

- **PolicyIndexer**: RAG system that indexes policy documents for semantic search
- **DocumentProcessor**: Extracts structured data from various document formats
- **ClaimAnalyzer**: Validates claims against policies and calculates settlements

These components use a multi-step AI approach:
1. Document classification and routing
2. OCR and text extraction
3. Entity extraction with specialized prompts
4. Policy matching with semantic search
5. Settlement calculation with business logic

### Authentication & Security (`auth/`)
Implements JWT-based authentication with role-based access control (RBAC):
- 7 predefined roles (Customer, Adjuster, Manager, etc.)
- Middleware for API endpoint protection
- Integration with Keycloak for enterprise auth

### Common Services (`services/common/`)
Shared utilities across microservices:
- **BaseService**: FastAPI service template with health checks
- **Database**: SQLAlchemy models and connections
- **Logger**: Centralized structured logging
- **Metrics**: Prometheus metrics collection

## Development Workflow

### Typical Development Session
1. **Environment Setup**: Run `.\setup.ps1` once
2. **Load Environment**: `. .\load-env.ps1` per session
3. **Test AI Pipeline**: `python test_ai_processing.py`
4. **Develop Services**: Start individual services as needed
5. **Integration Testing**: Use `.\test_system.ps1`

### Adding New Document Types
1. Extend document classification prompts in `DocumentProcessor`
2. Add specialized extraction logic for new document structure
3. Update the routing logic in `DocumentIntakeAgent`
4. Test with sample documents

### Extending AI Capabilities
1. **New Agent Types**: Follow the agent pattern in `MULTI_AGENT_ARCHITECTURE.md`
2. **Custom Models**: Configure in `services/ai_document_processor/config.py`
3. **Enhanced RAG**: Modify `PolicyIndexer` for better retrieval

## Important Notes

### PowerShell Environment
The project is optimized for Windows PowerShell development:
- PowerShell scripts auto-load `.env` files
- Python scripts use `python-dotenv` for environment variables
- Docker integration through PowerShell scripts

### Performance Characteristics
- **Processing Speed**: ~30 seconds average per claim
- **OCR Accuracy**: 95%+ for clear documents
- **Automation Rate**: 85% claims processed without human intervention
- **Concurrent Users**: 1000+ supported through microservices

### Production Deployment
The system is designed for production with:
- Kubernetes manifests in `infra/k8s/`
- Health checks on all services
- Prometheus metrics collection
- Structured logging for observability
- GDPR and BaFin compliance considerations

### Troubleshooting Common Issues

#### "GROQ_API_KEY not found"
Solution: Load environment with `. .\load-env.ps1` or check `.env` file exists

#### OCR Processing Errors
Solution: Install Tesseract OCR following `INSTALL_TESSERACT.md`

#### Docker Services Not Starting
Solution: Check Docker Desktop is running and ports aren't in use

#### Embedding Model Downloads
First run downloads ~90MB Sentence Transformers model (one-time)

## Business Context

This is a production-ready insurance platform with real customers:
- **Hallesche Insurance**: 50,000 claims/year
- **TK (Techniker Krankenkasse)**: POC phase
- Target: 85% automation rate, 60% cost reduction
- Compliance: GDPR, BaFin regulations

The codebase demonstrates enterprise-grade AI implementation with practical business applications in the German insurance market.