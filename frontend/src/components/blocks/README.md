# Blocks

The `blocks` folder contains small reusable UI components that can be used in different parts of the application.

## Principles

- **Universality**: components should be general enough for use in different contexts
- **Small size**: these are small components, not full features
- **Independence**: minimal dependency on business logic
- **Composition**: easily combined with other components

## When to Use `blocks` vs `ui`

- **`ui/`** - basic UI primitives from Shadcn/ui (buttons, inputs, dialogs)
- **`blocks/`** - project-specific reusable components (statuses, badges with logic, etc.)

## Components

### ProjectStatus

Component for displaying project status with icon and text.

```tsx
import { ProjectStatus } from '@/components/blocks';

<ProjectStatus status="active" />
<ProjectStatus status="draft" showIcon={false} />
```

### CheckboxCard

Beautiful card with checkbox, title and description. Highlights blue when active.

```tsx
import { CheckboxCard } from '@/components/blocks';

<CheckboxCard
  id="is-plural"
  checked={isPlural}
  onCheckedChange={setIsPlural}
  title="Plural key"
  description="Enable plural forms for this key"
/>

// With icon, purple theme and tooltip when disabled (for AI features)
<CheckboxCard
  id="autopilot"
  checked={autopilot}
  onCheckedChange={setAutopilot}
  variant="purple"
  title={
    <span className="flex items-center gap-1.5">
      <Sparkles className="h-3.5 w-3.5 text-purple-600" />
      Autopilot
    </span>
  }
  description="Automatically translate using AI"
  disabled={!hasDefaultValue}
  disabledReason="Enter a default value first to enable autopilot"
/>
```

### ColorPicker

Component for selecting color from palette with visual indication of selected color.

```tsx
import { ColorPicker } from '@/components/blocks';

<ColorPicker 
  value={color} 
  onChange={setColor} 
/>
```

### Combobox

Universal dropdown component with search. Can be used with any data.

```tsx
import { Combobox } from '@/components/blocks';

const options = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
];

<Combobox 
  options={options}
  value={selectedValue}
  onSelect={setSelectedValue}
  placeholder="Select language..."
  searchPlaceholder="Search languages..."
/>
```

### LoadingState

Universal component for displaying loading state.

```tsx
import { LoadingState } from '@/components/blocks';

<LoadingState message="Loading project..." />
<LoadingState message="Loading..." className="min-h-[40vh]" />
```

### ErrorState

Component for displaying errors with option to add back button.

```tsx
import { ErrorState } from '@/components/blocks';

<ErrorState 
  message="Error loading project"
  onBack={handleBack}
  backLabel="Back to Dashboard"
/>
```

### NotFoundState

Component for displaying "not found" state with option to add back button.

```tsx
import { NotFoundState } from '@/components/blocks';

<NotFoundState 
  message="Project not found"
  onBack={handleBack}
  backLabel="Back to Dashboard"
/>
```
