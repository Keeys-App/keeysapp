# Keys Search Feature

## Обзор

Реализована функция поиска ключей переводов с поддержкой поиска по имени ключа, описанию и значениям переводов.

## Архитектура

### Backend

#### GraphQL Schema (`backend/app/schemas/key.py`)

Добавлен параметр `search` в query `project_keys`:

```python
@strawberry.field
def project_keys(
    self, 
    info: Info, 
    project_id: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 50,
    search: Optional[str] = None
) -> KeysConnection:
```

#### Service Layer (`backend/app/services/key_service.py`)

Метод `get_project_keys_paginated` обновлен для поддержки поиска:

```python
def get_project_keys_paginated(
    db: Session, 
    project_public_id: str, 
    user_id: int,
    offset: int = 0,
    limit: int = 50,
    search: Optional[str] = None
) -> Optional[Dict[str, any]]:
```

**Поиск выполняется по:**
- Имени ключа (`key.key`)
- Описанию ключа (`key.description`)
- Значениям переводов (`translation.value`)

Использует case-insensitive поиск через `ilike()` с паттерном `%search%`.

### Frontend

#### Store (`frontend/src/stores/useKeysSearchStore.ts`)

Создан Zustand store для управления состоянием поиска:

```typescript
interface KeysSearchState {
  search: string;
  setSearch: (search: string) => void;
  clearSearch: () => void;
}
```

#### GraphQL Query (`frontend/src/graphql/keys.ts`)

Обновлен запрос `GET_PROJECT_KEYS`:

```graphql
query GetProjectKeys($projectId: String!, $offset: Int, $limit: Int, $search: String) {
  projectKeys(projectId: $projectId, offset: $offset, limit: $limit, search: $search) {
    # ...
  }
}
```

#### Components

##### `KeysSearch` (`frontend/src/components/key/KeysSearch.tsx`)

- Поле ввода с debounce (300ms)
- Кнопка очистки поиска (крестик)
- Отображение количества результатов
- Интеграция с `useKeysSearchStore`

Особенности:
- Локальное состояние для мгновенной отзывчивости UI
- Debounce для минимизации запросов к серверу
- Синхронизация с глобальным store

##### `KeyList` (`frontend/src/components/key/KeyList.tsx`)

Обновлен для:
- Использования параметра `search` из store
- Очистки кэша при изменении поискового запроса
- Передачи `search` в GraphQL запросы (initial + fetchMore)

##### `EmptySearchResults` (`frontend/src/components/key/EmptySearchResults.tsx`)

Новый компонент для отображения пустого состояния при отсутствии результатов поиска:
- Отображает текст поискового запроса
- Кнопка очистки поиска
- Использует компонент `Empty` из UI библиотеки

##### `KeyControls` (`frontend/src/components/key/KeyControls.tsx`)

Обновлен для передачи `totalCount` в `KeysSearch` для отображения количества результатов.

## Безопасность

### 🚨 CRITICAL: Error Handling

**Проблема:** При ошибках SQL детали могли раскрываться пользователям, нарушая ПРАВИЛО #1 проекта.

**Решение:**
1. **Backend**: Все ошибки ловятся и логируются с полными деталями, но пользователям возвращается только `DatabaseError` с generic сообщением: "An error occurred. Please try again later."
2. **Технические детали** (SQL запросы, stack traces, имена таблиц) логируются только на сервере и НИКОГДА не передаются клиенту
3. **Frontend**: Использует `getUserFriendlyErrorMessage()` для дополнительной фильтрации

```python
# Backend error handling (backend/app/schemas/key.py)
except Exception as e:
    # Log technical details (только в логах сервера)
    logger.error(f"Error in project_keys query: {type(e).__name__}: {str(e)}", exc_info=True)
    # Raise user-friendly error (это видит пользователь)
    raise DatabaseError(internal_message=f"Error loading keys: {type(e).__name__}: {str(e)}")
```

### SQL Query Optimization

Использован подход с подзапросом для избежания проблем с `DISTINCT` на JSON полях:
- Сначала получаем ID ключей через подзапрос с `Translation.key_id.distinct()`
- Затем загружаем полные данные ключей по этим ID
- Это решает проблему "could not identify an equality operator for type json"

## Использование

### Для пользователей

1. На странице ключей проекта введите текст в поле поиска
2. Результаты обновятся автоматически после 300мс
3. Отображается количество найденных результатов
4. Нажмите крестик для очистки поиска

### Для разработчиков

**Backend:**
```python
# Поиск выполняется автоматически в KeyService.get_project_keys_paginated
# при передаче параметра search
```

