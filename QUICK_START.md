# Quick Start Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL
- Yarn

## Setup

### 1. Clone and Navigate

```bash
cd /Users/mbrtn/Projects/locales
```

### 2. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done if venv exists)
pip install -r requirements.txt

# Create .env file
cp env.example .env

# Edit .env and set:
# DATABASE_URL=postgresql://user:password@localhost:5432/locales
# SECRET_KEY=your-random-secret-key-here

# Start the server
python main.py
```

Backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Start development server
yarn dev
```

Frontend will run on `http://localhost:5173`

## Using the Application

1. Open `http://localhost:5173` in your browser
2. Click "Sign up" to create a new account
3. Fill in email, username, and password
4. After registration, you'll be automatically logged in
5. You'll see the dashboard with your user information

## Testing Authentication

### Via GraphQL Playground

Open `http://localhost:8000/graphql`

**Register:**
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

**Login:**
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

**Get Current User** (add token to HTTP headers):
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
✅ GraphQL mutations: register, login
✅ GraphQL query: me (get current user)
✅ Automatic database table creation

### Frontend
✅ Login form with validation
✅ Registration form with validation
✅ Protected routes (redirect to login if not authenticated)
✅ Auth context for state management
✅ Token stored in localStorage
✅ Apollo Client configured with auth headers
✅ Beautiful UI with Radix UI components
✅ Dark/Light theme support

## Next Steps

Now you can:
- Add more features to the dashboard
- Create additional protected routes
- Add user profile management
- Implement role-based access control
- Add password reset functionality

See `AUTH_SETUP.md` for detailed documentation.

