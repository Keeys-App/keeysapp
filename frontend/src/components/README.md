# Components Structure

Компоненты организованы по модулям согласно принципам **Atomic Design** и правилам проекта.

## Структура

```
components/
├── ui/              # Atoms - базовые Shadcn UI компоненты
├── auth/            # Модуль аутентификации
├── project/         # Модуль управления проектами
└── layout/          # Layout компоненты
```

## Модули

### 🎨 UI Components (`ui/`)
Базовые компоненты Shadcn UI. Устанавливаются через CLI:
```bash
yarn dlx shadcn@latest add [component-name]
```

**Компоненты:**
- button, card, input, label, textarea
- select, dialog, alert, alert-dialog
- avatar, badge, dropdown-menu

### 🔐 Auth Module (`auth/`)
Компоненты для аутентификации пользователей.

**Компоненты:**
- `LoginForm` - форма входа
- `RegisterForm` - форма регистрации

**Использование:**
```tsx
import { LoginForm, RegisterForm } from '@/components/auth';
```

### 📁 Project Module (`project/`)
Компоненты для управления проектами локализации.

**Компоненты:**
- `ProjectCard` - карточка проекта
- `ProjectList` - список проектов с управлением
- `ProjectForm` - универсальная форма для создания/редактирования проекта
- `CreateProjectCard` - карточка для создания нового проекта
- `EmptyProjects` - компонент пустого состояния

**Использование:**
```tsx
import { ProjectList, ProjectCard, ProjectForm } from '@/components/project';

// ProjectForm используется на страницах CreateProjectPage и EditProjectPage
<ProjectForm mode="create" />
<ProjectForm mode="edit" project={project} />
```

### 🏗️ Layout Module (`layout/`)
Компоненты структуры приложения.

**Компоненты:**
- `Layout` - основной layout с header и навигацией
- `ProtectedRoute` - защищенный роут (требует авторизации)

**Использование:**
```tsx
import { Layout, ProtectedRoute } from '@/components/layout';
```

## Правила импорта

### ✅ Правильно
```tsx
// Используйте alias @ для импортов
import { LoginForm } from '@/components/auth';
import { ProjectList } from '@/components/project';
import { Button } from '@/components/ui/button';
```

### ❌ Неправильно
```tsx
// Не используйте относительные пути
import { LoginForm } from '../components/auth/LoginForm';
import { ProjectList } from '../../components/project';
```

## Добавление новых компонентов

1. **UI компоненты** - устанавливайте через Shadcn CLI
2. **Модульные компоненты** - добавляйте в соответствующий модуль
3. **Новый модуль** - создайте папку с `index.ts` для экспорта

### Пример создания нового модуля

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

- ✅ Используйте **TypeScript** для всех компонентов
- ✅ Следуйте правилам **ESLint** и **Prettier**
- ✅ Разделяйте большие компоненты на модули
- ✅ Используйте **Shadcn UI** для базовых компонентов
- ✅ Пишите комментарии на **английском**
- ✅ Применяйте **Atomic Design** pattern

