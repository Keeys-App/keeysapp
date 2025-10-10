# Project Export & Import Feature

## Overview

This feature allows users to export entire projects to JSON files for backup or sharing purposes, and import projects from JSON files.

## Export Format

The export format follows the i18n structure:

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
    "color": "#6366f1",
    "status": "active"
  },
  "locales": [
    {
      "code": "en",
      "locale": "en-US",
      "keys": {
        "button.submit": "Submit",
        "button.cancel": "Cancel"
      }
    },
    {
      "code": "ru",
      "locale": "ru-RU",
      "keys": {
        "button.submit": "Отправить",
        "button.cancel": "Отмена"
      }
    }
  ]
}
```

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
- All translation keys
- All translations organized by language

#### `ProjectService.import_project_data()`
Imports project data:
- Creates a new project with the provided configuration
- Creates all translation keys
- Creates all translations for each key and language
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
- Support other formats (CSV, XLSX, etc.)

