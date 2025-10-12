"""
Claims API Service
REST API for insurance claim management with CRUD operations
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
import os
import sys
import uuid
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.common.logger import get_logger, set_correlation_id
from services.common.metrics import increment, timer, gauge

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Claims API",
    description="API for managing insurance claims",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "insurance_claims"),
    "user": os.getenv("DB_USER", "insurance_admin"),
    "password": os.getenv("DB_PASSWORD", "dev_password_123")
}

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialize database tables if they don't exist."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create claims table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50) NOT NULL,
                policy_number VARCHAR(50) NOT NULL,
                claim_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'submitted',
                items JSONB NOT NULL DEFAULT '[]',
                total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
                currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                submitted_at TIMESTAMP,
                processed_at TIMESTAMP,
                approved_at TIMESTAMP,
                adjuster_id VARCHAR(50),
                metadata JSONB DEFAULT '{}'
            )
        """)
        
        # Create index on status for faster queries
        cur.execute("CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_claims_customer ON claims(customer_id)")
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Initialize database on startup
init_db()

# Pydantic models
class ClaimItem(BaseModel):
    date: str
    provider: str
    code: str
    description: Optional[str] = None
    quantity: float = 1
    net_amount: float
    gross_amount: Optional[float] = None
    currency: str = "EUR"
    covered_amount: float = 0
    deductible_applied: float = 0

class ClaimCreate(BaseModel):
    policy_number: str
    claim_type: str = Field(..., pattern="^(outpatient|inpatient|dental|vision|pharmacy|emergency)$")
    items: List[ClaimItem]
    total_amount: Optional[float] = None
    currency: str = "EUR"

class ClaimUpdate(BaseModel):
    status: Optional[str] = None
    adjuster_id: Optional[str] = None
    items: Optional[List[ClaimItem]] = None

class ClaimResponse(BaseModel):
    claim_id: str
    customer_id: str
    policy_number: str
    claim_type: str
    status: str
    items: List[ClaimItem]
    total_amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    adjuster_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

def generate_claim_id() -> str:
    """Generate unique claim ID"""
    random_part = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:8].upper()
    return f"CLM-{random_part}"

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Claims API starting up")
    set_correlation_id()
    
    # Initialize database
    init_db()
    
    # Load sample claims if they exist
    synthetic_dir = "data/synthetic"
    if os.path.exists(synthetic_dir):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            for filename in os.listdir(synthetic_dir):
            if filename.endswith('.json'):
                with open(os.path.join(synthetic_dir, filename), 'r') as f:
                    claim = json.load(f)
                    claims_db[claim['claim_id']] = claim
        logger.info(f"Loaded {len(claims_db)} sample claims")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    increment("api.health_check")
    return {"status": "healthy", "service": "claims-api", "timestamp": datetime.utcnow()}

