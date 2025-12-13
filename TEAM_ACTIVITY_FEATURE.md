# Team Activity Logging Feature

## Overview

Implemented complete activity logging system for projects and teams with UI for viewing change history.

## ✅ Implemented

### Backend

#### 1. Activity Logging in ProjectService
- ✅ `create_project` - logs project creation (`PROJECT_CREATE`)
- ✅ `update_project` - logs changes:
  - Name (`PROJECT_UPDATE_NAME`)
  - Description (`PROJECT_UPDATE_DESCRIPTION`)
  - Languages (`PROJECT_UPDATE_LANGUAGES`)
  - Default language (`PROJECT_UPDATE_DEFAULT_LANGUAGE`)
  - Color (`PROJECT_UPDATE_COLOR`)
  - Status (`PROJECT_UPDATE_STATUS`)
- ✅ `delete_project` - logs deletion (`PROJECT_DELETE`)
- ✅ `export_project_data` - logs export (`PROJECT_EXPORT`)
- ✅ `import_project_data` - logs import (`PROJECT_IMPORT`)

#### 2. Activity Logging in ProjectAccessService
- ✅ `grant_project_access` - logs:
  - Member addition (`MEMBER_ADD`)
  - Existing member role change (`MEMBER_ROLE_CHANGE`)
- ✅ `revoke_project_access` - logs removal (`MEMBER_REMOVE`)
- ✅ `update_project_access_role` - logs role change (`MEMBER_ROLE_CHANGE`)

#### 3. GraphQL API
- ✅ New query `teamActivity(teamId: String!, limit: Int)` in `TeamQuery`
- ✅ Added to main GraphQL schema
- ✅ Returns logs for all team projects
- ✅ **Filter by action type**: shows only team and project changes
  - ✅ Projects: create, update, delete, export, import
  - ✅ Team: add/remove/change member role
  - ❌ Excluded: keys, translations, reviews (available on project page)
- ✅ With access checks and eager loading for performance

### Frontend

#### 1. TypeScript Types
- ✅ `types/activity.ts` - types for ActivityLog and ActionType
- ✅ All action types (projects, team, keys, translations, reviews)

#### 2. GraphQL Queries
- ✅ `graphql/activityLogs.ts`:
  - `GET_TEAM_ACTIVITY` - get team activity
  - `GET_PROJECT_ACTIVITY` - get project activity

#### 3. UI Components
- ✅ `components/activity/ActivityItem.tsx` - single entry display
  - Icons and colors for all action types
  - Diff for changes
  - User information
  - Timestamps
- ✅ `components/activity/ActivityTimeline.tsx` - timeline with logs
  - Loading states
  - Error handling
  - Empty states

#### 4. Pages
- ✅ `pages/TeamLogsPage.tsx` - team activity page
  - Breadcrumbs navigation
  - Display of all team project changes
  - Retry on errors

#### 5. Routing & Navigation
- ✅ Added path `PATHS.TEAM_LOGS = '/team/:id/logs'`
- ✅ Added route in `App.tsx`
- ✅ "Activity" button on team page (`TeamPage.tsx`)
- ✅ **"Team Activity" item in left menu** (`AppSidebar.tsx`)
  - Shows only when team is selected
  - Uses `useTeamStore()` to get current team ID
  - Dynamically forms URL `/team/${selectedTeamId}/logs`

## 📊 Logged Actions

### Shown in Team Activity (13 types):

**Projects (10 types):**
- ✅ Create, update (name, description, languages, default language, color, status)
- ✅ Delete, export, import

**Team Management (3 types):**
- ✅ Add member
- ✅ Remove member
- ✅ Change member role

### NOT shown in Team Activity (9 types):

**Keys and translations:**
- ❌ Key actions (create, update, delete)
- ❌ Translation actions (update, delete, import, AI)
- ❌ Review actions (approve, reject)

> **Note:** Detailed key and translation log available on project page via `projectActivity` query

## 🎨 UI Features

- **Color coding**: each action type has its own color
- **Icons**: unique icons for each action type
- **Diff view**: shows "before/after" changes (only for detailed key logs)
- **Timeline**: visual timeline of events
- **User attribution**: displays user who performed action
- **Affected user**: for team actions shows affected user
- **Relative time**: "2 hours ago", "yesterday", etc.
- **Empty states**: beautiful empty states
- **Error handling**: retry buttons on errors
- **Simplified view**: Team Activity does NOT show diff for readability

## 📝 Data Structure

```typescript
interface ActivityLog {
  id: number;
  projectId: number | null;
  keyId: number | null;
  userId: number | null;
  affectedUserId: number | null;
  user: ActivityUser | null;
  affectedUser: ActivityUser | null;
  action: ActionType;
  fieldName: string | null;
  language: string | null;
  oldValue: string | null;
  newValue: string | null;
  createdAt: string;
}
```

## 🚀 Usage

### Viewing Team Activity

**Method 1: Via left menu**
1. Select team in TeamSwitcher (top menu)
2. **"Team Activity"** item appears in left menu
3. Click it to view activity

**Method 2: From team page**
1. Navigate to team page: `/team/:id`
2. Click "Activity" button in header
3. Opens page `/team/:id/logs` with all activity

### What's Logged Automatically

All changes in projects and access management are now automatically logged:

```python
# Backend automatically creates log when:
- ProjectService.create_project()
- ProjectService.update_project()
- ProjectService.delete_project()
- ProjectService.export_project_data()
- ProjectService.import_project_data()
- ProjectAccessService.grant_project_access()
- ProjectAccessService.revoke_project_access()
- ProjectAccessService.update_project_access_role()
```

## 🔒 Security

- ✅ Access check to team before showing logs
- ✅ SET NULL for foreign keys - history preserved even after deletion
- ✅ Technical errors not shown to user

## 📖 Additional Documentation

See `/docs/obsidian/Universal Activity Logging.md` for detailed documentation about:
- Database schema
- Action types
- Migration guide
- Performance considerations
- Data retention policies

## 🎯 Next Steps (optional)

### Possible improvements:
- [ ] Filters by action type (Project, Team, Keys, Translations)
- [ ] Filters by user
- [ ] Filters by date
- [ ] Search in logs
- [ ] Pagination/infinite scroll for large volumes
- [ ] Export history to CSV/JSON
- [ ] Show project name next to action
- [ ] Group by dates (Today, Yesterday, Last Week)
- [ ] Real-time updates via WebSocket
