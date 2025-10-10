# Environment Variables

> [!info] Полное описание всех переменных окружения проекта

## 📋 Обзор

Все переменные окружения хранятся в файле `.env` в корне папки `backend/`. Используйте `backend/env.example` как шаблон.

## 🗄️ База данных

### DATABASE_URL

**Описание:** URL подключения к PostgreSQL базе данных

**Формат:** `postgresql://username:password@host:port/database_name`

**Примеры:**
```env
# Локальная разработка
DATABASE_URL=postgresql://locales_user:locales_password@localhost:5432/locales_db

# Railway (автоматически)
DATABASE_URL=postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway

# Docker
DATABASE_URL=postgresql://postgres:postgres@db:5432/locales
```

**Обязательная:** ✅ Да

**Безопасность:**
- ⚠️ Никогда не коммитьте `.env` файл в git
- ⚠️ Не храните пароли в plain text в коде
- ⚠️ Используйте разные пароли для dev/prod

## 🔐 Безопасность (JWT)

### JWT_SECRET_KEY

**Описание:** Секретный ключ для подписи и проверки JWT токенов

**Формат:** Случайная строка длиной 32+ символа

**Генерация:**
```bash
# Способ 1: Python (рекомендуется)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Способ 2: OpenSSL
openssl rand -base64 32

# Способ 3: Python script
python3 << EOF
import secrets
print(secrets.token_urlsafe(32))
EOF
```

**Пример:**
```env
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

**Обязательная:** ✅ Да

**Безопасность:**
- 🔴 КРИТИЧНО: Используйте разные ключи для dev/prod
- 🔴 КРИТИЧНО: Никогда не коммитьте реальный ключ в git
- 🔴 КРИТИЧНО: Меняйте ключ при компрометации (все токены станут невалидными)
- ✅ Минимум 32 символа
- ✅ Используйте криптографически стойкий генератор (`secrets`, не `random`)

### JWT_ALGORITHM

**Описание:** Алгоритм шифрования для JWT токенов

**Формат:** Название алгоритма

**Значения:**
- `HS256` - HMAC SHA-256 (рекомендуется, по умолчанию)
- `HS384` - HMAC SHA-384
- `HS512` - HMAC SHA-512
- `RS256` - RSA SHA-256 (требует публичный/приватный ключ)

**Пример:**
```env
JWT_ALGORITHM=HS256
```

**Обязательная:** ❌ Нет (по умолчанию: `HS256`)

**Рекомендация:** Оставьте `HS256` если не знаете что выбрать

### ACCESS_TOKEN_EXPIRE_MINUTES

**Описание:** Время жизни JWT токена в минутах

**Формат:** Целое число (минуты)

**Примеры:**
```env
# 30 минут (production, высокая безопасность)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 7 дней (development, удобство)
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 1 день
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 1 год (mobile apps)
ACCESS_TOKEN_EXPIRE_MINUTES=525600
```

**Конвертация:**
- 1 час = 60 минут
- 1 день = 1440 минут (24 * 60)
- 7 дней = 10080 минут (7 * 24 * 60)
- 30 дней = 43200 минут (30 * 24 * 60)
- 1 год = 525600 минут (365 * 24 * 60)

**Обязательная:** ❌ Нет (по умолчанию: `525600` = 1 год)

**Рекомендации:**
- **Development:** 7 дней (10080) - не нужно постоянно логиниться
- **Production Web:** 30 минут - требует refresh token механизм
- **Production Mobile:** 30-90 дней - баланс удобства и безопасности
- **Internal tools:** 1 год - удобство для сотрудников

**Компромиссы:**
- ⬆️ Больше время = удобнее для пользователей, но менее безопасно
- ⬇️ Меньше время = безопаснее, но требует чаще логиниться

## 🌍 Окружение

### ENVIRONMENT

**Описание:** Тип окружения приложения

**Формат:** Строка

**Значения:**
- `development` - Разработка (по умолчанию)
- `production` - Продакшн
- `staging` - Тестовая среда
- `testing` - Автоматические тесты

**Пример:**
```env
ENVIRONMENT=development
```

**Обязательная:** ❌ Нет (по умолчанию: `development`)

**Влияние:**
- Логирование (более подробное в development)
- CORS политики (строже в production)
- Обработка ошибок (детальные в development)

### DEBUG

**Описание:** Режим отладки

**Формат:** Boolean (`true` / `false`)

**Пример:**
```env
# Development
DEBUG=true

