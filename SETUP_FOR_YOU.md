# 🚀 Quick Setup Guide - For Your Configuration

Based on what you have:
- ✅ Groq API key
- ✅ Gemini API key  
- ✅ Pinecone API key (environment unknown - **not needed, we'll use ChromaDB locally**)
- ❌ No OpenAI API key (that's fine!)

## Your Perfect Setup (FREE!)

You already have everything you need for the **BEST possible setup** - all for FREE! 🎉

### Step 1: Run the Setup Script

```powershell
.\setup-api-keys.ps1
```

When prompted:
1. **Groq API Key**: Paste your key
2. **Gemini API Key**: Paste your key (or skip if no credit card) 
3. **OpenAI API Key**: Just press Enter (skip it)

### Step 2: Test Your Setup

```powershell
python test_ai_processing.py
```

This will test:
- ✅ Groq for fast operations
- ✅ Gemini for high-quality extraction and embeddings
- ✅ ChromaDB for local vector storage (no Pinecone needed)

## What Happens With Your Keys?

### Priority System:
1. **Gemini** (primary) - Used for:
   - Document extraction
   - Policy analysis
   - Embeddings (FREE!)
   - Claim matching

2. **Groq** (fast operations) - Used for:
   - Quick classification
   - Backup when Gemini rate limits hit

### Why This Is Perfect:

| Feature | Your Setup | Cost |
|---------|-----------|------|
| Document Processing | Gemini 1.5 Pro | FREE |
| Policy Embeddings | Gemini embeddings | FREE |
| Claim Analysis | Gemini 1.5 Pro | FREE |
| Rate Limit | 60 requests/min | FREE |
| German Language | Excellent | FREE |
| **Total** | **Professional Grade** | **$0** |

## About Pinecone

You mentioned you have a Pinecone API key but don't know the environment.

**Good news**: You don't need it! Here's why:

- **ChromaDB** (local, free): Perfect for development and MVP
- **Pinecone** (cloud, paid): Only needed for production scale (100K+ documents)

We're using ChromaDB by default, which:
- ✅ Runs locally on your machine
- ✅ No setup needed
- ✅ Perfect for testing and development
- ✅ Handles thousands of documents easily

If you later need Pinecone, the environment is usually like:
- `us-east-1-aws`
- `eu-west-1-aws`
- `asia-southeast1-gcp`

But again, **you don't need it right now**!

## Your .env File Should Look Like:

```env
# Required
GROQ_API_KEY=your_actual_groq_key_here

# Recommended (FREE!)
GEMINI_API_KEY=your_gemini_key_here

# Not needed
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
```

## Quick Commands

```powershell
# Create .env file
.\setup-api-keys.ps1

# Test the system
python test_ai_processing.py

# Check Groq models available
.\check-groq-models.ps1

# Start the AI service
cd services/ai_processing
python api.py
```

## What You Get With This Setup

✅ **FREE tier** for everything
✅ **60 requests/minute** with Gemini
✅ **30 requests/minute** with Groq
✅ **Excellent German** language support
✅ **2M token context** window (Gemini 1.5 Pro)
✅ **768-dimension embeddings** (Gemini)
✅ **Local vector database** (ChromaDB)

## Summary

You're all set! You have:
1. ✅ Groq API key (required)
2. ✅ Gemini API key (perfect for quality!)
3. ❌ OpenAI not needed (Gemini is better for free)
4. ❌ Pinecone not needed (ChromaDB works great)

Just run `.\setup-api-keys.ps1` and you're good to go! 🚀
