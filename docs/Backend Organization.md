# Backend Organization

> [!info] Backend folder and file organization

## 📁 Folder Structure

```
backend/
├── app/                  # Main application code
├── tests/                # Unit tests (pytest)
├── migrations/           # Database migrations
├── scripts/              # Management utilities
└── integration_tests/    # Integration tests
```

## 📂 Folder Purpose

### app/ - Main Code
All production application code.

**Subfolders:**
- `core/` - Core (config, security, exceptions)
- `models/` - SQLAlchemy models
- `schemas/` - GraphQL schemas
- `services/` - Business logic
- `routers/` - REST API endpoints (empty, for future)
- `resolvers/` - GraphQL resolvers (empty, for future)

### tests/ - Unit Tests
Automated tests, run via pytest.

**Contains:**
- `conftest.py` - Fixtures for all tests
- `test_*.py` - Test modules

**Run:**
```bash
pytest
pytest -v
pytest --cov=app
```

**Statistics:** 51 tests, ~95% coverage, ~7 seconds

### migrations/ - DB Migrations
Scripts for database schema changes.

**Files:**
- `auto_migrate.py` - Automatic migrations (run on startup)
- `migrate_*.py` - Specific migrations
- `recreate_tables.py` - Complete DB rebuild (deletes data)

**Features:**
- ✅ Automatic run on application startup
- ✅ Idempotent (safe to run multiple times)
- ✅ Work on Railway automatically

**Manual run:**
```bash
python migrations/migrate_add_public_id.py
```

### scripts/ - Utilities
Helper scripts for development.

**Files:**
- `list_users.py` - Show all users
- `clear_users.py` - Delete all users

**Usage:**
```bash
python scripts/list_users.py
python scripts/clear_users.py
```

### integration_tests/ - Integration Tests
Tests via real HTTP API.

**Files:**
- `check_error_safety.py` - Check error safety

**Difference from unit tests:**
- Require running backend
- Make real HTTP requests
- Test end-to-end scenarios
- Run manually

**Usage:**
```bash
# 1. Start backend
python main.py

# 2. In another terminal:
python integration_tests/check_error_safety.py
```

## 🎯 Where to Add What

### New Database Model
```
app/models/my_model.py
```

### New GraphQL Type
```
app/schemas/my_schema.py
```

### New Service (business logic)
```
app/services/my_service.py
```

### New Test
```
tests/test_my_feature.py
```

### New Migration
```python
# 1. Create
migrations/migrate_add_new_field.py

# 2. Add to auto_migrate.py
migrations = [
    ("add_public_id", migrate_add_public_id_if_needed),
    ("add_new_field", migrate_add_new_field),  # Add
]
```

### New Utility
```
scripts/my_utility.py
```

### New Integration Test
```
integration_tests/test_my_integration.py
```

## 📋 Organization Rules

### Naming
- Modules: `snake_case.py` for all Python files
- Tests: `test_feature.py` for unit tests
- Migrations: `migrate_description.py` for migrations

- Classes: `PascalCase` for classes
- Test classes: `Test*` for test classes

- Functions: `snake_case` for functions
- Test functions: `test_*` for test functions

### Where NOT to Add Code

❌ **Don't add to backend root:**
- Utilities → `scripts/`
- Migrations → `migrations/`
- Tests → `tests/` or `integration_tests/`

❌ **Don't mix file types:**
- Production code → `app/`
- Tests → `tests/`
- Utilities → `scripts/`

## 🔄 Development Workflow

### 1. Model Change

```bash
# Edit model
app/models/user.py

# Create migration
migrations/migrate_add_field.py

# Add to auto_migrate.py

# Write tests
tests/test_new_model_feature.py

# Run tests
pytest
```

### 2. New Feature

```bash
# Model (if needed)
app/models/feature.py

# Service
app/services/feature_service.py

# GraphQL schema
app/schemas/feature.py

# Tests
tests/test_feature.py

# Run tests
pytest
```

### 3. Development Utility

```bash
# Create script
scripts/my_tool.py

# Add README to scripts/README.md

# Make executable
chmod +x scripts/my_tool.py
```

## 📊 Code Statistics

### Structure by Folders

```
app/              ~500 lines (production code)
tests/            ~1000 lines (51 tests)
migrations/       ~200 lines (3 migrations)
scripts/          ~100 lines (2 utilities)
integration_tests/ ~200 lines (1 test)

Total: ~2000 lines of code
```

### Test Coverage

```
app/models/       100% coverage
app/services/     100% coverage  
app/core/         95% coverage
app/schemas/      90% coverage

Overall: ~95% coverage
```

## 🧹 Maintaining Order

### Regular Checks

1. **No extra files in backend root**
2. **README.md in each special folder** (scripts, migrations, tests)
3. **`__init__.py` in each Python package**
4. **Tests for new code**

### When Adding File

Ask yourself:
- Is this production code? → `app/`
- Is this a test? → `tests/`
- Is this a migration? → `migrations/`
- Is this a utility? → `scripts/`
- Is this an integration test? → `integration_tests/`

## 🔗 Related Documents

- [[Project Structure]] - General project structure
- [[Railway Deployment]] - Deployment and migrations on Railway
- [[Testing Guide]] - Testing

---

*Updated: 2025-10-09*
