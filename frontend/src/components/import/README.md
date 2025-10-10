# Import Components

This directory contains components related to the import functionality for loading translations from various file formats.

## Components

### ImportContent

Main component that orchestrates the import functionality with a 3-step workflow. Loads project data, parses imported content, and saves translations.

```tsx
import { ImportContent } from '@/components/import';

<ImportContent project={project} />
```

**Workflow Steps:**
1. **Upload** - Load translation files via drag & drop or paste
2. **Language Matching** - Match each file to a target language with auto-detection
3. **Preview & Import** - Review changes and import translations

### ImportUpload

File upload and copy-paste component with drag-and-drop support for **multiple files**.

```tsx
import { ImportUpload, type ImportFile } from '@/components/import';

<ImportUpload onFilesLoaded={handleFilesLoaded} />
```

**Features:**
- Multiple file support - load several files at once
- Drag and drop file upload
- Click to browse file selection
- Copy-paste text input
- File list management with remove option
- Tab interface for switching between methods

### ImportLanguageMatcher

Component for matching uploaded files to target languages with auto-detection from filenames.

```tsx
import { ImportLanguageMatcher, type FileLanguageMapping } from '@/components/import';

<ImportLanguageMatcher
  files={fileMappings}
  languages={projectLanguages}
  onLanguageChange={handleLanguageChange}
/>
```

**Features:**
- Auto-detects language from filename patterns (e.g., `app-en.json` → English)
- Visual indicators for detected vs manually selected languages
- Select dropdown for each file
- Confidence badges for auto-detected languages

### ImportSettings

Settings panel for configuring import options including language selection, format, and import strategy.

```tsx
import { ImportSettings } from '@/components/import';

<ImportSettings
  languages={projectLanguages}
  options={options}
  onOptionsChange={setOptions}
/>
```

**Options:**
- **Target Language** - Select which language to import
- **Format** - Choose file format (i18n JSON)
- **Import Strategy** - Merge or Replace existing translations

### ImportPreview

Preview component displaying parsed translations before import, showing which keys are new and which will be updated.

```tsx
import { ImportPreview } from '@/components/import';

<ImportPreview
  translations={parsedData.translations}
  error={parsedData.error}
  existingKeys={existingKeys}
/>
```

## Utilities

### Import Formats (`utils/importFormats.ts`)

Utility functions for parsing various import formats:

- **parseI18nFormat** - Parse i18n format (simple key-value JSON)
- **parseImport** - Main function to parse import based on format
- **detectFormat** - Auto-detect format from content

### Language Detector (`utils/languageDetector.ts`)

Utility functions for detecting languages from filenames:

- **detectLanguageFromFilename** - Detects language from filename patterns
- **getBestLanguageMatch** - Returns best language match or null

**Supported Patterns:**
- End patterns: `app-en.json`, `translations.ru.json`
- Middle patterns: `en-US.json`, `ru_RU.json`
- Start patterns: `en.translations.json`
- Full names: `english.json`, `russian.json`

**Examples:**
```typescript
getBestLanguageMatch('app-en.json') // 'en'
getBestLanguageMatch('translations.ru.json') // 'ru'
getBestLanguageMatch('de-DE.json') // 'de'
getBestLanguageMatch('french.json') // 'fr'
```

## Import Strategies

### Merge (Default)

Adds new translation keys and updates existing ones. Keeps translations not present in the import file.

**Use case:** Adding new translations or updating specific keys without affecting others.

### Replace

Replaces all translations for the selected language with the imported ones. Translations not in the import will remain unchanged.

**Use case:** Complete replacement of translations for a language.

## Supported Formats

### i18n (JSON)

Simple key-value JSON format commonly used in i18n libraries:

```json
{
  "welcome": "Welcome!",
  "hello": "Hello",
  "goodbye": "Goodbye"
}
```

## Features

- 📤 **Multiple Files** - Import multiple translation files at once
- 🎯 **Drag & Drop** - Easy file upload with drag and drop
- 📋 **Copy-Paste** - Paste JSON directly from clipboard
- 🤖 **Auto Language Detection** - Detects language from filename patterns
- 🗺️ **Language Matching** - Match each file to target language
- 🔍 **Format Detection** - Automatically detects file format
- 👀 **Live Preview** - See what will be imported before confirming
- 🏷️ **Smart Badges** - Visual indicators for new/updated keys
- ⚙️ **Flexible Strategies** - Choose merge or replace strategy
- ✅ **Validation** - Parse errors shown with helpful messages
- 🔄 **GraphQL Integration** - Updates cache automatically after import
- 🎯 **Multi-Step Workflow** - Clear 3-step process for importing

## Workflow

### Step 1: Upload Files
- Configure import settings (format, strategy)
- Upload one or more translation files via drag & drop or file browser
- Or paste JSON content directly

### Step 2: Match Languages
- Auto-detected languages shown for each file
- Manually select or confirm target language for each file
- Visual indicators show detection confidence

### Step 3: Preview & Import
- Review all translations that will be imported
- See which keys are new vs updates
- Click "Import Translations" to save to project

## Multi-File Import Example

You can import multiple language files at once:
```
app-en.json  → English
app-ru.json  → Russian  
app-de.json  → German
```

The system will:
1. Auto-detect languages from filenames
2. Show language matching interface
3. Parse all files
4. Import translations for each language separately

## Error Handling

- Invalid JSON format detection
- Non-object values validation
- Empty file/content warnings
- Import failure notifications with partial success counts

