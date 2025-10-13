# Installing Tesseract OCR on Windows

Tesseract is required for extracting text from images and PDFs.

## Installation Steps

1. **Download Tesseract**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-v5.3.3.20231005.exe`)

2. **Run the Installer**:
   - Run the downloaded `.exe` file
   - **IMPORTANT**: During installation, select these language packs:
     - ✅ **German** (deu) - Required for insurance documents!
     - ✅ **English** (eng) - Already selected by default
   - Note the installation path (usually `C:\Program Files\Tesseract-OCR`)

3. **Add to PATH**:
   ```powershell
   # Run PowerShell as Administrator
   [Environment]::SetEnvironmentVariable(
       "Path",
       $env:Path + ";C:\Program Files\Tesseract-OCR",
       [EnvironmentVariableTarget]::Machine
   )
   ```

4. **Verify Installation**:
   ```powershell
   # Restart PowerShell, then test:
   tesseract --version
   tesseract --list-langs
   ```

   You should see both `eng` and `deu` in the language list.

## Alternative: Chocolatey

If you have Chocolatey installed:

```powershell
choco install tesseract
# Then manually download German language pack from:
# https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
# Place it in: C:\Program Files\Tesseract-OCR\tessdata\
```

## Verify It Works

```powershell
cd D:\Desktop\Insurance_Claim_Agent
.venv\Scripts\python.exe -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

If you see a version number, you're all set!
