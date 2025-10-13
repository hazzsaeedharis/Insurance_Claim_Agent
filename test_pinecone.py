"""Test Pinecone connection and find the environment"""

import os
from pinecone import Pinecone, ServerlessSpec

# Get API key from environment
api_key = os.getenv("PINECONE_API_KEY", "pcsk_UXMqD_7J8iHq5cd1BCKxNNVAhhfy1JhWH1h6mPzGpR4CPaHePxod4F61A8Cn6iW4ecFKF")

print(f"Testing Pinecone API key: {api_key[:20]}...")

try:
    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)
    
    print("\n[OK] Successfully connected to Pinecone!")
    
    # List all indexes
    indexes = pc.list_indexes()
    print(f"\nExisting indexes: {[idx.name for idx in indexes]}")
    
    # Try to create or get an index
    index_name = "insurance-policies"
    
    if index_name not in [idx.name for idx in indexes]:
        print(f"\nCreating new index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=384,  # Dimension for all-MiniLM-L6-v2 embeddings
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"  # Default region, will adjust if needed
            )
        )
        print(f"[OK] Index created!")
    else:
        print(f"\n[OK] Index '{index_name}' already exists")
    
    # Get index info
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    print(f"\nIndex stats:")
    print(f"  - Vectors: {stats.total_vector_count}")
    print(f"  - Dimension: {stats.dimension}")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    print("\nTrying to determine the correct region...")
    
    # Common Pinecone regions to try
    regions = ["us-east-1", "us-west-1", "eu-west-1", "asia-southeast1"]
    
    for region in regions:
        try:
            print(f"\nTrying region: {region}")
            pc = Pinecone(api_key=api_key)
            # Try to create index with this region
            pc.create_index(
                name="test-index",
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=region)
            )
            print(f"[SUCCESS] Success! Your Pinecone environment is likely: aws-{region}")
            # Clean up test index
            pc.delete_index("test-index")
            break
        except Exception as e:
            if "already exists" in str(e):
                print(f"[SUCCESS] Index exists - your environment might be: aws-{region}")
                break
            else:
                print(f"  Failed: {str(e)[:100]}...")
                continue
