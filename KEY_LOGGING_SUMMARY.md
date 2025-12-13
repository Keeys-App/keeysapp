# Key Logging Feature - Summary

## What's Done ✅

Implemented full audit (logging) system for all translation key changes.

## Main Components

### 1. Backend Models
- **`KeyLog`** model (`app/models/key_log.py`) - stores change history
- **`KeyActionType`** enum - action types (create, update, delete, etc.)

### 2. Database
- `key_logs` table with indexes for performance
- Automatic migration on application start
- CASCADE delete when key is deleted

### 3. Service Layer
- Method `KeyService._create_log()` - creates log entries
- Logging integrated into all methods:
  - `create_key()` - key creation + translations
  - `update_key()` - name/description changes (tags NOT logged)
  - `set_translation()` - translation creation/update
  - `delete_translation()` - translation deletion
  - `delete_key()` - key deletion
  - `batch_import_translations()` - bulk import

### 4. GraphQL API
- Query `keyLogs(keyId: String!, limit: Int)` - get history
- Types `KeyLogType` and `KeyActionTypeEnum`
- Automatic access rights check

### 5. Tests
- Full test suite in `tests/test_key_logging.py`
- Coverage of all usage scenarios

### 6. Documentation
- Detailed documentation in `docs/obsidian/Key Logging.md`

## What's Logged ✅

- ✅ Key creation
- ✅ Key name change
- ✅ Description change
- ✅ Translation creation
- ✅ Translation update
- ✅ Translation deletion
- ✅ Key deletion

## What's NOT Logged ❌

- ❌ Tag changes (metadata)
- ❌ Any other metadata

## Usage Example

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

## Running Migration

Migration runs automatically on application start. For manual run:

```bash
cd backend
source venv/bin/activate
python migrations/create_key_logs_table.py
```

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/test_key_logging.py -v
```

## Data Structure

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

1. ✅ **Timeline component** - displays change history as timeline
2. ✅ **Tabs in Key Management** - "History" (default) and "Settings" tabs
3. ✅ **Color indication** - different colors for different action types
4. ✅ **Relative time** - "2 hours ago" instead of absolute date
5. ✅ **Change display** - shows old and new values

## Future Enhancements

1. Show user name instead of userId
2. Ability to revert to previous versions
3. Filters by action type, user, date
4. Export change history

## Changed Files

### Backend

**New files:**
- `backend/app/models/key_log.py` - model
- `backend/migrations/create_key_logs_table.py` - migration
- `backend/tests/test_key_logging.py` - tests
- `docs/obsidian/Key Logging.md` - documentation

**Modified files:**
- `backend/app/models/__init__.py` - added KeyLog export
- `backend/app/services/key_service.py` - added logging
- `backend/app/schemas/key.py` - added GraphQL types and queries
- `backend/app/schemas/graphql.py` - added keyLogs query
- `backend/migrations/auto_migrate.py` - added auto-migration

### Frontend

**New files:**
- `frontend/src/components/key/KeyLogsTimeline.tsx` - timeline component for history display
- Change history displayed as timeline with color indicators

**Modified files:**
- `frontend/src/components/key/KeyManagement.tsx` - added tabs (History and Settings)
- `frontend/src/components/key/index.ts` - added KeyLogsTimeline export
- `frontend/src/graphql/keys.ts` - added GET_KEY_LOGS query
- `frontend/src/components/key/README.md` - updated documentation
- `frontend/package.json` - added date-fns package

### General
- `CHANGELOG.md` - updated changelog
- `KEY_LOGGING_SUMMARY.md` - added documentation

## Performance

- Indexes on frequently used fields
- Default limit: 50 entries
- Recommend configuring retention policy for old logs

## Security

- Log access only for users with project access
- User ID preserved even after user deletion (SET NULL)
- Logs deleted when key is deleted (CASCADE)
