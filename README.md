# Locales Монорепо

Монорепо для управления локализацией с фронтендом на React + TypeScript и бекендом на Python + FastAPI.

## Структура проекта

```
locales/
├── frontend/          # React + TypeScript + Vite
├── backend/           # Python + FastAPI
├── docker-compose.yml # Docker конфигурация
├── package.json       # Корневые скрипты
└── README.md
```

## Технологии

### Фронтенд
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Vite** - сборщик и dev сервер
- **Axios** - HTTP клиент
- **React Router** - маршрутизация

### Бекенд
- **FastAPI** - веб фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Alembic** - миграции
- **Pydantic** - валидация данных

### Инфраструктура
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация

## Быстрый старт

### Предварительные требования
- Node.js 18+
- Python 3.11+
- Docker и Docker Compose

### Установка

1. **Клонируйте репозиторий и установите зависимости:**
```bash
git clone <repository-url>
cd locales
npm run install:all
```

2. **Запустите проект с помощью Docker:**
```bash
docker-compose up --build
```

Или запустите локально:

3. **Запустите PostgreSQL:**
```bash
docker-compose up postgres -d
```

4. **Запустите бекенд:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

5. **Запустите фронтенд:**
```bash
cd frontend
npm run dev
```

## Доступные сервисы

- **Фронтенд**: http://localhost:3000
- **Бекенд API**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## API Endpoints

### Локализации

- `GET /api/v1/locales/` - Получить список локализаций
- `GET /api/v1/locales/{id}` - Получить локализацию по ID
- `POST /api/v1/locales/` - Создать новую локализацию
- `PUT /api/v1/locales/{id}` - Обновить локализацию
- `DELETE /api/v1/locales/{id}` - Удалить локализацию
- `GET /api/v1/locales/export/{language}` - Экспортировать локализации

### Параметры запросов

- `skip` - количество записей для пропуска (пагинация)
- `limit` - максимальное количество записей (по умолчанию 100)
- `language` - фильтр по языку (например: 'ru', 'en')
- `namespace` - фильтр по пространству имен

## Разработка

### Скрипты

```bash
# Установить все зависимости
npm run install:all

# Запустить все сервисы в режиме разработки
npm run dev

# Запустить только фронтенд
npm run dev:frontend

# Запустить только бекенд
npm run dev:backend

# Собрать фронтенд для продакшена
npm run build

# Очистить node_modules
npm run clean
```

### Структура базы данных

Таблица `locales`:
- `id` - уникальный идентификатор
- `key` - ключ локализации
- `value` - значение локализации
- `language` - язык (ru, en, etc.)
- `namespace` - пространство имен (default, admin, etc.)
- `is_active` - активна ли локализация
- `created_at` - дата создания
- `updated_at` - дата обновления

### Переменные окружения

Создайте файл `.env` в папке `backend/` на основе `env.example`:

```bash
cp backend/env.example backend/.env
```

## Docker

### Сборка и запуск
```bash
# Сборка всех сервисов
docker-compose build

# Запуск всех сервисов
docker-compose up

# Запуск в фоновом режиме
docker-compose up -d

# Остановка сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

### Логи
```bash
# Просмотр логов всех сервисов
docker-compose logs

# Просмотр логов конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

## Лицензия

MIT
