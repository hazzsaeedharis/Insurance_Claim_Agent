# 🌐 Web Demo Guide

## Quick Start (2 Steps!)

### Step 1: Start the AI Backend
```powershell
# In Terminal 1
cd D:\Desktop\Insurance_Claim_Agent
.venv\Scripts\python.exe -m uvicorn services.ai_processing.api:app --host 0.0.0.0 --port 8005 --reload
```

### Step 2: Open the Web Interface
```powershell
# In Terminal 2 (or just double-click)
cd D:\Desktop\Insurance_Claim_Agent\web
start index.html
```

That's it! The website will open in your browser.

---

## Alternative: One-Click Start

Run this script:
```powershell
.\start-web-demo.ps1
```

---

## Using the Demo

### 1. Click "Start Demo" or scroll to Demo section

### 2. Fill in the form:
- **Policy Number**: HK-2024-001234 (pre-filled)
- **Claim Type**: Select "Outpatient Treatment"
- **Amount**: 250.00 (pre-filled)
- **Document**: Click "Choose file" and upload:
  - `data/samples/documents/hallesche_valid_outpatient.pdf`

### 3. Click "Submit Claim"

Watch the magic happen:
- ✅ Document uploaded
- ✅ OCR extracts data
- ✅ AI analyzes against policy
- ✅ Fraud check
- ✅ Settlement calculated

### 4. See Results with Full Justification

The page will show:
- **Claim ID**: Automatically generated
- **Status**: APPROVED/REJECTED
- **Settlement**: Amount approved vs. claimed
- **Processing Time**: Real-time measurement
- **📄 Detailed Justification**: Full breakdown showing:
  - What was extracted
  - How coverage was calculated
  - Policy references
  - Line-by-line calculations

---

## Demo Tips for Customers/VCs

### Before Demo:
1. Open the website
2. Have the PDF ready to upload
3. Test it once to make sure everything works

### During Demo:
1. **Show the form** - "This is our customer portal"
2. **Upload document** - "Customer submits their claim"
3. **Watch pipeline** - "AI processes in real-time"
4. **Show results** - "Here's the breakdown with policy justification"
5. **Emphasize**:
   - Processing time (< 30 seconds)
   - Full transparency (shows exact calculations)
   - Policy references (compliance)
   - Accuracy (real extraction from German documents)

### Talking Points:
> "What you're seeing is a live claim being processed by our AI. It:
> - Reads the German document using OCR
> - Extracts structured data using AI
> - Matches it against the 70-page policy document
> - Calculates the exact reimbursement
> - Provides full justification for auditing
> 
> This entire process used to take 2-3 days. Now it's 30 seconds."

---

## Troubleshooting

### "API not responding"
The backend needs to be running:
```powershell
.venv\Scripts\python.exe -m uvicorn services.ai_processing.api:app --host 0.0.0.0 --port 8005
```

### "File upload not working"
Make sure you're uploading a PDF, PNG, JPG, or TIFF file.

### "Processing stuck"
Check the terminal where the API is running for errors. Common issues:
- Missing API keys (GROQ_API_KEY, PINECONE_API_KEY)
- Poppler not installed
- Tesseract not installed

### "CORS errors in browser"
Open the HTML file through a web server, not directly from file system:
```powershell
cd web
python -m http.server 8080
# Then go to http://localhost:8080
```

---

## What's Happening Under the Hood

1. **Frontend** (`web/index.html` + `app.js`):
   - Beautiful UI
   - Real-time animations
   - Calls backend API

2. **Backend** (`services/ai_processing/api.py`):
   - `/documents/extract` - Extracts data from PDF
   - `/claims/analyze` - Analyzes against policy
   - Returns JSON with results + justification

3. **AI Processing**:
   - `PolicyIndexer` - Searches 70-page policy in Pinecone
   - `DocumentProcessor` - OCR + AI extraction
   - `ClaimAnalyzer` - Matches claim to policy, calculates reimbursement

---

## Sample Documents to Upload

Located in `data/samples/documents/`:
- ✅ `hallesche_valid_outpatient.pdf` - Valid outpatient claim
- ❌ `hallesche_invalid_outpatient.pdf` - Invalid claim (for testing rejections)
- ⚠️ `hallesche_ambiguous_claim.pdf` - Edge case

---

## URLs Reference

| Service | URL |
|---------|-----|
| Web Demo | http://localhost:8080 (or just open index.html) |
| AI API Docs | http://localhost:8005/docs |
| Health Check | http://localhost:8005/health |
| Status | http://localhost:8005/status |

---

## Next Steps

1. ✅ Test locally
2. 📊 Practice your demo pitch
3. 🎥 Record a demo video (optional)
4. 🚀 Show to customers/VCs

---

## Need Help?

Check the API logs in the terminal where you started uvicorn. All requests and processing steps are logged there.

**The web demo is now fully functional with live AI processing!** 🎉

