# Integration Tests / Интеграционные тесты

Интеграционные тесты, которые проверяют работу всей системы через HTTP API.

## Отличие от unit-тестов

**Unit тесты (`tests/`):**
- Тестируют отдельные функции/классы
- Используют in-memory SQLite
- Быстрые (~7 секунд)
- Запускаются автоматически: `pytest`

**Integration тесты (`integration_tests/`):**
- Тестируют реальное API
- Используют реальную PostgreSQL БД
- Требуют запущенный backend
- Запускаются вручную

## Использование

### 1. Запустите backend

```bash
cd backend
source venv/bin/activate
python main.py
```

### 2. Запустите интеграционные тесты

```bash
# В другом терминале
cd backend
source venv/bin/activate
python integration_tests/<test_name>.py
```

## Доступные тесты

### check_error_safety.py
Проверяет что технические ошибки НИКОГДА не показываются пользователям.

```bash
python integration_tests/check_error_safety.py
```

**Что тестирует:**
- ✅ Duplicate email ошибка безопасна
- ✅ Wrong credentials ошибка безопасна
- ✅ User ID использует UUID (не integer)
- ✅ Нет SQL деталей в ответах
- ✅ Нет stack traces
- ✅ Нет путей к файлам

**Пример вывода:**
```
============================================================
  TESTING ERROR SAFETY
  Verifying that technical errors never reach users
============================================================

✅ Backend is running

TEST: Register with duplicate email
User sees: 'Email already registered'
✅ PASS: Error message is safe for users

...

Total: 3/3 tests passed
🎉 ALL TESTS PASSED!
```

## Добавление новых тестов

1. Создайте файл `test_<feature>.py` (БЕЗ префикса `test_` если не хотите чтобы pytest его подхватил)
2. Используйте `requests` для HTTP запросов
3. Проверяйте реальные ответы API
4. Убедитесь что backend запущен

Пример:
```python
import requests

def test_my_feature():
    response = requests.post(
        "http://localhost:8000/graphql",
        json={"query": "..."}
    )
    data = response.json()
    # Проверки...
```

## Когда запускать

- После изменений в error handling
- Перед деплоем в продакшен
- При добавлении новых API endpoints
- При изменении схемы базы данных

## CI/CD

Для автоматизации в CI/CD:

```yaml
# Пример для GitHub Actions
- name: Run integration tests
  run: |
    cd backend
    python main.py &
    sleep 5
    python integration_tests/check_error_safety.py
```

---

*Для unit-тестов смотрите папку `tests/`*

