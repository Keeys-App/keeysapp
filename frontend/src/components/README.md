# Components Structure

Components organized by modules according to **Atomic Design** principles and project rules.

## Structure

```
components/
├── ui/              # Atoms - basic Shadcn UI components
├── auth/            # Authentication module
├── project/         # Project management module
└── layout/          # Layout components
```

## Modules

### 🎨 UI Components (`ui/`)
Basic Shadcn UI components. Installed via CLI:
```bash
yarn dlx shadcn@latest add [component-name]
```

**Components:**
- button, card, input, label, textarea
- select, dialog, alert, alert-dialog
- avatar, badge, dropdown-menu

### 🔐 Auth Module (`auth/`)
Components for user authentication.

**Components:**
- `LoginForm` - login form
- `RegisterForm` - registration form

**Usage:**
```tsx
import { LoginForm, RegisterForm } from '@/components/auth';
```

### 📁 Project Module (`project/`)
Components for localization project management.

**Components:**
- `ProjectCard` - project card
- `ProjectList` - project list with management
- `ProjectForm` - universal form for creating/editing project
- `CreateProjectCard` - create new project card
- `EmptyProjects` - empty state component

**Usage:**
```tsx
import { ProjectList, ProjectCard, ProjectForm } from '@/components/project';

// ProjectForm used on CreateProjectPage and EditProjectPage
<ProjectForm mode="create" />
<ProjectForm mode="edit" project={project} />
```

### 🏗️ Layout Module (`layout/`)
Application structure components.

**Components:**
- `Layout` - main layout with header and navigation
- `ProtectedRoute` - protected route (requires authentication)

**Usage:**
```tsx
import { Layout, ProtectedRoute } from '@/components/layout';
```

## Import Rules

### ✅ Correct
```tsx
// Use @ alias for imports
import { LoginForm } from '@/components/auth';
import { ProjectList } from '@/components/project';
import { Button } from '@/components/ui/button';
```

### ❌ Wrong
```tsx
// Don't use relative paths
import { LoginForm } from '../components/auth/LoginForm';
import { ProjectList } from '../../components/project';
```

## Adding New Components

1. **UI components** - install via Shadcn CLI
2. **Module components** - add to appropriate module
3. **New module** - create folder with `index.ts` for exports

### Example Creating New Module

```
components/
└── settings/
    ├── index.ts
    ├── SettingsForm.tsx
    └── SettingsDialog.tsx
```

```ts
// index.ts
export { SettingsForm } from './SettingsForm';
export { SettingsDialog } from './SettingsDialog';
```

## Best Practices

- ✅ Use **TypeScript** for all components
- ✅ Follow **ESLint** and **Prettier** rules
- ✅ Split large components into modules
- ✅ Use **Shadcn UI** for basic components
- ✅ Write comments in **English**
- ✅ Apply **Atomic Design** pattern
