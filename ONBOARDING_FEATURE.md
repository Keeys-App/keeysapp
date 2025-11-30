# Onboarding Feature Implementation

## 📋 Overview

Реализована полноценная система onboarding для новых пользователей:
- 3-шаговый wizard (создание команды, приглашение участников, создание проекта)
- Хранение состояния в базе данных
- Защита от обхода через изменение URL
- Синхронизация между устройствами

## 🎯 Features

### Wizard Steps:

1. **Create Team** - Создание первой команды
2. **Invite Members** - Приглашение участников (опционально)
3. **Create Project** - Создание первого проекта с английским языком по умолчанию

### Security:

✅ Состояние хранится в PostgreSQL (поле `users.onboarding_completed`)  
✅ Невозможно обойти через localStorage/cookies  
✅ Редирект на `/onboarding` при попытке доступа к другим страницам  
✅ Синхронизация между всеми устройствами пользователя  

## 🚀 Deployment Steps

### 1. Backend Migration

```bash
cd backend
source venv/bin/activate
python -m migrations.add_onboarding_completed
```

**Результат:**
```
✓ Successfully added onboarding_completed column
Migration completed successfully!
```

### 2. Restart Backend Server

Перезапустите backend сервер для загрузки обновленной GraphQL схемы:

```bash
# В терминале с запущенным backend:
# 1. Остановите сервер (Ctrl+C)
# 2. Запустите снова:
python main.py
```

### 3. Frontend (автоматически)

Frontend автоматически перезагружается при изменениях. Никаких дополнительных действий не требуется.

## 📝 Database Changes

### Added Field:

```sql
ALTER TABLE users 
ADD COLUMN onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE;
```

### Migration File:

`backend/migrations/add_onboarding_completed.py`

**Rollback (если нужно):**
```bash
python -m migrations.add_onboarding_completed --downgrade
```

## 🔧 Technical Implementation

### Backend:

**Files Modified:**
- `backend/app/models/user.py` - добавлено поле `onboarding_completed`
- `backend/app/schemas/auth.py` - обновлен `UserType`, добавлена мутация `completeOnboarding`
- `backend/app/schemas/graphql.py` - зарегистрирована мутация в schema

**New GraphQL Mutation:**
```graphql
mutation CompleteOnboarding {
  completeOnboarding {
    id
    onboardingCompleted
  }
}
```

### Frontend:

**Files Created:**
- `frontend/src/stores/onboardingStore.ts` - Zustand store для локального состояния
- `frontend/src/pages/OnboardingPage.tsx` - страница wizard
- `frontend/src/components/onboarding/` - компоненты wizard
  - `OnboardingWizard.tsx` - главный компонент с progress indicator
  - `CreateTeamStep.tsx` - шаг 1: создание команды
  - `InviteMembersStep.tsx` - шаг 2: приглашение участников
  - `CreateProjectStep.tsx` - шаг 3: создание проекта

**Files Modified:**
- `frontend/src/App.tsx` - добавлен роут `/onboarding`
- `frontend/src/constants/paths.ts` - добавлена константа `PATHS.ONBOARDING`
- `frontend/src/pages/AuthPage.tsx` - проверка команд после регистрации
- `frontend/src/components/layout/Layout.tsx` - защита от обхода onboarding
- `frontend/src/contexts/AuthContext.tsx` - синхронизация статуса с backend
- `frontend/src/graphql/auth.ts` - обновлены queries/mutations

## 🧪 Testing Checklist

### Registration Flow:
- [ ] Новый пользователь регистрируется
- [ ] Автоматический редирект на `/onboarding`
- [ ] Wizard отображается корректно

### Wizard Flow:
- [ ] Шаг 1: Создание команды с валидацией
- [ ] Команда автоматически выбирается в TeamStore
- [ ] Шаг 2: Добавление участников (можно пропустить)
- [ ] Шаг 3: Английский язык предзаполнен
- [ ] Создание проекта работает
- [ ] Редирект на созданный проект

### Security:
- [ ] Попытка открыть `/` → редирект на `/onboarding`
- [ ] Попытка открыть `/teams` → редирект на `/onboarding`
- [ ] Изменение URL вручную не помогает обойти
- [ ] После завершения можно свободно перемещаться

### Multi-Device:
- [ ] Завершить onboarding на устройстве A
- [ ] Войти на устройстве B → сразу попадает на dashboard
- [ ] Очистка localStorage не помогает обойти
- [ ] Incognito режим использует данные с сервера

## 📚 Documentation

Подробная документация в:
- `frontend/src/components/onboarding/README.md` - полное описание компонентов и flow

## 🐛 Troubleshooting

### GraphQL Error: "Cannot query field 'onboardingCompleted'"

**Причина:** Backend сервер не перезапущен после миграции

**Решение:**
```bash
# Остановить backend (Ctrl+C)
# Запустить снова
cd backend
source venv/bin/activate
python main.py
```

### Пользователь застрял на onboarding

**Причина:** Поле в БД не обновилось

**Решение (временное для тестирования):**
```sql
UPDATE users SET onboarding_completed = true WHERE email = 'user@example.com';
```

### Миграция не применилась

**Проверка:**
```sql
\d users
-- Должен быть столбец onboarding_completed
```

**Повторная попытка:**
```bash
python -m migrations.add_onboarding_completed
```

## 🎨 UI/UX Features

- Красивый progress indicator с 3 шагами
- Анимации переходов между шагами
- Зеленые чекмарки для завершенных шагов
- Центрированный card layout
- Responsive design
- Toast notifications
- Global saving indicator в footer

## 🔮 Future Enhancements

Возможные улучшения:
- Email уведомления о приглашениях
- Импорт существующих проектов в onboarding
- Шаблоны команд и проектов
- Анимация конфетти при завершении
- Возможность вернуться к предыдущему шагу
- Сохранение прогресса при выходе

---

**Status:** ✅ Ready for Production  
**Date:** November 30, 2025  
**Migration:** Required (`add_onboarding_completed.py`)

