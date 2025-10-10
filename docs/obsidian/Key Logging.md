# Key Logging (Audit Trail)

## Overview

The key logging system provides a complete audit trail for all changes made to translation keys. Every action performed on keys is recorded in the `key_logs` table, including:

- Key creation
- Key name changes
- Description updates
- Translation creation/updates/deletion
- Key deletion

**Note:** Metadata changes (such as tags) are NOT logged as per project requirements.

## Database Schema

### KeyLog Model

Located in `app/models/key_log.py`:

```python
class KeyLog(Base):
    __tablename__ = "key_logs"
    
    id: int                    # Primary key
    key_id: int               # Foreign key to keys.id
    user_id: int              # Foreign key to users.id (SET NULL on delete)
    action: KeyActionType     # Type of action performed
    field_name: str           # Name of the field changed
    language: str             # Language code (for translations)
    old_value: str            # Previous value
    new_value: str            # New value
    created_at: datetime      # When the action occurred
```

### Action Types

```python
class KeyActionType(enum.Enum):
    CREATE = "create"                           # Key created
    UPDATE_KEY = "update_key"                   # Key name changed
    UPDATE_DESCRIPTION = "update_description"   # Description changed
    UPDATE_TRANSLATION = "update_translation"   # Translation added/updated
    DELETE_TRANSLATION = "delete_translation"   # Translation deleted
    DELETE = "delete"                           # Key deleted
```

## Automatic Logging

All logging happens automatically through the `KeyService` methods. No manual intervention needed.

### What Gets Logged

✅ **Logged:**
- Key creation (`CREATE`)
- Key name changes (`UPDATE_KEY`)
- Description changes (`UPDATE_DESCRIPTION`)
- Translation creation/updates (`UPDATE_TRANSLATION`)
- Translation deletion (`DELETE_TRANSLATION`)
- Key deletion (`DELETE`)

❌ **Not Logged:**
- Tag changes (metadata)
- Metadata updates

### Service Integration

The `KeyService._create_log()` helper method is called automatically by:

1. `create_key()` - logs key creation and initial translations
2. `update_key()` - logs name and description changes (not tags)
3. `set_translation()` - logs translation creation/updates
4. `delete_translation()` - logs translation deletion
5. `delete_key()` - logs key deletion
6. `batch_import_translations()` - logs all batch operations

## GraphQL API

### Query Logs

Get audit logs for a specific key:

```graphql
query GetKeyLogs($keyId: String!, $limit: Int) {
  keyLogs(keyId: $keyId, limit: $limit) {
    id
    keyId
    userId
    action
    fieldName
    language
    oldValue
    newValue
    createdAt
  }
}
```

**Parameters:**
- `keyId` (required): UUID of the key
- `limit` (optional): Maximum number of logs to return (default: 50)

**Returns:** List of logs ordered by `created_at DESC` (newest first)

### Types

```graphql
enum KeyActionTypeEnum {
  CREATE
  UPDATE_KEY
  UPDATE_DESCRIPTION
  UPDATE_TRANSLATION
  DELETE_TRANSLATION
  DELETE
}

type KeyLogType {
  id: Int!
  keyId: Int!
  userId: Int
  action: KeyActionTypeEnum!
  fieldName: String
  language: String
  oldValue: String
  newValue: String
  createdAt: DateTime!
}
```

## Usage Examples

### Example 1: Track Translation Changes

```python
# User updates a translation
KeyService.set_translation(
    db=db,
    key_public_id="abc-123",
    language="en",
    value="New translation",
    user_id=user.id
)

# Log entry created:
# - action: UPDATE_TRANSLATION
# - field_name: "translation"
# - language: "en"
# - old_value: "Old translation"
# - new_value: "New translation"
# - user_id: <user.id>
```

### Example 2: Track Key Renaming

```python
# User renames a key
KeyService.update_key(
    db=db,
    public_id="abc-123",
    key="new.key.name",
    user_id=user.id
)

# Log entry created:
# - action: UPDATE_KEY
# - field_name: "key"
# - old_value: "old.key.name"
# - new_value: "new.key.name"
# - user_id: <user.id>
```

### Example 3: Query Logs via GraphQL

```javascript
const { data } = await apolloClient.query({
  query: gql`
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
  `,
  variables: { keyId: keyUuid }
});

console.log('Key history:', data.keyLogs);
```

## Migration

The `key_logs` table is created automatically on application startup via the auto-migration system.

### Manual Migration

If needed, you can run the migration manually:

```bash
cd backend
python migrations/create_key_logs_table.py
```

## Testing

Comprehensive tests are available in `backend/tests/test_key_logging.py`:

```bash
cd backend
source venv/bin/activate
pytest tests/test_key_logging.py -v
```

Tests cover:
- Key creation logging
- Key update logging (name, description)
- Translation CRUD logging
- Batch import logging
- User tracking
- Metadata exclusion (tags not logged)

## Performance Considerations

### Indexing

The `key_logs` table has indexes on:
- `key_id` - for querying logs by key
- `user_id` - for querying logs by user
- `action` - for filtering by action type
- `created_at` - for ordering by time

### Data Retention

Consider implementing a log retention policy for high-volume projects:

```python
# Example: Delete logs older than 1 year
from datetime import datetime, timedelta

cutoff_date = datetime.now() - timedelta(days=365)
db.query(KeyLog).filter(KeyLog.created_at < cutoff_date).delete()
db.commit()
```

## Security

### Access Control

- Users can only view logs for keys in projects they have access to
- The `keyLogs` query checks project access before returning logs
- User IDs in logs use `SET NULL` on user deletion to preserve history

### Data Privacy

- Logs store the actual translation values for audit purposes
- Ensure compliance with data retention policies
- Consider PII implications when storing translation content

## Future Enhancements

Potential improvements:

1. **Frontend UI**: Display audit trail in key detail view
2. **Filtering**: Add filters by action type, user, date range
3. **Diff View**: Show side-by-side comparison of changes
4. **Notifications**: Alert on specific actions (e.g., deletions)
5. **Export**: Generate audit reports for compliance
6. **Rollback**: Allow reverting to previous values

## Related Documentation

- [Keys Module](Keys%20Module.md)
- [Security Best Practices](Security%20Best%20Practices.md)
- [Testing Guide](Testing%20Guide.md)


