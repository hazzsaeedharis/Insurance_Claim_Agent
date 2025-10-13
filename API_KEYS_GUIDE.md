# 🔑 API Keys Setup Guide

## What API Keys Do You Need?

### 1. **Groq API Key** (REQUIRED) ✅
- **Purpose**: Document extraction and text analysis using fast LLMs
- **Get it from**: https://console.groq.com/keys
- **Cost**: Free tier available with generous limits
- **Used for**:
  - Classifying document types
  - Extracting data from claims
  - Interpreting policy terms
  - Generating justifications

### 2. **Gemini API Key** (HIGHLY RECOMMENDED) 🌟
- **Purpose**: Google's best AI for extraction, embeddings, and analysis
- **Get it from**: https://makersuite.google.com/app/apikey
- **Cost**: **FREE tier with 60 requests/minute!**
- **Benefits**:
  - Excellent for German documents (multilingual)
  - Free embeddings (768 dimensions)
  - Gemini 1.5 Pro with 2M context window
  - Superior semantic understanding
  - More reliable structured output

### 3. **OpenAI API Key** (ALTERNATIVE) 💡
- **Purpose**: Alternative to Gemini for embeddings and GPT-4
- **Get it from**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (approximately $0.03 per claim with GPT-4)
- **Note**: Use this if you prefer OpenAI or already have credits

### 4. **Pinecone API Key** (OPTIONAL) 💡
- **Purpose**: Cloud-based vector database (alternative to local ChromaDB)
- **Get it from**: https://app.pinecone.io/
- **Cost**: Free tier available
- **Use if**: You need cloud-based storage or have large-scale requirements

## Setting Up Your API Keys

### Step 1: Create .env file
```bash
# Copy the template
cp env.template .env

# Edit the file with your keys
notepad .env  # or use your preferred editor
```

### Step 2: Add your keys to .env
```env
# Minimum required setup
GROQ_API_KEY=your_actual_groq_key_here

# Recommended for production (FREE tier!)
GEMINI_API_KEY=your_actual_gemini_key_here

# Optional alternative to Gemini
OPENAI_API_KEY=your_actual_openai_key_here
```

### Step 3: Test your setup
```bash
# Test Groq connection
.\check-groq-models.ps1

# Test the full pipeline
python test_ai_processing.py
```

## Cost Comparison

| Feature | Groq Only | Groq + Gemini (RECOMMENDED) | Groq + OpenAI | 
|---------|-----------|----------------------------|---------------|
| Document Classification | ✅ Free | ✅ Free | ✅ ~$0.0001/claim |
| Data Extraction | ✅ Free | ✅ Free | ✅ ~$0.001/claim |
| Policy Embeddings | ❌ Placeholder | ✅ Free | ✅ ~$0.0001/section |
| Complex Analysis | ⚠️ Good | ✅ Excellent | ✅ Excellent |
| German Language | ⚠️ Good | ✅ Excellent | ✅ Excellent |
| Rate Limits | 30/min | 60/min | Depends on tier |
| **Total Cost/Claim** | **$0** | **$0 (FREE!)** | **~$0.03** |

## Quick Start Commands

```powershell
# 1. Set your Groq API key (minimum required)
$env:GROQ_API_KEY = "your_key_here"

# 2. Set your Gemini API key (recommended - FREE!)
$env:GEMINI_API_KEY = "your_key_here"

# 3. Or set OpenAI API key (alternative)
$env:OPENAI_API_KEY = "your_key_here"

# 3. Check available models
.\check-groq-models.ps1

# 4. Run the test
python test_ai_processing.py

# 5. Start the AI service
cd services/ai_processing
python api.py
```

## Environment Variable Options

### For PowerShell (Temporary)
```powershell
$env:GROQ_API_KEY = "your_key"
$env:OPENAI_API_KEY = "your_key"
```

### For PowerShell (Permanent)
```powershell
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your_key", "User")
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_key", "User")
```

### For Docker
```bash
# Option 1: Pass when running
docker-compose run -e GROQ_API_KEY=your_key ai-processing-service

# Option 2: Use .env file (recommended)
# Docker Compose automatically loads .env file
docker-compose up ai-processing-service
```

## Available Groq Models (as of 2024)

Run `.\check-groq-models.ps1` to see current models. Popular ones include:

- **llama-3.3-70b-versatile**: Best quality, slower
- **llama-3.1-8b-instant**: Fast, good for simple tasks
- **mixtral-8x7b-32768**: Balanced performance (our default)
- **whisper-large-v3**: Speech-to-text

## Troubleshooting

### "API key not found"
```powershell
# Make sure key is set
echo $env:GROQ_API_KEY

# If empty, set it
$env:GROQ_API_KEY = "your_key_here"
```

### "Unauthorized" error
- Check if your API key is correct
- Ensure no extra spaces or quotes
- Try regenerating the key

### "Rate limit exceeded"
- Groq free tier: 30 requests/minute
- Consider upgrading or adding delays

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use .env files** that are gitignored
3. **Rotate keys regularly**
4. **Use different keys** for dev/staging/prod
5. **Monitor usage** to detect anomalies

## Questions?

- Groq Documentation: https://console.groq.com/docs
- OpenAI Documentation: https://platform.openai.com/docs
- Our Implementation: See `services/ai_document_processor/README.md`
