# AI JSON Validation - Structured Output

## Проблема

При работе с gibberish текстом (например, "asdasdasd"), AI мог возвращать извинения на целевом языке:
```
Lo siento, pero la entrada "asdasdasd" no contiene un significado claro...
```

Такие ответы показывались как валидные переводы, что было неправильно.

## Решение

Переход на **structured JSON output** от OpenAI. Теперь AI сам определяет, может ли он выполнить задачу.

## Формат ответа

### Для translate, rephrase, shorten:
```json
{
  "success": true,
  "result": "Translated/rephrased/shortened text",
  "reason": "optional reason if success=false"
}
```

### Для suggest_variants:
```json
{
  "success": true,
  "variants": ["variant 1", "variant 2", "variant 3"],
  "reason": "optional reason if success=false"
}
```

## Примеры

### ✅ Успешный случай (валидный текст)
**Input:** "Hello, world!"
**Response:**
```json
{
  "success": true,
  "result": "Hola, mundo!"
}
```
→ Показывается как suggestion

### ❌ Неуспешный случай (gibberish)
**Input:** "asdasdasd"
**Response:**
```json
{
  "success": false,
  "result": "",
  "reason": "The input appears to be random characters without clear meaning"
}
```
→ Показывается ошибка: "Unable to translate this text. Please try with different content."

## Преимущества

1. **Универсальность** - работает на всех языках
2. **AI сам решает** - не нужно прописывать паттерны для каждого языка
3. **Чистые результаты** - никогда не показывается извинения/объяснения как переводы
4. **Логирование** - в backend логах видно причину отказа AI

## Обновлённые методы

### AIService (backend/app/services/ai_service.py)

**translate()**
```python
response_format={"type": "json_object"}
# Парсинг JSON
response_data = json.loads(response_text)
if not response_data.get("success"):
    raise Exception("Unable to translate...")
return response_data["result"]
```

**rephrase()**, **shorten()** - аналогично

**suggest_variants()**
```python
response_format={"type": "json_object"}
response_data = json.loads(response_text)
if not response_data.get("success"):
    raise Exception("Unable to generate variants...")
return response_data["variants"][:count]
```

## System Prompts

Все промпты обновлены:
```
"You are a professional translator. "
"Respond ONLY with valid JSON in this exact format:
{"success": true/false, "result": "...", "reason": "..."}

Rules:
- If the text is translatable, set success=true and provide translation
- If the text is gibberish, set success=false and explain in reason
- NEVER include apologies or explanations in the result field
```

## Тестирование

### Запуск тестов
```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py -v
```

### Тест-кейсы

**test_translate_valid_text**
- Переводит "Hello, world!" на испанский
- Проверяет что результат не содержит извинений

**test_translate_gibberish**
- Пытается перевести "asdasdasd"
- Должен выбросить Exception
- Не должен возвращать "Lo siento..."

**test_rephrase_gibberish**
- Пытается перефразировать "xyzxyzxyz"
- Должен выбросить Exception

**test_suggest_variants_gibberish**
- Пытается сгенерировать варианты для "qweasdzxc"
- Должен выбросить Exception

**test_translate_to_russian/chinese/arabic**
- Проверяет работу на разных языках

### Ручное тестирование

1. Откройте ключ в UI
2. Выберите язык для перевода
3. Попробуйте перевести gibberish текст (например, "asdasd")
4. Должна показаться ошибка, а не карточка с извинениями
5. Попробуйте нормальный текст - должна показаться карточка

## Breaking Changes

### Backend API

Изменений в GraphQL API нет - всё работает как раньше.

### Frontend

Изменений не требуется - обрабатывается через существующую логику `success` полей.

## Логирование

### Успешный случай
```
INFO: Translation completed successfully
```

### Gibberish
```
WARNING: AI could not translate: The input appears to be random characters
INFO: Translation failed. Please try again.
```

## Миграции

Миграции не требуются - это изменение только в логике обработки ответов AI.

## Мониторинг

В production логах смотрите:
- `WARNING: AI could not translate/rephrase/shorten` - AI отказался
- Частота таких предупреждений показывает качество input данных

## Рекомендации

- Используйте валидацию на frontend перед отправкой в AI
- Минимальная длина текста: 2 символа
- Запретите отправку только пробелов/спецсимволов

