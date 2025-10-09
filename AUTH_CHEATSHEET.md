# Authentication System Cheat Sheet

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

### Register
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

### Get Current User
```graphql
query {
  me {
    id username email isActive
  }
}
```
**Headers:** `Authorization: Bearer <token>`

## 🎨 Frontend Usage

### Use Auth Context
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

### Protect Routes
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

## 🧪 Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Access protected route when authenticated
- [ ] Redirect to /auth when not authenticated
- [ ] Logout functionality
- [ ] Token persists after page refresh
- [ ] GraphQL me query works with token
- [ ] Invalid credentials show error
- [ ] Password validation (min 6 chars)
- [ ] Email validation

## 🛠️ Common Tasks

### Add New Protected Query
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

### Add New Protected Route
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

### Check if User is Admin
```tsx
const { user } = useAuth();

if (user?.isSuperuser) {
  // Show admin features
}
```

## 📝 User Model Fields

- `id` - Integer, primary key
- `email` - String, unique, required
- `username` - String, unique, required
- `hashed_password` - String (never exposed in API)
- `is_active` - Boolean (default: true)
- `is_superuser` - Boolean (default: false)
- `created_at` - DateTime
- `updated_at` - DateTime

## 🔄 Auth Flow

1. **Register/Login** → Receive JWT token
2. **Store token** → localStorage (automatic)
3. **Make requests** → Token added to headers (automatic)
4. **Access protected routes** → Token verified
5. **Logout** → Token removed from localStorage

## 🚨 Troubleshooting

**"Invalid credentials"**
- Check email/password are correct
- Verify user exists in database

**"Unauthorized"**
- Check token is present in localStorage
- Token may be expired (default: 30 minutes)
- Re-login to get new token

**Redirect loop**
- Clear localStorage: `localStorage.clear()`
- Check ProtectedRoute implementation

**CORS errors**
- Backend allows all origins in development
- Update CORS settings for production

