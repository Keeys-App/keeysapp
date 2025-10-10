# Key Logging Feature - Summary

## Что сделано ✅

Реализована полноценная система аудита (логирования) всех изменений ключей переводов.

## Основные компоненты

### 1. Backend Models
- **`KeyLog`** модель (`app/models/key_log.py`) - хранит историю изменений
- **`KeyActionType`** enum - типы действий (create, update, delete и т.д.)

### 2. Database
- Таблица `key_logs` с индексами для производительности
- Автоматическая миграция при запуске приложения
- CASCADE удаление при удалении ключа

### 3. Service Layer
- Метод `KeyService._create_log()` - создает записи логов
- Логирование интегрировано во все методы:
  - `create_key()` - создание ключа + переводы
  - `update_key()` - изменение имени/описания (теги НЕ логируются)
  - `set_translation()` - создание/обновление перевода
  - `delete_translation()` - удаление перевода
  - `delete_key()` - удаление ключа
  - `batch_import_translations()` - массовый импорт

### 4. GraphQL API
- Запрос `keyLogs(keyId: String!, limit: Int)` - получение истории
- Типы `KeyLogType` и `KeyActionTypeEnum`
- Автоматическая проверка прав доступа

### 5. Tests
- Полный набор тестов в `tests/test_key_logging.py`
- Покрытие всех сценариев использования

### 6. Documentation
- Детальная документация в `docs/obsidian/Key Logging.md`

## Что логируется ✅

- ✅ Создание ключа
- ✅ Изменение имени ключа
- ✅ Изменение описания
- ✅ Создание перевода
- ✅ Обновление перевода
- ✅ Удаление перевода
- ✅ Удаление ключа

## Что НЕ логируется ❌

- ❌ Изменение тегов (метаданные)
- ❌ Любые другие метаданные

## Пример использования

### GraphQL Query
```graphql
query GetKeyHistory($keyId: String!) {
  keyLogs(keyId: $keyId, limit: 20) {
    id
    action
    fieldName
    language
    oldValue
    newValue
    createdAt
    userId
  }
}
```

### Response
```json
{
  "data": {
    "keyLogs": [
      {
        "id": 5,
        "action": "UPDATE_TRANSLATION",
        "fieldName": "translation",
        "language": "en",
        "oldValue": "Old text",
        "newValue": "New text",
        "createdAt": "2025-10-10T10:30:00Z",
        "userId": 1
      },
      {
        "id": 4,
        "action": "UPDATE_KEY",
        "fieldName": "key",
        "language": null,
        "oldValue": "old.key.name",
        "newValue": "new.key.name",
        "createdAt": "2025-10-10T10:00:00Z",
        "userId": 1
      }
    ]
  }
}
```

## Запуск миграции

Миграция запускается автоматически при старте приложения. Для ручного запуска:

```bash
cd backend
source venv/bin/activate
python migrations/create_key_logs_table.py
```

## Запуск тестов

```bash
cd backend
source venv/bin/activate
pytest tests/test_key_logging.py -v
```

## Структура данных

```sql
CREATE TABLE key_logs (
    id SERIAL PRIMARY KEY,
    key_id INTEGER NOT NULL REFERENCES keys(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR NOT NULL,  -- create, update_key, update_description, etc.
    field_name VARCHAR(100),  -- key, description, translation
    language VARCHAR(10),     -- en, ru, etc. (only for translations)
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_key_logs_key_id ON key_logs(key_id);
CREATE INDEX idx_key_logs_user_id ON key_logs(user_id);
CREATE INDEX idx_key_logs_action ON key_logs(action);
CREATE INDEX idx_key_logs_created_at ON key_logs(created_at);
```

## UI Features ✅

1. ✅ **Timeline компонент** - отображает историю изменений в виде timeline
2. ✅ **Табы в Key Management** - вкладки "History" (дефолтная) и "Settings"
3. ✅ **Цветовая индикация** - разные цвета для разных типов действий
4. ✅ **Относительное время** - "2 часа назад" вместо абсолютной даты
5. ✅ **Отображение изменений** - показывает старые и новые значения

## Future Enhancements

1. Показывать имя пользователя вместо userId
2. Возможность отката к предыдущим версиям
3. Фильтры по типу действия, пользователю, дате
4. Экспорт истории изменений

## Файлы изменений

### Backend

**Новые файлы:**
- `backend/app/models/key_log.py` - модель
- `backend/migrations/create_key_logs_table.py` - миграция
- `backend/tests/test_key_logging.py` - тесты
- `docs/obsidian/Key Logging.md` - документация

**Измененные файлы:**
- `backend/app/models/__init__.py` - добавлен экспорт KeyLog
- `backend/app/services/key_service.py` - добавлено логирование
- `backend/app/schemas/key.py` - добавлены GraphQL типы и запросы
- `backend/app/schemas/graphql.py` - добавлен запрос keyLogs
- `backend/migrations/auto_migrate.py` - добавлена автомиграция

### Frontend

**Новые файлы:**
- `frontend/src/components/key/KeyLogsTimeline.tsx` - timeline компонент для отображения истории
- История изменений отображается в виде timeline с цветовыми индикаторами

**Измененные файлы:**
- `frontend/src/components/key/KeyManagement.tsx` - добавлены табы (History и Settings)
- `frontend/src/components/key/index.ts` - добавлен экспорт KeyLogsTimeline
- `frontend/src/graphql/keys.ts` - добавлен запрос GET_KEY_LOGS
- `frontend/src/components/key/README.md` - обновлена документация
- `frontend/package.json` - добавлен пакет date-fns

### Общие
- `CHANGELOG.md` - обновлен changelog
- `KEY_LOGGING_SUMMARY.md` - добавлена документация

## Производительность

- Индексы на часто используемые поля
- Лимит по умолчанию: 50 записей
- Рекомендуется настроить retention policy для старых логов

## Безопасность

- Доступ к логам только для пользователей с доступом к проекту
- User ID сохраняется даже после удаления пользователя (SET NULL)
- Логи удаляются при удалении ключа (CASCADE)


