# Authentication Cheatsheet

> [!tip] Quick reference for authentication system

## 🚀 Quick Commands

### Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend
```bash
cd frontend
yarn dev
```

## 📁 Key Files

### Backend
```
backend/app/
├── models/user.py              # User model
├── services/user_service.py    # User operations
├── schemas/auth.py             # GraphQL auth types
├── schemas/graphql.py          # Root schema
└── core/
    ├── security.py             # JWT utilities
    └── config.py               # Settings
```

### Frontend
```
frontend/src/
├── contexts/AuthContext.tsx    # Auth state
├── components/
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── ProtectedRoute.tsx
├── pages/
│   ├── AuthPage.tsx
│   └── DashboardPage.tsx
├── graphql/auth.ts             # Auth queries
└── lib/apollo.ts               # Apollo with auth
```

## 🔑 GraphQL API

### Registration
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "secret123"
  }) {
    accessToken
    user { id username email }
  }
}
```

### Login
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "secret123"
  }) {
    accessToken
    user { id username email }
  }
}
```

### Current User
```graphql
query {
  me {
    id username email isActive
  }
}
```
**Headers:** `Authorization: Bearer <token>`

## 🎨 Frontend

### Using Auth Context
```tsx
import { useAuth } from '../contexts/AuthContext';

function Component() {
  const { user, token, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <div>Please login</div>;
  }
  
  return <div>Welcome, {user?.username}!</div>;
}
```

### Route Protection
```tsx
<Route
  path="/protected"
  element={
    <ProtectedRoute>
      <YourComponent />
    </ProtectedRoute>
  }
/>
```

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🧪 Testing

```bash
# All tests
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Specific file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::TestUserModel::test_password_hashing
```

### Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Access protected route when authenticated
- [ ] Redirect to /auth when not authenticated
- [ ] Logout function
- [ ] Token persists after page refresh
- [ ] GraphQL query `me` works with token
- [ ] Wrong credentials show error
- [ ] Password validation (min 6 characters)
- [ ] Email validation

## 🛠️ Common Tasks

### Add Protected Query
```python
# backend/app/schemas/graphql.py
@strawberry.field
def my_protected_query(self, info: Info) -> str:
    # Get user from context
    request = info.context.get("request")
    auth_header = request.headers.get("Authorization")
    # ... verify token ...
    return "Protected data"
```

### Add Protected Route
```tsx
// frontend/src/App.tsx
<Route
  path="/new-page"
  element={
    <ProtectedRoute>
      <NewPage />
    </ProtectedRoute>
  }
/>
```

### Check Admin Rights
```tsx
const { user } = useAuth();

if (user?.isSuperuser) {
  // Show admin features
}
```

## 📝 User Model Fields

| Field | Type | Description |
|------|-----|----------|
| `id` | Integer | Primary key |
| `email` | String | Unique, required |
| `username` | String | Unique, required |
| `hashed_password` | String | Never returned in API |
| `is_active` | Boolean | Default: true |
| `is_superuser` | Boolean | Default: false |
| `created_at` | DateTime | Automatic |
| `updated_at` | DateTime | Automatic |

## 🔄 Auth Flow

1. **Register/Login** → Get JWT token
2. **Save token** → localStorage (automatic)
3. **Make requests** → Token added to headers (automatic)
4. **Access protected routes** → Token verified
5. **Logout** → Token removed from localStorage

## 🚨 Troubleshooting

| Problem | Solution |
|----------|---------|
| "Invalid credentials" | Check email/password, make sure user exists |
| "Unauthorized" | Check token presence in localStorage, may be expired |
| Redirect loop | Clear localStorage: `localStorage.clear()` |
| CORS errors | Backend allows all origins in dev mode |
| Token doesn't work | Token expires after 30 minutes, login again |

## 📊 Test Statistics

```
✅ 28 passed tests
├── 10 Model tests
├── 7 Security tests  
└── 11 Service tests

Coverage: ~95%
```

## 🔗 Related Documents

- [[Authentication Setup]] - Complete documentation
- [[Testing Guide]] - Testing guide
- [[Quick Start]] - Quick start

---

*Updated: 2025-10-09*
