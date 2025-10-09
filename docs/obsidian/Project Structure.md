# Project Structure

> [!info] Структура проекта Locales

## Общий обзор

```
Locales/
├── backend/                # FastAPI + GraphQL Backend
├── frontend/               # React + TypeScript Frontend
├── docs/                   # Документация (Obsidian)
├── BOILERPLATE_README.md   # README шаблона
├── GRAPHQL_SETUP.md        # Настройка GraphQL
├── README.md               # Основной README
└── node_modules/           # Node зависимости (root)
```

## Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Настройки приложения
│   │   └── security.py        # JWT и безопасность
│   ├── database.py            # Подключение к БД
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # Базовая модель SQLAlchemy
│   │   └── user.py           # Модель User
│   ├── resolvers/            # GraphQL resolvers (пустая)
│   ├── routers/              # REST API routers (пустая)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py           # GraphQL auth схемы
│   │   └── graphql.py        # Корневая GraphQL схема
│   └── services/
│       └── user_service.py   # Бизнес-логика пользователей
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_models.py        # Тесты моделей
│   ├── test_security.py      # Тесты безопасности
│   ├── test_services.py      # Тесты сервисов
│   └── README.md             # Документация тестов
├── venv/                     # Виртуальное окружение
├── clear_users.py            # Утилита очистки пользователей
├── list_users.py             # Утилита просмотра пользователей
├── Dockerfile                # Docker образ
├── env.example               # Пример .env файла
├── main.py                   # Точка входа приложения
├── pytest.ini                # Конфигурация pytest
├── railway.json              # Конфигурация Railway
├── requirements.txt          # Python зависимости
└── run_tests.sh             # Скрипт запуска тестов
```

### Backend - Ключевые файлы

| Файл | Описание |
|------|----------|
| `main.py` | Точка входа, настройка FastAPI и GraphQL |
| `app/database.py` | Подключение к PostgreSQL через SQLAlchemy |
| `app/models/user.py` | Модель User с хэшированием паролей |
| `app/services/user_service.py` | CRUD операции для пользователей |
| `app/schemas/auth.py` | GraphQL типы и мутации для авторизации |
| `app/core/security.py` | JWT создание и верификация |
| `app/core/config.py` | Настройки из .env |

## Frontend

```
frontend/
├── dist/                     # Собранные файлы
├── node_modules/             # Node зависимости
├── public/
│   └── vite.svg             # Публичные файлы
├── src/
│   ├── assets/
│   │   └── react.svg        # Ресурсы
│   ├── components/
│   │   ├── LoginForm.tsx     # Форма входа
│   │   ├── ProtectedRoute.tsx # Защита маршрутов
│   │   └── RegisterForm.tsx  # Форма регистрации
│   ├── contexts/
│   │   ├── AuthContext.tsx   # Управление авторизацией
│   │   └── ThemeContext.tsx  # Управление темой
│   ├── graphql/
│   │   ├── __init__.ts
│   │   └── auth.ts           # Auth queries и mutations
│   ├── lib/
│   │   └── apollo.ts         # Apollo Client настройка
│   ├── pages/
│   │   ├── AuthPage.tsx      # Страница входа/регистрации
│   │   └── DashboardPage.tsx # Защищенный дашборд
│   ├── App.css              # Стили App
│   ├── App.tsx              # Главный компонент с роутингом
│   ├── index.css            # Глобальные стили
│   └── main.tsx             # Точка входа React
├── Dockerfile               # Docker образ
├── env.example              # Пример .env файла
├── eslint.config.js         # ESLint конфигурация
├── index.html               # HTML шаблон
├── nginx.conf               # Nginx конфигурация
├── package.json             # Node зависимости и скрипты
├── railway.json             # Конфигурация Railway
├── README.md                # Frontend README
├── tsconfig.json            # TypeScript конфигурация
├── tsconfig.app.json        # TypeScript для приложения
├── tsconfig.node.json       # TypeScript для Node
├── vite.config.ts           # Vite конфигурация
└── yarn.lock                # Yarn lock файл
```

### Frontend - Ключевые файлы

| Файл | Описание |
|------|----------|
| `src/main.tsx` | Точка входа React приложения |
| `src/App.tsx` | Роутинг и основная структура |
| `src/lib/apollo.ts` | Apollo Client с auth link |
| `src/contexts/AuthContext.tsx` | Управление состоянием авторизации |
| `src/graphql/auth.ts` | GraphQL запросы авторизации |
| `src/components/LoginForm.tsx` | Компонент формы входа |
| `src/components/RegisterForm.tsx` | Компонент формы регистрации |
| `src/components/ProtectedRoute.tsx` | HOC для защиты маршрутов |
| `src/pages/AuthPage.tsx` | Страница авторизации |
| `src/pages/DashboardPage.tsx` | Защищенная страница дашборда |

## Документация

```
docs/
└── obsidian/
    ├── README.md                    # Главная страница документации
    ├── Quick Start.md               # Быстрый старт
    ├── Authentication Setup.md      # Настройка авторизации
    ├── Authentication Cheatsheet.md # Шпаргалка
    ├── Testing Guide.md             # Руководство по тестам
    ├── Project Structure.md         # Этот файл
    ├── Backend Development.md       # Разработка backend
    └── Frontend Development.md      # Разработка frontend
