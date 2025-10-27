# 🧪 TEST NOW - Quick Testing Guide

## ✅ What I Just Did

1. ✅ Installed all authentication dependencies
2. ✅ Started the application in background

## 🚀 Test Authentication (5 Minutes)

### Step 1: Open the Auth Page

Open your browser and navigate to:
```
file:///D:/Desktop/Insurance_Claim_Agent/frontend/auth.html
```

Or just open `frontend/auth.html` by double-clicking it.

### Step 2: Register a New Account

1. Click the **"Register"** tab
2. Fill in:
   - **Full Name**: `Test User`
   - **Email**: `test@example.com`
   - **Password**: `Test123!` (must have uppercase, lowercase, number, special char)
3. Click **"Create Account"**
4. You should see: ✅ "Account created successfully!"

### Step 3: Login

1. Switch to **"Login"** tab (or wait 2 seconds, it auto-switches)
2. Enter:
   - **Email**: `test@example.com`
   - **Password**: `Test123!`
3. Click **"Login"**
4. You should be redirected to `index.html` automatically!

### Step 4: Test Protected Features

1. You should now see your name in the navigation bar (top right)
2. Try to:
   - Upload a policy (should work ✅)
   - Submit a claim (should work ✅)
   - Access the demo section (should work ✅)

### Step 5: Test Logout

1. Click on your name in the navigation bar
2. Confirm logout
3. You'll be redirected to the auth page
4. Try to access the demo section → Should show "Authentication Required" overlay

## 🧪 Test API Directly (Optional)

### Test 1: Register via API

Open PowerShell and run:

```powershell
$body = @{
    email = "api@test.com"
    password = "ApiTest123!"
    full_name = "API Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

Expected: User details returned

### Test 2: Login via API

```powershell
$form = @{
    username = "api@test.com"
    password = "ApiTest123!"
}

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -Body $form

$response
# Save the access token
$token = $response.access_token
```

Expected: Access token and refresh token returned

### Test 3: Access Protected Endpoint

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/policies" `
    -Headers $headers
```

Expected: List of policies (or empty list if none uploaded)

### Test 4: Get Current User

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/auth/me" `
    -Headers $headers
```

Expected: Your user information

## 🔍 Check Application Status

### View API Documentation

Open browser:
```
http://localhost:8000/docs
```

You should see all the new authentication endpoints:
- `/auth/register`
- `/auth/login`
- `/auth/refresh`
- `/auth/logout`
- `/auth/me`
- `/auth/google/login`
- `/auth/google/callback`

### Check Health

```
http://localhost:8000/health
```

Should show database connection status.

## ⚠️ Troubleshooting

### "Database connection failed"

**Issue**: No PostgreSQL or SQLite database

**Quick Fix**: The app should create SQLite automatically. If not, check logs:

```powershell
Get-Content logs\app.log -Tail 50
```

### "Could not validate credentials"

**Issue**: Token expired or invalid

**Fix**: 
1. Clear browser localStorage (F12 → Application → Local Storage → Clear)
2. Login again

### "Password does not meet requirements"

**Issue**: Weak password

**Fix**: Use password with:
- 8+ characters
- Uppercase letter (A-Z)
- Lowercase letter (a-z)
- Number (0-9)
- Special character (!@#$%^&*)

Example: `MySecure123!`

### Application not starting

**Check if it's running:**

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

**View logs:**

```powershell
Get-Content logs\app.log -Tail 50
```

**Restart:**

```powershell
# Stop
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process

# Start
py run.py
```

## 📊 What to Check

After testing, verify:

- ✅ Can register new user
- ✅ Can login with email/password
- ✅ Token stored in localStorage
- ✅ Can access protected endpoints
- ✅ Can logout
- ✅ Protected sections show auth overlay when not logged in
- ✅ API documentation shows auth endpoints
- ✅ Health check shows database status

## 🎯 Next Steps

### If Everything Works:

1. **Setup PostgreSQL** (for production):
   ```powershell
   # Download from: https://www.postgresql.org/download/windows/
   # Or use Docker:
   docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
   ```

2. **Update .env**:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/insurance_claims
   ```

3. **Setup Google OAuth** (optional):
   - Follow instructions in `AUTHENTICATION.md`
   - Get credentials from Google Cloud Console
   - Add to `.env`

### If Something Doesn't Work:

1. Check `logs/app.log` for errors
2. Read `AUTHENTICATION.md` for detailed troubleshooting
3. Check `QUICK_START_AUTH.md` for setup help

## 📚 Documentation

- **Complete Guide**: `AUTHENTICATION.md`
- **Quick Start**: `QUICK_START_AUTH.md`
- **Deployment**: `DEPLOYMENT_CHECKLIST.md`
- **Implementation Summary**: `AUTHENTICATION_IMPLEMENTATION_SUMMARY.md`

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Can't access auth.html | Open as file:/// URL or serve via HTTP server |
| Login redirects to wrong page | Check FRONTEND_URL in .env |
| Token not working | Clear localStorage and login again |
| Database errors | Check DATABASE_URL in .env |
| Google OAuth not working | Verify credentials in Google Console |

---

**Ready to test?** Open `frontend/auth.html` and register your first account! 🚀

