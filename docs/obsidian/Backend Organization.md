# Backend Organization

> [!info] Организация папок и файлов backend

## 📁 Структура папок

```
backend/
├── app/                  # Основной код приложения
├── tests/                # Unit тесты (pytest)
├── migrations/           # Миграции базы данных
├── scripts/              # Утилиты управления
└── integration_tests/    # Интеграционные тесты
```

## 📂 Назначение папок

### app/ - Основной код
Весь production код приложения.

**Подпапки:**
- `core/` - Ядро (config, security, exceptions)
- `models/` - SQLAlchemy модели
- `schemas/` - GraphQL схемы
- `services/` - Бизнес-логика
- `routers/` - REST API endpoints (пустая, для будущего)
- `resolvers/` - GraphQL resolvers (пустая, для будущего)

### tests/ - Unit тесты
Автоматические тесты, запускаются через pytest.

**Содержит:**
- `conftest.py` - Fixtures для всех тестов
- `test_*.py` - Тестовые модули

**Запуск:**
```bash
pytest
pytest -v
pytest --cov=app
```

**Статистика:** 51 тест, ~95% coverage, ~7 секунд

### migrations/ - Миграции БД
Скрипты для изменения схемы базы данных.

**Файлы:**
- `auto_migrate.py` - Автоматические миграции (запускаются при старте)
- `migrate_*.py` - Конкретные миграции
- `recreate_tables.py` - Полная пересборка БД (удаляет данные)

**Особенности:**
- ✅ Автоматический запуск при старте приложения
- ✅ Идемпотентные (безопасно запускать много раз)
- ✅ Работают на Railway автоматически

**Запуск вручную:**
```bash
python migrations/migrate_add_public_id.py
```

### scripts/ - Утилиты
Вспомогательные скрипты для разработки.

**Файлы:**
- `list_users.py` - Показать всех пользователей
- `clear_users.py` - Удалить всех пользователей

**Использование:**
```bash
python scripts/list_users.py
python scripts/clear_users.py
```

### integration_tests/ - Интеграционные тесты
Тесты через реальное HTTP API.

**Файлы:**
- `check_error_safety.py` - Проверка безопасности ошибок

**Отличие от unit-тестов:**
- Требуют запущенный backend
- Делают реальные HTTP запросы
- Тестируют end-to-end сценарии
- Запускаются вручную

**Использование:**
```bash
# 1. Запустите backend
python main.py

# 2. В другом терминале:
python integration_tests/check_error_safety.py
```

## 🎯 Где что добавлять

### Новая модель базы данных
```
app/models/my_model.py
```

### Новый GraphQL тип
```
app/schemas/my_schema.py
```

### Новый сервис (бизнес-логика)
```
app/services/my_service.py
```

### Новый тест
```
tests/test_my_feature.py
```

### Новая миграция
```python
# 1. Создать
migrations/migrate_add_new_field.py

# 2. Добавить в auto_migrate.py
migrations = [
    ("add_public_id", migrate_add_public_id_if_needed),
    ("add_new_field", migrate_add_new_field),  # Добавить
]
```

### Новая утилита
```
scripts/my_utility.py
```

### Новый интеграционный тест
```
integration_tests/test_my_integration.py
```

## 📋 Правила организации

### Именование файлов

**Модули:**
- `snake_case.py` для всех Python файлов
- `test_feature.py` для unit-тестов
- `migrate_description.py` для миграций

**Классы:**
- `PascalCase` для классов
- `Test*` для тестовых классов

**Функции:**
- `snake_case` для функций
- `test_*` для тестовых функций

### Где НЕ добавлять код

❌ **Не добавляйте в корень backend:**
- Утилиты → `scripts/`
- Миграции → `migrations/`
- Тесты → `tests/` или `integration_tests/`

❌ **Не смешивайте типы файлов:**
- Production код → `app/`
- Тесты → `tests/`
- Утилиты → `scripts/`

## 🔄 Workflow разработки

### 1. Изменение модели

```bash
# Редактируйте модель
app/models/user.py

# Создайте миграцию
migrations/migrate_add_field.py

# Добавьте в auto_migrate.py

# Напишите тесты
tests/test_new_model_feature.py

# Запустите тесты
pytest
```

### 2. Новая фича

```bash
# Модель (если нужна)
app/models/feature.py

# Сервис
app/services/feature_service.py

# GraphQL схема
app/schemas/feature.py

# Тесты
tests/test_feature.py

# Запустите тесты
pytest
```

### 3. Утилита для разработки

```bash
# Создайте скрипт
scripts/my_tool.py

# Добавьте README в scripts/README.md

# Сделайте исполняемым
chmod +x scripts/my_tool.py
```

## 📊 Статистика кода

### Структура по папкам

```
app/              ~500 строк (production код)
tests/            ~1000 строк (51 тест)
migrations/       ~200 строк (3 миграции)
scripts/          ~100 строк (2 утилиты)
integration_tests/ ~200 строк (1 тест)

Total: ~2000 строк кода
```

### Покрытие тестами

```
app/models/       100% покрытие
app/services/     100% покрытие  
app/core/         95% покрытие
app/schemas/      90% покрытие

Overall: ~95% coverage
```

## 🧹 Поддержание порядка

### Регулярно проверяйте

1. **Нет лишних файлов в корне** backend
2. **README.md в каждой спецпапке** (scripts, migrations, tests)
3. **`__init__.py` в каждом пакете Python**
4. **Тесты для нового кода**

### При добавлении файла

Спросите себя:
- Это production код? → `app/`
- Это тест? → `tests/`
- Это миграция? → `migrations/`
- Это утилита? → `scripts/`
- Это интеграционный тест? → `integration_tests/`

## 🔗 Связанные документы

- [[Project Structure]] - Общая структура проекта
- [[Railway Deployment]] - Деплой и миграции на Railway
- [[Testing Guide]] - Тестирование

---

*Обновлено: 2025-10-09*

