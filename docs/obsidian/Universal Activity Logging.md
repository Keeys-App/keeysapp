# Universal Activity Logging System

## Overview

Universal activity logging system for tracking all project changes: project-level actions, key changes, translations and team management.

### Key Features

- ✅ **Single table** `activity_logs` for all activity types
- ✅ **SET NULL** foreign keys - history preserved even after entity deletion
- ✅ **Project Activity** - unified project activity feed
- ✅ **Extensibility** - easy to add new action types
- ✅ **Backward Compatibility** - old API `keyLogs` continues working

## Database Schema

### ActivityLog Model

```python
class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True)
    
    # Entity references (nullable for history preservation)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    key_id = Column(Integer, ForeignKey("keys.id", ondelete="SET NULL"), nullable=True)
    
    # Users
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    affected_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Action details
    action = Column(Enum(ActionType), nullable=False)
    field_name = Column(String(100), nullable=True)
    language = Column(String(10), nullable=True)
    
    # Change tracking
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Optional extra data
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Action Types

```python
class ActionType(enum.Enum):
    # Project actions
    PROJECT_CREATE = "PROJECT_CREATE"
    PROJECT_UPDATE_NAME = "PROJECT_UPDATE_NAME"
    PROJECT_UPDATE_DESCRIPTION = "PROJECT_UPDATE_DESCRIPTION"
    PROJECT_UPDATE_LANGUAGES = "PROJECT_UPDATE_LANGUAGES"
    PROJECT_UPDATE_DEFAULT_LANGUAGE = "PROJECT_UPDATE_DEFAULT_LANGUAGE"
    PROJECT_UPDATE_COLOR = "PROJECT_UPDATE_COLOR"
    PROJECT_UPDATE_STATUS = "PROJECT_UPDATE_STATUS"
    PROJECT_DELETE = "PROJECT_DELETE"
    PROJECT_EXPORT = "PROJECT_EXPORT"
    PROJECT_IMPORT = "PROJECT_IMPORT"
    
    # Team management
    MEMBER_ADD = "MEMBER_ADD"
    MEMBER_REMOVE = "MEMBER_REMOVE"
    MEMBER_ROLE_CHANGE = "MEMBER_ROLE_CHANGE"
    
    # Key actions
    KEY_CREATE = "KEY_CREATE"
    KEY_UPDATE = "KEY_UPDATE"
    KEY_UPDATE_DESCRIPTION = "KEY_UPDATE_DESCRIPTION"
    KEY_DELETE = "KEY_DELETE"
    
    # Translation actions
    TRANSLATION_UPDATE = "TRANSLATION_UPDATE"
    TRANSLATION_DELETE = "TRANSLATION_DELETE"
    TRANSLATION_IMPORT = "TRANSLATION_IMPORT"
    
    # Review actions
    REVIEW_APPROVE = "REVIEW_APPROVE"
    REVIEW_REJECT = "REVIEW_REJECT"
    REVIEW_DELETE = "REVIEW_DELETE"
