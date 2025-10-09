# Contexts

React Context API для глобального состояния приложения.

## Структура

```
contexts/
├── index.ts          # Barrel export
├── AuthContext.tsx   # Контекст аутентификации
└── ThemeContext.tsx  # Контекст темы (light/dark)
```

## Контексты

### 🔐 AuthContext
Управление состоянием аутентификации пользователя.

**Провайдер:**
```tsx
import { AuthProvider } from '@/contexts';

<AuthProvider>
  <App />
</AuthProvider>
```

**Хук:**
```tsx
import { useAuth } from '@/contexts';

const { user, isAuthenticated, isLoading, login, logout } = useAuth();
```

**API:**
- `user` - данные текущего пользователя
- `isAuthenticated` - статус авторизации
- `isLoading` - загрузка при проверке токена
- `login(token, user)` - авторизация пользователя
- `logout()` - выход из системы

### 🌗 ThemeContext
Управление темной/светлой темой приложения.

**Провайдер:**
```tsx
import { ThemeProvider } from '@/contexts';

<ThemeProvider>
  <App />
</ThemeProvider>
```

**Хук:**
```tsx
import { useTheme } from '@/contexts';

const { theme, toggleTheme } = useTheme();
```

**API:**
- `theme` - текущая тема ('light' | 'dark')
- `toggleTheme()` - переключение темы

**Особенности:**
- Сохранение темы в localStorage
- Автоматическое определение системной темы
- Применение класса `.dark` к `<html>`

## Использование

```tsx
// Импорт провайдеров
import { AuthProvider, ThemeProvider } from '@/contexts';

// Импорт хуков
import { useAuth, useTheme } from '@/contexts';

// Пример использования
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

- ✅ Используйте контексты для глобального состояния
- ✅ Локальное состояние держите в компонентах
- ✅ Создавайте custom хуки для доступа к контекстам
- ✅ Обрабатывайте ошибки при использовании вне Provider

