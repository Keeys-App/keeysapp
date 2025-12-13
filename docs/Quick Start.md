# Quick Start

> [!info] Keeys Project Quick Start

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL
- Yarn

## Installation and Running

### 1. Preparation

```bash
cd /Users/mbrtn/Projects/locales
```

### 2. Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Create .env file
cp env.example .env

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output and use as JWT_SECRET_KEY

# Configure .env:
# DATABASE_URL=postgresql://user:password@localhost:5432/locales_db
# JWT_SECRET_KEY=<generated_key>
# JWT_ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Start server
python main.py
```

Backend will be available at `http://localhost:8000`

### 3. Frontend

```bash
cd frontend

# Install dependencies
yarn install

# Start dev server
yarn dev
```

Frontend will be available at `http://localhost:5173`

## Using the Application

1. Open `http://localhost:5173` in browser
2. Click **"Sign up"** to create account
3. Fill the form:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `password123`
4. After registration you'll be automatically logged in
5. You'll see dashboard with user information

## Testing via GraphQL

Open `http://localhost:8000/graphql`

### Registration

```graphql
mutation {
  register(input: {
    email: "test@example.com"
    username: "testuser"
    password: "password123"
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

### Login

```graphql
mutation {
  login(input: {
    email: "test@example.com"
    password: "password123"
  }) {
    accessToken
    user {
      username
    }
  }
}
```

### Get Current User

```graphql
query {
  me {
    id
    username
    email
  }
}
```

HTTP Headers:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

## What's Included

### Backend
✅ User model with password hashing (bcrypt)  
✅ JWT authentication  
✅ GraphQL mutations: `register`, `login`  
✅ GraphQL query: `me` (get current user)  
✅ Automatic database table creation  

### Frontend
✅ Login form with validation  
✅ Registration form with validation  
✅ Protected routes (redirect to login if not authenticated)  
✅ Auth context for state management  
✅ Token saved in localStorage  
✅ Apollo Client configured with auth headers  
✅ Beautiful UI with Radix UI components  
✅ Dark/light theme support  

## Next Steps

- Add more features to dashboard
- Create additional protected routes
- Add user profile management
- Implement role-based access control
- Add password recovery feature

## Environment Variables

See full description of all variables in [[Environment Variables]].

**Required:**
- `DATABASE_URL` - PostgreSQL connection
- `JWT_SECRET_KEY` - secret key for JWT tokens

**Optional (have default values):**
- `JWT_ALGORITHM` - JWT encryption algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - token lifetime in minutes (default: 525600 = 1 year)

## Related Documents

- [[Environment Variables]] - Environment variables
- [[Authentication Setup]] - Detailed authentication documentation
- [[Authentication Cheatsheet]] - Authentication cheatsheet
- [[Testing Guide]] - Testing guide

---

*Updated: 2025-10-10*
