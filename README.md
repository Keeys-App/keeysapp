# Keeys - Translation Management System

> Localization management system with full authentication

## 🚀 Quick Start

### Requirements
- Python 3.12+
- Node.js 18+
- PostgreSQL
- Yarn

### Running Backend

**First, start PostgreSQL:**
```bash
# macOS (Homebrew)
brew services start postgresql@14

# or if Postgres.app is installed
# just launch the Postgres.app application
```

**Then start the backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend: http://localhost:8000

### Running Frontend
```bash
cd frontend
yarn dev
```
Frontend: http://localhost:5173

## 📚 Documentation

Full documentation is located in **Obsidian Vault**: `docs/obsidian/`

### 📖 Main Documents

| Document | Description |
|----------|----------|
| [README](docs/obsidian/README.md) | Main documentation page |
| [Quick Start](docs/obsidian/Quick%20Start.md) | Detailed quick start guide |
| [Authentication Setup](docs/obsidian/Authentication%20Setup.md) | Complete authentication system setup |
| [Authentication Cheatsheet](docs/obsidian/Authentication%20Cheatsheet.md) | Quick authentication reference |
| [Testing Guide](docs/obsidian/Testing%20Guide.md) | Testing guide (28 tests) |
| [Project Structure](docs/obsidian/Project%20Structure.md) | Detailed project structure |

### 🔍 How to Use Documentation

**In Obsidian (recommended):**
1. Open Obsidian
2. "Open folder as vault"
3. Select `docs/obsidian`
4. Use internal links for navigation

**In code editor:**
- Simply open `.md` files in `docs/obsidian/`

## 🏗️ Technology Stack

### Backend
- **FastAPI** - Modern web framework
- **Strawberry GraphQL** - GraphQL for Python
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** (pyjwt) - Authentication
- **bcrypt** - Password hashing
- **pytest** - Testing

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Radix UI** - UI components
- **Apollo Client** - GraphQL client
- **React Router** - Routing
- **Vite** - Build tool

## ✅ Implemented

### Authentication System
- ✅ User registration
- ✅ Login with JWT tokens
- ✅ Protected routes
- ✅ Password hashing (bcrypt)
- ✅ GraphQL API (queries & mutations)
- ✅ Authentication context on frontend
- ✅ Automatic token updates in headers
- ✅ Form validation

### Projects Module
- ✅ CRUD operations for projects (create, read, update, delete)
- ✅ Access control system (owner, admin, editor, viewer)
- ✅ Project member management
- ✅ Multi-language support (multiple languages per project)
- ✅ Color labels for projects
- ✅ Project statuses (active, archived, draft)
- ✅ UI with project cards (grid layout)
- ✅ Create/edit modal dialogs
- ✅ Access control checks on backend

### Testing
- ✅ 272 automated tests
- ✅ Code coverage ~95%
- ✅ Model tests
- ✅ Service tests
- ✅ Review/AI tests
- ✅ GraphQL tests
- ✅ Security/JWT tests
- ✅ Error handling tests

### UI/UX
- ✅ Beautiful forms with Radix UI
- ✅ Dark/light theme
- ✅ Client-side validation
- ✅ Error handling
- ✅ Responsive design
- ✅ Grid layout for project list
- ✅ Color picker for color selection
- ✅ Multi-select for languages

## 🧪 Testing

```bash
cd backend
source venv/bin/activate

# All tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

**Result:** ✅ 272 tests (~95% coverage)

**Includes:**
- ✅ AI Service & GraphQL tests
- ✅ GraphQL specific tests (Flow, Project, etc.)
- ✅ Key management & search tests
- ✅ Team service tests
- ✅ Security, Auth & JWT tests
- ✅ Service & Model tests

More details: [Testing Guide](docs/obsidian/Testing%20Guide.md)

## 🔐 Authentication

### GraphQL Playground
http://localhost:8000/graphql

**Registration:**
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "password123"
  }) {
    accessToken
    user { id username email }
  }
}
```

**Login:**
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "password123"
  }) {
    accessToken
    user { username }
  }
}
```

More details: [Authentication Setup](docs/obsidian/Authentication%20Setup.md)

## 📁 Project Structure

```
Keeys/
├── backend/                  # FastAPI + GraphQL
│   ├── app/                 # Application code
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # GraphQL schemas
│   │   ├── services/        # Business logic
│   │   └── core/            # Config, JWT, Exceptions
│   ├── tests/               # Unit tests (70)
│   ├── migrations/          # DB migrations (auto)
│   ├── scripts/             # Utilities
│   └── integration_tests/   # Integration tests
├── frontend/                # React + TypeScript
│   └── src/
│       ├── components/      # React components
│       ├── contexts/        # React contexts
│       ├── pages/           # Pages
│       └── graphql/         # GraphQL queries
└── docs/
    └── obsidian/            # Documentation
```

More details: [Project Structure](docs/obsidian/Project%20Structure.md)

## 🔗 Useful Links

| Service | URL |
|--------|-----|
| Backend API | http://localhost:8000 |
| GraphQL Playground | http://localhost:8000/graphql |
| Frontend App | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

## 🛠️ Development

### Backend
```bash
# Run with auto-reload
cd backend
source venv/bin/activate
python main.py

# Unit tests
pytest -v

# Coverage
pytest --cov=app --cov-report=html

# Utilities
python scripts/list_users.py
python scripts/clear_users.py

# Migrations (automatic on start or manual)
python migrations/migrate_add_public_id.py
```

### Frontend
```bash
# Dev server
cd frontend
yarn dev

# Linting
yarn lint

# Build
yarn build
```

## 🔄 Next Steps

### Translation Features
- [ ] Translation keys for projects
- [ ] Translation editor with multi-language support
- [ ] Import/export translations (JSON, YAML, CSV)
- [ ] Translation change history
- [ ] Translation comments

### Authentication Improvements
- [ ] Add password recovery
- [ ] Implement email confirmation
- [ ] Add OAuth (Google, GitHub)
- [ ] Implement refresh tokens

### Additional
- [ ] Add profile management
- [ ] Project search
- [ ] Filtering and sorting
- [ ] Project statistics
- [ ] API documentation

## 🤝 Contributing

1. Study the documentation in `docs/obsidian/`
2. Create a feature branch
3. Write code and tests
4. Ensure all tests pass
5. Create a Pull Request

## 📝 License

All rights reserved © 2025

---

**Documentation:** [docs/obsidian/](docs/obsidian/) | **Tests:** ✅ 70 passed (~95% coverage) | **Security:** UUID + Safe Errors
