# Quick Start

> [!info] Быстрый старт проекта Locales

## Предварительные требования

- Python 3.12+
- Node.js 18+
- PostgreSQL
- Yarn

## Установка и запуск

### 1. Подготовка

```bash
cd /Users/mbrtn/Projects/locales
```

### 2. Backend

```bash
cd backend

# Активировать виртуальное окружение
source venv/bin/activate

# Установить зависимости (если еще не установлены)
pip install -r requirements.txt

# Создать .env файл
cp env.example .env

# Сгенерировать JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Скопируйте вывод и используйте как JWT_SECRET_KEY

# Настроить .env:
# DATABASE_URL=postgresql://user:password@localhost:5432/locales_db
# JWT_SECRET_KEY=<сгенерированный_ключ>
# JWT_ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 дней

# Запустить сервер
python main.py
```

Backend будет доступен на `http://localhost:8000`

### 3. Frontend

```bash
cd frontend

# Установить зависимости
yarn install

# Запустить dev сервер
yarn dev
```

Frontend будет доступен на `http://localhost:5173`

## Использование приложения

1. Откройте `http://localhost:5173` в браузере
2. Нажмите **"Sign up"** для создания аккаунта
3. Заполните форму:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `password123`
4. После регистрации вы автоматически войдете в систему
5. Вы увидите дашборд с информацией о пользователе

## Тестирование через GraphQL

Откройте `http://localhost:8000/graphql`

### Регистрация

```graphql
mutation {
  register(input: {
    email: "test@example.com"
    username: "testuser"
    password: "password123"
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

### Вход

```graphql
mutation {
  login(input: {
    email: "test@example.com"
    password: "password123"
  }) {
    accessToken
    user {
      username
    }
  }
}
```

### Получить текущего пользователя

```graphql
query {
  me {
    id
    username
    email
  }
}
```

HTTP Headers:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

## Что включено

### Backend
✅ Модель User с хэшированием паролей (bcrypt)  
✅ JWT авторизация  
✅ GraphQL мутации: `register`, `login`  
✅ GraphQL query: `me` (получить текущего пользователя)  
✅ Автоматическое создание таблиц БД  

### Frontend
✅ Форма входа с валидацией  
✅ Форма регистрации с валидацией  
✅ Защищенные маршруты (редирект на login если не авторизован)  
✅ Auth context для управления состоянием  
✅ Токен сохраняется в localStorage  
✅ Apollo Client настроен с auth headers  
✅ Красивый UI с Radix UI компонентами  
✅ Поддержка темной/светлой темы  

## Следующие шаги

- Добавить больше функций на дашборд
- Создать дополнительные защищенные маршруты
- Добавить управление профилем пользователя
- Реализовать role-based access control
- Добавить функцию восстановления пароля

## Переменные окружения

Полное описание всех переменных смотрите в [[Environment Variables]].

**Обязательные:**
- `DATABASE_URL` - подключение к PostgreSQL
- `JWT_SECRET_KEY` - секретный ключ для JWT токенов

**Опциональные (есть дефолтные значения):**
- `JWT_ALGORITHM` - алгоритм шифрования JWT (по умолчанию: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - время жизни токена в минутах (по умолчанию: 525600 = 1 год)

## Связанные документы

- [[Environment Variables]] - Переменные окружения
- [[Authentication Setup]] - Подробная документация по авторизации
- [[Authentication Cheatsheet]] - Шпаргалка по авторизации
- [[Testing Guide]] - Руководство по тестированию

---

*Обновлено: 2025-10-10*

