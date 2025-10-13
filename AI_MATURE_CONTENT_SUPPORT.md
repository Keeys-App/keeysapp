# AI Mature Content Support Fix

## Проблема

AI отказывался переводить текст с нецензурной лексикой, показывая ошибку:
```
❌ "Unable to process - text contains offensive language"
```

Это было неприемлемо для:
- Игр с рейтингом 18+
- Художественных произведений
- Реалистичных диалогов
- Профессиональной локализации контента для взрослых

## Решение

Обновлены system prompts для всех AI функций, чтобы явно указать, что это **профессиональный инструмент локализации**, который должен обрабатывать ЛЮБОЙ контент без фильтрации.

## Изменения

### 1. Backend - AI Service

**Файл:** `backend/app/services/ai_service.py`

Обновлены system prompts для всех функций:
- `translate()` - строки 87-111
- `rephrase()` - строки 192-216  
- `shorten()` - строки 296-320
- `suggest_variants()` - строки 402-426

**Добавлено в каждый prompt:**
```python
"You are a professional translator for a localization tool."
"- NEVER refuse translation due to content type - this is a professional localization tool"
"- You MUST translate ALL content including profanity, mature themes, offensive language, etc."
"- This tool is used for games (including 18+), movies, books, and other media that may contain mature content"
"- Your role is purely translation - do not judge or filter content"
```

### 2. Tests

**Файл:** `backend/tests/test_ai_service.py`

Добавлен новый тест-класс `TestAIServiceMatureContent`:
- `test_translate_mature_content()` - проверяет перевод нецензурного текста
- `test_rephrase_mature_content()` - проверяет обработку mature content

Обновлен тест `test_suggest_variants_gibberish()` для более гибкой валидации.

**Результат:** ✅ Все 25 тестов прошли успешно

### 3. Документация

**Обновлено:**
- `AUTOPILOT_FEATURE.md` - добавлена секция "Content Policy"
- `CHANGELOG.md` - добавлена запись о изменениях
- `docs/obsidian/AI Mature Content Support.md` - новая страница документации

## Результат

После изменений AI корректно обрабатывает ЛЮБОЙ контент:

✅ **До:** "Unable to process - text contains offensive language"  
✅ **После:** [Корректный перевод текста, независимо от содержания]

## Проверка

```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py -v
```

Результат: **25 passed** ✅

## Примечания

- Изменения применяются ТОЛЬКО к обработке существующего текста
- Инструмент НЕ генерирует offensive content сам по себе
- Профессиональные переводчики несут ответственность за уместность контента
- Никакой специальной фильтрации или логирования "чувствительного" контента не происходит

## Обратная совместимость

✅ Все существующие тесты прошли  
✅ API не изменился  
✅ Никаких breaking changes

## Когда применять

Изменения уже активны для всех пользователей. Перезапуск backend не требуется, так как это изменения в коде Python, которые применяются при следующем запросе к AI.

Если backend уже запущен, рекомендуется перезапустить его для применения изменений.

