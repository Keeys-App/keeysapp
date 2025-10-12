# Lazy Loading для Списка Ключей

## Обзор

Реализована функция ленивой загрузки (lazy loading) ключей переводов с пагинацией на уровне GraphQL и infinite scroll на фронтенде. Это значительно улучшает производительность при работе с проектами, содержащими большое количество ключей.

## Backend Изменения

### 1. GraphQL Schema (`backend/app/schemas/key.py` и `backend/app/schemas/graphql.py`)

#### Новый тип `KeysConnection`
```python
@strawberry.type
class KeysConnection:
    """
    Paginated response type for keys.
    """
    keys: List[KeyType]
    total_count: int
    has_more: bool
```

#### Обновленный Query `project_keys`
```python
@strawberry.field
def project_keys(
    self, 
    info: Info, 
    project_id: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 50
) -> KeysConnection
```

**Параметры:**
- `project_id` - UUID проекта
- `offset` - количество ключей для пропуска (по умолчанию: 0)
- `limit` - максимальное количество возвращаемых ключей (по умолчанию: 50, максимум: 200)

**Возвращает:**
- `keys` - список ключей
- `total_count` - общее количество ключей в проекте
- `has_more` - флаг наличия дополнительных ключей для загрузки

#### Регистрация в Root Schema (`backend/app/schemas/graphql.py`)
```python
from app.schemas.key import KeyQuery, KeyMutation, KeyType, KeysConnection, ActivityLogType

@strawberry.type
class Query:
    # Include key queries
    project_keys: KeysConnection = strawberry.field(resolver=KeyQuery.project_keys)
```

**Важно:** Тип возвращаемого значения должен быть `KeysConnection`, а не `List[KeyType]`!

### 2. Key Service (`backend/app/services/key_service.py`)

#### Новый метод `get_project_keys_paginated`
```python
@staticmethod
def get_project_keys_paginated(
    db: Session, 
    project_public_id: str, 
    user_id: int,
    offset: int = 0,
    limit: int = 50
) -> Optional[Dict[str, any]]
```

**Особенности:**
- Использует SQL `OFFSET` и `LIMIT` для эффективной пагинации
- Eager loading переводов через `joinedload` для предотвращения N+1 проблемы
- Возвращает как список ключей, так и общее количество
- Проверяет права доступа пользователя к проекту

## Frontend Изменения

### 1. GraphQL Query (`frontend/src/graphql/keys.ts`)

#### Обновленный запрос `GET_PROJECT_KEYS`
```graphql
query GetProjectKeys($projectId: String!, $offset: Int, $limit: Int) {
  projectKeys(projectId: $projectId, offset: $offset, limit: $limit) {
    keys {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
    totalCount
    hasMore
  }
}
```

### 2. KeyList Component (`frontend/src/components/key/KeyList.tsx`)

#### Основные изменения:

**Константы:**
```typescript
const PAGE_SIZE = 50; // Размер страницы для загрузки
```

**State:**
```typescript
const [isLoadingMore, setIsLoadingMore] = useState(false);
```

**Функция загрузки дополнительных ключей:**
```typescript
const loadMoreKeys = useCallback(async () => {
  if (isLoadingMore || !hasMore) {
    return;
  }

  setIsLoadingMore(true);
  try {
    await fetchMore({
      variables: {
        offset: keys.length,
        limit: PAGE_SIZE,
      },
      updateQuery: (prev, { fetchMoreResult }) => {
        // Объединение предыдущих и новых ключей
        return {
          projectKeys: {
            ...fetchMoreResult.projectKeys,
            keys: [
              ...(prev.projectKeys?.keys || []),
              ...(fetchMoreResult.projectKeys?.keys || []),
            ],
          },
        };
      },
    });
  } finally {
    setIsLoadingMore(false);
  }
}, [fetchMore, keys.length, hasMore, isLoadingMore]);
```

**Автоматическая загрузка при прокрутке:**
```typescript
useEffect(() => {
  const [lastItem] = [...virtualizer.getVirtualItems()].reverse();

  if (!lastItem) {
    return;
  }

  if (
    lastItem.index >= keys.length - 1 &&
    hasMore &&
    !isLoadingMore &&
    !loading
  ) {
    loadMoreKeys();
  }
}, [
  hasMore,
  loadMoreKeys,
  keys.length,
  isLoadingMore,
  loading,
  virtualizer.getVirtualItems(),
]);
```

**UI индикаторы:**
- Скелетон загрузки при подгрузке дополнительных ключей
- Сообщение "Loaded all {totalCount} keys" когда все ключи загружены

## Преимущества

### Производительность
- **Уменьшение начального времени загрузки**: Вместо загрузки всех ключей сразу, загружается только первая страница (50 ключей)
- **Меньше нагрузки на БД**: SQL запросы с LIMIT выполняются быстрее
- **Меньше памяти на клиенте**: В DOM рендерится только видимая часть списка благодаря виртуализации

