# Migrations / Миграции базы данных

Скрипты для миграции схемы базы данных.

## Использование

Все миграции запускаются из папки `backend`:

```bash
cd backend
source venv/bin/activate
python migrations/<migration_name>.py
```

## Доступные миграции

### create_projects_tables.py
Создает таблицы для модуля проектов.

```bash
python migrations/create_projects_tables.py
```

**Что делает:**
1. Создает таблицу `projects` (id, public_id, name, description, languages, color, status, owner_id, timestamps)
2. Создает таблицу `project_members` (id, project_id, user_id, role, created_at)
3. Устанавливает foreign key constraints

**Когда использовать:**
- При первой установке модуля проектов
- Если таблицы существуют, предложит их пересоздать

**⚠️ Внимание:** 
- Пересоздание таблиц удалит все данные проектов!

### migrate_add_public_id.py
Добавляет колонку `public_id` (UUID) в таблицу users.

```bash
python migrations/migrate_add_public_id.py
```

**Что делает:**
1. Добавляет колонку `public_id` типа UUID
2. Генерирует UUID для всех существующих пользователей
3. Делает колонку NOT NULL
4. Добавляет UNIQUE constraint
5. Создает индекс для производительности

**Когда использовать:**
- При переходе с integer ID на UUID
- Один раз после обновления кода

**⚠️ Внимание:** 
- Сделайте backup базы данных перед запуском!
- Скрипт попросит подтверждение

### recreate_tables.py
Удаляет и пересоздает все таблицы базы данных.

```bash
python migrations/recreate_tables.py
```

**⚠️ ОПАСНО:** Удаляет ВСЕ данные!

**Что делает:**
1. Удаляет все таблицы (`DROP TABLE`)
2. Создает таблицы заново с актуальной схемой

**Когда использовать:**
- В development окружении
- Когда нужно полностью сбросить БД
- При критических изменениях схемы

**Требуется подтверждение:** Нужно ввести `DELETE ALL DATA`

## История миграций

| Дата | Миграция | Описание |
|------|----------|----------|
| 2025-10-09 | migrate_add_public_id | Добавлен UUID для безопасности |
| 2025-10-09 | create_projects_tables | Создание модуля проектов |

## Best Practices

1. **Backup** - Всегда делайте backup перед миграцией
2. **Testing** - Тестируйте миграции на копии БД
3. **Rollback** - Имейте план отката изменений
4. **Documentation** - Документируйте каждую миграцию
5. **Production** - Будьте особенно осторожны в продакшене

## Будущее

В будущем рекомендуется перейти на Alembic для автоматических миграций:

```bash
pip install alembic
alembic init alembic
```

---

*Для утилит управления смотрите папку `scripts/`*

