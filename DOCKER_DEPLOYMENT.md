# Docker Deployment Guide

## Overview

This guide explains how to deploy the complete Insurance Claim Processing system using Docker. All services run in containers, so you don't need to install PostgreSQL, Redis, or other dependencies locally.

## Prerequisites

1. **Docker Desktop** (with Docker Compose)
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Mac: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/engine/install/

2. **API Keys** (Required)
   - Groq API Key: https://console.groq.com/keys
   - Pinecone API Key: https://app.pinecone.io/

3. **API Keys** (Optional)
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Gemini API Key: https://makersuite.google.com/app/apikey

## Quick Start

### 1. Configure Environment Variables

Copy the template and add your API keys:
```powershell
Copy-Item env.template .env
notepad .env
```

**Minimum required** in `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1-aws
```

### 2. Start All Services

Run the startup script:
```powershell
.\start-docker-demo.ps1
```

Or manually:
```powershell
cd infra
docker-compose up -d
```

### 3. Wait for Services to Start

Services take 30-60 seconds to be fully operational. Check status:
```powershell
cd infra
docker-compose ps
```

### 4. Verify AI Service is Running

```powershell
curl http://localhost:8005/health
curl http://localhost:8005/status
```

## Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Database for claims and metadata |
| MinIO | 9000, 9001 | S3-compatible object storage |
| Redis | 6379 | Caching and message queue |
| RabbitMQ | 5672, 15672 | Message broker |
| Keycloak | 8080 | Identity and access management |
| AI Processing | 8005 | Document processing and claim analysis |

## Using the AI Processing API

### Index a Policy Document

```powershell
curl -X POST http://localhost:8005/policies/index \
  -F "policy_id=HALLESCHE_NK_SELECT_S" \
  -F "policy_name=Hallesche NK.select S" \
  -F "file=@data/policies/hallesche/pm255u-e-0922.pdf"
```

### Extract Data from Claim Document

```powershell
curl -X POST http://localhost:8005/documents/extract \
  -F "claim_id=CLAIM-001" \
  -F "document_type_hint=medical_invoice" \
  -F "file=@data/samples/documents/hallesche_valid_outpatient.pdf"
```

### Analyze a Claim

```powershell
curl -X POST http://localhost:8005/claims/analyze/CLAIM-001 \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLAIM-001",
    "policy_id": "HALLESCHE_NK_SELECT_S",
    "customer_id": "CUST-12345"
  }'
```

### Search Policy Terms

```powershell
curl "http://localhost:8005/policies/HALLESCHE_NK_SELECT_S/search?query=outpatient%20coverage&limit=5"
```

## Troubleshooting

### Services Won't Start

1. **Check Docker is running**:
   ```powershell
   docker info
   ```

2. **Check logs**:
   ```powershell
   cd infra
   docker-compose logs ai-processing-service
   ```

3. **Rebuild containers**:
   ```powershell
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### AI Service Errors

1. **Check API keys are set**:
   ```powershell
   docker-compose exec ai-processing-service env | grep API_KEY
   ```

2. **Check if Tesseract is installed**:
   ```powershell
   docker-compose exec ai-processing-service tesseract --version
   ```

3. **Check if Poppler is installed**:
   ```powershell
   docker-compose exec ai-processing-service pdftoppm -v
   ```

### Database Connection Issues

1. **Check PostgreSQL is healthy**:
   ```powershell
   docker-compose ps postgres
   ```

2. **Test connection**:
   ```powershell
   docker-compose exec postgres psql -U insurance_admin -d insurance_claims -c "SELECT 1;"
   ```

## Stopping Services

### Stop all services:
```powershell
cd infra
docker-compose down
```

### Stop and remove all data:
```powershell
cd infra
docker-compose down -v
```

## Development Workflow

### View logs in real-time:
```powershell
docker-compose logs -f ai-processing-service
```

### Restart a single service:
```powershell
docker-compose restart ai-processing-service
```

### Rebuild after code changes:
```powershell
docker-compose build ai-processing-service
docker-compose up -d ai-processing-service
```

### Access container shell:
```powershell
docker-compose exec ai-processing-service /bin/bash
```

## Data Persistence

All data is persisted in Docker volumes:
- `postgres_data` - Database
- `minio_data` - Uploaded documents
- `redis_data` - Cache
- `rabbitmq_data` - Message queue
- `ai_data` - Vector database (Pinecone is cloud-based)

These volumes persist even after `docker-compose down`.

## Performance Tips

1. **Allocate more resources to Docker**:
   - Docker Desktop → Settings → Resources
   - Recommended: 4 CPU cores, 8GB RAM

2. **Use local embeddings** (faster, no API calls):
   ```env
   EMBEDDING_STRATEGY=local
   ```

3. **Monitor resource usage**:
   ```powershell
   docker stats
   ```

## Next Steps

1. Index your policy documents
2. Test document extraction with sample claims
3. Review the API documentation at http://localhost:8005/docs
4. Integrate with your frontend or other services

## Support

For issues or questions, check the logs and ensure all environment variables are correctly set in the `.env` file.