```

## Migration

### Automatic Migration

Migration runs automatically on application startup:

```bash
cd backend
python main.py
```

Migration:
1. Renames `key_logs` → `activity_logs`
2. Adds new fields: `project_id`, `affected_user_id`, `extra_data`
3. Changes CASCADE → SET NULL for foreign keys
4. Updates enum types
5. Adds new indexes
6. Migrates existing data

### Manual Migration

```bash
cd backend
source venv/bin/activate
python migrations/migrate_to_activity_logs.py
```

## GraphQL API

### Queries

#### 1. Key Logs (Legacy, still works)

```graphql
query GetKeyLogs($keyId: String!, $limit: Int) {
  keyLogs(keyId: $keyId, limit: $limit) {
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

#### 2. Project Activity (NEW! 🎉)

```graphql
query GetProjectActivity($projectId: String!, $limit: Int) {
  projectActivity(projectId: $projectId, limit: $limit) {
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
    action
    fieldName
    language
    oldValue
    newValue
    createdAt
  }
}
```

**Response Example:**

```json
{
  "data": {
    "projectActivity": [
      {
        "id": 123,
        "projectId": 5,
        "keyId": 42,
        "userId": 1,
        "affectedUserId": null,
        "user": {
          "id": "uuid",
          "email": "user@example.com",
          "username": "john"
        },
        "action": "TRANSLATION_UPDATE",
        "fieldName": "translation",
        "language": "en",
        "oldValue": "Old text",
        "newValue": "New text",
        "createdAt": "2025-10-12T10:30:00Z"
      },
      {
        "id": 122,
        "projectId": 5,
        "keyId": null,
        "userId": 1,
        "affectedUserId": 2,
        "user": {
          "id": "uuid",
          "email": "admin@example.com"
        },
        "affectedUser": {
          "id": "uuid2",
          "email": "newmember@example.com"
        },
        "action": "MEMBER_ADD",
        "fieldName": "role",
        "oldValue": null,
        "newValue": "editor",
        "createdAt": "2025-10-12T09:00:00Z"
      }
    ]
  }
}
```

## Service Integration

### Adding Logs in KeyService

```python
from app.models.activity_log import ActivityLog, ActionType

KeyService._create_log(
    db=db,
    key_id=key.id,
    user_id=user_id,
    action=ActionType.KEY_CREATE,
    field_name="key",
    new_value=key_name,
    project_id=project.id
)
```

### Adding Logs in ProjectService (TODO)

```python
from app.models.activity_log import ActivityLog, ActionType

def create_log(
    db: Session,
    project_id: int,
    user_id: int,
    action: ActionType,
    **kwargs
):
    log = ActivityLog(
        project_id=project_id,
        user_id=user_id,
        action=action,
        **kwargs
    )
    db.add(log)
```

## Frontend Usage

### GraphQL Query for Project Activity

```typescript
// frontend/src/graphql/activityLogs.ts
import { gql } from '@apollo/client';

export const GET_PROJECT_ACTIVITY = gql`
  query GetProjectActivity($projectId: String!, $limit: Int) {
    projectActivity(projectId: $projectId, limit: $limit) {
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
`;
```

### Component Example

```typescript
import { useQuery } from '@apollo/client';
import { GET_PROJECT_ACTIVITY } from '@/graphql/activityLogs';

function ProjectActivity({ projectId }: { projectId: string }) {
  const { data, loading } = useQuery(GET_PROJECT_ACTIVITY, {
    variables: { projectId, limit: 50 }
  });
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div>
      {data?.projectActivity.map(log => (
        <ActivityItem key={log.id} log={log} />
      ))}
    </div>
  );
}
```

## Action Type Mapping

### Project-Level Actions

| Action | Description | Fields |
|--------|-------------|--------|
| `PROJECT_CREATE` | Project created | `new_value`: project name |
| `PROJECT_UPDATE_NAME` | Name changed | `old_value`, `new_value` |
| `PROJECT_UPDATE_DESCRIPTION` | Description changed | `old_value`, `new_value` |
| `PROJECT_UPDATE_LANGUAGES` | Languages updated | `extra_data`: languages array |
| `PROJECT_UPDATE_COLOR` | Color changed | `old_value`, `new_value` |
| `PROJECT_DELETE` | Project deleted | `old_value`: project name |
| `PROJECT_EXPORT` | Data exported | `extra_data`: export details |
| `PROJECT_IMPORT` | Data imported | `extra_data`: import stats |

### Team Management Actions

| Action | Description | Fields |
|--------|-------------|--------|
| `MEMBER_ADD` | Member added | `affected_user_id`, `new_value`: role |
| `MEMBER_REMOVE` | Member removed | `affected_user_id`, `old_value`: role |
| `MEMBER_ROLE_CHANGE` | Role changed | `affected_user_id`, `old_value`, `new_value` |

### Key Actions

| Action | Description | Fields |
|--------|-------------|--------|
| `KEY_CREATE` | Key created | `key_id`, `new_value`: key name |
| `KEY_UPDATE` | Key renamed | `key_id`, `old_value`, `new_value` |
| `KEY_UPDATE_DESCRIPTION` | Description changed | `key_id`, `old_value`, `new_value` |
| `KEY_DELETE` | Key deleted | `key_id`, `old_value`: key name |

### Translation Actions

| Action | Description | Fields |
|--------|-------------|--------|
| `TRANSLATION_UPDATE` | Translation added/updated | `key_id`, `language`, `old_value`, `new_value` |
| `TRANSLATION_DELETE` | Translation deleted | `key_id`, `language`, `old_value` |
| `TRANSLATION_IMPORT` | Translation imported | `key_id`, `language`, `new_value` |

### Review Actions

| Action | Description | Fields |
|--------|-------------|--------|
| `REVIEW_APPROVE` | Translation approved | `key_id`, `language`, `new_value`: comment |
| `REVIEW_REJECT` | Translation rejected | `key_id`, `language`, `new_value`: comment |
| `REVIEW_DELETE` | Review deleted | `key_id`, `language` |

## UI Implementation Guide

### Project Activity Page

**Recommended structure:**

```
/projects/:id/activity
```

**Features to implement:**

1. **Timeline View**
   - Chronological list of all activities
   - Group by date (Today, Yesterday, Last Week, etc.)
   - Show user avatars and names
   - Different icons for different action types

2. **Filtering**
   - By action type (Project, Keys, Translations, Team)
   - By user
   - By date range

3. **Search**
   - Search in old/new values
   - Search by key name
   - Search by user name

4. **Action Details**
   - Clickable items (e.g., click on key name → open key)
   - Show diffs for changed values
   - Link to affected users

5. **Pagination**
   - Load more on scroll
   - Initial load: 50-100 items
   - Performance: use virtualization for large lists

### UI Components Needed

```typescript
// ActivityTimeline.tsx - main timeline component
// ActivityItem.tsx - single activity item
// ActivityFilters.tsx - filtering controls
// ActivityIcon.tsx - icons for different action types
// ActivityDiff.tsx - show before/after changes
```

## Performance Considerations

### Indexes

Already created:
- `ix_activity_logs_project_id`
- `ix_activity_logs_key_id`
- `ix_activity_logs_user_id`
- `ix_activity_logs_action`
- `ix_activity_logs_created_at`
- `ix_activity_logs_affected_user_id`

### Optimizations

1. **Use eager loading** for user relationships
2. **Limit results** (default: 100)
3. **Pagination** instead of loading all logs
4. **Consider partitioning** for very large tables (millions of rows)

### Data Retention

Consider implementing:

```python
# Example: Archive logs older than 1 year
from datetime import datetime, timedelta

cutoff_date = datetime.now() - timedelta(days=365)
old_logs = db.query(ActivityLog).filter(
    ActivityLog.created_at < cutoff_date
).all()

# Move to archive table or delete
```

## Migration from KeyLog

### Backward Compatibility

Old code using `KeyLog` will continue to work:

```python
# This still works
from app.models.key_log import KeyLog, KeyActionType
```

But it's recommended to migrate to:

```python
# New way
from app.models.activity_log import ActivityLog, ActionType
```

### Action Name Changes

| Old (KeyActionType) | New (ActionType) |
|---------------------|-------------------|
| `CREATE` | `KEY_CREATE` |
| `UPDATE_KEY` | `KEY_UPDATE` |
| `UPDATE_DESCRIPTION` | `KEY_UPDATE_DESCRIPTION` |
| `UPDATE_TRANSLATION` | `TRANSLATION_UPDATE` |
| `DELETE_TRANSLATION` | `TRANSLATION_DELETE` |
| `DELETE` | `KEY_DELETE` |
| `IMPORT` | `TRANSLATION_IMPORT` |
| `REVIEW_APPROVE` | Same |
| `REVIEW_REJECT` | Same |
| `REVIEW_DELETE` | Same |

## TODO: Project-Level Logging

Currently only key-level actions are logged. To add project-level logging:

1. Add logging to `ProjectService` methods:
   - `create_project()`
   - `update_project()`
   - `delete_project()`
   - `add_project_member()`
   - `remove_project_member()`
   - `export_project_data()`

2. Example:

```python
def update_project(self, db, project_id, name=None, **kwargs):
    project = self.get_project(db, project_id)
    
    if name and name != project.name:
        # Log name change
        log = ActivityLog(
            project_id=project.id,
            user_id=user_id,
            action=ActionType.PROJECT_UPDATE_NAME,
            field_name="name",
            old_value=project.name,
            new_value=name
        )
        db.add(log)
        
        project.name = name
    
    db.commit()
```

## Testing

See `backend/tests/test_activity_logging.py` for comprehensive tests (TODO).

## Related Documentation

- [Key Logging](Key%20Logging.md) - Original key-only logging system
- [Database Schema](Project%20Structure.md)
- [Security Best Practices](Security%20Best%20Practices.md)
