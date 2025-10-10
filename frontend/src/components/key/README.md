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

### KeyManagement

A tabbed component for managing a selected translation key. Displayed in the right panel when a key is selected.

**Props:**
- `selectedKey` (TranslationKey | null): The currently selected key
- `projectLanguages` (Language[] | LanguageWithLocale[]): Project languages
- `projectId` (string): Project UUID
- `availableTags` (string[]): Available tags for the project

**Features:**
- **History Tab (default)**: Displays audit trail of all key changes using KeyLogsTimeline
- **Settings Tab**: Allows editing key name, description, and tags
- Auto-save functionality with change detection
- Global saving state integration

**Tabs:**
1. **History**: Timeline view of all changes made to the key
2. **Settings**: Form to edit key properties

### KeyLogsTimeline

A timeline component that displays the audit trail of a translation key's changes.

**Props:**
- `keyId` (string): UUID of the key to display logs for
- `limit` (number, optional): Maximum number of logs to show (default: 50)

**Features:**
- Timeline view with colored icons for different action types
- Shows old and new values for changes
- Relative time display (e.g., "2 hours ago")
- Automatic refresh when key changes
- Color-coded action indicators:
  - 🟢 Green: CREATE - Key or translation created
  - 🔵 Blue: UPDATE_KEY, UPDATE_DESCRIPTION - Key or description changed
  - 🟣 Purple: UPDATE_TRANSLATION - Translation updated
  - 🟠 Orange: DELETE_TRANSLATION - Translation deleted
  - 🔴 Red: DELETE - Key deleted

**Action Types:**
- `CREATE`: Key creation
- `UPDATE_KEY`: Key name changed
- `UPDATE_DESCRIPTION`: Description changed
- `UPDATE_TRANSLATION`: Translation added/updated
- `DELETE_TRANSLATION`: Translation removed
- `DELETE`: Key deleted

**Usage:**
```tsx
import { KeyLogsTimeline } from '@/components/key';

function KeyHistoryView() {
  return <KeyLogsTimeline keyId={keyUuid} limit={50} />;
}
```

## Future Enhancements

- Add bulk operations
- Add search and filtering
- Add sorting options
- Add export/import functionality
- ✅ ~~Add translation history~~ (implemented as KeyLogsTimeline)
- Add ability to revert to previous values from history
- Add user name display in timeline (currently shows userId)
- Add filtering in timeline (by action type, date range)

