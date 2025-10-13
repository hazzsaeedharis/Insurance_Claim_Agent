"""
Policy Document Indexer
Extracts and indexes insurance policy documents for RAG-based retrieval
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

import chromadb
from chromadb.config import Settings
import pypdf2
import pdfplumber
from groq import Groq
import openai

from services.ai_document_processor.config import ai_config, POLICY_SECTIONS

logger = logging.getLogger(__name__)


@dataclass
class PolicySection:
    """Represents a section of a policy document"""
    policy_id: str
    section_id: str
    section_type: str
    title: str
    text: str
    page_numbers: List[int]
    metadata: Dict[str, Any]


class PolicyIndexer:
    """Indexes policy documents for efficient retrieval"""
    
    def __init__(self):
        """Initialize the indexer with vector database"""
        # Initialize ChromaDB (local) or Pinecone based on config
        if ai_config.vector_db_type == "chromadb":
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            self.collection = self.client.get_or_create_collection(
                name=ai_config.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            # TODO: Add Pinecone support
            raise NotImplementedError("Pinecone support coming soon")
        
        # Initialize LLMs
        self.groq_client = Groq(api_key=ai_config.groq_api_key)
        
        # Initialize OpenAI if available
        if ai_config.openai_api_key:
            openai.api_key = ai_config.openai_api_key
            self.use_openai = True
        else:
            self.use_openai = False
            logger.warning("OpenAI API key not set, using Groq for all operations")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information"""
        pages = []
        
        # Try pdfplumber first (better for tables)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        pages.append({
                            "page_num": i + 1,
                            "text": text,
                            "tables": page.extract_tables()
                        })
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying pypdf2: {e}")
            # Fallback to pypdf2
            with open(pdf_path, 'rb') as file:
                reader = pypdf2.PdfReader(file)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        pages.append({
                            "page_num": i + 1,
                            "text": text,
                            "tables": []
                        })
        
        return pages
    
    def segment_policy_document(self, pages: List[Dict[str, Any]], policy_id: str) -> List[PolicySection]:
        """Segment policy document into logical sections"""
        sections = []
        current_section = None
        section_counter = 0
        
        for page in pages:
            text = page["text"]
            lines = text.split('\n')
            
            for line in lines:
                # Check if this line is a section header
                section_type = self._identify_section_type(line)
                
                if section_type:
                    # Save previous section if exists
                    if current_section:
                        sections.append(current_section)
                    
                    # Start new section
                    section_counter += 1
                    current_section = PolicySection(
                        policy_id=policy_id,
                        section_id=f"{policy_id}_section_{section_counter}",
                        section_type=section_type,
                        title=line.strip(),
                        text=line + "\n",
                        page_numbers=[page["page_num"]],
                        metadata={}
                    )
                elif current_section:
                    # Add to current section
                    current_section.text += line + "\n"
                    if page["page_num"] not in current_section.page_numbers:
                        current_section.page_numbers.append(page["page_num"])
        
        # Don't forget the last section
        if current_section:
            sections.append(current_section)
        
        # Extract metadata for each section
        for section in sections:
            section.metadata = self._extract_section_metadata(section)
        
        return sections
    
    def _identify_section_type(self, line: str) -> Optional[str]:
        """Identify if a line is a section header and its type"""
        line_lower = line.lower().strip()
        
        # Check against known section types
        for section_type, keywords in POLICY_SECTIONS.items():
            for keyword in keywords:
                if keyword in line_lower and len(line) < 100:  # Headers are usually short
                    return section_type
        
        # Check for numbered sections (e.g., "1. Leistungen", "2.3 Ausschlüsse")
        if re.match(r'^\d+\.?\d*\s+[A-Z]', line) and len(line) < 100:
            # Try to identify type from content
            for section_type, keywords in POLICY_SECTIONS.items():
                for keyword in keywords:
                    if keyword in line_lower:
                        return section_type
            return "general"  # Unknown section type
        
        return None
    
    def _extract_section_metadata(self, section: PolicySection) -> Dict[str, Any]:
        """Extract metadata from section text using LLM"""
        prompt = f"""
        Analyze this insurance policy section and extract the following information:
        
        Section Type: {section.section_type}
        Section Text:
        {section.text[:2000]}  # Limit to first 2000 chars
        
        Extract:
        1. Coverage percentage (if mentioned)
        2. Deductible amounts (if mentioned)
        3. Annual or per-case limits (if mentioned)
        4. Waiting periods (if mentioned)
        5. Key conditions or requirements
        6. Excluded items (if this is an exclusions section)
        
        Return as JSON with the following structure:
        {{
            "coverage_percentage": null or number (e.g., 80),
            "deductible": null or {{"amount": number, "currency": "EUR", "per": "year|case"}},
            "limits": null or {{"amount": number, "currency": "EUR", "per": "year|case|lifetime"}},
            "waiting_period_days": null or number,
            "conditions": [],
            "exclusions": []
        }}
        
        Be precise and only include information explicitly stated in the text.
        """
        
        try:
            if self.use_openai:
                # Use GPT-4 for best accuracy
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an insurance policy analyst. Extract information precisely."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                metadata = json.loads(response.choices[0].message.content)
            else:
                # Use Groq as fallback
                response = self.groq_client.chat.completions.create(
                    model=ai_config.groq_model,
                    messages=[
                        {"role": "system", "content": "You are an insurance policy analyst. Extract information precisely as JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                metadata = json.loads(response.choices[0].message.content)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using OpenAI or fallback"""
        if self.use_openai:
            # Use OpenAI embeddings (best quality for multilingual)
            response = openai.Embedding.create(
                model=ai_config.embedding_model,
                input=texts
            )
            return [item["embedding"] for item in response["data"]]
        else:
            # TODO: Implement fallback embedding model
            # For now, we'll use a placeholder
            logger.warning("OpenAI embeddings not available, using placeholder")
            return [[0.0] * 1536 for _ in texts]  # Placeholder embeddings
    
    def index_policy_document(self, pdf_path: str, policy_id: str, policy_name: str) -> Dict[str, Any]:
        """Main method to index a policy document"""
        logger.info(f"Indexing policy document: {policy_name} (ID: {policy_id})")
        
        # Extract text from PDF
        pages = self.extract_text_from_pdf(pdf_path)
        logger.info(f"Extracted {len(pages)} pages from PDF")
        
        # Segment into sections
        sections = self.segment_policy_document(pages, policy_id)
        logger.info(f"Identified {len(sections)} sections")
        
        # Prepare for indexing
        documents = []
        metadatas = []
        ids = []
        
        for section in sections:
            # Chunk long sections
            chunks = self._chunk_text(section.text, ai_config.chunk_size, ai_config.chunk_overlap)
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{section.section_id}_chunk_{i}"
                
                documents.append(chunk)
                ids.append(doc_id)
                metadatas.append({
                    "policy_id": policy_id,
                    "policy_name": policy_name,
                    "section_id": section.section_id,
                    "section_type": section.section_type,
                    "section_title": section.title,
                    "page_numbers": ",".join(map(str, section.page_numbers)),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **{f"metadata_{k}": json.dumps(v) if isinstance(v, (dict, list)) else v 
                       for k, v in section.metadata.items()}
                })
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} chunks")
        embeddings = self.generate_embeddings(documents)
        
        # Index in vector database
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully indexed {len(documents)} chunks")
        
        return {
            "policy_id": policy_id,
            "policy_name": policy_name,
            "total_pages": len(pages),
            "total_sections": len(sections),
            "total_chunks": len(documents),
            "section_types": list(set(s.section_type for s in sections))
        }
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.8:  # Only if we're not losing too much
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def search_policy(self, query: str, policy_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant policy sections"""
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"policy_id": policy_id} if policy_id else None
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        
        return formatted_results


# Example usage
if __name__ == "__main__":
    # Initialize indexer
    indexer = PolicyIndexer()
    
    # Index a policy document
    result = indexer.index_policy_document(
        pdf_path="data/policies/hallesche/pm255u-e-0922.pdf",
        policy_id="HALLESCHE_NK_SELECT_S",
        policy_name="Hallesche NK.select S"
    )
    
    print(f"Indexing complete: {result}")
    
    # Search for coverage information
    search_results = indexer.search_policy(
        query="outpatient treatment coverage percentage",
        policy_id="HALLESCHE_NK_SELECT_S"
    )
    
    print(f"\nSearch results: {len(search_results)} found")
    for result in search_results[:2]:
        print(f"- {result['text'][:100]}...")
        print(f"  Metadata: {result['metadata']}")
