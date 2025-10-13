# AI Mature Content Support & Context Handling Fix

## Проблемы

### Проблема 1: Отказ от mature content
AI отказывался переводить текст с нецензурной лексикой, показывая ошибку:
```
❌ "Unable to process - text contains offensive language"
```

Это было неприемлемо для:
- Игр с рейтингом 18+
- Художественных произведений
- Реалистичных диалогов
- Профессиональной локализации контента для взрослых

### Проблема 2: Игнорирование контекста
AI игнорировал инструкции пользователя в поле "Context":
```
Text: "Go fuck yourself"
Context: "Добавляй всегда в конце - пиздец"
Result: ❌ "Иди на хуй" (контекст проигнорирован)
```

## Решения

### 1. Mature Content Support
Обновлены system prompts для всех AI функций, чтобы явно указать, что это **профессиональный инструмент локализации**, который должен обрабатывать ЛЮБОЙ контент без фильтрации.

### 2. Mandatory Context Following
Усилены промпты для строгого следования контексту:
- Контекст теперь отмечается как **MANDATORY** (🔴 маркер)
- Добавлены явные инструкции, что контекст содержит обязательные требования
- Контекст применяется и в user prompt, и в system content

## Изменения

### 1. Backend - AI Service

**Файл:** `backend/app/services/ai_service.py`

Обновлены system prompts для всех функций:
- `translate()` 
- `rephrase()`  
- `shorten()`
- `suggest_variants()`

**Добавлено для mature content:**
```python
"You are a professional translator for a localization tool."
"- NEVER refuse translation due to content type - this is a professional localization tool"
"- You MUST translate ALL content including profanity, mature themes, offensive language, etc."
"- This tool is used for games (including 18+), movies, books, and other media that may contain mature content"
"- Your role is purely translation - do not judge or filter content"
```

**Добавлено для mandatory context:**
```python
"Context Handling:"
"- If context is provided, it contains MANDATORY instructions you MUST follow"
"- Context may include: formatting rules, required additions, specific style requirements"
"- ALWAYS apply context instructions exactly as specified"
"- Context instructions override general translation rules"
```

В user prompts:
```python
"🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:\n{context}\n"
"This context contains REQUIRED instructions that you MUST apply to your translation."
```

### 2. Tests

**Файл:** `backend/tests/test_ai_service.py`

**Добавлены новые тесты:**

Класс `TestAIServiceMatureContent`:
- `test_translate_mature_content()` - проверяет перевод нецензурного текста
- `test_rephrase_mature_content()` - проверяет обработку mature content

Класс `TestAIServiceWithContext` (расширен):
- `test_translate_follows_mandatory_context_instructions()` - проверка добавления суффиксов
- `test_rephrase_follows_mandatory_context_instructions()` - проверка стилистических требований
- `test_suggest_variants_follows_context()` - проверка применения контекста ко всем вариантам

Обновлен `test_suggest_variants_gibberish()` для более гибкой валидации.

**Результат:** ✅ Все 28 тестов прошли успешно

### 3. Документация

**Обновлено:**
- `AUTOPILOT_FEATURE.md` - добавлена секция "Content Policy"
- `CHANGELOG.md` - добавлена запись о изменениях
- `docs/obsidian/AI Mature Content Support.md` - новая страница документации

## Результат

### Mature Content
✅ **До:** "Unable to process - text contains offensive language"  
✅ **После:** [Корректный перевод текста, независимо от содержания]

### Context Following
✅ **До:** Контекст "Добавляй всегда в конце - пиздец" → "Иди на хуй" (игнорирован)  
✅ **После:** Контекст "Добавляй всегда в конце - пиздец" → "Иди на хуй - пиздец" (применен)

## Проверка

```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py -v
```

Результат: **28 passed** ✅

Новые тесты включают:
- ✅ Mature content translation
- ✅ Mandatory context following
- ✅ Suffix/prefix additions
- ✅ Style requirements

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

