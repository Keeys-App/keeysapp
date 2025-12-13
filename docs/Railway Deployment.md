# Railway Deployment

> [!info] Railway deployment guide

## Overview

Railway automatically deploys backend and frontend on git push.

## 🚀 Quick Deploy

### 1. Preparation

Make sure you have:
- Account on [Railway.app](https://railway.app)
- Railway CLI installed (optional)

### 2. Create Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your repository

### 3. Backend Setup

Railway will automatically detect `railway.json` and deploy backend.

**Environment variables (set automatically):**
- `DATABASE_URL` - Railway PostgreSQL
- `PORT` - Application port

**Additional variables (set manually):**
```env
SECRET_KEY=your-production-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> [!warning] SECRET_KEY
> Generate secure key for production!
> ```python
> import secrets
> print(secrets.token_urlsafe(32))
> ```

### 4. Frontend Setup

1. Add new service in project
2. Select `frontend` folder
3. Set variables:

```env
VITE_API_URL=https://your-backend-url.railway.app
```

### 5. PostgreSQL Database

Railway can automatically create PostgreSQL:

1. In project click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically link with backend (set `DATABASE_URL`)

## 🔄 Migrations on Railway

### Automatic Migrations

Migrations run **automatically** on application startup!

```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    # Automatic migrations
    from migrations.auto_migrate import run_all_migrations
    run_all_migrations()
    
    yield
```

**What happens:**
1. Railway runs `python main.py`
2. On startup checks for needed migrations
3. If `public_id` column missing - it's added
4. UUIDs generated for existing users
5. Application starts

**Benefits:**
- ✅ No manual action needed
- ✅ Safe - checks before running
- ✅ Idempotent - can run multiple times
- ✅ Works on every deploy

### Manual Migration Run

If you need to run migration manually on Railway:

```bash
# Via Railway CLI
railway run python migrations/migrate_add_public_id.py

# Or via Railway Shell
railway shell
source venv/bin/activate
python migrations/migrate_add_public_id.py
```

## 📝 Railway Configuration

### backend/railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### frontend/railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "yarn build && yarn preview"
  }
}
```

## 🔧 Troubleshooting

### Migration didn't run

**Check logs:**
```bash
railway logs
```

**Look for:**
```
🔄 Checking for pending migrations...
✅ Migration: public_id column added successfully
```

### Database connection failed

**Check:**
1. PostgreSQL service created and running
2. `DATABASE_URL` set automatically by Railway
3. Backend and Database in same project

### Migration crashed

**Solution:**
1. Check logs: `railway logs`
2. Try manual run via Railway Shell
3. As last resort - recreate tables (will delete data):

```bash
railway shell
python migrations/recreate_tables.py
```

## 🔐 Production Security

### Required Settings

```env
# Railway Environment Variables
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=<auto-set-by-railway>
PORT=<auto-set-by-railway>
ENVIRONMENT=production
DEBUG=False
```

### CORS Setup

Update `main.py` for production:

```python
# Development
if settings.environment == "development":
    allow_origins = ["*"]
else:
    # Production - only your domains
    allow_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://your-app.railway.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Migration Monitoring

### Migration Logs

Railway automatically logs:

```
INFO: Application startup
🔄 Checking for pending migrations...
Checking migration: add_public_id
✅ Migration: public_id column already exists, skipping
✅ Migrations check complete: 1/1 successful
INFO: Application startup complete
```

### On First Deploy

```
🔄 Migration: Adding public_id column to users table
✅ Column added
✅ Generated UUIDs for 0 user(s)
✅ Migration: public_id column added successfully
```

## 🎯 Best Practices

1. **Automatic migrations** - Use `auto_migrate.py` (already configured)
2. **Idempotency** - Migrations safe to run multiple times
3. **Logging** - Check Railway logs after deploy
4. **Backup** - Railway makes automatic backups
5. **Rollback** - Have rollback plan in git

## 🔄 Deploy Process

```
1. git push
   ↓
2. Railway detects changes
   ↓
3. Railway builds application
   ↓
4. Starts main.py
   ↓
5. Creates tables (if needed)
   ↓
6. Runs migrations (automatically)
   ↓
7. Application ready ✅
```

## 📱 Railway CLI

### Installation

```bash
npm install -g @railway/cli
```

### Commands

```bash
# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run command
railway run python migrations/migrate_add_public_id.py

# Open shell
railway shell

# View variables
railway variables
```

## 🆕 Adding New Migration

### 1. Create Script

```python
# migrations/migrate_add_new_field.py
def migrate_add_new_field():
    if check_column_exists('users', 'new_field'):
        logger.info("Column exists, skipping")
        return True
    
    # Add column
    # ...
    return True
```

### 2. Add to auto_migrate.py

```python
def run_all_migrations():
    migrations = [
        ("add_public_id", migrate_add_public_id_if_needed),
        ("add_new_field", migrate_add_new_field),  # New migration
    ]
    # ...
```

### 3. Commit and Push

```bash
git add .
git commit -m "Add migration for new_field"
git push
```

Railway will automatically run new migration on deploy!

## 🔗 Useful Links

- [Railway Docs](https://docs.railway.app/)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)
- [Environment Variables](https://docs.railway.app/develop/variables)

## Related Documents

- [[Quick Start]] - Local development
- [[Security Best Practices]] - Security
- [[Project Structure]] - Project structure

---

*Updated: 2025-10-09*
