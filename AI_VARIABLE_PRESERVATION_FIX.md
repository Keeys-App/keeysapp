# AI Variable Preservation Fix

## Проблема

AI автоперевод переводил переменные в фигурных скобках (например, `{date}`, `{data}`, `{name}`) вместо того, чтобы сохранять их в исходном виде. Это приводило к поломке шаблонов строк в приложении.

### Пример проблемы

**До исправления:**
```
Исходный текст: "Next payment: {date}"
Перевод на итальянский: "Prossimo pagamento: {data}"  ❌ Переменная переведена!
```

**После исправления:**
```
Исходный текст: "Next payment: {date}"
Перевод на итальянский: "Prossimo pagamento: {date}"  ✅ Переменная сохранена!
```

## Решение

Добавлены явные инструкции во все промпты AI сервиса, чтобы сохранять переменные в фигурных скобках без изменений.

### Изменения в коде

#### `backend/app/services/ai_service.py`

Во все методы добавлены следующие правила в system prompt:

```python
"- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
"- NEVER translate or modify variable names inside curly braces - they are code placeholders"
```

Затронутые методы:
- ✅ `translate()` - перевод текста
- ✅ `rephrase()` - перефразирование
- ✅ `shorten()` - сокращение текста
- ✅ `suggest_variants()` - генерация вариантов

### Тесты

Добавлен новый класс тестов `TestAIServiceVariablePreservation` в `backend/tests/test_ai_service.py`:

- ✅ `test_translate_preserves_single_variable()` - одна переменная
- ✅ `test_translate_preserves_multiple_variables()` - несколько переменных
- ✅ `test_rephrase_preserves_variables()` - перефразирование
- ✅ `test_shorten_preserves_variables()` - сокращение
- ✅ `test_suggest_variants_preserves_variables()` - варианты
- ✅ `test_translate_preserves_complex_variables()` - сложные имена переменных

## Как проверить

### Запуск тестов

```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py::TestAIServiceVariablePreservation -v
```

### Ручная проверка

1. Создайте ключ перевода с переменными, например: `"Hello {name}, next payment: {date}"`
2. Используйте автоперевод на любой язык
3. Убедитесь, что переменные `{name}` и `{date}` сохранились в переводе

## Примеры правильной работы

### Перевод
```
EN: "Hello {name}, your order {orderId} will arrive on {date}"
ES: "Hola {name}, tu pedido {orderId} llegará el {date}"
```

### Перефразирование
```
Original: "Your payment of {amount} is due on {date}"
Rephrased: "Payment due: {amount} on {date}"
```

### Сокращение
```
Original: "We kindly remind you that your next payment of {amount} is scheduled for {date}"
Shortened: "Payment reminder: {amount} due {date}"
```

### Варианты
```
Original: "Welcome back, {username}!"
Variant 1: "Hello again, {username}!"
Variant 2: "Great to see you, {username}!"
Variant 3: "Welcome, {username}!"
```

## Технические детали

### Типы переменных

AI корректно обрабатывает:
- Простые имена: `{name}`, `{date}`, `{count}`
- С подчеркиванием: `{user_id}`, `{order_number}`
- С цифрами: `{item1}`, `{value2}`
- CamelCase: `{orderId}`, `{userName}`

### Как это работает

OpenAI API получает system prompt с явными инструкциями:
1. Все переменные в фигурных скобках - это плейсхолдеры кода
2. Их нельзя переводить или модифицировать
3. Они должны быть сохранены в точности как есть

Model (`gpt-4o-mini` по умолчанию) следует этим инструкциям и сохраняет переменные неизменными во всех типах операций.

## Влияние на систему

- ✅ **Обратная совместимость**: Не ломает существующий функционал
- ✅ **Производительность**: Нет влияния на скорость работы
- ✅ **Качество переводов**: Улучшено - переменные больше не ломаются
- ✅ **Покрытие тестами**: Добавлено 6 новых тестов

## Дата изменения

12 октября 2025

## Связанные файлы

- `backend/app/services/ai_service.py` - AI сервис с исправлениями
- `backend/tests/test_ai_service.py` - тесты для проверки

