# Security Best Practices

> [!warning] Рекомендации по безопасности приложения

## 🔐 Идентификаторы пользователей

### Проблема автоинкремента

**Не используйте автоинкремент ID для публичных API!**

```python
# ❌ ПЛОХО - предсказуемые ID
id = 1, 2, 3, 4...
```

**Проблемы:**
1. **Enumeration attack** - легко перебрать всех пользователей
2. **Information disclosure** - узнать количество пользователей
3. **Предсказуемость** - угадать ID других пользователей

### Решение - UUID

```python
# ✅ ХОРОШО - непредсказуемые UUID
public_id = UUID('550e8400-e29b-41d4-a716-446655440000')
```

**Преимущества:**
- ✅ Невозможно перебрать
- ✅ Не раскрывает количество записей
- ✅ Глобально уникальный
- ✅ Безопасно использовать в URL

### Реализация в проекте

```python
class User(Base):
    id = Column(Integer, primary_key=True)          # Внутреннее использование
    public_id = Column(UUID, unique=True)           # Публичное API
    # ...
```

**В GraphQL:**
```graphql
type User {
  id: String!  # UUID как строка
  email: String!
  username: String!
}
```

**В JWT токенах:**
```python
# Храним public_id, а не internal id
access_token = create_access_token(data={"sub": str(user.public_id)})
```

## 🔑 Пароли

### Хэширование

```python
# ✅ Используем bcrypt
import bcrypt

hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

**Не используйте:**
- ❌ MD5
- ❌ SHA1
- ❌ Простой SHA256
- ❌ Хранение в plain text

### Ограничения bcrypt

```python
# bcrypt ограничен 72 байтами
def _truncate_password_bytes(password: str) -> bytes:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return password_bytes
```

### Требования к паролям

**Минимальные требования:**
- ✅ Минимум 6 символов (лучше 8-12)
- ✅ Максимум 72 символа (ограничение bcrypt)

**Рекомендуется добавить:**
- Минимум 1 заглавная буква
- Минимум 1 строчная буква
- Минимум 1 цифра
- Минимум 1 спецсимвол

## 🎫 JWT Токены

### Хранение JWT_SECRET_KEY

```env
# ✅ В .env файле
JWT_SECRET_KEY=randomly-generated-long-secret-key-here
JWT_ALGORITHM=HS256

# ❌ НЕ в коде
JWT_SECRET_KEY = "hardcoded-secret"  # НИКОГДА!
```

**Генерация безопасного ключа:**
```bash
# Способ 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Способ 2: OpenSSL
openssl rand -base64 32

# Способ 3: Python script
python3 << EOF
import secrets
print(secrets.token_urlsafe(32))
EOF
```

**Пример вывода:**
```
fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

Скопируйте этот ключ в `.env` файл:
```env
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

### Время жизни токенов

```env
# Разработка - длинные токены для удобства
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 дней

# Production - короткие токены для безопасности
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 30 минут

# Длинные refresh tokens (если реализовано)
REFRESH_TOKEN_EXPIRE_DAYS=7  # 7 дней
```

**Рекомендации:**
- **Development:** 7 дней (10080 минут) - удобно для разработки
- **Production:** 30 минут - безопаснее, требует refresh token
- **Mobile apps:** 1 год - пользователи не любят постоянно логиниться

### Хранение токенов на клиенте

```typescript
// ✅ ХОРОШО - localStorage для web app
localStorage.setItem('authToken', token);

// ⚠️ ЛУЧШЕ - httpOnly cookies (защита от XSS)
// Требует изменений на backend

// ❌ ПЛОХО - обычные cookies без httpOnly
```

## 🌐 CORS

### Development

```python
# ✅ Разрешить все для разработки
allow_origins=["*"]
```

### Production

```python
# ✅ Только конкретные домены
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## 🛡️ Валидация входных данных

### Email

```typescript
// ✅ Валидация на клиенте
<TextField.Root type="email" required />

// ✅ Валидация на сервере
from pydantic import EmailStr

email: EmailStr  # Автоматическая валидация
```

### Username

```python
# ✅ Проверка на уникальность
existing = UserService.get_user_by_username(db, username)
if existing:
    raise Exception("Username already taken")
```

### Пароли

```typescript
// ✅ Клиентская валидация
if (password.length < 6) {
  setError('Password must be at least 6 characters long');
}

if (password.length > 72) {
  setError('Password must be no more than 72 characters');
}
```

## 🔒 Защита маршрутов

### Backend

```python
# ✅ Проверка токена
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
// ✅ ProtectedRoute компонент
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

> [!tip] Рекомендация
> Добавьте rate limiting для защиты от brute-force атак

```python
# TODO: Реализовать
# - Максимум 5 попыток входа за 15 минут
# - Временная блокировка после превышения
# - Капча после 3 неудачных попыток
```

## 📊 Логирование

### Что логировать

```python
# ✅ Логировать
- Успешные входы
- Неудачные попытки входа
- Изменения пароля
- Создание пользователей
- Изменение прав доступа

# ❌ НЕ логировать
- Пароли (даже хэшированные)
- Токены
- Секретные ключи
```

### Пример

```python
import logging

logger = logging.getLogger(__name__)

# Успешный вход
logger.info(f"User {user.username} logged in successfully")

# Неудачная попытка
logger.warning(f"Failed login attempt for email: {email}")
```

## 🔐 Checklist безопасности

### Backend
- [x] UUID для публичных ID
- [x] bcrypt для паролей
- [x] JWT с истечением
- [x] Валидация email
- [x] Проверка уникальности username/email
- [x] Автоматическая обрезка паролей (72 байта)
- [ ] Rate limiting для входа
- [ ] Логирование попыток входа
- [ ] Email верификация
- [ ] 2FA (Two-Factor Authentication)
- [ ] Password reset с токеном
- [ ] Account lockout после N попыток

### Frontend
- [x] Валидация форм
- [x] Обработка ошибок
- [x] Защищенные маршруты
- [x] autocomplete атрибуты
- [x] maxLength для полей
- [ ] CSP (Content Security Policy)
- [ ] HTTPS only в продакшене
- [ ] Безопасное хранение токенов

### Infrastructure
- [ ] HTTPS
- [ ] Firewall
- [ ] Regular security updates
- [ ] Backup strategy
- [ ] Monitoring и alerting
- [ ] Penetration testing

## 🎯 Best Practices

1. **Принцип наименьших привилегий** - давайте только необходимые права
2. **Defense in depth** - множественные слои защиты
3. **Fail securely** - при ошибке блокируйте доступ
4. **Don't trust user input** - всегда валидируйте
5. **Keep secrets secret** - никогда не коммитьте секреты
6. **Regular updates** - обновляйте зависимости
7. **Monitor and log** - отслеживайте подозрительную активность

## 📚 Ресурсы

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://curity.io/resources/learn/jwt-best-practices/)

## Связанные документы

- [[Environment Variables]] - Переменные окружения
- [[Authentication Setup]] - Настройка авторизации
- [[Testing Guide]] - Тестирование безопасности
- [[Project Structure]] - Структура проекта

---

*Обновлено: 2025-10-10*

