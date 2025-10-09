# Key Components

This directory contains components for managing translation keys.

## Components

### KeyList

A component that displays a list of translation keys for a project with inline translation editing.

**Props:**
- `projectId` (string): The UUID of the project to display keys for
- `projectLanguages` (string[]): Array of language codes from the project

**Usage:**
```tsx
import { KeyList } from '@/components/key';

function ProjectPage() {
  return (
    <KeyList 
      projectId={projectId} 
      projectLanguages={project.languages} 
    />
  );
}
```

**Display Format:**
Each key is displayed in a card with:
- Key name (monospace font)
- Optional description
- All project languages displayed in format:
  ```
  language | translation (or "No translation")
  ```
- Hover on any row to see Edit/Add button

### TranslationEditor

An inline editor for translations. Supports both editing existing translations and adding new ones.

**Features:**
- Shows "No translation" for missing translations
- Edit/Add button appears on hover
- Inline editing with Save/Cancel buttons
- Automatic refresh after save

### CreateKeyForm

A simple form to create new translation keys.

**Features:**
- Key name input
- Optional description
- Automatic list refresh after creation

## Future Enhancements

- Add bulk operations
- Add search and filtering
- Add sorting options
- Add export/import functionality
- Add translation history