```

## Конфигурационные файлы

### Backend

| Файл | Назначение |
|------|------------|
| `requirements.txt` | Python зависимости |
| `pytest.ini` | Настройки pytest |
| `.env` | Переменные окружения (не в git) |
| `env.example` | Пример .env |
| `Dockerfile` | Docker образ |
| `railway.json` | Деплой на Railway |

### Frontend

| Файл | Назначение |
|------|------------|
| `package.json` | Node зависимости и скрипты |
| `yarn.lock` | Версии зависимостей |
| `tsconfig.json` | TypeScript конфигурация |
| `vite.config.ts` | Vite build tool |
| `eslint.config.js` | Линтер |
| `.env` | Переменные окружения (не в git) |
| `env.example` | Пример .env |

## Соглашения по именованию

### Backend (Python)

```python
# Файлы: snake_case
user_service.py
auth_schema.py

# Классы: PascalCase
class UserService:
class AuthPayload:

# Функции и переменные: snake_case
def create_user():
user_data = {}

# Константы: UPPER_SNAKE_CASE
DATABASE_URL = "..."
SECRET_KEY = "..."
```

### Frontend (TypeScript/React)

```typescript
// Файлы компонентов: PascalCase
LoginForm.tsx
AuthContext.tsx

// Файлы утилит: camelCase
apollo.ts
auth.ts

// Компоненты: PascalCase
const LoginForm: FC = () => {}

// Функции и переменные: camelCase
const handleSubmit = () => {}
const userData = {}

// Константы: UPPER_SNAKE_CASE
const API_BASE_URL = "..."

// Типы и интерфейсы: PascalCase
interface User {}
type AuthContextType = {}
```

## Git структура

```
.git/
.gitignore              # Игнорируемые файлы
  ├── .env              # Секреты
  ├── venv/             # Python venv
  ├── node_modules/     # Node модули
  ├── __pycache__/      # Python cache
  └── dist/             # Build файлы
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Порты по умолчанию

| Сервис | Порт | URL |
|--------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| GraphQL Playground | 8000 | http://localhost:8000/graphql |
| Frontend Dev | 5173 | http://localhost:5173 |
| PostgreSQL | 5432 | localhost:5432 |

## Утилиты

### Backend

```bash
# Просмотр пользователей
python list_users.py

# Очистка пользователей
python clear_users.py

# Запуск тестов
pytest
./run_tests.sh
```

### Frontend

```bash
# Development
yarn dev

# Build
yarn build

# Lint
yarn lint

# Preview production build
yarn preview
```

## Связанные документы

- [[Quick Start]] - Быстрый старт
- [[Authentication Setup]] - Настройка авторизации
- [[Backend Development]] - Разработка backend
- [[Frontend Development]] - Разработка frontend

---

*Обновлено: 2025-10-09*

