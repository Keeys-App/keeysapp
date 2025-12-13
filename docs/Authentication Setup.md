# Authentication Setup

> [!success] Complete authentication system documentation

## Overview

Authentication system uses:
- **Backend**: JWT tokens, bcrypt for password hashing
- **Frontend**: React Context API, React Router for protected routes
- **GraphQL**: Mutations for registration/login, queries for current user

## Backend

### Installing Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file in `backend` folder:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/locales
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> [!warning] Important
> Change `SECRET_KEY` to random secure string in production!

### Database Migration

User table is created automatically on application startup. For manual creation:

```python
from app.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)
```

### Starting Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

Server will start at `http://localhost:8000`

## Frontend

### Installing Dependencies

```bash
cd frontend
yarn install
```

### Environment Variables

Create `.env` file in `frontend` folder (optional):

```env
VITE_API_URL=http://localhost:8000
```

### Starting Frontend

```bash
cd frontend
yarn dev
```

Application will start at `http://localhost:5173`

## Functionality

### Backend

#### Models

**User Model** (`backend/app/models/user.py`):
- `id` - Integer, primary key
- `email` - String, unique, indexed
- `username` - String, unique, indexed
- `hashed_password` - String
- `is_active` - Boolean (default: True)
- `is_superuser` - Boolean (default: False)
- `created_at` - DateTime
- `updated_at` - DateTime

Methods:
- `verify_password(plain_password)` - Password check
- `get_password_hash(password)` - Password hashing

#### GraphQL API

**Mutations:**

```graphql
# Registration
mutation Register($input: RegisterInput!) {
  register(input: $input) {
    accessToken
    tokenType
    user {
      id
      email
      username
      isActive
      isSuperuser
    }
  }
}

# Login
mutation Login($input: LoginInput!) {
  login(input: $input) {
    accessToken
    tokenType
    user {
      id
      email
      username
      isActive
      isSuperuser
    }
  }
}
```

**Queries:**

```graphql
# Get current user
query Me {
  me {
    id
    email
    username
    isActive
    isSuperuser
  }
}
```

> [!note] Authentication
> Query `me` requires header: `Authorization: Bearer <token>`

#### Security

- JWT tokens for authentication
- Bcrypt password hashing
- Automatic password truncation to 72 bytes (bcrypt limitation)
- Token expiration (configurable)
- Endpoint protection via Authorization header

### Frontend

#### Contexts

**AuthContext** (`frontend/src/contexts/AuthContext.tsx`):
- Authentication state management
- Storing user and token in localStorage
- `login` and `logout` functions
- `isAuthenticated` flag

#### Components

**LoginForm** (`frontend/src/components/LoginForm.tsx`):
- Email and password login
- Error handling
- Switch to registration

**RegisterForm** (`frontend/src/components/RegisterForm.tsx`):
- Email, username and password registration
- Password confirmation
- Validation (min 6 characters, max 72)
- Error handling

**ProtectedRoute** (`frontend/src/components/ProtectedRoute.tsx`):
- Wrapper for protected pages
- Redirect to `/auth` if not authenticated
- Show loading during check

#### Pages

**AuthPage** (`frontend/src/pages/AuthPage.tsx`):
- Login/registration page
- Switch between forms

**DashboardPage** (`frontend/src/pages/DashboardPage.tsx`):
- Protected dashboard
- Display user information
- Logout function

#### Routing

```
/auth         - Login/registration page
/             - Protected dashboard
/* (others)   - Redirect to /
```

## Usage Examples

### GraphQL Playground

Open `http://localhost:8000/graphql`

**Registration:**
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "secret123"
  }) {
    accessToken
    user {
      id
      username
      email
    }
  }
}
```

**Login:**
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "secret123"
  }) {
    accessToken
    user {
      username
    }
  }
}
```

**Current user:**
```graphql
query {
  me {
    id
    username
    email
  }
}
```

Header:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

### Frontend

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

## Security Considerations

1. **Secrets** - Don't commit .env files
2. **SECRET_KEY** - Use random string in production
3. **HTTPS** - Always use HTTPS for token transmission
4. **Token expiration** - Configure appropriate lifetime
5. **Password complexity** - Minimum 6 characters (can increase)
6. **CORS** - Update allowed origins in production

## File Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py           # Settings
│   │   └── security.py         # JWT utilities
│   ├── models/
│   │   ├── user.py            # User model
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py            # GraphQL auth types
│   │   └── graphql.py         # Root GraphQL schema
│   └── services/
│       └── user_service.py    # User business logic
└── requirements.txt           # With pyjwt and bcrypt

frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx      # Login form
│   │   ├── RegisterForm.tsx   # Registration form
│   │   └── ProtectedRoute.tsx # Route protection
│   ├── contexts/
│   │   ├── AuthContext.tsx    # Auth management
│   │   └── ThemeContext.tsx   # Theme management
│   ├── graphql/
│   │   └── auth.ts            # Auth queries/mutations
│   ├── pages/
│   │   ├── AuthPage.tsx       # Login/registration page
│   │   └── DashboardPage.tsx  # Protected dashboard
│   ├── lib/
│   │   └── apollo.ts          # Apollo Client with auth
│   └── App.tsx                # Application with routing
```

## Next Steps

1. Add password recovery
2. Implement email confirmation
3. Add OAuth (Google, GitHub)
4. Implement refresh tokens
5. Add profile management
6. Implement RBAC (Role-Based Access Control)
7. Add rate limiting for login
8. Add audit logging

## Troubleshooting

### Backend

- Check DATABASE_URL
- Make sure PostgreSQL is running
- Check SECRET_KEY in .env
- Make sure venv is activated

### Frontend

- Clear localStorage if auth problems
- Check API_URL points to correct backend
- Check CORS on backend
- Check browser console for errors

### Auth Problems

- Check token in Authorization header
- Token may be expired (default 30 minutes)
- Make sure user exists and is_active=True
- Check password correctness

## Related Documents

- [[Authentication Cheatsheet]] - Quick reference
- [[Testing Guide]] - System testing
- [[Quick Start]] - Quick start

---

*Updated: 2025-10-09*
