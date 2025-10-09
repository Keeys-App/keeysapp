# Authentication System Setup

This document describes the authentication system implementation in the Locales application.

## Overview

The authentication system uses:
- **Backend**: JWT tokens for authentication, bcrypt for password hashing
- **Frontend**: React Context API for state management, React Router for protected routes
- **GraphQL**: Mutations for register/login, queries for current user

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/locales
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

⚠️ **Important**: Change `SECRET_KEY` to a random secure string in production!

### 3. Database Migration

The User table will be created automatically on application startup. To manually create tables:

```python
from app.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)
```

### 4. Start Backend Server

```bash
cd backend
source venv/bin/activate
python main.py
```

The server will start on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
yarn install
```

### 2. Environment Variables

Create a `.env` file in the `frontend` directory (optional):

```env
VITE_API_URL=http://localhost:8000
```

### 3. Start Frontend Development Server

```bash
cd frontend
yarn dev
```

The app will start on `http://localhost:5173`

## Features

### Backend

#### Models
- **User Model** (`backend/app/models/user.py`)
  - id, email, username, hashed_password
  - is_active, is_superuser
  - created_at, updated_at
  - Password hashing and verification methods

#### GraphQL API

**Mutations:**
- `register(input: RegisterInput!)`: Register a new user
  - Input: email, username, password
  - Returns: access token and user data

- `login(input: LoginInput!)`: Authenticate a user
  - Input: email, password
  - Returns: access token and user data

**Queries:**
- `me`: Get current authenticated user
  - Requires Authorization header: `Bearer <token>`
  - Returns: current user data or null

#### Security
- JWT token-based authentication
- Bcrypt password hashing
- Token expiration (configurable)
- Protected endpoints via Authorization header

### Frontend

#### Contexts
- **AuthContext** (`frontend/src/contexts/AuthContext.tsx`)
  - Manages authentication state
  - Stores user and token in localStorage
  - Provides login/logout functions

#### Components
- **LoginForm** (`frontend/src/components/LoginForm.tsx`)
  - Email and password login
  - Error handling
  - Switch to registration

- **RegisterForm** (`frontend/src/components/RegisterForm.tsx`)
  - Email, username, and password registration
  - Password confirmation
  - Validation (min 6 characters)
  - Error handling

- **ProtectedRoute** (`frontend/src/components/ProtectedRoute.tsx`)
  - Wrapper for protected pages
  - Redirects to /auth if not authenticated
  - Shows loading spinner during auth check

#### Pages
- **AuthPage** (`frontend/src/pages/AuthPage.tsx`)
  - Login and registration forms
  - Switch between login/register views

- **DashboardPage** (`frontend/src/pages/DashboardPage.tsx`)
  - Protected dashboard
  - Displays user information
  - Logout functionality

#### Routing
- `/auth` - Login/Register page
- `/` - Protected dashboard (requires authentication)
- All other routes redirect to `/`

## Usage Examples

### GraphQL Playground

Access GraphQL playground at `http://localhost:8000/graphql`

**Register a new user:**
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "secret123"
  }) {
    accessToken
    tokenType
    user {
      id
      email
      username
      isActive
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
    tokenType
    user {
      id
      email
      username
    }
  }
}
```

**Get current user** (with Authorization header):
```graphql
query {
  me {
    id
    email
    username
    isActive
    isSuperuser
  }
}
```

Set HTTP header:
```
Authorization: Bearer <your-token-here>
```

### Using the Frontend

1. Navigate to `http://localhost:5173`
2. If not authenticated, you'll be redirected to `/auth`
3. Register a new account or login with existing credentials
4. After successful authentication, you'll be redirected to the dashboard
5. Your session persists in localStorage (survives page refresh)
6. Click "Logout" to end your session

## Security Considerations

1. **Never commit sensitive data** - Keep `.env` files out of git
2. **Use strong SECRET_KEY** - Generate a random string for production
3. **HTTPS in production** - Always use HTTPS for token transmission
4. **Token expiration** - Configure appropriate token lifetime
5. **Password strength** - Current minimum is 6 characters (adjust as needed)
6. **CORS configuration** - Update allowed origins in production

## File Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   └── security.py        # JWT utilities
│   ├── models/
│   │   ├── user.py            # User model
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py            # GraphQL auth types
│   │   └── graphql.py         # Root GraphQL schema
│   └── services/
│       └── user_service.py    # User business logic
└── requirements.txt           # Updated with pyjwt

frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx      # Login form component
│   │   ├── RegisterForm.tsx   # Registration form
│   │   └── ProtectedRoute.tsx # Route protection wrapper
│   ├── contexts/
│   │   ├── AuthContext.tsx    # Auth state management
│   │   └── ThemeContext.tsx   # Theme management
│   ├── graphql/
│   │   └── auth.ts            # Auth GraphQL queries/mutations
│   ├── pages/
│   │   ├── AuthPage.tsx       # Login/Register page
│   │   └── DashboardPage.tsx  # Protected dashboard
│   ├── lib/
│   │   └── apollo.ts          # Apollo Client with auth link
│   └── App.tsx                # App with routing
```

## Next Steps

1. Add password reset functionality
2. Implement email verification
3. Add OAuth providers (Google, GitHub, etc.)
4. Implement refresh tokens
5. Add user profile management
6. Add role-based access control (RBAC)
7. Add rate limiting for login attempts
8. Add audit logging for security events

## Troubleshooting

**Backend issues:**
- Check DATABASE_URL is correct
- Ensure PostgreSQL is running
- Verify SECRET_KEY is set in .env
- Check Python virtual environment is activated

**Frontend issues:**
- Clear localStorage if having auth issues
- Check API_URL points to correct backend
- Verify CORS is configured on backend
- Check browser console for errors

**Authentication issues:**
- Verify token is included in Authorization header
- Check token hasn't expired
- Ensure user exists and is_active=True
- Verify password is correct

