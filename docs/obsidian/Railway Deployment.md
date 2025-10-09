# Railway Deployment

> [!info] Руководство по развертыванию на Railway

## Обзор

Railway автоматически развертывает backend и frontend при push в git.

## 🚀 Быстрый деплой

### 1. Подготовка

Убедитесь что есть:
- Аккаунт на [Railway.app](https://railway.app)
- Railway CLI установлен (опционально)

### 2. Создание проекта

1. Зайдите на [Railway Dashboard](https://railway.app/dashboard)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите ваш репозиторий

### 3. Настройка Backend

Railway автоматически обнаружит `railway.json` и развернет backend.

**Переменные окружения (устанавливаются автоматически):**
- `DATABASE_URL` - Railway PostgreSQL
- `PORT` - Порт для приложения

**Дополнительные переменные (установите вручную):**
```env
SECRET_KEY=your-production-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> [!warning] SECRET_KEY
> Сгенерируйте безопасный ключ для продакшена!
> ```python
> import secrets
> print(secrets.token_urlsafe(32))
> ```

### 4. Настройка Frontend

1. Добавьте новый сервис в проекте
2. Выберите папку `frontend`
3. Установите переменные:

```env
VITE_API_URL=https://your-backend-url.railway.app
```

### 5. PostgreSQL Database

Railway может автоматически создать PostgreSQL:

1. В проекте нажмите **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway автоматически свяжет с backend (установит `DATABASE_URL`)

## 🔄 Миграции на Railway

### Автоматические миграции

Миграции запускаются **автоматически** при старте приложения!

```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    # Автоматические миграции
    from migrations.auto_migrate import run_all_migrations
    run_all_migrations()
    
    yield
```

**Что происходит:**
1. Railway запускает `python main.py`
2. При старте проверяются нужные миграции
3. Если `public_id` колонки нет - она добавляется
4. Генерируются UUID для существующих пользователей
5. Приложение запускается

**Преимущества:**
- ✅ Не нужно ничего делать вручную
- ✅ Безопасно - проверяет перед запуском
- ✅ Идемпотентно - можно запускать много раз
- ✅ Работает при каждом деплое

### Ручной запуск миграций

Если нужно запустить миграцию вручную на Railway:

```bash
# Через Railway CLI
railway run python migrations/migrate_add_public_id.py

# Или через Railway Shell
railway shell
source venv/bin/activate
python migrations/migrate_add_public_id.py
```

## 📝 Railway Configuration

### backend/railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### frontend/railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "yarn build && yarn preview"
  }
}
```

## 🔧 Troubleshooting

### Миграция не запустилась

**Проверьте логи:**
```bash
railway logs
```

**Ищите:**
```
🔄 Checking for pending migrations...
✅ Migration: public_id column added successfully
```

### Database connection failed

**Проверьте:**
1. PostgreSQL сервис создан и запущен
2. `DATABASE_URL` установлена автоматически Railway
3. Backend и Database в одном проекте

### Миграция упала

**Решение:**
1. Проверьте логи: `railway logs`
2. Попробуйте ручной запуск через Railway Shell
3. В крайнем случае - пересоздайте таблицы (удалит данные):

```bash
railway shell
python migrations/recreate_tables.py
```

## 🔐 Безопасность на Production

### Обязательные настройки

```env
# Railway Environment Variables
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=<auto-set-by-railway>
PORT=<auto-set-by-railway>
ENVIRONMENT=production
DEBUG=False
```

### CORS настройка

Обновите `main.py` для production:

```python
# Development
if settings.environment == "development":
    allow_origins = ["*"]
else:
    # Production - только ваши домены
    allow_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://your-app.railway.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Мониторинг миграций

### Логи миграций

Railway автоматически логирует:

```
INFO: Application startup
🔄 Checking for pending migrations...
Checking migration: add_public_id
✅ Migration: public_id column already exists, skipping
✅ Migrations check complete: 1/1 successful
INFO: Application startup complete
```

### При первом деплое

```
🔄 Migration: Adding public_id column to users table
✅ Column added
✅ Generated UUIDs for 0 user(s)
✅ Migration: public_id column added successfully
```

## 🎯 Best Practices

1. **Автоматические миграции** - Используйте `auto_migrate.py` (уже настроено)
2. **Идемпотентность** - Миграции безопасно запускать много раз
3. **Логирование** - Проверяйте логи Railway после деплоя
4. **Backup** - Railway делает автоматические backup
5. **Rollback** - Имейте план отката в git

## 🔄 Процесс деплоя

```
1. git push
   ↓
2. Railway обнаруживает изменения
   ↓
3. Railway собирает приложение
   ↓
4. Запускается main.py
   ↓
5. Создаются таблицы (если нужно)
   ↓
6. Запускаются миграции (автоматически)
   ↓
7. Приложение готово ✅
```

## 📱 Railway CLI

### Установка

```bash
npm install -g @railway/cli
```

### Команды

```bash
# Логин
railway login

# Подключиться к проекту
railway link

# Посмотреть логи
railway logs

# Запустить команду
railway run python migrations/migrate_add_public_id.py

# Открыть shell
railway shell

# Посмотреть переменные
railway variables
```

## 🆕 Добавление новой миграции

### 1. Создайте скрипт

```python
# migrations/migrate_add_new_field.py
def migrate_add_new_field():
    if check_column_exists('users', 'new_field'):
        logger.info("Column exists, skipping")
        return True
    
    # Add column
    # ...
    return True
```

### 2. Добавьте в auto_migrate.py

```python
def run_all_migrations():
    migrations = [
        ("add_public_id", migrate_add_public_id_if_needed),
        ("add_new_field", migrate_add_new_field),  # Новая миграция
    ]
    # ...
```

### 3. Commit и push

```bash
git add .
git commit -m "Add migration for new_field"
git push
```

Railway автоматически запустит новую миграцию при деплое!

## 🔗 Полезные ссылки

- [Railway Docs](https://docs.railway.app/)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)
- [Environment Variables](https://docs.railway.app/develop/variables)

## Связанные документы

- [[Quick Start]] - Локальная разработка
- [[Security Best Practices]] - Безопасность
- [[Project Structure]] - Структура проекта

---

*Обновлено: 2025-10-09*

