# Authentication Setup

> [!success] Полная документация системы авторизации

## Обзор

Система авторизации использует:
- **Backend**: JWT токены, bcrypt для хэширования паролей
- **Frontend**: React Context API, React Router для защищенных маршрутов
- **GraphQL**: Мутации для регистрации/входа, queries для текущего пользователя

## Backend

### Установка зависимостей

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Переменные окружения

Создайте `.env` файл в папке `backend`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/locales
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> [!warning] Важно
> Измените `SECRET_KEY` на случайную безопасную строку в продакшене!

### Миграция базы данных

Таблица User создается автоматически при запуске приложения. Для ручного создания:

```python
from app.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)
```

### Запуск Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

Сервер запустится на `http://localhost:8000`

## Frontend

### Установка зависимостей

```bash
cd frontend
yarn install
```

### Переменные окружения

Создайте `.env` файл в папке `frontend` (опционально):

```env
VITE_API_URL=http://localhost:8000
```

### Запуск Frontend

```bash
cd frontend
yarn dev
```

Приложение запустится на `http://localhost:5173`

## Функциональность

### Backend

#### Модели

**User Model** (`backend/app/models/user.py`):
- `id` - Integer, primary key
- `email` - String, unique, indexed
- `username` - String, unique, indexed
- `hashed_password` - String
- `is_active` - Boolean (default: True)
- `is_superuser` - Boolean (default: False)
- `created_at` - DateTime
- `updated_at` - DateTime

Методы:
- `verify_password(plain_password)` - Проверка пароля
- `get_password_hash(password)` - Хэширование пароля

#### GraphQL API

**Мутации:**

```graphql
# Регистрация
mutation Register($input: RegisterInput!) {
  register(input: $input) {
    accessToken
    tokenType
    user {
      id
      email
      username
      isActive
      isSuperuser
    }
  }
}

# Вход
mutation Login($input: LoginInput!) {
  login(input: $input) {
    accessToken
    tokenType
    user {
      id
      email
      username
      isActive
      isSuperuser
    }
  }
}
```

**Queries:**

```graphql
# Получить текущего пользователя
query Me {
  me {
    id
    email
    username
    isActive
    isSuperuser
  }
}
```

> [!note] Авторизация
> Для query `me` требуется заголовок: `Authorization: Bearer <token>`

#### Безопасность

- JWT токены для авторизации
- Bcrypt хэширование паролей
- Автоматическое обрезание паролей до 72 байт (ограничение bcrypt)
- Истечение токенов (настраивается)
- Защита эндпоинтов через Authorization header

### Frontend

#### Контексты

**AuthContext** (`frontend/src/contexts/AuthContext.tsx`):
- Управление состоянием авторизации
- Хранение user и token в localStorage
- Функции `login` и `logout`
- Флаг `isAuthenticated`

#### Компоненты

**LoginForm** (`frontend/src/components/LoginForm.tsx`):
- Email и password вход
- Обработка ошибок
- Переключение на регистрацию

**RegisterForm** (`frontend/src/components/RegisterForm.tsx`):
- Email, username и password регистрация
- Подтверждение пароля
- Валидация (мин. 6 символов, макс. 72)
- Обработка ошибок

**ProtectedRoute** (`frontend/src/components/ProtectedRoute.tsx`):
- Обертка для защищенных страниц
- Редирект на `/auth` если не авторизован
- Показ загрузки во время проверки

#### Страницы

**AuthPage** (`frontend/src/pages/AuthPage.tsx`):
- Страница входа/регистрации
- Переключение между формами

**DashboardPage** (`frontend/src/pages/DashboardPage.tsx`):
- Защищенный дашборд
- Отображение информации о пользователе
- Функция logout

#### Роутинг

```
/auth         - Страница входа/регистрации
/             - Защищенный дашборд
/* (другие)   - Редирект на /
```

## Примеры использования

### GraphQL Playground

Откройте `http://localhost:8000/graphql`

**Регистрация:**
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "secret123"
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

**Вход:**
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "secret123"
  }) {
    accessToken
    user {
      username
    }
  }
}
```

**Текущий пользователь:**
```graphql
query {
  me {
    id
    username
    email
  }
}
```

Заголовок:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

### Frontend

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

## Соображения безопасности

1. **Секретные данные** - Не коммитьте .env файлы
2. **SECRET_KEY** - Используйте случайную строку в продакшене
3. **HTTPS** - Всегда используйте HTTPS для передачи токенов
4. **Истечение токенов** - Настройте подходящее время жизни
5. **Сложность паролей** - Минимум 6 символов (можно увеличить)
6. **CORS** - Обновите разрешенные источники в продакшене

## Структура файлов

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py           # Настройки
│   │   └── security.py         # JWT утилиты
│   ├── models/
│   │   ├── user.py            # Модель User
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py            # GraphQL auth типы
│   │   └── graphql.py         # Корневая GraphQL схема
│   └── services/
│       └── user_service.py    # Бизнес-логика пользователей
└── requirements.txt           # С pyjwt и bcrypt

frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx      # Форма входа
│   │   ├── RegisterForm.tsx   # Форма регистрации
│   │   └── ProtectedRoute.tsx # Защита маршрутов
│   ├── contexts/
│   │   ├── AuthContext.tsx    # Управление авторизацией
│   │   └── ThemeContext.tsx   # Управление темой
│   ├── graphql/
│   │   └── auth.ts            # Auth queries/mutations
│   ├── pages/
│   │   ├── AuthPage.tsx       # Страница входа/регистрации
│   │   └── DashboardPage.tsx  # Защищенный дашборд
│   ├── lib/
│   │   └── apollo.ts          # Apollo Client с auth
│   └── App.tsx                # Приложение с роутингом
```

## Следующие шаги

1. Добавить восстановление пароля
2. Реализовать подтверждение email
3. Добавить OAuth (Google, GitHub)
4. Реализовать refresh tokens
5. Добавить управление профилем
6. Реализовать RBAC (Role-Based Access Control)
7. Добавить rate limiting для входа
8. Добавить аудит логирование

## Troubleshooting

### Backend

- Проверьте DATABASE_URL
- Убедитесь что PostgreSQL запущен
- Проверьте SECRET_KEY в .env
- Убедитесь что venv активирован

### Frontend

- Очистите localStorage при проблемах с auth
- Проверьте API_URL на правильный backend
- Проверьте CORS на backend
- Смотрите консоль браузера на ошибки

### Проблемы авторизации

- Проверьте токен в Authorization header
- Токен может истечь (по умолчанию 30 минут)
- Убедитесь что user exists и is_active=True
- Проверьте правильность пароля

## Связанные документы

- [[Authentication Cheatsheet]] - Быстрая справка
- [[Testing Guide]] - Тестирование системы
- [[Quick Start]] - Быстрый старт

---

*Обновлено: 2025-10-09*

