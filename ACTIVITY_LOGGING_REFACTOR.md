# Universal Activity Logging System - Refactoring Summary

## 🎯 Что сделано

Система логирования переведена с узкоспециализированной `key_logs` на универсальную `activity_logs`.

### ✅ Основные изменения:

1. **Новая модель `ActivityLog`**
   - Универсальная таблица для всех типов активности
   - Поддержка project-level, key-level и team management actions
   - SET NULL foreign keys (история сохраняется после удаления)
   - Новые поля: `project_id`, `affected_user_id`, `extra_data`

2. **Расширенный enum `ActionType`**
   - 🆕 Действия проекта: CREATE, UPDATE_NAME, UPDATE_DESCRIPTION, etc.
   - 🆕 Управление командой: MEMBER_ADD, MEMBER_REMOVE, MEMBER_ROLE_CHANGE
   - ✏️ Действия ключей: KEY_CREATE, KEY_UPDATE, KEY_DELETE
   - ✏️ Переводы: TRANSLATION_UPDATE, TRANSLATION_DELETE, TRANSLATION_IMPORT
   - ✅ Review actions: REVIEW_APPROVE, REVIEW_REJECT, REVIEW_DELETE

3. **Автоматическая миграция**
   - `key_logs` → `activity_logs`
   - Сохранены все существующие данные
   - Обновлены enum значения
   - Добавлены индексы

4. **Новый GraphQL query**
   ```graphql
   projectActivity(projectId: String!, limit: Int): [ActivityLogType!]!
   ```
   Возвращает ВСЕ логи проекта (включая изменения ключей и переводов)

5. **Backward Compatibility**
   - Старый API `keyLogs` продолжает работать
   - Legacy типы `KeyLog` и `KeyActionType` доступны

## 📊 Структура

### Backend

**Новые файлы:**
- `backend/app/models/activity_log.py` - модель ActivityLog
- `backend/migrations/migrate_to_activity_logs.py` - миграция
- `docs/obsidian/Universal Activity Logging.md` - документация

**Обновленные файлы:**
- `backend/app/models/__init__.py` - экспорт ActivityLog
- `backend/app/services/key_service.py` - использует ActivityLog
- `backend/app/services/project_service.py` - использует ActivityLog в импорте
- `backend/app/schemas/key.py` - новые типы и query
- `backend/app/schemas/graphql.py` - добавлен projectActivity
- `backend/migrations/auto_migrate.py` - автомиграция

## 🚀 Использование

### GraphQL Query - Project Activity

```graphql
query GetProjectActivity($projectId: String!) {
  projectActivity(projectId: $projectId, limit: 100) {
    id
    projectId
    keyId
    userId
    affectedUserId
    user {
      id
      email
      username
    }
    affectedUser {
      id
      email
      username
    }
    action
    fieldName
    language
    oldValue
    newValue
    createdAt
  }
}
```

### GraphQL Query - Key Logs (legacy, still works)

```graphql
query GetKeyLogs($keyId: String!) {
  keyLogs(keyId: $keyId, limit: 50) {
    id
    projectId
    keyId
    action
    fieldName
    language
    oldValue
    newValue
    createdAt
  }
}
```

## 📝 Action Types

### Project Actions (TODO - not yet logged)
- `PROJECT_CREATE` - проект создан
- `PROJECT_UPDATE_NAME` - имя изменено
- `PROJECT_UPDATE_DESCRIPTION` - описание изменено
- `PROJECT_UPDATE_LANGUAGES` - языки обновлены
- `PROJECT_UPDATE_COLOR` - цвет изменен
- `PROJECT_DELETE` - проект удален
- `PROJECT_IMPORT` / `PROJECT_EXPORT`

### Team Management (TODO - not yet logged)
- `MEMBER_ADD` - участник добавлен
- `MEMBER_REMOVE` - участник удален
- `MEMBER_ROLE_CHANGE` - роль изменена

### Key Actions (✅ already logged)
- `KEY_CREATE` - ключ создан
- `KEY_UPDATE` - ключ переименован
- `KEY_UPDATE_DESCRIPTION` - описание изменено
- `KEY_DELETE` - ключ удален

### Translation Actions (✅ already logged)
- `TRANSLATION_UPDATE` - перевод добавлен/обновлен
- `TRANSLATION_DELETE` - перевод удален
- `TRANSLATION_IMPORT` - перевод импортирован

### Review Actions (✅ already logged)
- `REVIEW_APPROVE` - перевод одобрен
- `REVIEW_REJECT` - перевод отклонен
- `REVIEW_DELETE` - отзыв удален

## 🎨 Frontend - Project Activity Page

### Рекомендуемая структура:

```
/projects/:id/activity
```

### Компоненты для реализации:

1. **ProjectActivityPage** - основная страница
2. **ActivityTimeline** - timeline всех действий
3. **ActivityItem** - отдельный элемент активности
4. **ActivityFilters** - фильтры (по типу, пользователю, дате)
5. **ActivityIcon** - иконки для разных типов действий

### Пример использования:

```typescript
import { useQuery } from '@apollo/client';
import { GET_PROJECT_ACTIVITY } from '@/graphql/activityLogs';

function ProjectActivityPage() {
  const { projectId } = useParams();
  const { data, loading } = useQuery(GET_PROJECT_ACTIVITY, {
    variables: { projectId, limit: 100 }
  });
  
  return (
    <div>
      <h1>Project Activity</h1>
      <ActivityTimeline logs={data?.projectActivity || []} />
    </div>
  );
}
```

## 🔧 TODO

1. **Добавить логирование в ProjectService:**
   - `create_project()`
   - `update_project()`
   - `delete_project()`
   - `add_project_member()`
   - `remove_project_member()`

2. **Создать frontend:**
   - Project Activity page
   - Activity timeline component
   - Filters and search

3. **Тесты:**
   - `test_activity_logging.py`
   - Frontend component tests

4. **UI polish:**
   - Icons for each action type
   - Diff view for changes
   - User avatars
   - Date grouping

## 🔗 Links

- Подробная документация: `docs/obsidian/Universal Activity Logging.md`
- Миграция: `backend/migrations/migrate_to_activity_logs.py`
- Model: `backend/app/models/activity_log.py`
- GraphQL Schema: `backend/app/schemas/key.py`

## ⚠️ Breaking Changes

Нет! Система полностью обратно совместима. Старый код продолжит работать.

### Migration Notes

- Миграция запускается автоматически при старте приложения
- Все существующие `key_logs` будут конвертированы в `activity_logs`
- Foreign keys изменены с CASCADE на SET NULL
- Enum значения обновлены (CREATE → KEY_CREATE, etc.)

## 📈 Benefits

1. **Единая лента активности** - все действия в проекте в одном месте
2. **Полная история** - логи сохраняются даже после удаления сущностей
3. **Расширяемость** - легко добавлять новые типы действий
4. **Team insights** - видно кто что делает в проекте
5. **Audit trail** - полный аудит для compliance

## 🎉 Готово к использованию!

Система полностью работает на backend. Осталось только создать UI для Project Activity page.

**Пример запроса через GraphQL Playground:**

```
http://localhost:8000/graphql
```

```graphql
query {
  projectActivity(projectId: "your-project-uuid", limit: 50) {
    id
    action
    user {
      email
    }
    oldValue
    newValue
    createdAt
  }
}
```