### Масштабируемость
- **Поддержка больших проектов**: Проекты с тысячами ключей теперь загружаются мгновенно
- **Адаптивная загрузка**: Ключи загружаются по мере необходимости
- **Ограничение максимального размера страницы**: Защита от злоупотреблений (max 200 ключей за запрос)

### UX
- **Плавная прокрутка**: Виртуализация + lazy loading работают вместе
- **Визуальная обратная связь**: Индикаторы загрузки и счетчик загруженных ключей
- **Нет лишних ожиданий**: Пользователь может начать работать сразу после загрузки первой страницы

## Совместимость

- Старый метод `get_project_keys` сохранен для обратной совместимости
- Apollo Client кеширование работает корректно с пагинированными запросами
- Виртуализация (@tanstack/react-virtual) продолжает работать с динамическим списком

## Технические детали

### Backend
- **ORM**: SQLAlchemy с eager loading
- **GraphQL**: Strawberry
- **Безопасность**: Валидация параметров, проверка прав доступа, ограничение максимального limit

### Frontend
- **Apollo Client**: `fetchMore` для подгрузки данных
- **React Hooks**: `useCallback`, `useEffect` для оптимизации
- **Виртуализация**: @tanstack/react-virtual для рендеринга только видимых элементов

## Тестирование

### Проверка функционала:
1. Открыть проект с большим количеством ключей (>50)
2. Убедиться, что загружаются только первые 50 ключей
3. Прокрутить список вниз
4. Проверить автоматическую подгрузку следующей страницы
5. Убедиться в отображении индикатора загрузки
6. Дождаться загрузки всех ключей и проверить финальное сообщение

### Проверка производительности:
```bash
# Backend тесты (если есть)
cd backend
python -m pytest tests/test_key_performance.py

# Проверка GraphQL запросов
# Открыть GraphQL Playground и выполнить:
query {
  projectKeys(projectId: "...", offset: 0, limit: 50) {
    keys { id key }
    totalCount
    hasMore
  }
}
```

## Кастомный Скроллбар

### Проблема
При использовании lazy loading нативный скроллбар изменяет размер по мере загрузки новых элементов, что создает плохой UX - пользователь не понимает реальное количество элементов.

### Решение
Реализован кастомный скроллбар (`CustomScrollbar` компонент), который:

1. **Показывает реальные пропорции**: Размер и позиция скроллбара рассчитываются на основе `totalCount`, а не загруженных элементов
2. **Индикатор прогресса**: Внутри ползунка отображается прогресс загрузки (синий цвет заполняет пропорционально загруженным элементам)
3. **Процент загрузки**: Отображается текстовый индикатор процента загруженных ключей
4. **Интерактивность**: Поддерживает клик по треку и drag & drop ползунка

### Особенности реализации

**Виртуализация с totalCount:**
```typescript
const virtualizer = useVirtualizer({
  count: totalCount || keys.length, // Используем totalCount, а не keys.length
  // ...
});
```

**Рендеринг незагруженных элементов:**
```typescript
const key = keys[virtualItem.index];

// Если ключ еще не загружен, показываем skeleton
if (!key) {
  return <KeySkeleton />;
}
```

**Скрытие нативного скроллбара:**
```css
.hide-scrollbar {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}
.hide-scrollbar::-webkit-scrollbar {
  display: none; /* Chrome, Safari and Opera */
}
```

### Компоненты

- **`CustomScrollbar`** (`frontend/src/components/ui/custom-scrollbar.tsx`) - Кастомный скроллбар
- **Обновлен** `KeyList.tsx` - Интеграция кастомного скроллбара и виртуализации с totalCount

## Возможные улучшения

1. ~~**Кастомный скроллбар с правильными пропорциями**~~ ✅ Реализовано
2. **Предзагрузка**: Начинать загрузку следующей страницы заранее (при достижении 80% списка) - частично реализовано (загрузка за 10 элементов до конца)
3. **Кеширование на уровне Service Worker**: Для офлайн поддержки
4. **Виртуальная прокрутка с двусторонней загрузкой**: Загрузка в обе стороны при прокрутке
5. **Поиск и фильтрация**: Адаптировать пагинацию для работы с фильтрами
6. **Метрики**: Добавить аналитику для отслеживания времени загрузки страниц

## Миграция

Изменения обратно совместимы. Если старый код вызывает `projectKeys` без параметров `offset` и `limit`, они будут использовать значения по умолчанию (0 и 50).

Обновление не требует миграции базы данных - все изменения только на уровне логики.

**После обновления кода необходимо перезапустить backend сервер**, чтобы GraphQL схема обновилась с новым типом `KeysConnection`.

