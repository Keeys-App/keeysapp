# FastAPI + GraphQL + React Boilerplate

Чистый бойлерплейт для быстрого старта разработки с современным стеком технологий.

## 🚀 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **Strawberry GraphQL** - GraphQL библиотека для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **Alembic** - миграции базы данных

### Frontend
- **React 19** - библиотека для создания пользовательских интерфейсов
- **TypeScript** - типизированный JavaScript
- **Apollo Client** - GraphQL клиент для React
- **Vite** - быстрый сборщик и dev-сервер

## 📁 Структура проекта

```
├── backend/                 # Python FastAPI приложение
│   ├── app/
│   │   ├── core/           # Конфигурация
│   │   ├── database.py     # Настройка БД
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # GraphQL схемы
│   │   └── routers/        # REST API роутеры (если нужны)
│   ├── main.py            # Точка входа
│   └── requirements.txt   # Python зависимости
│
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── graphql/        # GraphQL запросы и мутации
│   │   ├── lib/           # Утилиты (Apollo Client)
│   │   └── main.tsx       # Точка входа
│   └── package.json       # Node.js зависимости
│
└── docs/                  # Документация
```

## 🛠 Установка и запуск

### Backend

1. **Создайте виртуальное окружение:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте базу данных:**
   - Создайте PostgreSQL базу данных
   - Скопируйте `env.example` в `.env` и настройте переменные

4. **Запустите сервер:**
   ```bash
   python main.py
   ```

### Frontend

1. **Установите зависимости:**
   ```bash
   cd frontend
   yarn install
   ```

2. **Запустите dev-сервер:**
   ```bash
   yarn dev
   ```

## 🔗 Endpoints

- **Backend API:** http://localhost:8000
- **GraphQL Playground:** http://localhost:8000/graphql
- **Frontend:** http://localhost:5173

## 📝 Демо функционал

Бойлерплейт включает базовый демо функционал:

### GraphQL Schema
```graphql
type User {
  id: Int!
  name: String!
  email: String!
}

type Query {
  hello: String!
  users: [User!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
}
```

### Примеры запросов

**Query:**
```graphql
query {
  hello
  users {
    id
    name
    email
  }
}
```

**Mutation:**
```graphql
mutation {
  createUser(name: "John Doe", email: "john@example.com") {
    id
    name
    email
  }
}
```

## 🎯 Следующие шаги

1. **Спроектируйте вашу предметную область**
2. **Создайте SQLAlchemy модели** в `backend/app/models/`
3. **Определите GraphQL схему** в `backend/app/schemas/`
4. **Создайте React компоненты** в `frontend/src/components/`
5. **Добавьте GraphQL запросы** в `frontend/src/graphql/`

## 🧹 Очистка

Если нужно убрать демо функционал:

1. Удалите `backend/app/schemas/graphql.py`
2. Удалите `frontend/src/components/Demo.tsx`
3. Удалите `frontend/src/graphql/demo.ts`
4. Обновите `frontend/src/App.tsx`

## 📚 Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [Apollo Client](https://www.apollographql.com/docs/react/)
- [React Documentation](https://react.dev/)

---

**Готово к разработке! 🚀**
