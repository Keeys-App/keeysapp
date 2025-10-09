# GraphQL Integration Setup

## Обзор

В проект успешно интегрирован GraphQL с использованием:
- **Backend**: Strawberry GraphQL + FastAPI
- **Frontend**: Apollo Client + React

## Backend Changes

### Новые зависимости
- `strawberry-graphql[fastapi]==0.221.0`

### Новые файлы
- `app/schemas/graphql.py` - GraphQL типы и схемы
- `app/resolvers/locale_resolver.py` - GraphQL резолверы
- `app/schemas/schema.py` - Основная GraphQL схема

### Обновленные файлы
- `main.py` - добавлен GraphQL endpoint на `/graphql`
- `requirements.txt` - добавлена зависимость strawberry-graphql

## Frontend Changes

### Новые зависимости
- `@apollo/client` - GraphQL клиент
- `graphql` - GraphQL библиотека

### Новые файлы
- `src/lib/apollo.ts` - Apollo Client конфигурация
- `src/graphql/locales.ts` - GraphQL запросы и мутации
- `src/components/LocaleForm.tsx` - Форма для создания/редактирования локалей

### Обновленные файлы
- `src/main.tsx` - добавлен ApolloProvider
- `src/components/LocaleManager.tsx` - переписан для использования GraphQL
- `package.json` - добавлены GraphQL зависимости

## GraphQL Endpoints

### Queries
```graphql
# Получить все локали с фильтрацией
query GetLocales($filter: LocaleFilter, $skip: Int, $limit: Int) {
  locales(filter: $filter, skip: $skip, limit: $limit) {
    id
    key
    value
    language
    namespace
    isActive
    createdAt
    updatedAt
  }
}

# Получить локаль по ID
query GetLocale($id: Int!) {
  locale(id: $id) {
    id
    key
    value
    language
    namespace
    isActive
    createdAt
    updatedAt
  }
}

# Экспорт локалей в JSON
query ExportLocales($language: String!, $namespace: String) {
  exportLocales(language: $language, namespace: $namespace)
}
```

### Mutations
```graphql
# Создать новую локаль
mutation CreateLocale($input: LocaleCreateInput!) {
  createLocale(input: $input) {
    id
    key
    value
    language
    namespace
    isActive
    createdAt
    updatedAt
  }
}

# Обновить локаль
mutation UpdateLocale($id: Int!, $input: LocaleUpdateInput!) {
  updateLocale(id: $id, input: $input) {
    id
    key
    value
    language
    namespace
    isActive
    createdAt
    updatedAt
  }
}

# Удалить локаль
mutation DeleteLocale($id: Int!) {
  deleteLocale(id: $id) {
    success
    message
  }
}
```

## Запуск

### Backend
```bash
cd backend
# Активировать виртуальное окружение
source venv/bin/activate
# Установить новые зависимости
pip install -r requirements.txt
# Запустить сервер
python main.py
```

### Frontend
```bash
cd frontend
# Установить новые зависимости
yarn install
# Запустить dev сервер
yarn dev
```

## GraphQL Playground

После запуска backend, GraphQL Playground будет доступен по адресу:
- http://localhost:8000/graphql

## Новые возможности

1. **Фильтрация локалей** - по языку, namespace и статусу активности
2. **CRUD операции** - создание, чтение, обновление и удаление локалей через GraphQL
3. **Экспорт локалей** - получение локалей в JSON формате
4. **Улучшенный UI** - форма для создания/редактирования с валидацией
5. **Реальное время** - автоматическое обновление данных после мутаций

## Преимущества GraphQL

1. **Точные запросы** - получаете только нужные данные
2. **Единый endpoint** - все операции через `/graphql`
3. **Типизация** - строгая типизация на клиенте и сервере
4. **Интроспекция** - автоматическая документация API
5. **Кэширование** - Apollo Client автоматически кэширует данные
