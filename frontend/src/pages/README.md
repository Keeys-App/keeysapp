# Pages

Страницы приложения организованы по функциональности.

## Структура

```
pages/
├── AuthPage.tsx            # Аутентификация (логин/регистрация)
├── DashboardPage.tsx       # Главная страница (список проектов)
├── ProjectPage.tsx         # Страница проекта (ключи переводов)
├── CreateProjectPage.tsx   # Создание нового проекта
├── EditProjectPage.tsx     # Редактирование проекта
├── ExportPage.tsx          # Экспорт переводов
├── ImportPage.tsx          # Импорт переводов
└── index.ts                # Экспорты
```

## Страницы

### AuthPage (`/auth`)
Страница аутентификации с переключением между формами входа и регистрации.

**Компоненты:**
- `LoginForm` - форма входа
- `RegisterForm` - форма регистрации

### DashboardPage (`/`)
Главная страница приложения со списком проектов пользователя.

**Компоненты:**
- `ProjectList` - список проектов
- `ProjectCard` - карточка проекта
- `CreateProjectCard` - карточка создания проекта

### CreateProjectPage (`/project/create`)
Страница создания нового проекта.

**Компоненты:**
- `ProjectForm` с `mode="create"`

**Breadcrumbs:**
- Dashboard → Create Project

**Особенности:**
- Отдельная страница вместо модального окна
- Возможность использовать браузерную навигацию
- После создания перенаправляет на главную страницу

### EditProjectPage (`/project/:id/edit`)
Страница редактирования существующего проекта.

**Компоненты:**
- `ProjectForm` с `mode="edit"`

**Breadcrumbs:**
- Dashboard → [Project Name] → Edit

**Особенности:**
- Загружает данные проекта из GET_PROJECTS
- Показывает LoadingState во время загрузки
- Показывает NotFoundState если проект не найден
- После сохранения перенаправляет на страницу проекта
- Breadcrumbs динамически обновляются с именем проекта

### ProjectPage (`/project/:id`)
Страница проекта с ключами переводов и управлением.

**Функции:**
- Просмотр и редактирование ключей
- Управление переводами
- Навигация к экспорту/импорту

### ExportPage (`/project/:id/export`)
Страница экспорта переводов в различные форматы.

**Форматы:**
- JSON
- YAML
- CSV
- и другие

### ImportPage (`/project/:id/import`)
Страница импорта переводов из файлов.

**Поддерживаемые форматы:**
- JSON
- YAML
- CSV

## Роутинг

Все роуты определены в `constants/paths.ts`:

```typescript
export const PATHS = {
  AUTH: '/auth',
  HOME: '/',
  DASHBOARD: '/',
  PROJECT: '/project/:id',
  PROJECT_CREATE: '/project/create',
  PROJECT_EDIT: '/project/:id/edit',
  EXPORT: '/project/:id/export',
  IMPORT: '/project/:id/import',
} as const;
```

## Защита роутов

Все страницы кроме `AuthPage` защищены компонентом `ProtectedRoute`:

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
  {/* ... другие защищенные роуты */}
</Route>
```

## Best Practices

- ✅ Используйте константы из `PATHS` вместо hardcoded строк
- ✅ Используйте `useNavigate` для программной навигации
- ✅ Используйте `Link` для декларативной навигации
- ✅ Обрабатывайте состояния загрузки и ошибок
- ✅ Показывайте fallback UI (LoadingState, ErrorState, NotFoundState)

## Примеры навигации

### С использованием Link
```tsx
import { Link } from 'react-router-dom';
import { PATHS } from '@/constants/paths';

<Link to={PATHS.PROJECT_CREATE}>Create Project</Link>
<Link to={PATHS.PROJECT_EDIT.replace(':id', projectId)}>Edit</Link>
```

### С использованием useNavigate
```tsx
import { useNavigate } from 'react-router-dom';
import { PATHS } from '@/constants/paths';

const navigate = useNavigate();

// Переход на создание проекта
navigate(PATHS.PROJECT_CREATE);

// Переход на редактирование с ID
navigate(PATHS.PROJECT_EDIT.replace(':id', projectId));

// Назад
navigate(-1);
```
