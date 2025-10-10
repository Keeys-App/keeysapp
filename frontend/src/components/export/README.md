# Export Components

This directory contains components related to the export functionality for translating project data into various formats.

## Components

### ExportContent

Main component that orchestrates the export functionality. Loads translation keys and manages the export process.

```tsx
import { ExportContent } from '@/components/export';

<ExportContent project={project} />
```

### ExportSettings

Settings panel for configuring export options including language selection, format, indentation, and sorting.

```tsx
import { ExportSettings } from '@/components/export';

<ExportSettings
  languages={projectLanguages}
  options={options}
  onOptionsChange={setOptions}
/>
```

### ExportPreview

Code preview component using shadcn/ui CodeBlock to display the generated export with syntax highlighting.

```tsx
import { ExportPreview } from '@/components/export';

<ExportPreview code={exportCode} filename={filename} />
```

## Utilities

### Export Formats

Utility functions for generating various export formats:

- **generateI18nFormat** - Generate i18n format (simple key-value JSON)
- **generateExport** - Main function to generate export based on format
- **getFileExtension** - Get file extension for export format
- **getExportFilename** - Generate filename for export

## Supported Formats

### i18n (JSON)

Simple key-value JSON format commonly used in i18n libraries:

```json
{
  "welcome": "Welcome!",
  "hello": "Hello"
}
```

## Features

- 📝 **Live Preview** - See export result in real-time with syntax highlighting
- ⚙️ **Configurable** - Choose language, indent size, and sorting options
- 💾 **Download** - Export to file with one click
- 🎨 **Beautiful UI** - Built with shadcn/ui components
- 🔄 **Format Support** - Currently supports i18n format, more coming soon

