# Project Structure

> [!info] Keeys Project Structure

## Overview

```
Keeys/
├── backend/                # FastAPI + GraphQL Backend
├── frontend/               # React + TypeScript Frontend
├── docs/                   # Documentation (Obsidian)
├── BOILERPLATE_README.md   # Template README
├── GRAPHQL_SETUP.md        # GraphQL Setup
├── README.md               # Main README
└── node_modules/           # Node dependencies (root)
```

## Backend

```
backend/
├── app/                      # Main application code
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── security.py        # JWT utilities
│   │   └── exceptions.py      # Custom exceptions (safe)
│   ├── database.py            # DB connection
│   ├── models/
│   │   ├── base.py           # Base model
│   │   └── user.py           # User model (with UUID)
│   ├── schemas/
│   │   ├── auth.py           # GraphQL auth schemas
│   │   └── graphql.py        # Root GraphQL schema
│   └── services/
│       └── user_service.py   # Business logic
├── tests/                    # Unit tests (pytest)
│   ├── conftest.py           # Fixtures
│   ├── test_models.py        # Model tests (10)
│   ├── test_security.py      # JWT tests (7)
│   ├── test_services.py      # Service tests (11)
│   ├── test_user_service_uuid.py  # UUID tests (5)
│   └── test_error_handling.py     # Security tests (18)
├── migrations/               # DB migrations
│   ├── auto_migrate.py       # Automatic migrations
│   ├── migrate_add_public_id.py   # Add UUID
│   ├── recreate_tables.py    # Recreate tables
│   └── README.md
├── scripts/                  # Utilities
│   ├── clear_users.py        # Clear users
│   ├── list_users.py         # List users
│   └── README.md
├── integration_tests/        # Integration tests
│   ├── check_error_safety.py # Check error safety
│   └── README.md
├── venv/                     # Virtual environment
├── Dockerfile                # Docker image
├── env.example               # .env example
├── main.py                   # Entry point
├── pytest.ini                # pytest configuration
├── railway.json              # Railway config
├── requirements.txt          # Dependencies
└── run_tests.sh             # Run tests with coverage
```

### Backend - Key Files

| File | Description |
|------|----------|
| `main.py` | Entry point, FastAPI and GraphQL setup |
| `app/database.py` | PostgreSQL connection via SQLAlchemy |
| `app/models/user.py` | User model with UUID and password hashing |
| `app/services/user_service.py` | CRUD operations for users |
| `app/schemas/auth.py` | GraphQL types and mutations for auth |
| `app/core/security.py` | JWT creation and verification |
| `app/core/exceptions.py` | Safe custom exceptions |
| `app/core/config.py` | Settings from .env |
| `migrations/auto_migrate.py` | Automatic migrations on start |
| `scripts/list_users.py` | User viewing utility |
| `scripts/clear_users.py` | User clearing utility |

## Frontend

```
frontend/
├── dist/                     # Built files
├── node_modules/             # Node dependencies
├── public/
│   └── vite.svg             # Public files
├── src/
│   ├── assets/
│   │   └── react.svg        # Resources
│   ├── components/
│   │   ├── LoginForm.tsx     # Login form
│   │   ├── ProtectedRoute.tsx # Route protection
│   │   └── RegisterForm.tsx  # Registration form
│   ├── contexts/
│   │   ├── AuthContext.tsx   # Auth management
│   │   └── ThemeContext.tsx  # Theme management
│   ├── graphql/
│   │   ├── __init__.ts
│   │   └── auth.ts           # Auth queries and mutations
│   ├── lib/
│   │   └── apollo.ts         # Apollo Client setup
│   ├── pages/
│   │   ├── AuthPage.tsx      # Login/registration page
│   │   └── DashboardPage.tsx # Protected dashboard
│   ├── App.css              # App styles
│   ├── App.tsx              # Main component with routing
│   ├── index.css            # Global styles
│   └── main.tsx             # React entry point
├── Dockerfile               # Docker image
├── env.example              # .env example file
├── eslint.config.js         # ESLint configuration
├── index.html               # HTML template
├── nginx.conf               # Nginx configuration
├── package.json             # Node dependencies and scripts
├── railway.json             # Railway configuration
├── README.md                # Frontend README
├── tsconfig.json            # TypeScript configuration
├── tsconfig.app.json        # TypeScript for application
├── tsconfig.node.json       # TypeScript for Node
├── vite.config.ts           # Vite configuration
└── yarn.lock                # Yarn lock file
```

