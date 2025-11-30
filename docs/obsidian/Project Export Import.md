# Project Export & Import Feature

## Overview

This feature allows users to export entire projects to JSON files for backup or sharing purposes, and import projects from JSON files.

## Export Format

The export format follows the i18n structure with separate keys and translations sections:

```json
{
  "name": "Project Name",
  "config": {
    "description": "Project description",
    "languages": [
      {
        "code": "en",
        "locale": "en-US"
      },
      {
        "code": "ru",
        "locale": "ru-RU"
      }
    ],
    "defaultLanguage": "en",
    "availableTags": ["ui", "common", "errors"],
    "color": "#6366f1",
    "status": "active"
  },
  "keys": [
    {
      "key": "button.submit",
      "description": "Submit button label",
      "tags": ["ui", "common"]
    },
    {
      "key": "button.cancel",
      "description": "Cancel button label",
      "tags": ["ui"]
    }
  ],
  "locales": [
    {
      "code": "en",
      "keys": {
        "button.submit": "Submit",
        "button.cancel": "Cancel"
      }
    },
    {
      "code": "ru",
      "keys": {
        "button.submit": "Отправить",
        "button.cancel": "Отмена"
      }
    }
  ]
}
```

### Format Structure

1. **`name`**: Project name
2. **`config`**: Project configuration
   - `description`: Project description
   - `languages`: Array of language objects with `code` and `locale` (supports custom locales!)
   - `defaultLanguage`: Default language code
   - `availableTags`: Array of available tag names for the project
   - `color`: Project color (hex)
   - `status`: Project status
3. **`keys`**: Array of all translation keys with descriptions and tags
   - Each key has: `key` (the key string), `description` (optional description), and `tags` (array of tag names)
4. **`locales`**: Array of translations organized by language
   - Each locale has: `code` (to match with `config.languages`) and `keys` (object with translations)
   - Note: `locale` info is not duplicated here - it's already in `config.languages`

**Why this structure?**
- **`config.languages`** stores language metadata (code + custom locale)
- **`keys`** provides descriptions in one place (not duplicated per language)
- **`locales`** focuses only on translations, referencing languages by `code`
- No data duplication - each piece of information in one place

### Backward Compatibility

The import supports files without the `keys` array. In this case:
- Keys will be created from translations in `locales`
- Descriptions will be empty
- All keys will still be imported successfully

## Backend Implementation

### REST API Endpoints

#### Export Project
- **Endpoint**: `GET /api/projects/{project_id}/export`
- **Authentication**: Required (Bearer token)
- **Response**: JSON file with project data
- **Permissions**: User must have access to the project (owner or member)

#### Import Project
- **Endpoint**: `POST /api/projects/import`
- **Authentication**: Required (Bearer token)
- **Request**: Multipart form data with JSON file
- **Response**: Created project ID and name
- **Permissions**: Any authenticated user can import projects

### Service Methods

#### `ProjectService.export_project_data()`
Exports project data including:
- Project metadata (name, description, color, status)
- Language configurations
- All translation keys with descriptions (in `keys` array)
- All translations organized by language (in `locales` array)

#### `ProjectService.import_project_data()`
Imports project data:
- Creates a new project with the provided configuration
- Creates all translation keys with descriptions and tags from `keys` array
- Creates all translations for each key and language from `locales` array
- Logs all import actions (keys and translations) with `KeyActionType.IMPORT` for audit trail
- Maintains key descriptions and tags during import
- Uses transactions to ensure data consistency

## Frontend Implementation

### Export Project

**Location**: Project Keys page (Actions menu)

**Usage**:
1. Open any project
2. Click "Actions" menu in the toolbar
3. Select "Export Project"
4. JSON file will be automatically downloaded

**File naming**: `{project_name}_export.json`

### Import Project

**Location**: Dashboard page

**Usage**:
1. Go to Dashboard
2. Click "Import Project" button (top right)
3. Select a JSON file with project data
4. Click "Import"
5. The project will be created and added to your projects list

**Validation**:
- Only JSON files are accepted
- Project name is required in the file
- Invalid JSON format will show an error

## Use Cases

### Backup Projects
Export projects regularly to create backups:
1. Export project to JSON
2. Store the file in a secure location
3. Import when needed to restore the project

### Share Projects
Share project configurations with team members:
1. Export the project
2. Send the JSON file to team members
3. Team members can import and work on a copy

### Template Projects
Create project templates:
1. Create a project with common keys and structure
2. Export it
3. Use as a template by importing for new projects

## Security Considerations

- Authentication is required for both export and import
- Exported files contain all translation data
- Users can only export projects they have access to
- Imported projects are created under the importing user's ownership
- No sensitive user data is included in exports

## Error Handling

### Export Errors
- **401**: User not authenticated
- **404**: Project not found or access denied
- **500**: Server error during export

### Import Errors
- **400**: Invalid file format (not JSON)
- **400**: Missing required fields (e.g., project name)
- **401**: User not authenticated
- **500**: Server error during import

## Technical Notes

### Database Transactions
Import operations use database transactions to ensure data consistency. If any part of the import fails, all changes are rolled back.

### Performance
- Export queries are optimized to minimize database load
- Large projects with many keys may take longer to export/import
- Consider adding progress indicators for large projects in future updates

### Future Improvements
- Add export/import progress indicators
- Support partial imports (e.g., only keys, only translations)
- Add export filters (e.g., specific languages only)
- Validate translations before import
- Support more formats (CSV, XLSX, Android XML, etc.)

## Supported Translation Formats

In addition to the full project JSON export/import, the system supports exporting and importing translations in various formats:

### i18n (JSON)
Simple key-value JSON format commonly used in i18n libraries:

```json
{
  "welcome": "Welcome!",
  "hello": "Hello"
}
```

### iOS Strings (.strings)
Apple's localization format used in iOS/macOS applications:

```strings
/* Welcome message */
"welcome" = "Welcome!";

/* Greeting */
"hello" = "Hello";
```

**Features:**
- Supports comments (single-line `//` and block `/* */`)
- Proper escaping for special characters (`"`, `\`, `\n`, `\t`)
- Key descriptions are exported as comments
- Compatible with Xcode and Apple's localization tools

**Import features:**
- Auto-detection of format from file content
- Handles escaped characters properly
- Supports multiline values with `\n`

