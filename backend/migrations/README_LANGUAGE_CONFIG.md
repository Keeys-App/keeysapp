# Language Configuration Migration

## Overview

This migration updates the project language storage from simple language codes to language configuration objects with custom locales.

## Changes

### Before (Old Format)
```json
{
  "languages": ["en", "ru", "de"]
}
```

### After (New Format)
```json
{
  "languages": [
    {"code": "en", "locale": "en-US"},
    {"code": "ru", "locale": "ru-RU"},
    {"code": "de", "locale": "de-DE"}
  ]
}
```

## Running the Migration

To migrate existing projects to the new format:

```bash
# Activate virtual environment
source venv/bin/activate

# Run migration
python migrations/migrate_languages_to_config.py
```

## Features

### Backend

1. **Model Changes** (`app/models/project.py`)
   - Updated `languages` field to store array of objects with `code` and `locale`

2. **GraphQL Schema** (`app/schemas/project.py`)
   - Added `LanguageConfigType` with `code` and `locale` fields
   - Added `LanguageConfigInput` for mutations
   - Updated `ProjectType.languages` to return `List[LanguageConfigType]`
   - Updated input types to accept `List[LanguageConfigInput]`

3. **Service Layer** (`app/services/project_service.py`)
   - Updated `create_project` to handle language configuration objects
   - Updated `update_project` to handle language configuration objects
   - Automatic conversion from input objects to JSON storage format

4. **Backward Compatibility**
   - `build_project_type` function automatically converts old string format to new object format
   - Default locales applied based on language code
   - Existing projects with old format will work seamlessly

### Frontend

1. **Type Definitions** (`frontend/src/graphql/projects.ts`)
   - Added `LanguageConfig` interface with `code` and `locale`
   - Added `LanguageConfigInput` for mutations
   - Updated `Project` interface to use `LanguageConfig[]`

2. **New Component** (`frontend/src/components/project/LanguageConfigEditor.tsx`)
   - Visual language selector with flags and names
   - Edit locale for each language
   - Dialog for customizing locale codes
   - Examples and validation

3. **Updated Components**
   - `ProjectForm`: Now uses `LanguageConfigEditor` component
   - `ProjectPage`: Displays both language code and locale
   - `ProjectKeysPage`: Updated language filtering logic
   - `ImportContent`: Updated language filtering logic
   - `ExportContent`: Updated language filtering logic

## Default Locale Mappings

The migration automatically assigns default locales based on language codes:

| Code | Default Locale |
|------|---------------|
| en   | en-US         |
| es   | es-ES         |
| fr   | fr-FR         |
| de   | de-DE         |
| it   | it-IT         |
| pt   | pt-PT         |
| ru   | ru-RU         |
| zh   | zh-CN         |
| ja   | ja-JP         |
| ko   | ko-KR         |
| ar   | ar-SA         |
| hi   | hi-IN         |
| ... (see migration file for full list)

## Custom Locales

Users can now customize locales for each language. Common use cases:

- **English**: `en-US`, `en-GB`, `en-AU`
- **Spanish**: `es-ES`, `es-MX`, `es-AR`
- **Portuguese**: `pt-PT`, `pt-BR`
- **Chinese**: `zh-CN`, `zh-TW`, `zh-HK`
- **French**: `fr-FR`, `fr-CA`

## API Examples

### Create Project with Custom Locales

```graphql
mutation {
  createProject(input: {
    name: "My App"
    languages: [
      { code: "en", locale: "en-US" }
      { code: "en", locale: "en-GB" }
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

### Update Project Languages

```graphql
mutation {
  updateProject(input: {
    id: "project-uuid"
    languages: [
      { code: "en", locale: "en-US" }
      { code: "es", locale: "es-MX" }
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

## Rollback

If you need to rollback to the old format, you can manually update the database:

```python
from app.database import get_db
from app.models.project import Project

db = next(get_db())
projects = db.query(Project).all()

for project in projects:
    # Convert back to simple codes
    if project.languages and isinstance(project.languages[0], dict):
        project.languages = [lang['code'] for lang in project.languages]

db.commit()
```

**Note**: This will lose custom locale information.

## Testing

After migration:

1. Verify projects display correctly in UI
2. Test creating new projects with custom locales
3. Test editing existing project languages
4. Verify translations still work correctly
5. Test export/import functionality

## Support

For issues or questions, refer to:
- Backend migration script: `migrations/migrate_languages_to_config.py`
- GraphQL schema: `app/schemas/project.py`
- Frontend component: `frontend/src/components/project/LanguageConfigEditor.tsx`

