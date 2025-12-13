# Error Handling Best Practices

## 🚨 CRITICAL RULE: NEVER EXPOSE TECHNICAL ERRORS TO USERS

**THIS IS THE MOST IMPORTANT RULE IN THE PROJECT!**

### ❌ NEVER DO THIS:
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### ✅ ALWAYS DO THIS:
```python
except Exception as e:
    logger.error(f"Technical error details: {type(e).__name__}: {str(e)}")
    # Generic user-friendly message
    raise HTTPException(status_code=500, detail="Operation failed. Please try again.")
```

## Why This Matters

1. **Security**: Technical errors expose database structure, SQL queries, file paths
2. **User Experience**: Users don't understand technical jargon
3. **Professionalism**: Technical errors look unprofessional

## Examples of What NEVER to Show Users

- ❌ SQL queries and database errors
- ❌ Python stack traces
- ❌ File system paths
- ❌ Internal variable names
- ❌ Library/framework error messages
- ❌ Database column names

## User-Friendly Error Messages

Always use simple, actionable messages:

- ✅ "Failed to save changes. Please try again."
- ✅ "Unable to load data. Please refresh the page."
- ✅ "File format not supported. Please use JSON files."
- ✅ "Something went wrong. Please contact support if the problem persists."

## Critical Importance ⚠️

**NEVER show technical errors to users directly!**

This is a security violation and poor UX.

## Error Handling Principles

### ❌ Wrong

```typescript
onError: (error) => {
  toast(`Error: ${error.message}`);
  // Technical details exposed to user!
}

// Or
catch (err) => {
  setError(err.message);
  // SQL errors, stack traces - user sees everything!
}
```

### ✅ Correct

```typescript
import { getUserFriendlyErrorMessage } from '@/lib/utils';

onError: (error) => {
  const message = getUserFriendlyErrorMessage(
    error, 
    'Failed to update. Please try again.'
  );
  toast.error(message);
}
```

## getUserFriendlyErrorMessage Function

Centralized function in `lib/utils.ts` for handling all GraphQL errors.

### What It Does

1. **Logs technical details** to console for developers
2. **Handles specific error codes** (UNAUTHENTICATED, FORBIDDEN, etc.)
3. **Filters safe messages** (e.g., "already exists")
4. **Returns fallback** for all other cases

### Usage

```typescript
import { getUserFriendlyErrorMessage } from '@/lib/utils';

const message = getUserFriendlyErrorMessage(
  error,
  'Fallback message if nothing specific matches'
);
toast.error(message);
```

## What Should NOT Reach Users

- ❌ Stack traces
- ❌ SQL queries/errors
- ❌ Database table names
- ❌ GraphQL variable names
- ❌ Server file paths
- ❌ Library versions
- ❌ IP addresses
- ❌ Any technical implementation details

## What CAN Be Shown

- ✅ "Failed to create project"
- ✅ "Invalid input data"
- ✅ "This key already exists"
- ✅ "Unable to connect to server"
- ✅ "Please try again later"

## Rules for All Components

### 1. Apollo Client Mutations

```typescript
const [mutation] = useMutation(MUTATION, {
  onCompleted: () => {
    toast.success('Operation completed successfully');
  },
  onError: (error) => {
    // ✅ ALWAYS use getUserFriendlyErrorMessage
    const message = getUserFriendlyErrorMessage(error, 'Operation failed');
    toast.error(message);
  },
});
```

### 2. Try-Catch Blocks

```typescript
try {
  // ... code
} catch (err) {
  // ✅ ALWAYS handle through getUserFriendlyErrorMessage
  const message = getUserFriendlyErrorMessage(
    err as Error, 
    'Operation failed'
  );
  setError(message);
}
```

### 3. Logging for Developers

```typescript
// ✅ Log EVERYTHING for development
console.error('Technical details:', error);
console.error('Stack:', error.stack);
console.error('GraphQL errors:', error.graphQLErrors);

// ❌ But show user only safe messages
toast.error(getUserFriendlyErrorMessage(error, fallback));
```

## Backend: Safe Error Messages

### ✅ Good Backend Messages

```python
raise ValueError("Project with this name already exists")
raise ValueError("Invalid language code")
raise PermissionError("You don't have permission to edit this project")
```

### ❌ Bad Backend Messages

```python
raise Exception(f"Variable '$input' got invalid value...")  # Technical details
raise Exception(f"SQL Error: {str(e)}")  # SQL errors
raise Exception(f"Failed at line 145 in service.py")  # File paths
```

## Pre-Commit Check

Before each commit check:

```bash
# Search for direct error.message usage
grep -r "error\.message" frontend/src/components/

# Search for toast with error
grep -r "toast.*error\." frontend/src/components/

# Search for console.error without getUserFriendlyErrorMessage after
grep -r "console\.error" frontend/src/components/
```

## Existing Implementations

All following components already use correct error handling:

- ✅ `TranslationEditor.tsx`
- ✅ `CreateKeyDialog.tsx`
- ✅ `CreateProjectDialog.tsx`
- ✅ `EditProjectDialog.tsx`
- ✅ `ProjectList.tsx`
- ✅ `LoginForm.tsx`
- ✅ `RegisterForm.tsx`

Use them as reference when creating new components.

## Testing

When testing check:

1. **Disconnect backend** - should show "Unable to connect to server"
2. **Invalid data** - should show understandable messages
3. **DB errors** - should NOT show technical details
4. **GraphQL errors** - should be handled and shown user-friendly

## Additional Security

### Apollo Client errorLink

In `lib/apollo.ts` errorLink is configured to:

1. Automatically catch authentication errors
2. Clear tokens on 401/403
3. Redirect to login page

This is additional protection layer, but **DOES NOT replace** component-level handling!

## Checklist

- [ ] All mutations use `getUserFriendlyErrorMessage` in `onError`
- [ ] All try-catch blocks handle errors via `getUserFriendlyErrorMessage`
- [ ] Technical errors logged via `console.error` for development
- [ ] User sees only understandable messages
- [ ] No direct usage of `error.message` in toast/alert
- [ ] Backend doesn't return technical details in error messages

---

**Remember:** Every technical error shown to user is:
1. **Attack vector** for hackers
2. **Poor UX** for users
3. **Potential data leak**

Always handle errors correctly!