**Frontend:**
```typescript
import { useKeysSearchStore } from '@/stores';

const { search, setSearch, clearSearch } = useKeysSearchStore();

// Установить поисковый запрос
setSearch('button');

// Очистить поиск
clearSearch();
```

## Производительность

- **Debounce**: 300ms для минимизации запросов
- **Cache invalidation**: Кэш очищается при изменении поискового запроса
- **Database indexing**: Используется существующий индекс на `keys.key`
- **Lazy loading**: Виртуализация списка работает с результатами поиска

## Ограничения

- Поиск case-insensitive
- Минимальная длина запроса: нет ограничений (можно искать по 1 символу)
- Поиск выполняется по полному совпадению подстроки (LIKE %search%)

## Возможные улучшения

1. **Full-text search**: Использование PostgreSQL Full-Text Search для более релевантного поиска
2. **Фильтры**: Добавить фильтры по тегам, статусу перевода, языкам
3. **История поиска**: Сохранение недавних поисковых запросов
4. **Подсветка**: Выделение найденных совпадений в результатах
5. **Сортировка**: Сортировка результатов по релевантности

## Testing

### Backend

Реализованы комплексные тесты для функции поиска в `backend/tests/test_key_search.py`:

```bash
# Запуск всех тестов поиска
cd backend
source venv/bin/activate
python -m pytest tests/test_key_search.py -v
```

**Покрытие тестами:**

✅ **12 тестов** охватывают следующие сценарии:

1. **`test_search_by_key_name`** - Поиск по имени ключа (например, "button")
2. **`test_search_by_description`** - Поиск по описанию ключа
3. **`test_search_by_translation_value`** - Поиск по значению перевода (на любом языке)
4. **`test_search_case_insensitive`** - Проверка регистронезависимого поиска
5. **`test_search_partial_match`** - Частичное совпадение (например, "err" найдет "error")
6. **`test_search_no_results`** - Поиск без результатов
7. **`test_search_with_pagination`** - Пагинация результатов поиска
8. **`test_search_empty_query`** - Пустой запрос возвращает все ключи
9. **`test_search_whitespace_query`** - Запрос только с пробелами
10. **`test_search_multiple_languages`** - Поиск на разных языках
11. **`test_search_unauthorized_user`** - Проверка доступа
12. **`test_search_with_special_characters`** - Поиск со спецсимволами

**Результаты:**
```
12 passed in 2.52s ✅
```

### Frontend

Frontend тесты можно добавить для компонентов:

```bash
# TODO: Добавить E2E тесты для UI поиска
yarn test KeysSearch
```

**Тестовые сценарии для frontend:**
- Debounce работает (300мс задержка)
- Индикатор загрузки показывается при вводе
- Счетчик результатов обновляется
- Кнопка очистки работает
- Состояние синхронизируется с store

## Индикатор загрузки

### UX Улучшения

Вместо показа скелетонов при поиске, индикатор загрузки отображается **в самом поле поиска**:

- ⚡ **Мгновенная обратная связь**: спиннер появляется при вводе текста
- 🔄 **Два состояния**: 
  - `isTyping` - пользователь печатает (debounce 300мс)
  - `isLoading` - выполняется GraphQL запрос
- 🎯 **Минималистичный UI**: нет отвлекающих скелетонов
- 👁️ **Всегда видимый**: индикатор в поле поиска на виду

```typescript
// KeysSearch.tsx
const showLoading = isLoading || isTyping;

<InputGroupButton>
  {showLoading ? <Spinner /> : <Search />}
</InputGroupButton>
```

**Логика отображения:**
- Скелетоны показываются **только** при первой загрузке страницы
- При поиске: только спиннер в поле поиска + обновление списка
- Если список уже загружен: плавная замена без скелетонов

## Related Files

### Backend
- `backend/app/services/key_service.py` - Логика поиска с подзапросами
- `backend/app/schemas/key.py` - GraphQL resolver с обработкой ошибок
- `backend/tests/test_key_search.py` - **12 тестов** для поиска

### Frontend
- `frontend/src/stores/useKeysSearchStore.ts` - Zustand store для состояния поиска
- `frontend/src/components/key/KeysSearch.tsx` - Поле поиска с debounce и индикатором
- `frontend/src/components/key/KeyList.tsx` - Виртуализированный список с поиском
- `frontend/src/components/key/EmptySearchResults.tsx` - Пустое состояние для поиска
- `frontend/src/components/key/KeyControls.tsx` - Панель управления ключами
- `frontend/src/graphql/keys.ts` - GraphQL запросы

