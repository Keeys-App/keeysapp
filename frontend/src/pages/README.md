# Pages

Application pages organized by functionality.

## Structure

```
pages/
├── AuthPage.tsx            # Authentication (login/registration)
├── DashboardPage.tsx       # Main page (project list)
├── ProjectPage.tsx         # Project overview page (statistics)
├── ProjectKeysPage.tsx     # Translation keys page
├── CreateProjectPage.tsx   # Create new project
├── EditProjectPage.tsx     # Edit project
├── ExportPage.tsx          # Export translations
├── ImportPage.tsx          # Import translations
└── index.ts                # Exports
```

## Pages

### AuthPage (`/auth`)
Authentication page with switching between login and registration forms.

**Components:**
- `LoginForm` - login form
- `RegisterForm` - registration form

### DashboardPage (`/`)
Main application page with user's project list.

**Components:**
- `ProjectList` - project list
- `ProjectCard` - project card
- `CreateProjectCard` - create project card

### CreateProjectPage (`/project/create`)
New project creation page.

**Components:**
- `ProjectForm` with `mode="create"`

**Breadcrumbs:**
- Dashboard → Create Project

**Features:**
- Separate page instead of modal dialog
- Ability to use browser navigation
- After creation redirects to main page

### EditProjectPage (`/project/:id/edit`)
Existing project editing page.

**Components:**
- `ProjectForm` with `mode="edit"`

**Breadcrumbs:**
- Dashboard → [Project Name] → Edit

**Features:**
- Loads project data from GET_PROJECTS
- Shows LoadingState during loading
- Shows NotFoundState if project not found
- After saving redirects to project page
- Breadcrumbs dynamically update with project name

### ProjectPage (`/project/:id`)
Project overview page with general information and statistics.

**Components:**
- Translation statistics (progress, key count, languages)
- Project language list
- Team information (owner and members)
- Quick actions (go to keys, export, import)

**Breadcrumbs:**
- Dashboard → [Project Name]

**Features:**
- Translation progress visualization
- Display of completed and remaining translations count
- Quick access to translation keys
- Display all configured languages with default language marker

### ProjectKeysPage (`/project/:id/keys`)
Project translation keys management page.

**Components:**
- `KeyList` - translation keys list
- `CreateKeyDialog` - new key creation dialog

**Breadcrumbs:**
- Dashboard → [Project Name] → Keys

**Features:**
- View and edit keys
- Manage translations
- Create new keys

### ExportPage (`/project/:id/export`)
Export translations to various formats page.

**Formats:**
- JSON
- YAML
- CSV
- and others

### ImportPage (`/project/:id/import`)
Import translations from files page.

**Supported formats:**
- JSON
- YAML
- CSV

## Routing

All routes defined in `constants/paths.ts`:

```typescript
export const PATHS = {
  AUTH: '/auth',
  HOME: '/',
  DASHBOARD: '/',
  PROJECT: '/project/:id',
  PROJECT_KEYS: '/project/:id/keys',
  PROJECT_CREATE: '/project/create',
  PROJECT_EDIT: '/project/:id/edit',
  EXPORT: '/project/:id/export',
  IMPORT: '/project/:id/import',
} as const;
```

## Route Protection

All pages except `AuthPage` are protected by `ProtectedRoute` component:

```tsx
<Route
  element={
    <ProtectedRoute>
      <Layout />
    </ProtectedRoute>
  }
>
  <Route path={PATHS.DASHBOARD} element={<DashboardPage />} />
  <Route path={PATHS.PROJECT_CREATE} element={<CreateProjectPage />} />
  <Route path={PATHS.PROJECT_EDIT} element={<EditProjectPage />} />
  <Route path={PATHS.PROJECT} element={<ProjectPage />} />
  <Route path={PATHS.PROJECT_KEYS} element={<ProjectKeysPage />} />
  <Route path={PATHS.EXPORT} element={<ExportPage />} />
  <Route path={PATHS.IMPORT} element={<ImportPage />} />
</Route>
```

## Best Practices

- ✅ Use constants from `PATHS` instead of hardcoded strings
- ✅ Use `useNavigate` for programmatic navigation
- ✅ Use `Link` for declarative navigation
- ✅ Handle loading and error states
- ✅ Show fallback UI (LoadingState, ErrorState, NotFoundState)

## Navigation Examples

### Using Link
```tsx
import { Link } from 'react-router-dom';
import { PATHS } from '@/constants/paths';

<Link to={PATHS.PROJECT_CREATE}>Create Project</Link>
<Link to={PATHS.PROJECT.replace(':id', projectId)}>Project Overview</Link>
<Link to={PATHS.PROJECT_KEYS.replace(':id', projectId)}>Translation Keys</Link>
<Link to={PATHS.PROJECT_EDIT.replace(':id', projectId)}>Edit</Link>
```

### Using useNavigate
```tsx
import { useNavigate } from 'react-router-dom';
import { PATHS } from '@/constants/paths';

const navigate = useNavigate();

// Navigate to create project
navigate(PATHS.PROJECT_CREATE);

// Navigate to project overview
navigate(PATHS.PROJECT.replace(':id', projectId));

// Navigate to project keys
navigate(PATHS.PROJECT_KEYS.replace(':id', projectId));

// Navigate to edit with ID
navigate(PATHS.PROJECT_EDIT.replace(':id', projectId));

// Go back
navigate(-1);
```
