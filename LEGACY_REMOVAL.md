# Удаление легаси поддержки строкового формата языков

## 🗑️ Проблема

Проект использовал два формата для хранения языков:
- **Старый (легаси)**: `["en", "ru"]` - массив строк
- **Новый**: `[{code: "en", locale: "en-US"}, {code: "ru", locale: "ru-RU"}]` - массив объектов

Поддержка обоих форматов создавала технический долг и усложняла кодовую базу.

## ✅ Решение

Полностью удалена поддержка легаси формата. Теперь поддерживается **только** новый формат с объектами.

## 📝 Изменения

### Backend

#### 1. `backend/app/services/project_service.py`

**Удалено из `create_project()`:**
```python
# УДАЛЕНО
elif isinstance(lang, str):
    languages_data.append({
        'code': lang,
        'locale': lang
    })
```

**Удалено из `update_project()`:**
```python
# УДАЛЕНО
elif isinstance(lang, str):
    languages_data.append({
        'code': lang,
        'locale': lang
    })
```

**Удалено из `export_project()`:**
```python
# УДАЛЕНО
if isinstance(lang, dict):
    code = lang.get('code', '')
else:
    # Old format support
    code = lang
```

**Теперь:**
```python
# lang всегда dict с 'code' и 'locale'
code = lang.get('code', '')
```

#### 2. `backend/app/schemas/project.py`

**Удалено из `build_project_type()`:**
```python
# УДАЛЕНО
elif isinstance(lang, str):
    # Old format (backward compatibility): "en"
    locale = DEFAULT_LANGUAGE_LOCALES.get(lang, f'{lang}-{lang.upper()}')
    languages.append(LanguageConfigType(code=lang, locale=locale))
```

**Теперь:**
```python
# lang всегда dict с 'code' и 'locale'
languages.append(LanguageConfigType(
    code=lang.get('code', ''),
    locale=lang.get('locale', '')
))
```

### Frontend

#### 3. `frontend/src/components/project/ProjectForm.tsx`

**Удалено:**
```typescript
// УДАЛЕНО: Fallback для старого формата
const code = String(lang);
const langConfig = LANGUAGE_CONFIGS.find((l) => l.code === code);
return {
  code: code,
  locale: langConfig?.locale || `${code}-${code.toUpperCase()}`,
};
```

**Теперь:**
```typescript
// Языки всегда в правильном формате: {code: string, locale: string}
const languages = (project.languages || []).map(
  (lang): LanguageConfigInput => ({
    code: lang.code,
    locale: lang.locale,
  })
);
```

**Также удален неиспользуемый импорт:**
```typescript
// УДАЛЕНО
import { LANGUAGE_CONFIGS } from "@/types/project";
```

### Тесты

Обновлены **все** тесты на использование нового формата:

#### `test_project_service.py`
- Все `languages=["en"]` → `languages=[{"code": "en", "locale": "en-US"}]`
- Все `languages=["ru"]` → `languages=[{"code": "ru", "locale": "ru-RU"}]`
- И т.д.

#### `test_translation_progress.py`
- Все `languages=["en"]` → `languages=[{"code": "en", "locale": "en-US"}]`
- Все `languages=["en", "ru"]` → `languages=[{"code": "en", "locale": "en-US"}, {"code": "ru", "locale": "ru-RU"}]`

#### `test_key_performance.py`
- Обновлен на использование объектов с `code` и `locale`

## 🧪 Результаты тестирования

```bash
76 passed, 3 warnings in 12.95s
```

**Все тесты прошли успешно!** ✅

## 🚀 Преимущества

1. **Упрощение кода** - меньше условных проверок и конвертаций
2. **Улучшение читаемости** - код стал чище и понятнее
3. **Меньше багов** - нет риска случайной обработки неправильного формата
4. **Единообразие** - один формат данных во всем приложении
5. **Проще поддержка** - не нужно помнить о двух форматах

## ⚠️ Breaking Changes

### Если у вас есть старые данные в базе

Если в вашей базе данных остались проекты со старым форматом (массивы строк), они **перестанут работать**.

**Решение:** Запустите миграцию для конвертации старых данных:

```bash
cd backend
source venv/bin/activate
python migrations/migrate_languages_to_config.py
```

Эта миграция конвертирует все старые форматы в новые.

### Если вы используете API напрямую

Если вы отправляете запросы к API с языками в старом формате:

**Раньше работало:**
```json
{
  "name": "My Project",
  "languages": ["en", "ru"]
}
```

**Теперь ТОЛЬКО так:**
```json
{
  "name": "My Project",
  "languages": [
    {"code": "en", "locale": "en-US"},
    {"code": "ru", "locale": "ru-RU"}
  ]
}
```

## 📚 Связанные документы

- [README_LANGUAGE_CONFIG.md](backend/migrations/README_LANGUAGE_CONFIG.md) - Документация по миграции языков
- [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) - Оптимизация N+1 запросов

## ✅ Чеклист для разработчиков

- [x] Удалена поддержка строкового формата в backend
- [x] Удалена поддержка строкового формата в frontend
- [x] Обновлены все тесты
- [x] Все тесты проходят успешно
- [x] Обновлена документация

## 🎯 Заключение

Легаси код успешно удален! Проект теперь использует **только** современный формат языков с объектами `{code, locale}`, что делает код чище, безопаснее и проще в поддержке.