@app.post("/claims", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim: ClaimCreate,
    # Temporarily disable auth for MVP demo
    # current_user: User = Depends(require_permission("claim:create:own"))
):
    """Create a new insurance claim"""
    with timer("api.claim.create"):
        claim_id = generate_claim_id()
        customer_id = "DEMO-USER-001"  # For MVP demo
        
        # Calculate total if not provided
        total_amount = claim.total_amount
        if total_amount is None:
            total_amount = sum(item.net_amount for item in claim.items)
        
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Insert claim into database
            cur.execute("""
                INSERT INTO claims (
                    claim_id, customer_id, policy_number, claim_type,
                    status, items, total_amount, currency,
                    submitted_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                claim_id,
                customer_id,
                claim.policy_number,
                claim.claim_type,
                "submitted",
                json.dumps([item.dict() for item in claim.items]),
                total_amount,
                claim.currency,
                datetime.utcnow(),
                json.dumps({
                    "source": "api",
                    "user_agent": "claims-api/1.0"
                })
            ))
            
            new_claim = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            # Metrics
            increment("claims.created")
            increment(f"claims.type.{claim.claim_type}")
            gauge("claims.total_amount", total_amount)
            
            logger.info(f"Created claim {claim_id}")
            
            return ClaimResponse(**new_claim)
            
        except Exception as e:
            logger.error(f"Error creating claim: {e}")
            raise HTTPException(status_code=500, detail="Error creating claim")

@app.get("/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    # Temporarily disable auth for MVP demo
    # current_user: User = Depends(get_current_user)
):
    """Get a specific claim by ID"""
    with timer("api.claim.get"):
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("SELECT * FROM claims WHERE claim_id = %s", (claim_id,))
            claim = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if not claim:
                increment("claims.not_found")
                raise HTTPException(status_code=404, detail="Claim not found")
            
            # Parse JSON fields
            claim['items'] = json.loads(claim['items']) if claim['items'] else []
            claim['metadata'] = json.loads(claim['metadata']) if claim['metadata'] else {}
            
            increment("claims.retrieved")
            return ClaimResponse(**claim)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving claim: {e}")
            raise HTTPException(status_code=500, detail="Error retrieving claim")

@app.get("/claims", response_model=List[ClaimResponse])
async def list_claims(
    status: Optional[str] = None,
    claim_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """List claims with optional filters"""
    with timer("api.claims.list"):
        # Filter claims based on user permission
        if "claim:read:all" in current_user.permissions:
            filtered_claims = list(claims_db.values())
        else:
            filtered_claims = [c for c in claims_db.values() if c["customer_id"] == current_user.id]
        
        # Apply filters
        if status:
            filtered_claims = [c for c in filtered_claims if c["status"] == status]
        if claim_type:
            filtered_claims = [c for c in filtered_claims if c["claim_type"] == claim_type]
        
        # Pagination
        paginated = filtered_claims[offset:offset + limit]
        
        increment("claims.listed")
        gauge("claims.list.count", len(paginated))
        
        return [ClaimResponse(**claim) for claim in paginated]

@app.put("/claims/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: str,
    update: ClaimUpdate,
    current_user: User = Depends(require_permission("claim:update:all"))
):
    """Update a claim (adjuster only)"""
    with timer("api.claim.update"):
        if claim_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim = claims_db[claim_id]
        
        # Update fields
        if update.status:
            claim["status"] = update.status
            if update.status in ["approved", "rejected"]:
                claim["processed_at"] = datetime.utcnow()
        
        if update.adjuster_id:
            claim["adjuster_id"] = update.adjuster_id
        
        if update.items:
            claim["items"] = [item.dict() for item in update.items]
            claim["total_amount"] = sum(item.net_amount for item in update.items)
        
        claim["updated_at"] = datetime.utcnow()
        
        increment("claims.updated")
        increment(f"claims.status.{claim['status']}")
        
        logger.info(f"Updated claim {claim_id} by {current_user.id}")
        
        return ClaimResponse(**claim)

@app.post("/claims/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    current_user: User = Depends(require_permission("claim:approve"))
):
    """Approve a claim"""
    with timer("api.claim.approve"):
        if claim_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim = claims_db[claim_id]
        
        if claim["status"] != "under_review":
            raise HTTPException(status_code=400, detail="Claim must be under review to approve")
        
        claim["status"] = "approved"
        claim["processed_at"] = datetime.utcnow()
        claim["adjuster_id"] = current_user.id
        claim["updated_at"] = datetime.utcnow()
        
        increment("claims.approved")
        gauge("claims.approved.amount", claim["total_amount"])
        
        logger.info(f"Claim {claim_id} approved by {current_user.id}")
        
        return {"message": "Claim approved", "claim_id": claim_id}

@app.post("/claims/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    reason: str,
    current_user: User = Depends(require_permission("claim:approve"))
):
    """Reject a claim"""
    with timer("api.claim.reject"):
        if claim_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim = claims_db[claim_id]
        
        if claim["status"] not in ["submitted", "under_review"]:
            raise HTTPException(status_code=400, detail="Invalid claim status for rejection")
        
        claim["status"] = "rejected"
        claim["processed_at"] = datetime.utcnow()
        claim["adjuster_id"] = current_user.id
        claim["updated_at"] = datetime.utcnow()
        claim["metadata"]["rejection_reason"] = reason
        
        increment("claims.rejected")
        
        logger.info(f"Claim {claim_id} rejected by {current_user.id}: {reason}")
        
        return {"message": "Claim rejected", "claim_id": claim_id, "reason": reason}

@app.post("/claims/{claim_id}/documents")
async def upload_document(
    claim_id: str,
    file: UploadFile = File(...),
    document_type: str = "receipt",
    current_user: User = Depends(get_current_user)
):
    """Upload a document for a claim"""
    with timer("api.document.upload"):
        if claim_id not in claims_db:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim = claims_db[claim_id]
        
        # Check permission
        if current_user.id != claim["customer_id"] and "document:upload:all" not in current_user.permissions:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate file
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Calculate checksum
        content = await file.read()
        checksum = hashlib.sha256(content).hexdigest()
        
        # Create document record
        document = {
            "document_id": doc_id,
            "document_type": document_type,
            "filename": file.filename,
            "storage_key": f"claims/{claim_id}/{doc_id}/{file.filename}",
            "checksum": checksum,
            "size_bytes": len(content),
            "mimetype": file.content_type,
            "uploaded_at": datetime.utcnow(),
            "uploaded_by": current_user.id,
            "verified": False
        }
        
        # Add to claim
        if "documents" not in claim:
            claim["documents"] = []
        claim["documents"].append(document)
        
        increment("documents.uploaded")
        gauge("documents.size", len(content))
        
        logger.info(f"Document {doc_id} uploaded for claim {claim_id}")
        
        return {"document_id": doc_id, "message": "Document uploaded successfully"}

@app.get("/stats")
async def get_stats(current_user: User = Depends(require_permission("report:read:all"))):
    """Get claims statistics"""
    with timer("api.stats"):
        total_claims = len(claims_db)
        status_counts = {}
        type_counts = {}
        total_amount = 0
        
        for claim in claims_db.values():
            status_counts[claim["status"]] = status_counts.get(claim["status"], 0) + 1
            type_counts[claim["claim_type"]] = type_counts.get(claim["claim_type"], 0) + 1
            total_amount += claim["total_amount"]
        
        return {
            "total_claims": total_claims,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "total_amount": total_amount,
            "average_amount": total_amount / total_claims if total_claims > 0 else 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)