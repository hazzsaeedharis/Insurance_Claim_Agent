# 🔐 Authentication Guide

Complete guide to the authentication system in Insurance Claim Agent.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Setup](#setup)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Overview

The Insurance Claim Agent uses a modern authentication system with:
- **Email/Password Login**: Traditional authentication with secure password hashing
- **Google OAuth2**: Single sign-on with Google accounts
- **JWT Tokens**: Stateless access tokens for API authentication
- **Refresh Tokens**: Long-lived tokens for session management
- **PostgreSQL**: Database-backed user storage

### Token Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. Login (email/password or Google)
       ▼
┌─────────────┐
│   Backend   │
└──────┬──────┘
       │ 2. Verify credentials
       │ 3. Generate tokens
       ▼
┌─────────────┐
│  Database   │ Store refresh token
└──────┬──────┘
       │ 4. Return tokens
       ▼
┌─────────────┐
│   Client    │ Store in localStorage + cookie
└──────┬──────┘
       │ 5. Use access token for API calls
       ▼
┌─────────────┐
│   Backend   │ Verify token on each request
└─────────────┘
```

## Architecture

### Components

#### Backend
- **`backend/auth/jwt.py`**: JWT token creation and verification
- **`backend/auth/password.py`**: Password hashing and validation
- **`backend/auth/oauth.py`**: Google OAuth2 integration
- **`backend/routers/auth.py`**: Authentication API endpoints
- **`backend/models/user.py`**: User database model
- **`backend/models/refresh_token.py`**: Refresh token storage

#### Frontend
- **`frontend/auth.html`**: Login/Register UI
- **`frontend/auth.js`**: Authentication logic
- **`frontend/auth-callback.html`**: OAuth callback handler
- **`frontend/app.js`**: Token management and API calls

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),  -- NULL for OAuth users
    google_id VARCHAR(255) UNIQUE,  -- NULL for email/password users
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(500) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key authentication packages:
- `sqlalchemy` - ORM for database
- `psycopg2-binary` - PostgreSQL driver
- `python-jose[cryptography]` - JWT handling
- `pwdlib[argon2]` - Password hashing
- `authlib` - OAuth2 client

### 2. Setup PostgreSQL

```bash
# Install PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
psql -U postgres
CREATE DATABASE insurance_claims;
\q
```

### 3. Configure Environment

Edit `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/insurance_claims

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your_secret_key_here

# JWT Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth2 (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 4. Setup Google OAuth2 (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google+ API"
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins:
   - `http://localhost:8000`
   - `http://localhost:3000`
7. Authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback`
8. Copy **Client ID** and **Client Secret** to `.env`

## Usage

### Email/Password Registration

```javascript
// Frontend
const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'SecurePass123!',
        full_name: 'John Doe'
    })
});

const user = await response.json();
```

### Email/Password Login

```javascript
// Frontend
const formData = new FormData();
formData.append('username', 'user@example.com');  // OAuth2 uses 'username'
formData.append('password', 'SecurePass123!');

const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    body: formData,
    credentials: 'include'  // Include cookies
});

const { access_token, refresh_token } = await response.json();

// Store tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

### Google OAuth Login

```javascript
// Frontend - Redirect to Google
window.location.href = 'http://localhost:8000/auth/google/login';

// Backend handles OAuth flow and redirects back with tokens
// Tokens are extracted from URL in auth-callback.html
```

### Making Authenticated Requests

```javascript
// Frontend
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, options);
    
    // Handle token expiration
    if (response.status === 401) {
        await refreshAccessToken();
        // Retry request
    }
    
    return response;
}

// Use it
const response = await authenticatedFetch('http://localhost:8000/api/policies');
```

### Token Refresh

```javascript
// Frontend
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('http://localhost:8000/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    const { access_token, refresh_token: newRefreshToken } = await response.json();
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', newRefreshToken);
}
```

### Logout

```javascript
// Frontend
async function logout() {
    const token = localStorage.getItem('access_token');
    
    await fetch('http://localhost:8000/auth/logout', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        credentials: 'include'
    });
    
    // Clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Redirect to login
    window.location.href = 'auth.html';
}
```

## API Reference

### POST /auth/register

Register a new user.

