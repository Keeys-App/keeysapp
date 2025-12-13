# Key Logging UI - Guide

## Overview

Implemented full UI for viewing translation key change history as timeline component.

## UI Structure

### Key Management - Tabs

When key is selected in list, right panel displays `KeyManagement` with two tabs:

```
┌─────────────────────────────────┐
│     Key Management              │
├─────────────────────────────────┤
│  [ History ] [ Settings ]       │
├─────────────────────────────────┤
│                                 │
│   (tab content)                 │
│                                 │
└─────────────────────────────────┘
```

#### 1. History (default tab)

Timeline with history of all key changes:

```
○ Created                    2 hours ago
  Created:
  ┌────────────────────────┐
  │ button.submit          │
  └────────────────────────┘

○ Translation updated       1 hour ago
  en
  Old:
  ┌────────────────────────┐
  │ Submit                 │ (strikethrough, red background)
  └────────────────────────┘
  New:
  ┌────────────────────────┐
  │ Submit form            │ (green background)
  └────────────────────────┘

○ Description changed      30 minutes ago
  Old:
  ┌────────────────────────┐
  │ Old description        │ (strikethrough, red background)
  └────────────────────────┘
  New:
  ┌────────────────────────┐
  │ New description        │ (green background)
  └────────────────────────┘
```

#### 2. Settings

Key editing form (previous functionality):
- Key Name (textarea)
- Description (textarea)
- Tags (editor)
- Save Changes (button)

## Color Indication

Timeline uses color indicators for different action types:

| Color | Action | Icon |
|------|----------|--------|
| 🟢 Green | CREATE | Plus |
| 🔵 Blue | UPDATE_KEY, UPDATE_DESCRIPTION | Edit, FileText |
| 🟣 Purple | UPDATE_TRANSLATION | Languages |
| 🟠 Orange | DELETE_TRANSLATION | Trash2 |
| 🔴 Red | DELETE | Trash2 |

## Change Display

### Creation (new value only)
```
Created:
┌────────────────────────┐
│ new value              │ (green background)
└────────────────────────┘
```

### Update (old and new value)
```
Old:
┌────────────────────────┐
│ old value              │ (red background, strikethrough)
└────────────────────────┘
New:
┌────────────────────────┐
│ new value              │ (green background)
└────────────────────────┘
```

### Deletion (old value only)
```
Deleted:
┌────────────────────────┐
│ deleted value          │ (red background, strikethrough)
└────────────────────────┘
```

## Features

### Automatic Updates
- When switching between keys, timeline automatically loads new key's history
- Uses `useEffect` with `keyId` dependency

### Relative Time
- Shows relative time instead of absolute dates
- Uses `date-fns` with locale support
- Examples: "2 hours ago", "yesterday", "3 days ago"

### Loading States
- Skeletons during loading (5 placeholders)
- Error message if failed to load
- Empty state if no history

### Language Labels
For translations shows language code:
```
○ Translation updated
  [en]  ← language code
  Old: ...
  New: ...
```

## Technical Details

### Components

#### `KeyManagement.tsx`
```tsx
<Tabs defaultValue="history">
  <TabsList>
    <TabsTrigger value="history">History</TabsTrigger>
    <TabsTrigger value="settings">Settings</TabsTrigger>
  </TabsList>
  
  <TabsContent value="history">
    <KeyLogsTimeline keyId={selectedKey.id} />
  </TabsContent>
  
  <TabsContent value="settings">
    {/* editing form */}
  </TabsContent>
</Tabs>
```

#### `KeyLogsTimeline.tsx`
```tsx
export const KeyLogsTimeline: FC<KeyLogsTimelineProps> = ({
  keyId,
  limit = 50,
}) => {
  const { data, loading, error, refetch } = useQuery(GET_KEY_LOGS, {
    variables: { keyId, limit },
  });
  
  // Timeline rendering...
}
```

### GraphQL Query

```graphql
query GetKeyLogs($keyId: String!, $limit: Int) {
  keyLogs(keyId: $keyId, limit: $limit) {
    id
    keyId
    userId
    action
    fieldName
    language
    oldValue
    newValue
    createdAt
  }
}
```

### Data Types

```typescript
interface KeyLog {
  id: number;
  keyId: number;
  userId: number | null;
  action: string;
  fieldName: string | null;
  language: string | null;
  oldValue: string | null;
  newValue: string | null;
  createdAt: string;
}
```

## Styling

### Timeline Line
- Vertical line left of icons
- Gray color (`bg-border`)
- Absolute positioning

### Action Icons
- Circular (32x32px)
- Colored background depending on action
- White icon inside
- z-index: 10 (above line)

### Value Blocks
- Monospace font for code
- Rounded corners
- Padding: 8px
- Border and background match type (old/new/deleted)

## Usage

1. **Select a key** in keys list
2. **History tab opens by default** with timeline
3. **View change history** - scroll down for older entries
4. **Switch to Settings** if you need to edit key

## Performance

- Default limit: 50 entries (adjustable)
- Lazy loading on scroll not implemented (future)
- Automatic refetch on key change

## Accessibility

- Color indication duplicated with icons
- Text labels for all actions
- Keyboard navigation works via standard Radix UI tabs

## Future Improvements

1. ✅ Infinite scroll for large history
2. ✅ Filters by action type
3. ✅ Filters by date
4. ✅ Display user name instead of ID
5. ✅ Ability to revert to previous version
6. ✅ Export history to file

## Example Workflow

### Scenario 1: Creating key with translation

1. User creates key `button.submit` with description and English translation "Submit"
2. Timeline shows 2 entries:
   - CREATE: key creation
   - UPDATE_TRANSLATION: translation addition

### Scenario 2: Changing translation

1. User changes translation from "Submit" to "Submit form"
2. Timeline shows UPDATE_TRANSLATION entry with both values
3. Old value shown strikethrough on red background
4. New value shown on green background

### Scenario 3: Renaming key

1. User changes key name from `button.submit` to `form.submit_button`
2. Timeline shows UPDATE_KEY entry
3. Both values displayed in monospace font

## Troubleshooting

### Logs not loading
- Check that backend is running
- Check project access rights
- Open DevTools and check GraphQL query

### Timeline empty
- Normal for new keys without changes
- Shows "No history yet" message

### Error "Failed to load history"
- Network or backend problem
- Check console for GraphQL errors
