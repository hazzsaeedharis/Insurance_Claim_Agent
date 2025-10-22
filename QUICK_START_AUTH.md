# 🚀 Quick Start - Authentication

Get authentication up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python --version

# Check PostgreSQL (need 12+)
psql --version
```

## 1-Minute Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run setup script (interactive)
python setup_auth.py

# 3. Start application
python run.py
```

## Manual Setup (if script fails)

### Step 1: Create Database
```bash
psql -U postgres
CREATE DATABASE insurance_claims;
\q
```

### Step 2: Generate Secret Key
```bash
# Windows PowerShell
python -c "import secrets; print(secrets.token_hex(32))"

# Linux/Mac
openssl rand -hex 32
```

### Step 3: Create .env File
```env
# Copy from env.example and fill in:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/insurance_claims
SECRET_KEY=<paste_generated_key_here>
GOOGLE_CLIENT_ID=<optional>
GOOGLE_CLIENT_SECRET=<optional>
```

### Step 4: Start Application
```bash
python run.py
```

## First Login

1. Open browser: `http://localhost:8000/frontend/auth.html`
2. Click "Register" tab
3. Fill in:
   - Email: `admin@example.com`
   - Password: `Admin123!` (must meet requirements)
   - Name: `Admin User`
4. Click "Create Account"
5. Login with credentials
6. Start using the app!

## Google OAuth Setup (Optional)

### Get Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "Google+ API"
3. Credentials → Create OAuth 2.0 Client ID
4. Add redirect URI: `http://localhost:8000/auth/google/callback`
5. Copy Client ID and Secret to `.env`

### Test OAuth
1. Restart application
2. Go to auth page
3. Click "Continue with Google"
4. Sign in with Google account
5. Redirected back logged in!

## Quick Test

### Test API (Terminal)
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","full_name":"Test"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -F "username=test@test.com" \
  -F "password=Test123!"

# Copy access_token from response

# Test protected endpoint
curl http://localhost:8000/api/policies \
  -H "Authorization: Bearer <paste_token_here>"
```

### Test UI (Browser)
1. Open `frontend/index.html`
2. Click "Login" → Login with credentials
3. Try to upload a policy (should work)
4. Click logout
5. Try to upload a policy (should show auth required)

## Troubleshooting

### "Database connection failed"
```bash
# Check if PostgreSQL is running
# Windows: services.msc → PostgreSQL
# Mac: brew services list
# Linux: systemctl status postgresql

# Start PostgreSQL if needed
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### "Could not validate credentials"
- Check if access token is included in request
- Token might be expired (15 min), try refreshing
- Clear localStorage and login again

### "Password does not meet requirements"
Password must have:
- 8+ characters
- Uppercase letter
- Lowercase letter
- Number
- Special character (!@#$%^&*)

Example: `MySecure123!`

### "Google OAuth error"
- Verify redirect URI matches exactly in Google Console
- Check Client ID and Secret in `.env`
- Restart application after changing `.env`

## Common Commands

```bash
# Check database
psql -U postgres -d insurance_claims -c "\dt"

# View users
psql -U postgres -d insurance_claims -c "SELECT * FROM users;"

# View logs
tail -f logs/app.log

# Reset database (WARNING: deletes all data)
psql -U postgres -c "DROP DATABASE insurance_claims;"
psql -U postgres -c "CREATE DATABASE insurance_claims;"
python run.py  # Recreates tables
```

## Password Requirements

✅ **Valid**: `MySecure123!`, `Test@Pass1`, `Admin#2024`
❌ **Invalid**: `password`, `12345678`, `Password` (no special char)

## API Endpoints

### Public
- `POST /auth/register` - Create account
- `POST /auth/login` - Get tokens
- `GET /auth/google/login` - OAuth redirect

### Protected (need Bearer token)
- `GET /auth/me` - Current user
- `POST /auth/logout` - End session
- `GET /api/policies` - List policies
- `POST /api/policies/index` - Upload policy
- `POST /api/documents/extract` - Extract claim
- `POST /api/claims/analyze/{id}` - Analyze claim

## Next Steps

1. ✅ Authentication working? → Read [AUTHENTICATION.md](AUTHENTICATION.md) for details
2. ✅ Want to customize? → Check `backend/config.py` for settings
3. ✅ Ready to deploy? → See README.md deployment section
4. ✅ Need help? → Check troubleshooting in AUTHENTICATION.md

## Quick Reference

| Task | Command/Action |
|------|----------------|
| Setup | `python setup_auth.py` |
| Start | `python run.py` |
| Login UI | `frontend/auth.html` |
| API Docs | `http://localhost:8000/docs` |
| Check Health | `http://localhost:8000/health` |
| View Logs | `logs/app.log` |
| Database | `psql -U postgres -d insurance_claims` |

---

**Need more help?** See [AUTHENTICATION.md](AUTHENTICATION.md) for complete documentation.

