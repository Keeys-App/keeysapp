# Key Components

This directory contains components for managing translation keys.

## Components

### KeyList

A component that displays a list of translation keys for a project.

**Props:**
- `projectId` (string): The UUID of the project to display keys for

**Usage:**
```tsx
import { KeyList } from '@/components/key';

function ProjectPage() {
  return (
    <KeyList projectId={projectId} />
  );
}
```

**Display Format:**
Each key is displayed in a card with:
- Key name (monospace font)
- Optional description
- List of translations in format:
  ```
  {language} {translation}
  ```

## Future Enhancements

- Add create/edit/delete functionality
- Add inline translation editing
- Add search and filtering
- Add sorting options
- Add export/import functionality

