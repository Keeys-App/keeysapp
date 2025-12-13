# Removing Legacy String Format Language Support

## 🗑️ Problem

Project used two formats for storing languages:
- **Old (legacy)**: `["en", "ru"]` - array of strings
- **New**: `[{code: "en", locale: "en-US"}, {code: "ru", locale: "ru-RU"}]` - array of objects

Supporting both formats created technical debt and complicated codebase.

## ✅ Solution

Completely removed legacy format support. Now **only** new format with objects is supported.

## 📝 Changes

### Backend

#### 1. `backend/app/services/project_service.py`

**Removed from `create_project()`:**
```python
# REMOVED
elif isinstance(lang, str):
    languages_data.append({
        'code': lang,
        'locale': lang
    })
```

**Removed from `update_project()`:**
```python
# REMOVED
elif isinstance(lang, str):
    languages_data.append({
        'code': lang,
        'locale': lang
    })
```

**Removed from `export_project()`:**
```python
# REMOVED
if isinstance(lang, dict):
    code = lang.get('code', '')
else:
    # Old format support
    code = lang
```

**Now:**
```python
# lang is always dict with 'code' and 'locale'
code = lang.get('code', '')
```

#### 2. `backend/app/schemas/project.py`

**Removed from `build_project_type()`:**
```python
# REMOVED
elif isinstance(lang, str):
    # Old format (backward compatibility): "en"
    locale = DEFAULT_LANGUAGE_LOCALES.get(lang, f'{lang}-{lang.upper()}')
    languages.append(LanguageConfigType(code=lang, locale=locale))
```

**Now:**
```python
# lang is always dict with 'code' and 'locale'
languages.append(LanguageConfigType(
    code=lang.get('code', ''),
    locale=lang.get('locale', '')
))
```

### Frontend

#### 3. `frontend/src/components/project/ProjectForm.tsx`

**Removed:**
```typescript
// REMOVED: Fallback for old format
const code = String(lang);
const langConfig = LANGUAGE_CONFIGS.find((l) => l.code === code);
return {
  code: code,
  locale: langConfig?.locale || `${code}-${code.toUpperCase()}`,
};
```

**Now:**
```typescript
// Languages always in correct format: {code: string, locale: string}
const languages = (project.languages || []).map(
  (lang): LanguageConfigInput => ({
    code: lang.code,
    locale: lang.locale,
  })
);
```

**Also removed unused import:**
```typescript
// REMOVED
import { LANGUAGE_CONFIGS } from "@/types/project";
```

### Tests

Updated **all** tests to use new format:

#### `test_project_service.py`
- All `languages=["en"]` → `languages=[{"code": "en", "locale": "en-US"}]`
- All `languages=["ru"]` → `languages=[{"code": "ru", "locale": "ru-RU"}]`
- etc.

#### `test_translation_progress.py`
- All `languages=["en"]` → `languages=[{"code": "en", "locale": "en-US"}]`
- All `languages=["en", "ru"]` → `languages=[{"code": "en", "locale": "en-US"}, {"code": "ru", "locale": "ru-RU"}]`

#### `test_key_performance.py`
- Updated to use objects with `code` and `locale`

## 🧪 Test Results

```bash
76 passed, 3 warnings in 12.95s
```

**All tests passed successfully!** ✅

## 🚀 Benefits

1. **Code simplification** - fewer conditional checks and conversions
2. **Improved readability** - code is cleaner and clearer
3. **Fewer bugs** - no risk of accidentally handling wrong format
4. **Consistency** - single data format throughout application
5. **Easier maintenance** - no need to remember two formats

## ⚠️ Breaking Changes

### If you have old data in database

If your database still has projects with old format (string arrays), they **will stop working**.

**Solution:** Run migration to convert old data:

```bash
cd backend
source venv/bin/activate
python migrations/migrate_languages_to_config.py
```

This migration converts all old formats to new ones.

### If you use API directly

If you send API requests with languages in old format:

**Previously worked:**
```json
{
  "name": "My Project",
  "languages": ["en", "ru"]
}
```

**Now ONLY this way:**
```json
{
  "name": "My Project",
  "languages": [
    {"code": "en", "locale": "en-US"},
    {"code": "ru", "locale": "ru-RU"}
  ]
}
```

## 📚 Related Documents

- [README_LANGUAGE_CONFIG.md](backend/migrations/README_LANGUAGE_CONFIG.md) - Language migration documentation
- [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) - N+1 query optimization

## ✅ Developer Checklist

- [x] Removed string format support in backend
- [x] Removed string format support in frontend
- [x] Updated all tests
- [x] All tests pass successfully
- [x] Updated documentation

## 🎯 Conclusion

Legacy code successfully removed! Project now uses **only** modern language format with `{code, locale}` objects, making code cleaner, safer and easier to maintain.
