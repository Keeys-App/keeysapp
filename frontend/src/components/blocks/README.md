# Blocks

Папка `blocks` содержит небольшие переиспользуемые UI-компоненты, которые можно использовать в разных частях приложения.

## Принципы

- **Универсальность**: компоненты должны быть достаточно общими для использования в разных контекстах
- **Небольшой размер**: это мелкие компоненты, не полноценные features
- **Независимость**: минимальная зависимость от бизнес-логики
- **Композиция**: легко комбинируются с другими компонентами

## Когда использовать `blocks` vs `ui`

- **`ui/`** - базовые UI-примитивы из Shadcn/ui (кнопки, инпуты, диалоги)
- **`blocks/`** - специфичные для проекта переиспользуемые компоненты (статусы, badges с логикой, etc.)

## Компоненты

### ProjectStatus

Компонент для отображения статуса проекта с иконкой и текстом.

```tsx
import { ProjectStatus } from '@/components/blocks';

<ProjectStatus status="active" />
<ProjectStatus status="draft" showIcon={false} />
```

### CheckboxCard

Красивая карточка с чекбоксом, заголовком и описанием. При активации подсвечивается синим.

```tsx
import { CheckboxCard } from '@/components/blocks';

<CheckboxCard
  id="is-plural"
  checked={isPlural}
  onCheckedChange={setIsPlural}
  title="Plural key"
  description="Enable plural forms for this key"
/>

// С иконкой в заголовке
<CheckboxCard
  id="autopilot"
  checked={autopilot}
  onCheckedChange={setAutopilot}
  title={
    <span className="flex items-center gap-1.5">
      <Sparkles className="h-3.5 w-3.5 text-primary" />
      Autopilot
    </span>
  }
  description="Automatically translate using AI"
  disabled={!hasDefaultValue}
/>
```

### ColorPicker

Компонент для выбора цвета из палитры с визуальной индикацией выбранного цвета.

```tsx
import { ColorPicker } from '@/components/blocks';

<ColorPicker 
  value={color} 
  onChange={setColor} 
/>
```

### Combobox

Универсальный компонент выпадающего списка с поиском. Можно использовать с любыми данными.

```tsx
import { Combobox } from '@/components/blocks';

const options = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Russian' },
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

Универсальный компонент для отображения состояния загрузки.

```tsx
import { LoadingState } from '@/components/blocks';

<LoadingState message="Loading project..." />
<LoadingState message="Loading..." className="min-h-[40vh]" />
```

### ErrorState

Компонент для отображения ошибок с возможностью добавления кнопки возврата.

```tsx
import { ErrorState } from '@/components/blocks';

<ErrorState 
  message="Error loading project"
  onBack={handleBack}
  backLabel="Back to Dashboard"
/>
```

### NotFoundState

Компонент для отображения состояния "не найдено" с возможностью добавления кнопки возврата.

```tsx
import { NotFoundState } from '@/components/blocks';

<NotFoundState 
  message="Project not found"
  onBack={handleBack}
  backLabel="Back to Dashboard"
/>
```

