# Tag System for Translation Keys

Implemented complete tag system for translation keys with import/export support.

## What's Added

### Backend

1. **Database Models**
   - Added `tags` field (JSON array) to `keys` table
   - Added `available_tags` field (JSON array) to `projects` table

2. **GraphQL API**
   - `KeyType.tags: [String!]` - key tags array
   - `ProjectType.availableTags: [String!]` - project available tags
   - `CreateKeyInput.tags: [String]` - tags when creating key
   - `UpdateKeyInput.tags: [String]` - update key tags

3. **Services**
   - Automatic update of project `available_tags` when adding new tags
   - Tag support in project import/export

4. **Migration**
   - File: `backend/migrations/add_tags_support.py`

### Frontend

1. **Components**
   - `Tags` - basic tags component from shadcn (components/ui/tags.tsx)
   - `TagsEditor` - tag editor with autocomplete (components/key/TagsEditor.tsx)

2. **Integration**
   - CreateKeyDialog: "Metadata" tab contains tag editor
   - KeyManagement: "Meta" tab contains tag editor
   - Support for creating new tags "on the fly"

3. **Types**
   - Updated TypeScript types for `TranslationKey`, `Project`
   - Updated GraphQL queries

## Running Migration

### Backend

```bash
cd backend

# Activate venv
source venv/bin/activate

# Run migration
python migrations/add_tags_support.py
```

Migration will add new columns with default value `[]`, so it's safe for existing data.

### Frontend

No dependency installation required - all components already added.

## Usage

### Creating Key with Tags

1. Open key creation dialog
2. Go to "Metadata" tab
3. Select existing tags or create new ones by entering name and clicking "Create" option

### Editing Tags

1. Select key in list
2. In right panel go to "Meta" tab
3. Use tag editor to add/remove tags
4. Click "Save Tags"

### Import/Export

Tags automatically included in exported data:

```json
{
  "name": "My Project",
  "config": {
    "availableTags": ["ui", "backend", "validation"],
    ...
  },
  "keys": [
    {
      "key": "BUTTON.SUBMIT",
      "description": "Submit button",
      "tags": ["ui"]
    }
  ]
}
```

## Features

- **Autocomplete**: TagsEditor shows all available project tags
- **Create on the fly**: New tags automatically added to project `available_tags`
- **Search**: Filter tags by entered text
- **Save in project**: All unique tags saved at project level for convenience

## Technical Details

### Backend

- Tags stored as JSON string array
- When creating/updating key, project `available_tags` list automatically updated
- Export/import fully supports tags

### Frontend

- Tags component built on Radix UI Popover and Command
- TagsEditor supports keyboard management
- Uses global `useSaving` store to display saving status
