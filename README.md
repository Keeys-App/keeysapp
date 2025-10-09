# Locales - Translation Management System

> Система управления локализацией с полноценной системой авторизации

## 🚀 Быстрый старт

### Требования
- Python 3.12+
- Node.js 18+
- PostgreSQL
- Yarn

### Запуск Backend
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

### Тестирование
- ✅ 28 автоматических тестов
- ✅ Покрытие кода ~95%
- ✅ Тесты моделей (10)
- ✅ Тесты сервисов (11)
- ✅ Тесты безопасности (7)

### UI/UX
- ✅ Красивые формы с Radix UI
- ✅ Темная/светлая тема
- ✅ Валидация на клиенте
- ✅ Обработка ошибок
- ✅ Адаптивный дизайн

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

**Результат:** ✅ 28 passed in 6.01s (~95% coverage)

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
├── backend/          # FastAPI + GraphQL
│   ├── app/         # Код приложения
│   │   ├── models/     # SQLAlchemy модели
│   │   ├── schemas/    # GraphQL схемы
│   │   ├── services/   # Бизнес-логика
│   │   └── core/       # Конфигурация, JWT
│   └── tests/       # 28 тестов
├── frontend/        # React + TypeScript
│   └── src/
│       ├── components/  # React компоненты
│       ├── contexts/    # React contexts
│       ├── pages/       # Страницы
│       └── graphql/     # GraphQL queries
└── docs/
    └── obsidian/    # Документация
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

# Тесты
pytest -v

# Coverage
pytest --cov=app --cov-report=html
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

- [ ] Добавить восстановление пароля
- [ ] Реализовать подтверждение email
- [ ] Добавить OAuth (Google, GitHub)
- [ ] Реализовать refresh tokens
- [ ] Добавить управление профилем
- [ ] RBAC (Role-Based Access Control)
- [ ] Функционал управления переводами
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

**Документация:** [docs/obsidian/](docs/obsidian/) | **Тесты:** ✅ 28 passed (~95% coverage)
