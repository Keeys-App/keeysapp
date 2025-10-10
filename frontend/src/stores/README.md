# Stores

Global state management using Zustand.

## Saving Store

The saving store manages the global saving state across the application. It provides a centralized way to show saving indicators and disable actions during save operations.

### Usage

```typescript
import { useSaving, useSavingStore } from '@/stores';

function MyComponent() {
  const [updateData] = useMutation(UPDATE_DATA);
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const handleSave = async () => {
    await withSaving(
      async () => {
        await updateData({ variables: { input: data } });
      },
      "Saving data..." // Optional custom message for footer
    );
  };

  return (
    <Button 
      onClick={handleSave} 
      disabled={isSaving}
      variant="outline"
    >
      Save
    </Button>
  );
}
```

### Features

- **Global Footer Indicator**: Shows a spinner and message in the app footer during save operations
- **Automatic State Management**: Handles saving state automatically, including error cases
- **Custom Messages**: Provide descriptive messages for better UX
- **Button Disabling**: Use `isSaving` to disable buttons during operations

### Best Practices

1. Always wrap async save operations with `withSaving()`
2. Provide descriptive messages (e.g., "Updating description...", "Creating project...")
3. Use `isSaving` to disable buttons and prevent concurrent operations
4. Don't show local loading indicators - rely on the global footer

