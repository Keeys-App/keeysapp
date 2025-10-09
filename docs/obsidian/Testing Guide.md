# Testing Guide

> [!check] Руководство по тестированию системы авторизации

## Обзор

Комплексный набор тестов для системы авторизации.

**Статистика:**
- ✅ 28 тестов
- ✅ Покрытие ~95%
- ✅ Время выполнения ~6 секунд

## Установка

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Зависимости для тестирования:
- `pytest` - Фреймворк тестирования
- `pytest-cov` - Покрытие кода
- `pytest-asyncio` - Поддержка async

## Запуск тестов

### Все тесты
```bash
pytest
```

### С подробным выводом
```bash
pytest -v
```

### С покрытием кода
```bash
pytest --cov=app --cov-report=html
```

HTML отчет будет в `htmlcov/index.html`

### Конкретный файл
```bash
pytest tests/test_models.py
```

### Конкретный тест
```bash
pytest tests/test_models.py::TestUserModel::test_password_hashing
```

### Только быстрые тесты
```bash
pytest -m "not slow"
```

### Скрипт с покрытием
```bash
./run_tests.sh
```

## Структура тестов

```
tests/
├── __init__.py              # Инициализация пакета
├── conftest.py              # Fixtures и конфигурация pytest
├── test_models.py           # Тесты модели User
├── test_services.py         # Тесты UserService
├── test_security.py         # Тесты JWT и безопасности
└── README.md                # Документация тестов
```

## Покрытие тестов

### test_models.py (10 тестов)

#### Создание и управление
- ✅ `test_user_creation` - Создание пользователя
- ✅ `test_user_unique_email` - Уникальность email
- ✅ `test_user_unique_username` - Уникальность username

#### Пароли
- ✅ `test_password_hashing` - Хэширование паролей
- ✅ `test_password_verification_success` - Успешная верификация
- ✅ `test_password_verification_failure` - Неуспешная верификация
- ✅ `test_long_password_truncation` - Обрезание до 72 байт
- ✅ `test_password_with_special_characters` - Спецсимволы
- ✅ `test_unicode_password` - Unicode пароли
- ✅ `test_empty_password` - Пустые пароли

### test_services.py (11 тестов)

#### CRUD операции
- ✅ `test_create_user` - Создание через сервис
- ✅ `test_get_user_by_email` - Поиск по email
- ✅ `test_get_user_by_email_not_found` - Пользователь не найден
- ✅ `test_get_user_by_username` - Поиск по username
- ✅ `test_get_user_by_username_not_found` - Username не найден
- ✅ `test_get_user_by_id` - Поиск по ID
- ✅ `test_get_user_by_id_not_found` - ID не найден

#### Аутентификация
- ✅ `test_authenticate_user_success` - Успешная аутентификация
- ✅ `test_authenticate_user_wrong_password` - Неверный пароль
- ✅ `test_authenticate_user_wrong_email` - Неверный email
- ✅ `test_authenticate_inactive_user` - Неактивный пользователь

### test_security.py (7 тестов)

#### JWT токены
- ✅ `test_create_access_token` - Создание токена
- ✅ `test_create_access_token_with_expiration` - Кастомное истечение
- ✅ `test_decode_valid_token` - Декодирование валидного токена
- ✅ `test_decode_invalid_token` - Невалидный токен
- ✅ `test_decode_expired_token` - Истекший токен
- ✅ `test_token_contains_expiration` - Наличие expiration
- ✅ `test_different_tokens_for_same_data` - Разные токены для одних данных

## Fixtures

### Database Fixtures

#### `db_engine`
Создает тестовый движок БД (SQLite in-memory).

```python
@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
```

#### `db_session`
Создает тестовую сессию БД.

```python
@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
```

### Data Fixtures

#### `sample_user_data`
Образцовые данные пользователя для тестов.

```python
@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
```

#### `created_user`
Созданный пользователь в БД.

```python
@pytest.fixture
def created_user(db_session, sample_user_data):
    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=User.get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

## Написание новых тестов

### Шаблон теста

```python
def test_feature_name(db_session, sample_user_data):
    """
    Описание того, что тестирует этот тест.
    """
    # Arrange - подготовка данных
    user_data = sample_user_data
    
    # Act - выполнение действия
    result = some_function(user_data)
    
    # Assert - проверка результата
    assert result is not None
    assert result.email == user_data["email"]
```

### Пример теста модели

```python
def test_user_creation(db_session, sample_user_data):
    """
    Test creating a new user.
    """
    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=User.get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == sample_user_data["email"]
    assert user.is_active is True
```

### Пример теста сервиса

```python
def test_authenticate_user_success(db_session, created_user, sample_user_data):
    """
    Test successful user authentication.
    """
    user = UserService.authenticate_user(
        db_session,
        sample_user_data["email"],
        sample_user_data["password"]
    )

    assert user is not None
    assert user.id == created_user.id
```

## Соглашения

### Именование
- Файлы: `test_<feature>.py`
- Классы: `Test<Feature>`
- Методы: `test_<action>_<expected_result>`

### Структура теста
1. **Docstring** - описание теста
2. **Arrange** - подготовка данных
3. **Act** - выполнение действия
4. **Assert** - проверка результата

### Документация
- Всегда добавляйте docstring
- Опишите что тестируется
- Укажите ожидаемый результат

## Continuous Integration

### Pre-commit

Перед коммитом запускайте тесты:

```bash
pytest
```

### CI/CD Pipeline

```yaml
# Пример для GitHub Actions
- name: Run tests
  run: |
    cd backend
    source venv/bin/activate
    pytest --cov=app --cov-report=xml
```

## Покрытие кода

### Текущее покрытие

```
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                           0      0   100%
app/core/config.py                       15      0   100%
app/core/security.py                     20      0   100%
app/models/__init__.py                    2      0   100%
app/models/base.py                        3      0   100%
app/models/user.py                       25      0   100%
app/services/user_service.py             45      0   100%
app/schemas/auth.py                      60      2    97%
---------------------------------------------------------
TOTAL                                   170      2    99%
```

### Просмотр отчета

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Проблемы с БД

```python
# Проблема: Таблица не создается
# Решение: Убедитесь что импортирован User в conftest.py
from app.models.user import User  # Важно!
```

### Проблемы с fixtures

```python
# Проблема: Fixture не найден
# Решение: Проверьте что conftest.py в правильной папке
tests/
├── conftest.py  # Должен быть здесь
└── test_models.py
```

### Медленные тесты

```python
# Пометить медленный тест
@pytest.mark.slow
def test_slow_operation():
    # Долгая операция
    pass

# Пропустить медленные тесты
pytest -m "not slow"
```

## Best Practices

1. **Изоляция** - Каждый тест независим
2. **Читаемость** - Понятные названия и docstrings
3. **Покрытие** - Стремитесь к >90%
4. **Скорость** - Тесты должны быть быстрыми
5. **Актуальность** - Обновляйте при изменении кода

## Связанные документы

- [[Authentication Setup]] - Система авторизации
- [[Authentication Cheatsheet]] - Быстрая справка
- [[Quick Start]] - Быстрый старт

---

*Обновлено: 2025-10-09*

