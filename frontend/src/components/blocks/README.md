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

