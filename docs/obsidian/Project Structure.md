# Project Structure

> [!info] Структура проекта Keeys

## Общий обзор

```
Keeys/
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
├── app/                      # Основной код приложения
│   ├── core/
│   │   ├── config.py          # Настройки
│   │   ├── security.py        # JWT утилиты
│   │   └── exceptions.py      # Кастомные исключения (безопасные)
│   ├── database.py            # Подключение к БД
│   ├── models/
│   │   ├── base.py           # Базовая модель
│   │   └── user.py           # Модель User (с UUID)
│   ├── schemas/
│   │   ├── auth.py           # GraphQL auth схемы
│   │   └── graphql.py        # Корневая GraphQL схема
│   └── services/
│       └── user_service.py   # Бизнес-логика
├── tests/                    # Unit тесты (pytest)
│   ├── conftest.py           # Fixtures
│   ├── test_models.py        # Тесты моделей (10)
│   ├── test_security.py      # Тесты JWT (7)
│   ├── test_services.py      # Тесты сервисов (11)
│   ├── test_user_service_uuid.py  # Тесты UUID (5)
│   └── test_error_handling.py     # Тесты безопасности (18)
├── migrations/               # Миграции БД
│   ├── auto_migrate.py       # Автоматические миграции
│   ├── migrate_add_public_id.py   # Добавить UUID
│   ├── recreate_tables.py    # Пересоздать таблицы
│   └── README.md
├── scripts/                  # Утилиты
│   ├── clear_users.py        # Очистка пользователей
│   ├── list_users.py         # Список пользователей
│   └── README.md
├── integration_tests/        # Интеграционные тесты
│   ├── check_error_safety.py # Проверка безопасности ошибок
│   └── README.md
├── venv/                     # Виртуальное окружение
├── Dockerfile                # Docker образ
├── env.example               # Пример .env
├── main.py                   # Точка входа
├── pytest.ini                # Конфигурация pytest
├── railway.json              # Railway config
├── requirements.txt          # Зависимости
└── run_tests.sh             # Запуск тестов с coverage
```

### Backend - Ключевые файлы

| Файл | Описание |
|------|----------|
| `main.py` | Точка входа, настройка FastAPI и GraphQL |
| `app/database.py` | Подключение к PostgreSQL через SQLAlchemy |
| `app/models/user.py` | Модель User с UUID и хэшированием паролей |
| `app/services/user_service.py` | CRUD операции для пользователей |
| `app/schemas/auth.py` | GraphQL типы и мутации для авторизации |
| `app/core/security.py` | JWT создание и верификация |
| `app/core/exceptions.py` | Безопасные кастомные исключения |
| `app/core/config.py` | Настройки из .env |
| `migrations/auto_migrate.py` | Автоматические миграции при старте |
| `scripts/list_users.py` | Утилита просмотра пользователей |
| `scripts/clear_users.py` | Утилита очистки пользователей |

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

#### Скрипты управления (scripts/)
```bash
# Просмотр пользователей
python scripts/list_users.py

# Очистка пользователей
python scripts/clear_users.py
```

#### Миграции (migrations/)
```bash
# Автоматически при старте приложения
# Или вручную:
python migrations/migrate_add_public_id.py
python migrations/recreate_tables.py
```

#### Тесты
```bash
# Unit тесты
pytest

# С coverage
./run_tests.sh

# Интеграционные тесты
python integration_tests/check_error_safety.py
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

