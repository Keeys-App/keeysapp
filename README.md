# Locales - Translation Management System

> Система управления локализацией с полноценной системой авторизации

## 🚀 Быстрый старт

### Требования
- Python 3.12+
- Node.js 18+
- PostgreSQL
- Yarn

### Запуск Backend

**Сначала запустите PostgreSQL:**
```bash
# macOS (Homebrew)
brew services start postgresql@14

# или если установлен Postgres.appas
# просто запустите приложение Postgres.app
```

**Затем запустите backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend: http://localhost:8000

### Запуск Frontend
```bash
cd frontend
yarn dev
```
Frontend: http://localhost:5173

## 📚 Документация

Полная документация находится в **Obsidian Vault**: `docs/obsidian/`

### 📖 Основные документы

| Документ | Описание |
|----------|----------|
| [README](docs/obsidian/README.md) | Главная страница документации |
| [Quick Start](docs/obsidian/Quick%20Start.md) | Подробный быстрый старт |
| [Authentication Setup](docs/obsidian/Authentication%20Setup.md) | Полная настройка системы авторизации |
| [Authentication Cheatsheet](docs/obsidian/Authentication%20Cheatsheet.md) | Быстрая справка по авторизации |
| [Testing Guide](docs/obsidian/Testing%20Guide.md) | Руководство по тестированию (28 тестов) |
| [Project Structure](docs/obsidian/Project%20Structure.md) | Детальная структура проекта |

### 🔍 Как использовать документацию

**В Obsidian (рекомендуется):**
1. Откройте Obsidian
2. "Open folder as vault"
3. Выберите `docs/obsidian`
4. Используйте внутренние ссылки для навигации

**В редакторе кода:**
- Просто открывайте `.md` файлы в `docs/obsidian/`

## 🏗️ Технологический стек

### Backend
- **FastAPI** - Современный веб-фреймворк
- **Strawberry GraphQL** - GraphQL для Python
- **PostgreSQL** - База данных
- **SQLAlchemy** - ORM
- **JWT** (pyjwt) - Авторизация
- **bcrypt** - Хэширование паролей
- **pytest** - Тестирование

### Frontend
- **React 19** - UI библиотека
- **TypeScript** - Типизация
- **Radix UI** - Компоненты UI
- **Apollo Client** - GraphQL клиент
- **React Router** - Маршрутизация
- **Vite** - Сборка

## ✅ Реализовано

### Система авторизации
- ✅ Регистрация пользователей
- ✅ Вход с JWT токенами
- ✅ Защищенные маршруты
- ✅ Хэширование паролей (bcrypt)
- ✅ GraphQL API (queries & mutations)
- ✅ Контекст авторизации на frontend
- ✅ Автоматическое обновление токенов в headers
- ✅ Валидация форм

### Модуль проектов
- ✅ CRUD операции для проектов (создание, чтение, обновление, удаление)
- ✅ Система прав доступа (owner, admin, editor, viewer)
- ✅ Управление участниками проектов
- ✅ Многоязычность (поддержка нескольких языков в проекте)
- ✅ Цветовые метки для проектов
- ✅ Статусы проектов (active, archived, draft)
- ✅ UI с карточками проектов (grid layout)
- ✅ Модальные окна создания/редактирования
- ✅ Проверка прав доступа на backend

### Тестирование
- ✅ 70 автоматических тестов
- ✅ Покрытие кода ~95%
- ✅ Тесты моделей (10)
- ✅ Тесты сервисов (30)
- ✅ Тесты безопасности/JWT (7)
- ✅ Тесты UUID (5)
- ✅ Тесты обработки ошибок (18)

### UI/UX
- ✅ Красивые формы с Radix UI
- ✅ Темная/светлая тема
- ✅ Валидация на клиенте
- ✅ Обработка ошибок
- ✅ Адаптивный дизайн
- ✅ Grid layout для списка проектов
- ✅ Color picker для выбора цвета
- ✅ Multi-select для языков

