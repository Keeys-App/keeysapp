# Changelog

## [2025-10-10] - Project Overview Page

### ✅ Изменено

#### Frontend
- ✅ **Реорганизация страниц проекта:**
  - Создана отдельная страница `ProjectPage` (`/project/:id`) - обзор проекта со статистикой
  - Создана отдельная страница `ProjectKeysPage` (`/project/:id/keys`) - управление ключами переводов
  - Обновлены пути в `PATHS`:
    - `PROJECT: '/project/:id'` - обзор проекта
    - `PROJECT_KEYS: '/project/:id/keys'` - ключи проекта
  - Обновлена документация в `frontend/src/pages/README.md`

#### ProjectPage - Обзор проекта
- **Статистика перевода:**
  - Визуализация общего прогресса с Progress Bar
  - Количество завершенных и оставшихся переводов
  - Общее количество ключей и языков
- **Быстрые действия:**
  - Переход к ключам переводов
  - Экспорт переводов
  - Импорт переводов
- **Информация о проекте:**
  - Список языков с отметкой языка по умолчанию
  - Информация о команде (владелец и члены)
  - Даты создания и последнего обновления
  - ID проекта

#### ProjectKeysPage - Управление ключами
- Перенесен функционал из старой `ProjectPage`
- Список ключей с переводами
- Создание новых ключей
- Редактирование существующих ключей

#### Breadcrumbs
- ProjectPage: Dashboard → [Project Name]
- ProjectKeysPage: Dashboard → [Project Name] → Keys

#### Файлы
- **Создано:**
  - `frontend/src/pages/ProjectKeysPage.tsx` - страница ключей переводов
- **Обновлено:**
  - `frontend/src/pages/ProjectPage.tsx` - изменена на страницу обзора
  - `frontend/src/constants/paths.ts` - добавлен `PROJECT_KEYS`
  - `frontend/src/App.tsx` - добавлен роут для ключей
  - `frontend/src/pages/index.ts` - экспорт `ProjectKeysPage`
  - `frontend/src/pages/README.md` - обновлена документация

#### Преимущества
- ✅ Лучший UX - сначала показывается обзор проекта
- ✅ Быстрый доступ к статистике и важной информации
- ✅ Удобная навигация между разделами проекта
- ✅ Карточки быстрых действий для основных операций

---

## [2025-10-10] - Project Management Refactoring

### ✅ Изменено

#### Frontend
- ✅ **Рефакторинг создания/редактирования проектов:**
  - Удалены модальные окна `CreateProjectDialog` и `EditProjectDialog`
  - Создан общий компонент `ProjectForm` с поддержкой режимов `mode='create'` и `mode='edit'`
  - Добавлены новые страницы:
    - `CreateProjectPage` (`/project/create`) - создание проекта
    - `EditProjectPage` (`/project/:id/edit`) - редактирование проекта
  - Обновлена навигация в `ProjectList`, `CreateProjectCard` и `EmptyProjects`
  - Добавлены новые константы путей в `PATHS`:
    - `PROJECT_CREATE` - создание проекта
    - `PROJECT_EDIT` - редактирование проекта
  - Добавлены breadcrumbs для обеих страниц:
    - CreateProjectPage: Dashboard → Create Project
    - EditProjectPage: Dashboard → [Project Name] → Edit

#### Преимущества
- ✅ Единый источник логики для создания и редактирования
- ✅ Улучшенный UX - отдельные страницы вместо модалок
- ✅ Возможность использовать браузерную навигацию (назад/вперед)
- ✅ Прямые ссылки на создание/редактирование проектов
- ✅ Меньше дублирования кода

#### Файлы
- **Создано:**
  - `frontend/src/components/project/ProjectForm.tsx` - общая форма проекта
  - `frontend/src/pages/CreateProjectPage.tsx` - страница создания
  - `frontend/src/pages/EditProjectPage.tsx` - страница редактирования
- **Обновлено:**
  - `frontend/src/App.tsx` - добавлены новые роуты
  - `frontend/src/constants/paths.ts` - добавлены новые пути
  - `frontend/src/components/project/ProjectList.tsx` - навигация вместо диалогов
  - `frontend/src/components/project/index.ts` - обновлены экспорты
  - `frontend/src/pages/index.ts` - экспорт новых страниц
- **Удалено:**
  - `frontend/src/components/project/CreateProjectDialog.tsx`
  - `frontend/src/components/project/EditProjectDialog.tsx`

---

## [2025-10-09] - Authentication System

### ✅ Добавлено

