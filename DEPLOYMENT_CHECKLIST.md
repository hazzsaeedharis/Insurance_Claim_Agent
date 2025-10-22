# 🚀 Deployment Checklist - Authentication

Security checklist before deploying to production.

## ⚠️ Critical Security Items

### 1. Environment Variables
- [ ] Generate NEW `SECRET_KEY` for production (never reuse dev key)
  ```bash
  openssl rand -hex 32
  ```
- [ ] Set strong PostgreSQL password
- [ ] Update `DATABASE_URL` with production credentials
- [ ] Set `DEBUG_MODE=False` in production
- [ ] Update `FRONTEND_URL` to production domain
- [ ] Update `GOOGLE_REDIRECT_URI` to production callback URL

### 2. HTTPS/SSL
- [ ] Enable HTTPS for all endpoints
- [ ] Set `secure=True` for cookies in `backend/routers/auth.py`:
  ```python
  response.set_cookie(
      key="refresh_token",
      value=refresh_token_str,
      httponly=True,
      secure=True,  # ← Change to True
      samesite="strict",  # ← Change to strict
      max_age=...
  )
  ```
- [ ] Update CORS origins to production domains only
- [ ] Enable HSTS headers

### 3. Database Security
- [ ] Use strong PostgreSQL password (16+ chars, mixed)
- [ ] Restrict database access to application server only
- [ ] Enable SSL for database connections
- [ ] Set up database backups (daily minimum)
- [ ] Use connection pooling limits
- [ ] Enable database audit logging

### 4. OAuth2 Configuration
- [ ] Register production domain in Google Cloud Console
- [ ] Add production redirect URIs
- [ ] Use separate OAuth credentials for production
- [ ] Restrict OAuth scopes to minimum required
- [ ] Enable OAuth consent screen

### 5. Rate Limiting
- [ ] Implement rate limiting on auth endpoints:
  ```python
  # Add to backend/routers/auth.py
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  
  @router.post("/login")
  @limiter.limit("5/minute")
  async def login(...):
      ...
  ```
- [ ] Set limits:
  - Login: 5 attempts/minute
  - Register: 3 attempts/minute
  - Refresh: 10 attempts/minute

### 6. Logging & Monitoring
- [ ] Enable production logging
- [ ] Log authentication events (login, logout, failed attempts)
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor failed login attempts
- [ ] Alert on suspicious activity
- [ ] Log token refresh events

### 7. Token Security
- [ ] Verify `ACCESS_TOKEN_EXPIRE_MINUTES=15` (or less)
- [ ] Verify `REFRESH_TOKEN_EXPIRE_DAYS=7` (or less)
- [ ] Implement token rotation on refresh
- [ ] Add token revocation on password change
- [ ] Clean up expired tokens regularly

### 8. Password Policy
- [ ] Enforce password complexity (already implemented)
- [ ] Add password history (prevent reuse)
- [ ] Implement account lockout after 5 failed attempts
- [ ] Add CAPTCHA after 3 failed attempts
- [ ] Force password change every 90 days (optional)

### 9. Input Validation
- [ ] Validate all user inputs
- [ ] Sanitize email addresses
- [ ] Check for SQL injection (SQLAlchemy protects, but verify)
- [ ] Prevent XSS in user-generated content
- [ ] Validate file uploads (if any)

### 10. Dependencies
- [ ] Update all dependencies to latest stable versions
- [ ] Run security audit:
  ```bash
  pip install safety
  safety check
  ```
- [ ] Remove unused dependencies
- [ ] Pin dependency versions in requirements.txt

## 🔧 Configuration Checklist

### Environment File (.env)
```env
# Production values
DEBUG_MODE=False
API_HOST=0.0.0.0
API_PORT=8000

# Strong secret key
SECRET_KEY=<64-char-hex-string>

# Production database
DATABASE_URL=postgresql://user:strong_password@db.example.com:5432/insurance_claims

# Production OAuth
GOOGLE_CLIENT_ID=<prod_client_id>
GOOGLE_CLIENT_SECRET=<prod_client_secret>
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback

# Production frontend
FRONTEND_URL=https://yourdomain.com

# Security headers
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### CORS Configuration
Update `backend/api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Cookie Settings
Update `backend/routers/auth.py`:
```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token_str,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="strict",  # Strict CSRF protection
    domain="yourdomain.com",  # Set domain
    max_age=settings.refresh_token_expire_days * 24 * 60 * 60
)
```

## 🧪 Pre-Deployment Testing