**Request:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-10-21T12:00:00Z"
}
```

### POST /auth/login

Login with email and password.

**Request (Form Data):**
```
username=user@example.com
password=SecurePass123!
```

**Response:**
```json
{
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 900
}
```

### POST /auth/refresh

Refresh access token.

**Request:**
```json
{
    "refresh_token": "eyJhbGci..."
}
```

**Response:**
```json
{
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 900
}
```

### POST /auth/logout

Logout and revoke refresh token.

**Headers:**
```
Authorization: Bearer eyJhbGci...
```

**Response:**
```json
{
    "message": "Successfully logged out"
}
```

### GET /auth/me

Get current user information.

**Headers:**
```
Authorization: Bearer eyJhbGci...
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-10-21T12:00:00Z"
}
```

### GET /auth/google/login

Redirect to Google OAuth login.

**Response:** 302 Redirect to Google

### GET /auth/google/callback

Handle Google OAuth callback.

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: CSRF protection token

**Response:** 302 Redirect to frontend with tokens

## Security

### Password Security

#### Hashing Algorithm
- **Argon2id**: Memory-hard algorithm recommended by OWASP
- **Cost Factor**: Default parameters (memory: 65536 KB, iterations: 3, parallelism: 4)
- **Salt**: Automatically generated per password

#### Password Requirements
```python
# Enforced in backend/auth/password.py
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
```

### JWT Security

#### Access Token
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiry**: 15 minutes
- **Storage**: localStorage (client-side)
- **Claims**:
  ```json
  {
    "sub": "user@example.com",
    "user_id": 1,
    "exp": 1634567890,
    "iat": 1634567000,
    "type": "access"
  }
  ```

#### Refresh Token
- **Algorithm**: HS256
- **Expiry**: 7 days
- **Storage**: httpOnly cookie + database
- **Revocation**: Supported via database flag
- **Claims**:
  ```json
  {
    "sub": "user@example.com",
    "user_id": 1,
    "exp": 1635172800,
    "iat": 1634567000,
    "type": "refresh"
  }
  ```

### OAuth2 Security

#### CSRF Protection
- **State Parameter**: Random 32-byte token
- **Storage**: httpOnly cookie (10-minute expiry)
- **Verification**: State must match on callback

#### Token Exchange
- Authorization code exchanged server-side
- No tokens exposed to client during OAuth flow
- HTTPS required in production

### API Security

#### Protected Endpoints
All endpoints under `/api/` require authentication:
- `/api/policies/*`
- `/api/documents/*`
- `/api/claims/*`

#### CORS Configuration
```python
allow_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    settings.frontend_url
]
allow_credentials = True
allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
allow_headers = ["Content-Type", "Authorization"]
```

#### Rate Limiting (Planned)
- Login: 5 attempts per minute per IP
- Register: 3 attempts per minute per IP
- Token refresh: 10 attempts per minute per user

## Troubleshooting

### Common Issues

#### 1. "Could not validate credentials"

**Cause:** Invalid or expired access token

**Solution:**
```javascript
// Implement automatic token refresh
if (response.status === 401) {
    await refreshAccessToken();
    // Retry request
}
```

#### 2. "Database connection failed"

**Cause:** PostgreSQL not running or wrong credentials

**Solution:**
```bash
# Check PostgreSQL status
# Windows: services.msc → PostgreSQL
# Mac: brew services list
# Linux: systemctl status postgresql

# Verify connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

#### 3. "Invalid refresh token"

**Cause:** Refresh token expired or revoked

**Solution:**
```javascript
// Redirect to login
localStorage.clear();
window.location.href = 'auth.html';
```

#### 4. "Google OAuth error"

**Cause:** Invalid OAuth2 configuration

**Solution:**
1. Verify redirect URI matches exactly in Google Console
2. Check Client ID and Secret in `.env`
3. Ensure Google+ API is enabled

#### 5. "Password does not meet requirements"

**Cause:** Weak password

**Solution:**
```
Use a password with:
- At least 8 characters
- Uppercase and lowercase letters
- Numbers
- Special characters
Example: MySecure123!
```

### Debug Mode

Enable detailed logging:

```python
# backend/config.py
debug_mode: bool = True

# Check logs
tail -f logs/app.log
```

### Testing Authentication

```bash
# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -F "username=test@example.com" \
  -F "password=Test123!"

# Test protected endpoint
curl http://localhost:8000/api/policies \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Best Practices

### Production Deployment

1. **Use HTTPS**: Always use TLS/SSL in production
2. **Secure Cookies**: Set `secure=True` for cookies
3. **Strong Secret**: Generate a strong JWT secret key
4. **Database Security**: Use strong PostgreSQL password
5. **Rate Limiting**: Implement rate limiting on auth endpoints
6. **Monitoring**: Log authentication events
7. **Token Rotation**: Implement token rotation policy
8. **Account Lockout**: Lock accounts after failed attempts

### Development

1. **Never commit** `.env` file
2. **Use different secrets** for dev/prod
3. **Test token expiration** scenarios
4. **Validate all inputs** on both client and server
5. **Handle errors gracefully** in UI

---

**For more information, see:**
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

