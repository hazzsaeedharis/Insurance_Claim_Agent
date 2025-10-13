# API Keys Setup

## Required API Keys

### 1. Groq API Key (Required)
- Sign up at: https://console.groq.com
- Get your API key from: https://console.groq.com/keys
- Set as environment variable: `GROQ_API_KEY`

### 2. OpenAI API Key (Recommended)
- Sign up at: https://platform.openai.com
- Get your API key from: https://platform.openai.com/api-keys
- Set as environment variable: `OPENAI_API_KEY`
- Required for best quality embeddings and extraction

## Setting Environment Variables

### Option 1: Export in Terminal
```bash
export GROQ_API_KEY="your_groq_key_here"
export OPENAI_API_KEY="your_openai_key_here"
```

### Option 2: Create .env file
```bash
# Create .env file in project root
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Option 3: Docker Compose
```bash
# Pass when running docker-compose
GROQ_API_KEY=your_key docker-compose up
```

## Test Your Setup
```bash
python test_ai_processing.py
```