### Functional Tests
- [ ] Test user registration
- [ ] Test email/password login
- [ ] Test Google OAuth login
- [ ] Test token refresh
- [ ] Test logout
- [ ] Test protected endpoints
- [ ] Test token expiration
- [ ] Test invalid credentials
- [ ] Test concurrent sessions

### Security Tests
- [ ] Test SQL injection attempts
- [ ] Test XSS attempts
- [ ] Test CSRF protection
- [ ] Test brute force protection
- [ ] Test token tampering
- [ ] Test expired token handling
- [ ] Test revoked token handling
- [ ] Test OAuth state parameter validation

### Load Tests
- [ ] Test with 100 concurrent users
- [ ] Test login endpoint under load
- [ ] Test token refresh under load
- [ ] Monitor database connections
- [ ] Check memory usage
- [ ] Check CPU usage

## 📊 Monitoring Setup

### Metrics to Track
- [ ] Login success rate
- [ ] Login failure rate
- [ ] Token refresh rate
- [ ] Active sessions count
- [ ] Failed authentication attempts
- [ ] Database connection pool usage
- [ ] API response times
- [ ] Error rates

### Alerts to Configure
- [ ] High failed login rate (>10/minute)
- [ ] Database connection failures
- [ ] High API error rate (>5%)
- [ ] Slow response times (>2s)
- [ ] Disk space low (<10%)
- [ ] Memory usage high (>80%)

## 🔐 Compliance Checklist

### GDPR (if applicable)
- [ ] Add privacy policy
- [ ] Implement data export
- [ ] Implement data deletion
- [ ] Add consent management
- [ ] Log data access
- [ ] Implement data retention policy

### General
- [ ] Document authentication flow
- [ ] Create incident response plan
- [ ] Set up backup procedures
- [ ] Define password reset process
- [ ] Create user support documentation

## 🚀 Deployment Steps

### 1. Pre-Deployment
```bash
# 1. Update code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run security audit
safety check

# 4. Run tests
pytest backend/tests/

# 5. Check linting
flake8 backend/
```

### 2. Database Migration
```bash
# 1. Backup database
pg_dump -U user insurance_claims > backup_$(date +%Y%m%d).sql

# 2. Run migrations (if using Alembic)
alembic upgrade head

# 3. Verify tables
psql -U user -d insurance_claims -c "\dt"
```

### 3. Deploy Application
```bash
# 1. Set environment variables
export DEBUG_MODE=False
export SECRET_KEY=<production_key>
# ... other vars

# 2. Start application
gunicorn backend.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### 4. Post-Deployment
- [ ] Verify health endpoint: `https://yourdomain.com/health`
- [ ] Test login flow
- [ ] Check logs for errors
- [ ] Monitor metrics dashboard
- [ ] Test from different locations
- [ ] Verify SSL certificate
- [ ] Test OAuth flow
- [ ] Check database connections

## 🔄 Rollback Plan

If deployment fails:

1. **Stop application**
   ```bash
   pkill -f gunicorn
   ```

2. **Restore database** (if needed)
   ```bash
   psql -U user insurance_claims < backup_YYYYMMDD.sql
   ```

3. **Revert code**
   ```bash
   git checkout <previous_commit>
   ```

4. **Restart application**
   ```bash
   python run.py
   ```

## 📝 Post-Deployment Checklist

### Day 1
- [ ] Monitor error logs
- [ ] Check authentication metrics
- [ ] Verify all features working
- [ ] Test from multiple devices
- [ ] Check database performance

### Week 1
- [ ] Review security logs
- [ ] Check for suspicious activity
- [ ] Monitor resource usage
- [ ] Gather user feedback
- [ ] Update documentation

### Month 1
- [ ] Security audit
- [ ] Performance review
- [ ] Update dependencies
- [ ] Review access logs
- [ ] Plan improvements

## 🆘 Emergency Contacts

Document these before deployment:

- **DevOps Lead**: [Name, Phone, Email]
- **Security Team**: [Contact Info]
- **Database Admin**: [Contact Info]
- **On-Call Engineer**: [Contact Info]
- **Hosting Provider Support**: [Contact Info]

## 📚 Documentation Links

- Production runbook: [Link]
- Incident response plan: [Link]
- Architecture diagram: [Link]
- API documentation: [Link]
- User guide: [Link]

---

## ✅ Final Sign-Off

Before going live, confirm:

- [ ] All critical security items completed
- [ ] All tests passing
- [ ] Monitoring configured
- [ ] Backups working
- [ ] Rollback plan tested
- [ ] Team notified
- [ ] Documentation updated

**Deployed by**: _______________
**Date**: _______________
**Version**: _______________
**Approved by**: _______________

---

**Remember**: Security is an ongoing process, not a one-time task. Regular audits and updates are essential!

