"""Document Management Service API."""

import io
import hashlib
import json
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from minio import Minio
from minio.error import S3Error
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize FastAPI
app = FastAPI(
    title="Document Service",
    description="Document upload, storage and retrieval service",
    version="1.0.0"
)

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "insurance-documents"

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "insurance_claims",
    "user": "postgres",
    "password": "postgres"
}

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure bucket exists
try:
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
except Exception as e:
    print(f"Warning: Could not create MinIO bucket: {e}")


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    document_id: str
    claim_id: str
    filename: str
    content_type: str
    size: int
    checksum: str
    storage_path: str
    uploaded_at: datetime
    status: str = "pending"
    extracted_text: Optional[str] = None
    classification: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document response model."""
    document_id: str
    claim_id: str
    filename: str
    content_type: str
    size: int
    status: str
    uploaded_at: datetime
    download_url: str


def get_db():
    """Database connection dependency."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "document-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    claim_id: str = Form(...),
    document_type: str = Form("general"),
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    """Upload a document to MinIO and store metadata."""
    try:
        # Generate document ID
        document_id = str(uuid4())
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        # Generate storage path
        storage_path = f"{claim_id}/{document_id}/{file.filename}"
        
        # Upload to MinIO
        minio_client.put_object(
            MINIO_BUCKET,
            storage_path,
            io.BytesIO(content),
            file_size,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Store metadata in database
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (
                    document_id, claim_id, filename, content_type,
                    size, checksum, storage_path, document_type,
                    status, uploaded_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    document_id, claim_id, file.filename, 
                    file.content_type or "application/octet-stream",
                    file_size, checksum, storage_path, document_type,
                    "uploaded", datetime.utcnow()
                )
            )
            db.commit()
        
        # Generate download URL
        download_url = f"/documents/{document_id}/download"
        
        return DocumentResponse(
            document_id=document_id,
            claim_id=claim_id,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            size=file_size,
            status="uploaded",
            uploaded_at=datetime.utcnow(),
            download_url=download_url
        )
        
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/documents/{document_id}")
async def get_document_info(document_id: str, db=Depends(get_db)):
    """Get document metadata."""
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM documents WHERE document_id = %s",
            (document_id,)
        )
        doc = cursor.fetchone()
        
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return dict(doc)


@app.get("/documents/{document_id}/download")
async def download_document(document_id: str, db=Depends(get_db)):
    """Download a document from MinIO."""
    # Get document metadata
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT storage_path, filename, content_type FROM documents WHERE document_id = %s",
            (document_id,)
        )
        doc = cursor.fetchone()
        
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Get object from MinIO
        response = minio_client.get_object(MINIO_BUCKET, doc['storage_path'])
        
        return StreamingResponse(
            io.BytesIO(response.read()),
            media_type=doc['content_type'],
            headers={
                "Content-Disposition": f"attachment; filename={doc['filename']}"
            }
        )
    except S3Error as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    finally:
        response.close()
        response.release_conn()


@app.get("/documents/claim/{claim_id}")
async def list_claim_documents(claim_id: str, db=Depends(get_db)):
    """List all documents for a claim."""
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            SELECT document_id, filename, content_type, size, 
                   status, uploaded_at, document_type
            FROM documents 
            WHERE claim_id = %s
            ORDER BY uploaded_at DESC
            """,
            (claim_id,)
        )
        documents = cursor.fetchall()
    
    return {
        "claim_id": claim_id,
        "document_count": len(documents),
        "documents": documents
    }


@app.put("/documents/{document_id}/status")
async def update_document_status(
    document_id: str,
    status: str,
    extracted_text: Optional[str] = None,
    classification: Optional[str] = None,
    db=Depends(get_db)
):
    """Update document processing status."""
    with db.cursor() as cursor:
        # Build update query dynamically
        updates = ["status = %s"]
        params = [status]
        
        if extracted_text:
            updates.append("extracted_text = %s")
            params.append(extracted_text)
        
        if classification:
            updates.append("classification = %s")
            params.append(classification)
        
        params.append(document_id)
        
        cursor.execute(
            f"UPDATE documents SET {', '.join(updates)} WHERE document_id = %s",
            params
        )
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document status updated", "document_id": document_id}


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str, db=Depends(get_db)):
    """Delete a document from storage and database."""
    # Get storage path
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT storage_path FROM documents WHERE document_id = %s",
            (document_id,)
        )
        doc = cursor.fetchone()
        
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from MinIO
        minio_client.remove_object(MINIO_BUCKET, doc['storage_path'])
        
        # Delete from database
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM documents WHERE document_id = %s",
                (document_id,)
            )
            db.commit()
        
        return {"message": "Document deleted", "document_id": document_id}
        
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)