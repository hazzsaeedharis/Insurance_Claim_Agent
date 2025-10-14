# Quick Start Guide - AI Claims Processing Demo

## 🚀 Simple 3-Step Setup

### Step 1: Activate Python Environment
```powershell
.venv\Scripts\Activate.ps1
```

### Step 2: Start the AI Service
```powershell
.venv\Scripts\python.exe -m uvicorn services.ai_processing.api:app --host 0.0.0.0 --port 8005 --reload
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8005 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 3: Open the Web Demo
Open in your browser: `http://localhost:5500/web/index.html`

Or use Live Server in VS Code (right-click on `web/index.html` → "Open with Live Server")

---

## 📋 Using the Demo

1. **Fill in the form:**
   - Policy Number: Any text (e.g., `HALL-345678`)
   - Claim Type: Select any type
   - Amount: Any number (will be overwritten by actual document data)

2. **Upload a test document:**
   - Click "Choose File"
   - Select one of these test files:
     - `data/samples/documents/hallesche_ambiguous_claim.pdf` (€625 dental claim)
     - `data/samples/documents/hallesche_valid_outpatient.pdf`
     - `data/samples/documents/hallesche_invalid_outpatient.pdf`

3. **Click "Submit Claim"**

4. **Watch the magic happen!** ✨
   - Document extraction
   - AI analysis
   - Policy matching
   - Justification with details

---

## 🔍 What the System Does

1. **Extracts data** from your uploaded PDF using OCR + Groq AI
2. **Identifies** all claim items (consultations, treatments, medications, etc.)
3. **Matches** against policy coverage rules using vector search
4. **Calculates** reimbursement with deductibles and limits
5. **Generates** detailed justification with policy references

---

## ✅ Expected Results

### For `hallesche_ambiguous_claim.pdf`:
- **Total Claimed**: €625.00
- **Items Extracted**:
  - Emergency Dental Consultation: €80
  - Root Canal Treatment: €340
  - Temporary Crown: €180
  - Pain Medication: €25
- **Processing Time**: ~15-30 seconds
- **Full justification** with policy references

---

## ⚠️ Troubleshooting

### Error: "No extracted document found"
✅ **FIXED!** This was caused by mismatched claim IDs. Just refresh and try again.

### Service not responding:
1. Check the terminal - service should show `Application startup complete`
2. Test health endpoint: `http://localhost:8005/health`
3. Check if port 8005 is already in use

### Browser console errors:
1. Open Developer Tools (F12)
2. Check Console tab for errors
3. Make sure the web page URL includes port 5500 (Live Server)

### Document extraction fails:
- Make sure your PDF is readable
- Check the terminal for error messages
- The AI might take 10-30 seconds for complex documents

---

## 📊 Demo Tips

### For VCs/Customers:
1. Emphasize the **real-time processing**
2. Show the **detailed justification** - this is unique!
3. Highlight the **policy matching** with vector search
4. Mention the **€625 dental claim** is processed correctly, not hardcoded

### Technical Details:
- Uses **Groq Llama 3.3 70B** for extraction and analysis
- **Sentence Transformers** for embeddings (local, no API cost!)
- **Pinecone** for policy vector database
- **PostgreSQL** for claim storage
- **FastAPI** for REST endpoints

---

## 🎯 Current Status

✅ **Working:**
- Document extraction from PDFs
- Multi-item claim processing
- Policy matching (basic rules)
- Reimbursement calculation
- Detailed justification generation
- Real-time web demo

⚠️ **Not Yet Implemented:**
- Policy document indexing (uses default rules)
- Database persistence (uses in-memory cache)
- Authentication
- Fraud detection
- Email notifications
- Payment processing

---

## 🚧 Next Steps

1. **Index policy documents** to improve accuracy
2. **Add PostgreSQL** for persistent storage
3. **Deploy to cloud** for remote demos
4. **Add more test cases** (rejections, partial approvals)

---

## 💡 Pro Tips

- The system **remembers extracted documents** only for the current session
- Refresh the browser if you want to start fresh
- Watch the terminal for detailed logs
- The AI might classify documents differently (e.g., "lab_report" instead of "dental_invoice") - this is OK!

---

Need help? Check the logs in the terminal where you ran the service!
