# Error Handling

## Overview

Улучшенная система обработки ошибок для отображения понятных сообщений пользователям при сохранении безопасности.

## Функция `getUserFriendlyErrorMessage`

### Основные принципы:

1. **Безопасность прежде всего** - никогда не показывать технические детали (SQL, stack traces, пути к файлам)
2. **Понятные сообщения** - показывать причину ошибки на языке пользователя
3. **Логирование** - все технические детали записываются в консоль для разработчиков

### Типы обрабатываемых ошибок:

#### Authentication Errors
```typescript
// Backend: AuthenticationError
// Frontend показывает: "Invalid credentials"
```

#### Validation Errors
```typescript
// Backend: "Email already registered"
// Frontend показывает: "Email already registered."

// Backend: "Password must be at least 8 characters long"
// Frontend показывает: "Password must be at least 8 characters long."
```

#### Authorization Errors
```typescript
// Backend: UnauthorizedError
// Frontend показывает: "You need to be logged in to perform this action."
```

#### Network Errors
```typescript
// Backend недоступен
// Frontend показывает: "Unable to connect to the server. Please check your internet connection."
```

### Безопасные паттерны ошибок:

Функция распознает следующие типы сообщений как безопасные для показа пользователям:

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

### Примеры использования:

```typescript
// В компоненте
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

### Очистка сообщений:

Функция автоматически:
- Удаляет технические детали (`Variable $input:`, `input.field:`)
- Убирает пути к переменным (`$variableName`)
- Делает первую букву заглавной
- Добавляет точку в конце, если её нет

**До очистки:**
```
Variable $input: Email already registered
```

**После очистки:**
```
Email already registered.
```

## Backend Integration

### Backend Exceptions (`backend/app/core/exceptions.py`)

#### UserAlreadyExistsError
```python
# Пользователь с таким email уже существует
raise UserAlreadyExistsError(field="email")
# Сообщение: "Email already registered"

# Пользователь с таким username уже существует
raise UserAlreadyExistsError(field="username")
# Сообщение: "Username already taken"
```

#### ValidationError
```python
# Валидация не прошла
raise ValidationError("Password must be at least 8 characters long")
# Сообщение передается как есть
```

#### AuthenticationError
```python
# Неверные credentials
raise AuthenticationError()
# Сообщение: "Invalid credentials"
```

#### UnauthorizedError
```python
# Требуется авторизация
raise UnauthorizedError()
# Сообщение: "Authentication required. Please log in."
```

#### DatabaseError
```python
# Ошибка базы данных - НИКОГДА не показывать детали!
raise DatabaseError()
# Сообщение: "An error occurred. Please try again later."
```

## Best Practices

### ✅ DO:

```typescript
// Использовать getUserFriendlyErrorMessage для всех ошибок
const errorMessage = getUserFriendlyErrorMessage(err, 'Fallback message');
setError(errorMessage);

// Логировать технические детали
console.error('Technical error:', err);

// Показывать конкретные причины из backend
// Backend: "Email already registered"
// Показываем: "Email already registered."
```

### ❌ DON'T:

```typescript
// НЕ показывать сырые ошибки
setError(err.message); // ❌

// НЕ показывать технические детали
setError(`Database error: ${err.toString()}`); // ❌

// НЕ игнорировать конкретные сообщения
setError('Something went wrong'); // ❌ если backend дал конкретную причину
```

## Testing Error Messages

### Тесты для проверки:

1. **Регистрация с существующим email:**
   - Ожидается: "Email already registered."
   - Не должно быть: "Registration failed. Please try again."

2. **Короткий пароль:**
   - Ожидается: "Password must be at least 8 characters long."

3. **Неверный логин:**
   - Ожидается: "Invalid credentials."

4. **Недоступен сервер:**
   - Ожидается: "Unable to connect to the server. Please check your internet connection."

5. **Нет авторизации:**
   - Ожидается: "You need to be logged in to perform this action."

## Security Considerations

### 🔒 Что НИКОГДА не показывать:

- SQL запросы и ошибки БД
- Stack traces
- Пути к файлам
- Названия таблиц и колонок
- Внутренние идентификаторы
- Версии библиотек

### ✅ Что безопасно показывать:

- "Email already registered"
- "Password too short"
- "Invalid input"
- "Not found"
- "Permission denied"
- "Required field missing"

## Future Improvements

Возможные улучшения:
- [ ] Поддержка i18n (перевод ошибок)
- [ ] Более детальные validation errors с указанием поля
- [ ] Categorization errors (error types)
- [ ] Retry logic для network errors
- [ ] Error boundaries для React компонентов

---

**Version:** 1.0  
**Last Updated:** November 30, 2025

