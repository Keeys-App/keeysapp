# Team Activity Logging Feature

## Обзор

Реализована полная система логирования активности для проектов и команд с UI для просмотра истории изменений.

## ✅ Реализовано

### Backend

#### 1. Activity Logging в ProjectService
- ✅ `create_project` - логирует создание проекта (`PROJECT_CREATE`)
- ✅ `update_project` - логирует изменения:
  - Имени (`PROJECT_UPDATE_NAME`)
  - Описания (`PROJECT_UPDATE_DESCRIPTION`)
  - Языков (`PROJECT_UPDATE_LANGUAGES`)
  - Языка по умолчанию (`PROJECT_UPDATE_DEFAULT_LANGUAGE`)
  - Цвета (`PROJECT_UPDATE_COLOR`)
  - Статуса (`PROJECT_UPDATE_STATUS`)
- ✅ `delete_project` - логирует удаление (`PROJECT_DELETE`)
- ✅ `export_project_data` - логирует экспорт (`PROJECT_EXPORT`)
- ✅ `import_project_data` - логирует импорт (`PROJECT_IMPORT`)

#### 2. Activity Logging в ProjectAccessService
- ✅ `grant_project_access` - логирует:
  - Добавление участника (`MEMBER_ADD`)
  - Изменение роли существующего участника (`MEMBER_ROLE_CHANGE`)
- ✅ `revoke_project_access` - логирует удаление (`MEMBER_REMOVE`)
- ✅ `update_project_access_role` - логирует изменение роли (`MEMBER_ROLE_CHANGE`)

#### 3. GraphQL API
- ✅ Новый query `teamActivity(teamId: String!, limit: Int)` в `TeamQuery`
- ✅ Добавлен в основную схему GraphQL
- ✅ Возвращает логи для всех проектов команды
- ✅ **Фильтр по типу действий**: показываются только изменения команды и проектов
  - ✅ Проекты: создание, обновление, удаление, экспорт, импорт
  - ✅ Команда: добавление/удаление/изменение роли участников
  - ❌ Исключены: ключи, переводы, ревью (есть на странице проекта)
- ✅ С проверкой доступа и eager loading для производительности

### Frontend

#### 1. TypeScript Types
- ✅ `types/activity.ts` - типы для ActivityLog и ActionType
- ✅ Все типы действий (проекты, команда, ключи, переводы, ревью)

#### 2. GraphQL Queries
- ✅ `graphql/activityLogs.ts`:
  - `GET_TEAM_ACTIVITY` - получение активности команды
  - `GET_PROJECT_ACTIVITY` - получение активности проекта

#### 3. UI Components
- ✅ `components/activity/ActivityItem.tsx` - отображение одной записи
  - Иконки и цвета для всех типов действий
  - Diff для изменений
  - Информация о пользователях
  - Временные метки
- ✅ `components/activity/ActivityTimeline.tsx` - timeline с логами
  - Loading states
  - Error handling
  - Empty states

#### 4. Pages
- ✅ `pages/TeamLogsPage.tsx` - страница активности команды
  - Breadcrumbs навигация
  - Отображение всех изменений в проектах команды
  - Retry при ошибках

#### 5. Routing & Navigation
- ✅ Добавлен путь `PATHS.TEAM_LOGS = '/team/:id/logs'`
- ✅ Добавлен роут в `App.tsx`
- ✅ Кнопка "Activity" на странице команды (`TeamPage.tsx`)
- ✅ **Пункт "Team Activity" в левом меню** (`AppSidebar.tsx`)
  - Показывается только когда команда выбрана
  - Использует `useTeamStore()` для получения ID текущей команды
  - Динамически формирует URL `/team/${selectedTeamId}/logs`

## 📊 Логируемые действия

### В Team Activity отображаются (13 типов):

**Проекты (10 типов):**
- ✅ Создание, обновление (имя, описание, языки, default language, цвет, статус)
- ✅ Удаление, экспорт, импорт

**Управление командой (3 типа):**
- ✅ Добавление участника
- ✅ Удаление участника
- ✅ Изменение роли участника

### НЕ отображаются в Team Activity (9 типов):

**Ключи и переводы:**
- ❌ Действия с ключами (создание, обновление, удаление)
- ❌ Действия с переводами (обновление, удаление, импорт, AI)
- ❌ Действия с ревью (одобрение, отклонение)

> **Примечание:** Детальный лог ключей и переводов доступен на странице проекта через query `projectActivity`

## 🎨 UI Features

- **Цветовая кодировка**: каждый тип действия имеет свой цвет
- **Иконки**: уникальные иконки для каждого типа действия
- **Diff view**: показывает изменения "до/после" (только для детальных логов ключей)
- **Timeline**: визуальная линия времени событий
- **User attribution**: отображение пользователя, выполнившего действие
- **Affected user**: для действий с командой показывает затронутого пользователя
- **Relative time**: "2 hours ago", "yesterday", etc.
- **Empty states**: красивые пустые состояния
- **Error handling**: retry кнопки при ошибках
- **Упрощенный вид**: в Team Activity НЕ показывается diff для читаемости

## 📝 Структура данных

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

## 🚀 Использование

### Просмотр активности команды

**Способ 1: Через левое меню**
1. Выбрать команду в TeamSwitcher (верхнее меню)
2. В левом меню появится пункт **"Team Activity"**
3. Нажать на него для просмотра активности

**Способ 2: Со страницы команды**
1. Перейти на страницу команды: `/team/:id`
2. Нажать кнопку "Activity" в header
3. Откроется страница `/team/:id/logs` со всей активностью

### Что логируется автоматически

Все изменения в проектах и управлении доступом теперь автоматически логируются:

```python
# Backend автоматически создает лог при:
- ProjectService.create_project()
- ProjectService.update_project()
- ProjectService.delete_project()
- ProjectService.export_project_data()
- ProjectService.import_project_data()
- ProjectAccessService.grant_project_access()
- ProjectAccessService.revoke_project_access()
- ProjectAccessService.update_project_access_role()
```

## 🔒 Безопасность

- ✅ Проверка доступа к команде перед показом логов
- ✅ SET NULL для foreign keys - история сохраняется даже после удаления
- ✅ Не показываются технические ошибки пользователю

## 📖 Дополнительная документация

См. `/docs/obsidian/Universal Activity Logging.md` для подробной документации о:
- Database schema
- Action types
- Migration guide
- Performance considerations
- Data retention policies

## 🎯 Next Steps (опционально)

### Возможные улучшения:
- [ ] Фильтры по типу действия (Project, Team, Keys, Translations)
- [ ] Фильтры по пользователю
- [ ] Фильтры по дате
- [ ] Поиск в логах
- [ ] Pagination/infinite scroll для больших объемов
- [ ] Экспорт истории в CSV/JSON
- [ ] Показывать название проекта рядом с действием
- [ ] Группировка по датам (Today, Yesterday, Last Week)
- [ ] Real-time обновления через WebSocket

