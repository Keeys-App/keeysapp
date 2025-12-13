# Keeys Documentation

Welcome to the Keeys project documentation!

## 📚 Contents

### Getting Started
- [[Quick Start]] - Project quick start
- [[Environment Variables]] - Environment variables
- [[Project Structure]] - Project structure

### Main Features
- [[Teams System]] - **NEW!** Team system and collaboration
- [[Keys Module]] - Translation keys management
- [[Keys Search Feature]] - **NEW!** Key search with tests
- [[Universal Activity Logging]] - Logging all actions
- [[Project Export Import]] - Project export and import

### Authentication
- [[Authentication Setup]] - Complete authentication system documentation
- [[Authentication Cheatsheet]] - Authentication cheatsheet
- [[Security Best Practices]] - Security recommendations
- [[Testing Guide]] - Testing guide

### Development
- [[Backend Organization]] - Backend folder organization
- [[Database Enums and Migrations]] - Working with enums and migrations
- [[Error Handling Best Practices]] - Error handling
- [[Railway Deployment]] - Railway deployment

## 🚀 Quick Start

1. Clone repository
2. Follow instructions in [[Quick Start]]
3. Study [[Authentication Setup]] to understand authentication system

## 🏗️ Architecture

```
Keeys/
├── backend/          # FastAPI + GraphQL + PostgreSQL
│   ├── app/         # Main application code
│   └── tests/       # Tests
└── frontend/        # React + Radix UI + Apollo Client
    └── src/         # Frontend source code
```

## 📖 Main Technologies

**Backend:**
- FastAPI
- Strawberry GraphQL
- PostgreSQL
- SQLAlchemy
- JWT (pyjwt)
- bcrypt

**Frontend:**
- React 19
- TypeScript
- Radix UI
- Apollo Client
- React Router

## 🔐 Authentication System

Complete registration and authentication system with JWT tokens and UUID for security.

**Features:**
- ✅ UUID instead of auto-increment (protection against enumeration)
- ✅ Safe error handling (SQL never shown to users)
- ✅ JWT tokens with expiration
- ✅ bcrypt password hashing

More details: [[Authentication Setup]] | [[Security Best Practices]]

## 🧪 Testing

**272 automated tests** cover authentication system, security and functionality.

**Includes:**
- Model and service tests
- AI Service & GraphQL tests
- Key management & search tests
- Team service tests
- JWT token and UUID tests
- **Error handling tests** (SQL never reaches frontend)
- **SQL injection protection tests**

More details: [[Testing Guide]] | [[Keys Search Feature]]

## 📝 Conventions

- Code in English
- Comments in English
- UI/UX in English
- Documentation in English

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Create Pull Request

---

*Documentation updated: 2025-12-13*
