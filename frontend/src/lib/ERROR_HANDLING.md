# Error Handling

## Overview

Improved error handling system for displaying user-friendly messages while maintaining security.

## `getUserFriendlyErrorMessage` Function

### Core Principles:

1. **Security first** - never show technical details (SQL, stack traces, file paths)
2. **Clear messages** - show error reason in user's language
3. **Logging** - all technical details logged to console for developers

### Types of Handled Errors:

#### Authentication Errors
```typescript
// Backend: AuthenticationError
// Frontend shows: "Invalid credentials"
```

#### Validation Errors
```typescript
// Backend: "Email already registered"
// Frontend shows: "Email already registered."

// Backend: "Password must be at least 8 characters long"
// Frontend shows: "Password must be at least 8 characters long."
```

#### Authorization Errors
```typescript
// Backend: UnauthorizedError
// Frontend shows: "You need to be logged in to perform this action."
```

#### Network Errors
```typescript
// Backend unavailable
// Frontend shows: "Unable to connect to the server. Please check your internet connection."
```

### Safe Error Patterns:

Function recognizes following message types as safe for users:

- `already exists` / `already registered`
- `not found`
- `required`
- `invalid`
- `too short` / `too long`
- `must be` / `cannot be`
- `does not match`
- `incorrect`
- `failed`
- `Authentication required`
- `Permission denied`

### Usage Examples:

```typescript
// In component
import { getUserFriendlyErrorMessage } from '@/lib/utils';

try {
  await registerMutation({ variables: { input } });
} catch (err: any) {
  const errorMessage = getUserFriendlyErrorMessage(
    err, 
    'Registration failed. Please try again.'
  );
  setError(errorMessage);
}
```

### Message Cleanup:

Function automatically:
- Removes technical details (`Variable $input:`, `input.field:`)
- Removes variable paths (`$variableName`)
- Capitalizes first letter
- Adds period at end if missing

**Before cleanup:**
```
Variable $input: Email already registered
```

**After cleanup:**
```
Email already registered.
```

## Backend Integration

### Backend Exceptions (`backend/app/core/exceptions.py`)

#### UserAlreadyExistsError
```python
# User with this email already exists
raise UserAlreadyExistsError(field="email")
# Message: "Email already registered"

# User with this username already exists
raise UserAlreadyExistsError(field="username")
# Message: "Username already taken"
```

#### ValidationError
```python
# Validation failed
raise ValidationError("Password must be at least 8 characters long")
# Message passed as-is
```

#### AuthenticationError
```python
# Invalid credentials
raise AuthenticationError()
# Message: "Invalid credentials"
```

#### UnauthorizedError
```python
# Authorization required
raise UnauthorizedError()
# Message: "Authentication required. Please log in."
```

#### DatabaseError
```python
# Database error - NEVER show details!
raise DatabaseError()
# Message: "An error occurred. Please try again later."
```

## Best Practices

### ✅ DO:

```typescript
// Use getUserFriendlyErrorMessage for all errors
const errorMessage = getUserFriendlyErrorMessage(err, 'Fallback message');
setError(errorMessage);

// Log technical details
console.error('Technical error:', err);

// Show specific reasons from backend
// Backend: "Email already registered"
// Show: "Email already registered."
```

### ❌ DON'T:

```typescript
// DON'T show raw errors
setError(err.message); // ❌

// DON'T show technical details
setError(`Database error: ${err.toString()}`); // ❌

// DON'T ignore specific messages
setError('Something went wrong'); // ❌ if backend gave specific reason
```

## Testing Error Messages

### Tests to check:

1. **Register with existing email:**
   - Expected: "Email already registered."
   - Should not be: "Registration failed. Please try again."

2. **Short password:**
   - Expected: "Password must be at least 8 characters long."

3. **Wrong login:**
   - Expected: "Invalid credentials."

4. **Server unavailable:**
   - Expected: "Unable to connect to the server. Please check your internet connection."

5. **Not authorized:**
   - Expected: "You need to be logged in to perform this action."

## Security Considerations

### 🔒 What to NEVER show:

- SQL queries and DB errors
- Stack traces
- File paths
- Table and column names
- Internal identifiers
- Library versions

### ✅ What's safe to show:

- "Email already registered"
- "Password too short"
- "Invalid input"
- "Not found"
- "Permission denied"
- "Required field missing"

## Future Improvements

Possible improvements:
- [ ] i18n support (error translation)
- [ ] More detailed validation errors with field indication
- [ ] Error categorization (error types)
- [ ] Retry logic for network errors
- [ ] Error boundaries for React components

---

**Version:** 1.0  
**Last Updated:** November 30, 2025
