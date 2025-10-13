# 🚀 Quick Start - With Your .env File

You have a `.env` file, but PowerShell needs to load it first!

## Option 1: Load .env Once (Recommended)

```powershell
# Load your .env file into the current session
. .\load-env.ps1

# Now you can run any commands
.\check-groq-models.ps1
python test_ai_processing.py
```

## Option 2: Auto-Load (The scripts will load it automatically)

Just run the scripts - they'll automatically load from `.env`:

```powershell
# This will auto-load from .env
.\check-groq-models.ps1

# For Python scripts, use python-dotenv (already in requirements.txt)
python test_ai_processing.py
```

## Option 3: One-Line Commands

```powershell
# Check Groq models (loads .env automatically now)
.\check-groq-models.ps1

# Test the full system
python test_ai_processing.py
```

---

## What's in Your .env File?

Your `.env` should look like this for the FREE setup:

```env
# Minimum required (100% FREE!)
GROQ_API_KEY=your_actual_groq_key_here
EMBEDDING_STRATEGY=local

# Optional (skip for free)
GEMINI_API_KEY=
OPENAI_API_KEY=
HUGGINGFACE_API_KEY=
```

---

## Test Your Setup

### Step 1: Check Groq Connection
```powershell
.\check-groq-models.ps1
```

Expected output:
```
[>] Loading API key from .env file...
[OK] Successfully retrieved models!

Available Models:
----------------
Model ID: llama-3.3-70b-versatile
Model ID: llama-3.1-8b-instant
Model ID: mixtral-8x7b-32768
...
```

### Step 2: Test Full Pipeline
```powershell
python test_ai_processing.py
```

Expected output:
```
🔑 API Key Status:
   - Groq API Key: ✅ Set
   - Gemini API Key: ⚠️  Not set
   - OpenAI API Key: ⚠️  Not set

🚀 Testing AI Document Processing Pipeline
1. Initializing components...
✅ Components initialized

2. Testing Policy Indexing...
✅ Using local Sentence Transformers for embeddings (FREE)
...
```

---

## Troubleshooting

### "GROQ_API_KEY not found"

**Solution**: The .env file exists but isn't loaded. Run:
```powershell
. .\load-env.ps1
```

### "No module named 'dotenv'"

**Solution**: Install requirements:
```powershell
pip install -r requirements.txt
```

### "Downloading model..."

**Solution**: First time setup - it's downloading the FREE embedding model (~90MB). This only happens once!

---

## Daily Workflow

```powershell
# 1. Navigate to project
cd D:\Desktop\Insurance_Claim_Agent

# 2. Load environment (if not auto-loaded)
. .\load-env.ps1

# 3. Test/develop
python test_ai_processing.py

# 4. Run services
python services/ai_processing/api.py
```

---

## Why PowerShell Doesn't Auto-Load .env

Unlike bash/zsh, PowerShell doesn't automatically read `.env` files. You have two options:

1. **Manual load** (do once per session): `. .\load-env.ps1`
2. **Let scripts auto-load** (our scripts now do this automatically!)

Python uses `python-dotenv` which automatically loads `.env` files, so Python scripts work without extra steps!

---

## Next Steps

✅ Your .env is ready
✅ Scripts auto-load from .env
✅ You're all set!

Just run: `.\check-groq-models.ps1` to verify everything works!