# Production
DEBUG=false
```

**Обязательная:** ❌ Нет (по умолчанию: `true`)

**Влияние:**
- ✅ `true`: Подробные ошибки, hot reload, debug логи
- ❌ `false`: Скрытие деталей ошибок, production оптимизации

## 🚀 Сервер

### PORT

**Описание:** Порт для запуска backend сервера

**Формат:** Целое число

**Пример:**
```env
PORT=8000
```

**Обязательная:** ❌ Нет (по умолчанию: `8000`)

**Примечание:**
- Railway автоматически устанавливает порт
- В локальной разработке обычно `8000`
- Frontend ожидает backend на `8000` (или `VITE_API_URL`)

## 📝 Полный пример .env файла

### Development (локальная разработка)

```env
# Database
DATABASE_URL=postgresql://locales_user:locales_password@localhost:5432/locales_db

# Security - JWT
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 дней

# Environment
ENVIRONMENT=development
DEBUG=true
PORT=8000
```

### Production

```env
# Database (предоставляется Railway)
DATABASE_URL=postgresql://postgres:***@containers-us-west-123.railway.app:5432/railway

# Security - JWT
JWT_SECRET_KEY=***PRODUCTION_SECRET_KEY***
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 30 минут

# Environment
ENVIRONMENT=production
DEBUG=false
PORT=8000
```

## 🛠️ Настройка с нуля

### Шаг 1: Копируем шаблон

```bash
cd backend
cp env.example .env
```

### Шаг 2: Генерируем JWT_SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Скопируйте результат, например:
```
fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
```

### Шаг 3: Редактируем .env

```bash
nano .env  # или любой другой редактор
```

Заполняем:
```env
DATABASE_URL=postgresql://locales_user:locales_password@localhost:5432/locales_db
JWT_SECRET_KEY=fN3K_5mP9xQ2wR8tY7uI4oP3lK6jH5gF9dS2aQ1w
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=development
DEBUG=true
```

### Шаг 4: Проверяем

```bash
# Активируем venv
source venv/bin/activate

# Запускаем сервер
python main.py
```

Если всё ок, увидите:
```
Database URL: postgresql://locales_user:***@localhost:5432/locales_db
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## ⚠️ Важные предупреждения

### Не коммитьте .env

**Файл `.gitignore` должен содержать:**
```gitignore
.env
.env.local
.env.*.local
```

**Проверка:**
```bash
git status
# .env НЕ должен появиться в списке
```

### Разные ключи для окружений

| Окружение | JWT_SECRET_KEY | ACCESS_TOKEN_EXPIRE |
|-----------|----------------|---------------------|
| Development | `dev_secret_123` | 10080 (7 дней) |
| Staging | `staging_secret_456` | 1440 (1 день) |
| Production | `prod_secret_789` | 30 (30 минут) |

### Railway автоматические переменные

Railway автоматически предоставляет:
- `DATABASE_URL` - подключение к PostgreSQL
- `PORT` - порт для сервера
- `RAILWAY_ENVIRONMENT` - окружение (production/staging)

Вам нужно добавить только:
- `JWT_SECRET_KEY` ⚠️ ОБЯЗАТЕЛЬНО
- `JWT_ALGORITHM` (опционально)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (опционально)

## 🔗 Связанные документы

- [[Quick Start]] - Быстрый старт с настройкой переменных
- [[Security Best Practices]] - Безопасность и JWT токены
- [[Railway Deployment]] - Настройка переменных на Railway
- [[Authentication Setup]] - Система авторизации

## 📚 Дополнительные ресурсы

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Python secrets module](https://docs.python.org/3/library/secrets.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

*Обновлено: 2025-10-10*

