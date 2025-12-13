# Security Best Practices

> [!warning] Application Security Recommendations

## 🔐 User Identifiers

### Auto-Increment Problem

**Don't use auto-increment IDs for public APIs!**

```python
# ❌ BAD - predictable IDs
id = 1, 2, 3, 4...
```

**Problems:**
1. **Enumeration attack** - easy to iterate over all users
2. **Information disclosure** - learn user count
3. **Predictability** - guess other user IDs

### Solution - UUID

```python
# ✅ GOOD - unpredictable UUIDs
public_id = UUID('550e8400-e29b-41d4-a716-446655440000')
```

**Benefits:**
- ✅ Impossible to enumerate
- ✅ Doesn't reveal record count
- ✅ Globally unique
- ✅ Safe to use in URLs

### Implementation in Project

```python
class User(Base):
    id = Column(Integer, primary_key=True)          # Internal use
    public_id = Column(UUID, unique=True)           # Public API
    # ...
```

**In GraphQL:**
```graphql
type User {
  id: String!  # UUID as string
  email: String!
  username: String!
}
```

**In JWT tokens:**
```python
# Store public_id, not internal id
access_token = create_access_token(data={"sub": str(user.public_id)})
```

## 🔑 Passwords

### Hashing

```python
# ✅ Use bcrypt
import bcrypt

hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

**Don't use:**
- ❌ MD5
- ❌ SHA1
- ❌ Plain SHA256
- ❌ Plain text storage

### bcrypt Limitations

```python
# bcrypt limited to 72 bytes
def _truncate_password_bytes(password: str) -> bytes:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return password_bytes
```

### Password Requirements

**Minimum requirements:**
- ✅ Minimum 6 characters (better 8-12)
- ✅ Maximum 72 characters (bcrypt limitation)

**Recommended to add:**
- Minimum 1 uppercase letter
- Minimum 1 lowercase letter
- Minimum 1 digit
- Minimum 1 special character

## 🎫 JWT Tokens

### Storing JWT_SECRET_KEY

```env
# ✅ In .env file
JWT_SECRET_KEY=randomly-generated-long-secret-key-here
JWT_ALGORITHM=HS256

# ❌ NOT in code
JWT_SECRET_KEY = "hardcoded-secret"  # NEVER!
```

**Generating secure key:**
```bash
# Method 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32

# Method 3: Python script
python3 << EOF
import secrets
print(secrets.token_urlsafe(32))
EOF
```

**Example output:**
```
fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

Copy this key to `.env` file:
```env
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

### Token Lifetime

```env
# Development - long tokens for convenience
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Production - short tokens for security
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 30 minutes

# Long refresh tokens (if implemented)
REFRESH_TOKEN_EXPIRE_DAYS=7  # 7 days
```

**Recommendations:**
- **Development:** 7 days (10080 minutes) - convenient for development
- **Production:** 30 minutes - safer, requires refresh token
- **Mobile apps:** 1 year - users don't like constant logins

### Storing Tokens on Client

```typescript
// ✅ GOOD - localStorage for web app
localStorage.setItem('authToken', token);

// ⚠️ BETTER - httpOnly cookies (XSS protection)
// Requires backend changes

// ❌ BAD - regular cookies without httpOnly
```

## 🌐 CORS

### Development

```python
# ✅ Allow all for development
allow_origins=["*"]
```

### Production

```python
# ✅ Only specific domains
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## 🛡️ Input Data Validation

### Email

```typescript
// ✅ Client validation
<TextField.Root type="email" required />

// ✅ Server validation
from pydantic import EmailStr

email: EmailStr  # Automatic validation
```

### Username

```python
# ✅ Check uniqueness
existing = UserService.get_user_by_username(db, username)
if existing:
    raise Exception("Username already taken")
```

### Passwords

```typescript
// ✅ Client validation
if (password.length < 6) {
  setError('Password must be at least 6 characters long');
}

if (password.length > 72) {
  setError('Password must be no more than 72 characters');
}
```

## 🔒 Route Protection

### Backend

```python
# ✅ Token check
def get_current_user(token: str) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401)
    
    public_id = payload.get("sub")
    user = UserService.get_user_by_public_id(db, public_id)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401)
    
    return user
```

### Frontend

```tsx
// ✅ ProtectedRoute component
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  }
/>
```

## 🚫 Rate Limiting

> [!tip] Recommendation
> Add rate limiting to protect against brute-force attacks

```python
# TODO: Implement
# - Maximum 5 login attempts per 15 minutes
# - Temporary block after exceeding
# - Captcha after 3 failed attempts
```

## 📊 Logging

### What to Log

```python
# ✅ Log
- Successful logins
- Failed login attempts
- Password changes
- User creation
- Permission changes

# ❌ DO NOT log
- Passwords (even hashed)
- Tokens
- Secret keys
```

### Example

```python
import logging

logger = logging.getLogger(__name__)

# Successful login
logger.info(f"User {user.username} logged in successfully")

# Failed attempt
logger.warning(f"Failed login attempt for email: {email}")
```

## 🔐 Security Checklist

### Backend
- [x] UUID for public IDs
- [x] bcrypt for passwords
- [x] JWT with expiration
- [x] Email validation
- [x] Username/email uniqueness check
- [x] Automatic password truncation (72 bytes)
- [ ] Rate limiting for login
- [ ] Login attempt logging
- [ ] Email verification
- [ ] 2FA (Two-Factor Authentication)
- [ ] Password reset with token
- [ ] Account lockout after N attempts

### Frontend
- [x] Form validation
- [x] Error handling
- [x] Protected routes
- [x] autocomplete attributes
- [x] maxLength for fields
- [ ] CSP (Content Security Policy)
- [ ] HTTPS only in production
- [ ] Secure token storage

### Infrastructure
- [ ] HTTPS
- [ ] Firewall
- [ ] Regular security updates
- [ ] Backup strategy
- [ ] Monitoring and alerting
- [ ] Penetration testing

## 🎯 Best Practices

1. **Principle of least privilege** - grant only necessary permissions
2. **Defense in depth** - multiple security layers
3. **Fail securely** - block access on error
4. **Don't trust user input** - always validate
5. **Keep secrets secret** - never commit secrets
6. **Regular updates** - update dependencies
7. **Monitor and log** - track suspicious activity

## 📚 Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://curity.io/resources/learn/jwt-best-practices/)

## Related Documents

- [[Environment Variables]] - Environment variables
- [[Authentication Setup]] - Authentication setup
- [[Testing Guide]] - Security testing
- [[Project Structure]] - Project structure

---

*Updated: 2025-10-10*