## 🧪 Тестирование

```bash
cd backend
source venv/bin/activate

# Все тесты
pytest

# С подробным выводом
pytest -v

# С покрытием
pytest --cov=app --cov-report=html
```

**Результат:** ✅ 70 passed in 12.19s (~95% coverage)

**Включает:**
- ✅ 10 тестов моделей
- ✅ 7 тестов JWT/безопасности  
- ✅ 30 тестов сервисов (11 user + 19 project)
- ✅ 5 тестов UUID
- ✅ 18 тестов обработки ошибок и защиты

Подробнее: [Testing Guide](docs/obsidian/Testing%20Guide.md)

## 🔐 Авторизация

### GraphQL Playground
http://localhost:8000/graphql

**Регистрация:**
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    username: "johndoe"
    password: "password123"
  }) {
    accessToken
    user { id username email }
  }
}
```

**Вход:**
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "password123"
  }) {
    accessToken
    user { username }
  }
}
```

Подробнее: [Authentication Setup](docs/obsidian/Authentication%20Setup.md)

## 📁 Структура проекта

```
Locales/
├── backend/                  # FastAPI + GraphQL
│   ├── app/                 # Код приложения
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # GraphQL схемы
│   │   ├── services/        # Бизнес-логика
│   │   └── core/            # Config, JWT, Exceptions
│   ├── tests/               # Unit тесты (70)
│   ├── migrations/          # БД миграции (авто)
│   ├── scripts/             # Утилиты
│   └── integration_tests/   # Интеграционные тесты
├── frontend/                # React + TypeScript
│   └── src/
│       ├── components/      # React компоненты
│       ├── contexts/        # React contexts
│       ├── pages/           # Страницы
│       └── graphql/         # GraphQL queries
└── docs/
    └── obsidian/            # Документация
```

Подробнее: [Project Structure](docs/obsidian/Project%20Structure.md)

## 🔗 Полезные ссылки

| Сервис | URL |
|--------|-----|
| Backend API | http://localhost:8000 |
| GraphQL Playground | http://localhost:8000/graphql |
| Frontend App | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

## 🛠️ Разработка

### Backend
```bash
# Запуск с автоперезагрузкой
cd backend
source venv/bin/activate
python main.py

# Unit тесты
pytest -v

# Coverage
pytest --cov=app --cov-report=html

# Утилиты
python scripts/list_users.py
python scripts/clear_users.py

# Миграции (автоматически при старте или вручную)
python migrations/migrate_add_public_id.py
```

### Frontend
```bash
# Dev сервер
cd frontend
yarn dev

# Линтинг
yarn lint

# Сборка
yarn build
```

## 🔄 Следующие шаги

### Функционал переводов
- [ ] Ключи переводов (keys) для проектов
- [ ] Редактор переводов с поддержкой множественных языков
- [ ] Импорт/экспорт переводов (JSON, YAML, CSV)
- [ ] История изменений переводов
- [ ] Комментарии к переводам

### Улучшения авторизации
- [ ] Добавить восстановление пароля
- [ ] Реализовать подтверждение email
- [ ] Добавить OAuth (Google, GitHub)
- [ ] Реализовать refresh tokens

### Дополнительно
- [ ] Добавить управление профилем
- [ ] Поиск по проектам
- [ ] Фильтрация и сортировка
- [ ] Статистика по проектам
- [ ] API документация

## 🤝 Вклад в проект

1. Изучите документацию в `docs/obsidian/`
2. Создайте feature branch
3. Напишите код и тесты
4. Убедитесь что все тесты проходят
5. Создайте Pull Request

## 📝 Лицензия

Все права защищены © 2025

---

**Документация:** [docs/obsidian/](docs/obsidian/) | **Тесты:** ✅ 70 passed (~95% coverage) | **Безопасность:** UUID + Safe Errors
