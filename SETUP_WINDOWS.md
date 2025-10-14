# 🪟 Complete Windows Setup Guide

This guide will get your AI Document Processing system fully functional on Windows.

## Quick Summary

You need to install:
1. ✅ Poppler (for PDF processing)
2. ✅ Tesseract OCR (for text extraction)
3. ✅ Python packages (already done!)

---

## Step 1: Install Poppler

### Download & Extract
1. Download: https://github.com/oschwartz10612/poppler-windows/releases/latest
2. Download the `Release-XX.XX.X-X.zip` file
3. Extract to `C:\Program Files\poppler`

### Add to PATH (PowerShell as Admin)
```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Program Files\poppler\Library\bin",
    [EnvironmentVariableTarget]::Machine
)
```

### Verify
```powershell
# Restart PowerShell
pdftoppm -v
```

---

## Step 2: Install Tesseract OCR

### Download & Install
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Get the latest `.exe` installer
3. During installation, select:
   - ✅ **German (deu)** language pack
   - ✅ **English (eng)** language pack

### Add to PATH (PowerShell as Admin)
```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Program Files\Tesseract-OCR",
    [EnvironmentVariableTarget]::Machine
)
```

### Verify
```powershell
# Restart PowerShell
tesseract --version
tesseract --list-langs  # Should show 'deu' and 'eng'
```

---

## Step 3: Test Everything

After installing both Poppler and Tesseract, restart your terminal and test:

```powershell
cd D:\Desktop\Insurance_Claim_Agent

# Load environment variables
. .\load-env.ps1

# Test the full system
.venv\Scripts\python.exe test_ai_processing.py
```

---

## Troubleshooting

### "poppler not found"
- Make sure you added the `Library\bin` folder to PATH
- Restart your terminal/IDE
- Check path: `echo $env:Path | Select-String poppler`

### "tesseract not found"
- Make sure Tesseract is installed
- Restart your terminal/IDE
- Check: `tesseract --version`

### "German language pack not found"
- Re-run the Tesseract installer
- Select the German (deu) language pack during installation
- Or manually download `deu.traineddata` and place in `C:\Program Files\Tesseract-OCR\tessdata\`

---

## Current Model Configuration

Your system now uses:
- **Groq Model**: `llama-3.3-70b-versatile` (best quality)
- **Embeddings**: Local Sentence Transformers (FREE)
- **Vector DB**: Pinecone (cloud-based)

---

## Next Steps

Once everything is installed:

1. **Test the system**: `.venv\Scripts\python.exe test_ai_processing.py`
2. **Index your policies**: The system will automatically index policy documents
3. **Process claims**: Upload documents and let the AI analyze them!

Everything working? You're ready to process insurance claims! 🎉
