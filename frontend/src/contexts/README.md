# Contexts

React Context API for global application state.

## Structure

```
contexts/
├── index.ts          # Barrel export
├── AuthContext.tsx   # Authentication context
└── ThemeContext.tsx  # Theme context (light/dark)
```

## Contexts

### 🔐 AuthContext
User authentication state management.

**Provider:**
```tsx
import { AuthProvider } from '@/contexts';

<AuthProvider>
  <App />
</AuthProvider>
```

**Hook:**
```tsx
import { useAuth } from '@/contexts';

const { user, isAuthenticated, isLoading, login, logout } = useAuth();
```

**API:**
- `user` - current user data
- `isAuthenticated` - authentication status
- `isLoading` - loading during token check
- `login(token, user)` - authorize user
- `logout()` - logout

### 🌗 ThemeContext
Application dark/light theme management.

**Provider:**
```tsx
import { ThemeProvider } from '@/contexts';

<ThemeProvider>
  <App />
</ThemeProvider>
```

**Hook:**
```tsx
import { useTheme } from '@/contexts';

const { theme, toggleTheme } = useTheme();
```

**API:**
- `theme` - current theme ('light' | 'dark')
- `toggleTheme()` - toggle theme

**Features:**
- Save theme to localStorage
- Automatic system theme detection
- Apply `.dark` class to `<html>`

## Usage

```tsx
// Import providers
import { AuthProvider, ThemeProvider } from '@/contexts';

// Import hooks
import { useAuth, useTheme } from '@/contexts';

// Usage example
function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <YourApp />
      </AuthProvider>
    </ThemeProvider>
  );
}
```

## Best Practices

- ✅ Use contexts for global state
- ✅ Keep local state in components
- ✅ Create custom hooks for context access
- ✅ Handle errors when used outside Provider
