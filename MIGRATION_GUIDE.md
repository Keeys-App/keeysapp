# Migration Guide for Languages with Custom Locales

## What Changed?

Now you can configure custom locales for each language in every project!

**Before:**
- EN (English)
- RU (Russian)

**Now:**
- EN → en-US (English USA)
- EN → en-GB (English UK)
- RU → ru-RU (Russian Russia)
- PT → pt-BR (Portuguese Brazil)
- PT → pt-PT (Portuguese Portugal)

## Running Migration (for existing projects)

If you already have projects in database, run migration:

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run migration
python migrations/migrate_languages_to_config.py
```

Migration automatically:
- ✅ Converts old language codes to new format
- ✅ Applies default locales (en → en-US, ru → ru-RU, etc.)
- ✅ Preserves all existing data

## How to Use in UI?

### Creating/Editing Project

1. Open project create or edit form
2. In "Languages" section you'll see new interface:
   - Each language displays with flag, name and current locale
   - Click edit button (✏️) next to language
   - In dialog enter custom locale (e.g., `en-GB`, `pt-BR`)
   - Click "Save"

### Viewing Project

On project page now displays:
- Language code (EN)
- Custom locale (`en-US`)

## Examples of Popular Locales

### English
- `en-US` - USA
- `en-GB` - United Kingdom
- `en-AU` - Australia
- `en-CA` - Canada

### Spanish
- `es-ES` - Spain
- `es-MX` - Mexico
- `es-AR` - Argentina

### Portuguese
- `pt-PT` - Portugal
- `pt-BR` - Brazil

### Chinese
- `zh-CN` - Simplified (China)
- `zh-TW` - Traditional (Taiwan)
- `zh-HK` - Hong Kong

### French
- `fr-FR` - France
- `fr-CA` - Canada
- `fr-BE` - Belgium

## API Examples

### GraphQL Query (create project)

```graphql
mutation {
  createProject(input: {
    name: "My App"
    languages: [
      { code: "en", locale: "en-US" }
      { code: "es", locale: "es-MX" }
      { code: "pt", locale: "pt-BR" }
    ]
    defaultLanguage: "en"
  }) {
    id
    languages {
      code
      locale
    }
  }
}
```

### GraphQL Query (update project)

```graphql
mutation {
  updateProject(input: {
    id: "project-uuid"
    languages: [
      { code: "en", locale: "en-GB" }
      { code: "fr", locale: "fr-CA" }
    ]
  }) {
    id
    languages {
      code
      locale
    }
  }
}
```

## Backward Compatibility

✅ All existing projects will continue working
✅ API automatically converts old format to new
✅ Default locales applied automatically

## Support

If issues arise:
1. Check migration logs
2. See detailed documentation: `backend/migrations/README_LANGUAGE_CONFIG.md`
3. See code changes: `CHANGELOG.md`
