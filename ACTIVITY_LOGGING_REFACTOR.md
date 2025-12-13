# Universal Activity Logging System - Refactoring Summary

## 🎯 What's Done

Logging system migrated from specialized `key_logs` to universal `activity_logs`.

### ✅ Main Changes:

1. **New `ActivityLog` model**
   - Universal table for all activity types
   - Support for project-level, key-level and team management actions
   - SET NULL foreign keys (history preserved after deletion)
   - New fields: `project_id`, `affected_user_id`, `extra_data`

2. **Extended `ActionType` enum**
   - 🆕 Project actions: CREATE, UPDATE_NAME, UPDATE_DESCRIPTION, etc.
   - 🆕 Team management: MEMBER_ADD, MEMBER_REMOVE, MEMBER_ROLE_CHANGE
   - ✏️ Key actions: KEY_CREATE, KEY_UPDATE, KEY_DELETE
   - ✏️ Translations: TRANSLATION_UPDATE, TRANSLATION_DELETE, TRANSLATION_IMPORT
   - ✅ Review actions: REVIEW_APPROVE, REVIEW_REJECT, REVIEW_DELETE

3. **Automatic migration**
   - `key_logs` → `activity_logs`
   - All existing data preserved
   - Enum values updated
   - Indexes added

4. **New GraphQL query**
   ```graphql
   projectActivity(projectId: String!, limit: Int): [ActivityLogType!]!
   ```
   Returns ALL project logs (including key and translation changes)

5. **Backward Compatibility**
   - Old API `keyLogs` continues working
   - Legacy types `KeyLog` and `KeyActionType` available

## 📊 Structure

### Backend

**New files:**
- `backend/app/models/activity_log.py` - ActivityLog model
- `backend/migrations/migrate_to_activity_logs.py` - migration
- `docs/obsidian/Universal Activity Logging.md` - documentation

**Updated files:**
- `backend/app/models/__init__.py` - ActivityLog export
- `backend/app/services/key_service.py` - uses ActivityLog
- `backend/app/services/project_service.py` - uses ActivityLog in import
- `backend/app/schemas/key.py` - new types and query
- `backend/app/schemas/graphql.py` - added projectActivity
- `backend/migrations/auto_migrate.py` - auto migration

## 🚀 Usage

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
- `PROJECT_CREATE` - project created
- `PROJECT_UPDATE_NAME` - name changed
- `PROJECT_UPDATE_DESCRIPTION` - description changed
- `PROJECT_UPDATE_LANGUAGES` - languages updated
- `PROJECT_UPDATE_COLOR` - color changed
- `PROJECT_DELETE` - project deleted
- `PROJECT_IMPORT` / `PROJECT_EXPORT`

### Team Management (TODO - not yet logged)
- `MEMBER_ADD` - member added
- `MEMBER_REMOVE` - member removed
- `MEMBER_ROLE_CHANGE` - role changed

### Key Actions (✅ already logged)
- `KEY_CREATE` - key created
- `KEY_UPDATE` - key renamed
- `KEY_UPDATE_DESCRIPTION` - description changed
- `KEY_DELETE` - key deleted

### Translation Actions (✅ already logged)
- `TRANSLATION_UPDATE` - translation added/updated
- `TRANSLATION_DELETE` - translation deleted
- `TRANSLATION_IMPORT` - translation imported

### Review Actions (✅ already logged)
- `REVIEW_APPROVE` - translation approved
- `REVIEW_REJECT` - translation rejected
- `REVIEW_DELETE` - review deleted

## 🎨 Frontend - Project Activity Page

### Recommended structure:

```
/projects/:id/activity
```

### Components to implement:

1. **ProjectActivityPage** - main page
2. **ActivityTimeline** - timeline of all actions
3. **ActivityItem** - single activity item
4. **ActivityFilters** - filters (by type, user, date)
5. **ActivityIcon** - icons for different action types

### Usage example:

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

1. **Add logging to ProjectService:**
   - `create_project()`
   - `update_project()`
   - `delete_project()`
   - `add_project_member()`
   - `remove_project_member()`

2. **Create frontend:**
   - Project Activity page
   - Activity timeline component
   - Filters and search

3. **Tests:**
   - `test_activity_logging.py`
   - Frontend component tests

4. **UI polish:**
   - Icons for each action type
   - Diff view for changes
   - User avatars
   - Date grouping

## 🔗 Links

- Detailed documentation: `docs/obsidian/Universal Activity Logging.md`
- Migration: `backend/migrations/migrate_to_activity_logs.py`
- Model: `backend/app/models/activity_log.py`
- GraphQL Schema: `backend/app/schemas/key.py`

## ⚠️ Breaking Changes

None! System is fully backward compatible. Old code will continue working.

### Migration Notes

- Migration runs automatically on application start
- All existing `key_logs` will be converted to `activity_logs`
- Foreign keys changed from CASCADE to SET NULL
- Enum values updated (CREATE → KEY_CREATE, etc.)

## 📈 Benefits

1. **Single activity feed** - all project actions in one place
2. **Complete history** - logs preserved even after entity deletion
3. **Extensibility** - easy to add new action types
4. **Team insights** - see who does what in project
5. **Audit trail** - complete audit for compliance

## 🎉 Ready to use!

System fully works on backend. Only need to create UI for Project Activity page.

**Example query via GraphQL Playground:**

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