### Frontend - Key Files

| File | Description |
|------|----------|
| `src/main.tsx` | React application entry point |
| `src/App.tsx` | Routing and main structure |
| `src/lib/apollo.ts` | Apollo Client with auth link |
| `src/contexts/AuthContext.tsx` | Auth state management |
| `src/graphql/auth.ts` | Auth GraphQL queries |
| `src/components/LoginForm.tsx` | Login form component |
| `src/components/RegisterForm.tsx` | Registration form component |
| `src/components/ProtectedRoute.tsx` | HOC for route protection |
| `src/pages/AuthPage.tsx` | Authentication page |
| `src/pages/DashboardPage.tsx` | Protected dashboard page |

## Documentation

```
docs/
└── obsidian/
    ├── README.md                    # Main documentation page
    ├── Quick Start.md               # Quick start
    ├── Authentication Setup.md      # Auth setup
    ├── Authentication Cheatsheet.md # Cheatsheet
    ├── Testing Guide.md             # Test guide
    ├── Project Structure.md         # This file
    ├── Backend Development.md       # Backend development
    └── Frontend Development.md      # Frontend development
```

## Configuration Files

### Backend

| File | Purpose |
|------|------------|
| `requirements.txt` | Python dependencies |
| `pytest.ini` | pytest settings |
| `.env` | Environment variables (not in git) |
| `env.example` | .env example |
| `Dockerfile` | Docker image |
| `railway.json` | Railway deployment |

### Frontend

| File | Purpose |
|------|------------|
| `package.json` | Node dependencies and scripts |
| `yarn.lock` | Dependency versions |
| `tsconfig.json` | TypeScript configuration |
| `vite.config.ts` | Vite build tool |
| `eslint.config.js` | Linter |
| `.env` | Environment variables (not in git) |
| `env.example` | .env example |

## Naming Conventions

### Backend (Python)

```python
# Files: snake_case
user_service.py
auth_schema.py

# Classes: PascalCase
class UserService:
class AuthPayload:

# Functions and variables: snake_case
def create_user():
user_data = {}

# Constants: UPPER_SNAKE_CASE
DATABASE_URL = "..."
SECRET_KEY = "..."
```

### Frontend (TypeScript/React)

```typescript
// Component files: PascalCase
LoginForm.tsx
AuthContext.tsx

// Utility files: camelCase
apollo.ts
auth.ts

// Components: PascalCase
const LoginForm: FC = () => {}

// Functions and variables: camelCase
const handleSubmit = () => {}
const userData = {}

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = "..."

// Types and interfaces: PascalCase
interface User {}
type AuthContextType = {}
```

## Git Structure

```
.git/
.gitignore              # Ignored files
  ├── .env              # Secrets
  ├── venv/             # Python venv
  ├── node_modules/     # Node modules
  ├── __pycache__/      # Python cache
  └── dist/             # Build files
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Default Ports

| Service | Port | URL |
|--------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| GraphQL Playground | 8000 | http://localhost:8000/graphql |
| Frontend Dev | 5173 | http://localhost:5173 |
| PostgreSQL | 5432 | localhost:5432 |

## Utilities

### Backend

#### Management scripts (scripts/)
```bash
# View users
python scripts/list_users.py

# Clear users
python scripts/clear_users.py
```

#### Migrations (migrations/)
```bash
# Automatically on application start
# Or manually:
python migrations/migrate_add_public_id.py
python migrations/recreate_tables.py
```

#### Tests
```bash
# Unit tests
pytest

# With coverage
./run_tests.sh

# Integration tests
python integration_tests/check_error_safety.py
```

### Frontend

```bash
# Development
yarn dev

# Build
yarn build

# Lint
yarn lint

# Preview production build
yarn preview
```

## Related Documents

- [[Quick Start]] - Quick start
- [[Authentication Setup]] - Auth setup
- [[Backend Development]] - Backend development
- [[Frontend Development]] - Frontend development

---

*Updated: 2025-10-09*
