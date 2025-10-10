# Key Components

This directory contains components for managing translation keys.

## Components

### KeyControls

A header component with controls for managing translation keys.

**Props:**
- `onCreateKey` (function): Callback to open the create key dialog

**Features:**
- Displays "Translation Keys" heading
- "Create Key" button with icon

**Usage:**
```tsx
import { KeyControls } from '@/components/key';

function ProjectPage() {
  const handleCreateKey = () => {
    setIsCreateDialogOpen(true);
  };

  return <KeyControls onCreateKey={handleCreateKey} />;
}
```

### EmptyKeys

A component that displays an empty state when there are no translation keys in the project.

**Props:**
- `onCreateKey` (function): Callback to open the create key dialog

**Features:**
- Icon-based empty state
- "Create Key" button to start adding keys
- "Import Keys" button (coming soon)
- "Learn More" link (coming soon)

### KeyList

A component that displays a list of translation keys for a project with inline translation editing.

**Props:**
- `projectId` (string): The UUID of the project to display keys for
- `projectLanguages` (string[]): Array of language codes from the project
- `onCreateKey` (function): Callback to open the create key dialog

**Usage:**
```tsx
import { KeyList } from '@/components/key';

function ProjectPage() {
  const handleCreateKey = () => {
    setIsCreateDialogOpen(true);
  };

  return (
    <KeyList 
      projectId={projectId} 
      projectLanguages={project.languages}
      onCreateKey={handleCreateKey}
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

### CreateKeyDialog

A dialog component to create new translation keys.

**Props:**
- `open` (boolean): Controls dialog visibility
- `onOpenChange` (function): Callback when dialog state changes
- `projectId` (string): The UUID of the project to create keys for

**Features:**
- Key name input (required)
- Optional description
- Automatic list refresh after creation
- Form validation
- Dialog-based UI for better UX

## Future Enhancements

- Add bulk operations
- Add search and filtering
- Add sorting options
- Add export/import functionality
- Add translation history

