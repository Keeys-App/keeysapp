# Authentication Cheatsheet

> [!tip] Быстрая справка по системе авторизации

## 🚀 Быстрые команды

### Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend
```bash
cd frontend
yarn dev
```

## 📁 Ключевые файлы

### Backend
```
backend/app/
├── models/user.py              # Модель User
├── services/user_service.py    # Операции с пользователями
├── schemas/auth.py             # GraphQL auth типы
├── schemas/graphql.py          # Корневая схема
└── core/
    ├── security.py             # JWT утилиты
    └── config.py               # Настройки
```

### Frontend
```
frontend/src/
├── contexts/AuthContext.tsx    # Состояние авторизации
├── components/
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── ProtectedRoute.tsx
├── pages/
│   ├── AuthPage.tsx
│   └── DashboardPage.tsx
├── graphql/auth.ts             # Auth queries
└── lib/apollo.ts               # Apollo с auth
```

## 🔑 GraphQL API

### Регистрация
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "secret123"
  }) {
    accessToken
    user { id username email }
  }
}
```

### Вход
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "secret123"
  }) {
    accessToken
    user { id username email }
  }
}
```

### Текущий пользователь
```graphql
query {
  me {
    id username email isActive
  }
}
```
**Headers:** `Authorization: Bearer <token>`

## 🎨 Frontend

### Использование Auth Context
```tsx
import { useAuth } from '../contexts/AuthContext';

function Component() {
  const { user, token, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <div>Please login</div>;
  }
  
  return <div>Welcome, {user?.username}!</div>;
}
```

### Защита маршрутов
```tsx
<Route
  path="/protected"
  element={
    <ProtectedRoute>
      <YourComponent />
    </ProtectedRoute>
  }
/>
```

## 🔐 Переменные окружения

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🧪 Тестирование

```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# С coverage
pytest --cov=app --cov-report=html

# Конкретный файл
pytest tests/test_models.py

# Конкретный тест
pytest tests/test_models.py::TestUserModel::test_password_hashing
```

### Чек-лист тестирования

- [ ] Регистрация нового пользователя
- [ ] Вход с учетными данными
- [ ] Доступ к защищенному маршруту при авторизации
- [ ] Редирект на /auth когда не авторизован
- [ ] Функция logout
- [ ] Токен сохраняется после обновления страницы
- [ ] GraphQL query `me` работает с токеном
- [ ] Неверные учетные данные показывают ошибку
- [ ] Валидация пароля (мин 6 символов)
- [ ] Валидация email

## 🛠️ Частые задачи

### Добавить защищенный query
```python
# backend/app/schemas/graphql.py
@strawberry.field
def my_protected_query(self, info: Info) -> str:
    # Получить пользователя из контекста
    request = info.context.get("request")
    auth_header = request.headers.get("Authorization")
    # ... verify token ...
    return "Protected data"
```

### Добавить защищенный маршрут
```tsx
// frontend/src/App.tsx
<Route
  path="/new-page"
  element={
    <ProtectedRoute>
      <NewPage />
    </ProtectedRoute>
  }
/>
```

### Проверить права администратора
```tsx
const { user } = useAuth();

if (user?.isSuperuser) {
  // Показать функции администратора
}
```

## 📝 Поля User Model

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Primary key |
| `email` | String | Unique, required |
| `username` | String | Unique, required |
| `hashed_password` | String | Никогда не возвращается в API |
| `is_active` | Boolean | Default: true |
| `is_superuser` | Boolean | Default: false |
| `created_at` | DateTime | Автоматически |
| `updated_at` | DateTime | Автоматически |

## 🔄 Поток авторизации

1. **Register/Login** → Получить JWT токен
2. **Сохранить токен** → localStorage (автоматически)
3. **Делать запросы** → Токен добавляется в headers (автоматически)
4. **Доступ к защищенным маршрутам** → Токен верифицируется
5. **Logout** → Токен удаляется из localStorage

## 🚨 Troubleshooting

| Проблема | Решение |
|----------|---------|
| "Invalid credentials" | Проверьте email/password, убедитесь что пользователь существует |
| "Unauthorized" | Проверьте наличие токена в localStorage, может истек |
| Redirect loop | Очистите localStorage: `localStorage.clear()` |
| CORS errors | Backend разрешает все источники в dev режиме |
| Токен не работает | Токен истекает через 30 минут, войдите заново |

## 📊 Статистика тестов

```
✅ 28 passed tests
├── 10 Model tests
├── 7 Security tests  
└── 11 Service tests

Coverage: ~95%
```

## 🔗 Связанные документы

- [[Authentication Setup]] - Полная документация
- [[Testing Guide]] - Руководство по тестированию
- [[Quick Start]] - Быстрый старт

---

*Обновлено: 2025-10-09*