#### Backend
- ✅ Модель User с UUID для безопасности
- ✅ JWT авторизация (pyjwt)
- ✅ bcrypt хэширование паролей
- ✅ GraphQL API: `register`, `login`, `me`
- ✅ Кастомные безопасные исключения (SQL ошибки НИКОГДА не показываются пользователям)
- ✅ UserService для бизнес-логики
- ✅ Автоматические миграции при старте
- ✅ 51 автоматический тест (~95% coverage):
  - 10 тестов моделей
  - 7 тестов JWT/security
  - 11 тестов сервисов
  - 5 тестов UUID
  - 18 тестов обработки ошибок

#### Frontend
- ✅ AuthContext для управления состоянием
- ✅ LoginForm с Radix UI
- ✅ RegisterForm с Radix UI
- ✅ ProtectedRoute для защиты маршрутов
- ✅ AuthPage и DashboardPage
- ✅ Apollo Client с автоматической передачей JWT
- ✅ Валидация форм
- ✅ Обработка ошибок
- ✅ autocomplete атрибуты

#### Инфраструктура
- ✅ Организована структура папок:
  - `backend/app/` - код приложения
  - `backend/tests/` - unit тесты
  - `backend/migrations/` - миграции БД
  - `backend/scripts/` - утилиты
  - `backend/integration_tests/` - интеграционные тесты
- ✅ Автоматические миграции на Railway
- ✅ Документация в Obsidian (9 документов)

#### Документация
- ✅ README.md - Главная
- ✅ Quick Start - Быстрый старт
- ✅ Authentication Setup - Настройка авторизации
- ✅ Authentication Cheatsheet - Шпаргалка
- ✅ Security Best Practices - Безопасность
- ✅ Testing Guide - Тестирование
- ✅ Project Structure - Структура проекта
- ✅ Backend Organization - Организация backend
- ✅ Railway Deployment - Деплой

### 🔐 Безопасность

#### Защита от атак
- ✅ UUID вместо автоинкремента (защита от enumeration)
- ✅ Безопасная обработка ошибок (SQL детали скрыты)
- ✅ Защита от SQL injection
- ✅ bcrypt для паролей (автоматическое обрезание до 72 байт)
- ✅ JWT с истечением (30 минут)

#### Примеры безопасности

**Раньше (небезопасно):**
```
User ID: 1, 2, 3... (легко угадать)
Error: "psycopg.errors.UndefinedColumn: column users.public_id does not exist"
```

**Сейчас (безопасно):**
```
User ID: 550e8400-e29b-41d4-a716-446655440000 (невозможно угадать)
Error: "An error occurred. Please try again later." (техн. детали в логах)
```

### 🧪 Тесты

#### Coverage
```
Name                          Stmts   Miss  Cover
-------------------------------------------------
app/core/config.py               15      0   100%
app/core/security.py             20      0   100%
app/core/exceptions.py           50      2    96%
app/models/user.py               30      0   100%
app/services/user_service.py     55      1    98%
app/schemas/auth.py              85      5    94%
-------------------------------------------------
TOTAL                           255     8    95%
```

#### Типы тестов
- Unit тесты: 51 тест
- Integration тесты: 1 скрипт
- Общее время: ~7 секунд

### 📝 Миграции

#### auto_migrate.py
Автоматически запускается при старте:
- Проверяет нужны ли миграции
- Применяет только недостающие
- Логирует результаты
- Безопасно для production

#### migrate_add_public_id.py
- Добавляет UUID колонку
- Генерирует UUID для существующих пользователей
- Добавляет constraints и индексы

### 🛠️ Утилиты

#### Управление пользователями
- `scripts/list_users.py` - Просмотр
- `scripts/clear_users.py` - Очистка

#### Управление БД
- `migrations/migrate_add_public_id.py` - Миграция UUID
- `migrations/recreate_tables.py` - Пересборка (удаляет данные)

### 🔄 Railway интеграция

- ✅ Автоматические миграции при деплое
- ✅ Конфигурация в railway.json
- ✅ Поддержка DATABASE_URL
- ✅ Логирование миграций

### 📚 Документация

Вся документация в Obsidian Vault: `docs/obsidian/`

**Структура:**
- 9 документов
- Внутренние ссылки между документами
- Callouts для важной информации
- Примеры кода
- Пошаговые инструкции

## 🎯 Итого

### Статистика
- **Backend:** ~500 строк production кода
- **Тесты:** ~1000 строк, 51 тест
- **Миграции:** 3 скрипта
- **Утилиты:** 2 скрипта
- **Документация:** 9 документов
- **Coverage:** ~95%

### Безопасность
- ✅ UUID для публичных ID
- ✅ Безопасные сообщения об ошибках
- ✅ Защита от SQL injection
- ✅ Защита от enumeration attacks
- ✅ bcrypt для паролей
- ✅ JWT с истечением

### Качество
- ✅ 51 автоматический тест
- ✅ ~95% покрытие кода
- ✅ Полная документация
- ✅ Организованная структура
- ✅ Готово к production

---

*Создано: 2025-10-09*

