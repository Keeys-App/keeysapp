# Environment Variables

> [!info] Complete description of all project environment variables

## 📋 Overview

All environment variables are stored in `.env` file in `backend/` root. Use `backend/env.example` as template.

## 🗄️ Database

### DATABASE_URL

**Description:** PostgreSQL database connection URL

**Format:** `postgresql://username:password@host:port/database_name`

**Examples:**
```env
# Local development
DATABASE_URL=postgresql://locales_user:locales_password@localhost:5432/locales_db

# Railway (automatic)
DATABASE_URL=postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway

# Docker
DATABASE_URL=postgresql://postgres:postgres@db:5432/locales
```

**Required:** ✅ Yes

**Security:**
- ⚠️ Never commit `.env` file to git
- ⚠️ Don't store passwords in plain text in code
- ⚠️ Use different passwords for dev/prod

## 🔐 Security (JWT)

### JWT_SECRET_KEY

**Description:** Secret key for signing and verifying JWT tokens

**Format:** Random string of 32+ characters

**Generation:**
```bash
# Method 1: Python (recommended)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32

# Method 3: Python script
python3 << EOF
import secrets
print(secrets.token_urlsafe(32))
EOF
```

**Example:**
```env
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

**Required:** ✅ Yes

**Security:**
- 🔴 CRITICAL: Use different keys for dev/prod
- 🔴 CRITICAL: Never commit real key to git
- 🔴 CRITICAL: Change key on compromise (all tokens become invalid)
- ✅ Minimum 32 characters
- ✅ Use cryptographically strong generator (`secrets`, not `random`)

### JWT_ALGORITHM

**Description:** Encryption algorithm for JWT tokens

**Format:** Algorithm name

**Values:**
- `HS256` - HMAC SHA-256 (recommended, default)
- `HS384` - HMAC SHA-384
- `HS512` - HMAC SHA-512
- `RS256` - RSA SHA-256 (requires public/private key pair)

**Example:**
```env
JWT_ALGORITHM=HS256
```

**Required:** ❌ No (default: `HS256`)

**Recommendation:** Keep `HS256` if unsure what to choose

### ACCESS_TOKEN_EXPIRE_MINUTES

**Description:** JWT token lifetime in minutes

**Format:** Integer (minutes)

**Examples:**
```env
# 30 minutes (production, high security)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 7 days (development, convenience)
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 1 day
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 1 year (mobile apps)
ACCESS_TOKEN_EXPIRE_MINUTES=525600
```

**Conversion:**
- 1 hour = 60 minutes
- 1 day = 1440 minutes (24 * 60)
- 7 days = 10080 minutes (7 * 24 * 60)
- 30 days = 43200 minutes (30 * 24 * 60)
- 1 year = 525600 minutes (365 * 24 * 60)

**Required:** ❌ No (default: `525600` = 1 year)

**Recommendations:**
- **Development:** 7 days (10080) - no need to constantly login
- **Production Web:** 30 minutes - requires refresh token mechanism
- **Production Mobile:** 30-90 days - balance of convenience and security
- **Internal tools:** 1 year - convenience for employees

**Tradeoffs:**
- ⬆️ Longer time = more convenient for users, but less secure
- ⬇️ Shorter time = safer, but requires more frequent logins

## 🌍 Environment

### ENVIRONMENT

**Description:** Application environment type

**Format:** String

**Values:**
- `development` - Development (default)
- `production` - Production
- `staging` - Staging environment
- `testing` - Automated tests

**Example:**
```env
ENVIRONMENT=development
```

**Required:** ❌ No (default: `development`)

**Impact:**
- Logging (more verbose in development)
- CORS policies (stricter in production)
- Error handling (detailed in development)

### DEBUG

**Description:** Debug mode

**Format:** Boolean (`true` / `false`)

**Example:**
```env
# Development
DEBUG=true

# Production
DEBUG=false
```

**Required:** ❌ No (default: `true`)

**Impact:**
- ✅ `true`: Detailed errors, hot reload, debug logs
- ❌ `false`: Hide error details, production optimizations

## 🚀 Server

### PORT

**Description:** Port for backend server

**Format:** Integer

**Example:**
```env
PORT=8000
```

**Required:** ❌ No (default: `8000`)

**Note:**
- Railway automatically sets port
- In local development usually `8000`
- Frontend expects backend on `8000` (or `VITE_API_URL`)

## 📝 Complete .env File Example

### Development (local development)

```env
# Database
DATABASE_URL=postgresql://locales_user:locales_password@localhost:5432/locales_db

# Security - JWT
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Environment
ENVIRONMENT=development
DEBUG=true
PORT=8000
```

### Production

```env
# Database (provided by Railway)
DATABASE_URL=postgresql://postgres:***@containers-us-west-123.railway.app:5432/railway

# Security - JWT
JWT_SECRET_KEY=***PRODUCTION_SECRET_KEY***
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 30 minutes

# Environment
ENVIRONMENT=production
DEBUG=false
PORT=8000
```

## 🛠️ Setup from Scratch

### Step 1: Copy Template

```bash
cd backend
cp env.example .env
```

### Step 2: Generate JWT_SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy result, for example:
```
fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

### Step 3: Edit .env

```bash
nano .env  # or any other editor
```

Fill in:
```env
DATABASE_URL=postgresql://locales_user:locales_password@localhost:5432/locales_db
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=development
DEBUG=true
```

### Step 4: Verify

```bash
# Activate venv
source venv/bin/activate

# Start server
python main.py
```

If everything is OK, you'll see:
```
Database URL: postgresql://locales_user:***@localhost:5432/locales_db
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## ⚠️ Important Warnings

### Don't Commit .env

**`.gitignore` file should contain:**
```gitignore
.env
.env.local
.env.*.local
```

**Check:**
```bash
git status
# .env should NOT appear in list
```

### Different Keys for Environments

| Environment | JWT_SECRET_KEY | ACCESS_TOKEN_EXPIRE |
|-----------|----------------|---------------------|
| Development | `dev_secret_123` | 10080 (7 days) |
| Staging | `staging_secret_456` | 1440 (1 day) |
| Production | `prod_secret_789` | 30 (30 minutes) |

### Railway Automatic Variables

Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection
- `PORT` - server port
- `RAILWAY_ENVIRONMENT` - environment (production/staging)

You only need to add:
- `JWT_SECRET_KEY` ⚠️ REQUIRED
- `JWT_ALGORITHM` (optional)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (optional)

## 🔗 Related Documents

- [[Quick Start]] - Quick start with variable setup
- [[Security Best Practices]] - Security and JWT tokens
- [[Railway Deployment]] - Setting variables on Railway
- [[Authentication Setup]] - Authentication system

## 📚 Additional Resources

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Python secrets module](https://docs.python.org/3/library/secrets.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

*Updated: 2025-10-10*
