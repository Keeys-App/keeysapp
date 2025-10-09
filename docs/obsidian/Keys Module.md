# Keys Module

## Overview

The Keys module manages translation keys and their translations across different languages within projects. Each key belongs to a project and can have multiple translations in different languages.

## Database Schema

### Keys Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Internal primary key |
| public_id | UUID | Public identifier for API |
| key | String(500) | Translation key (e.g., "button.submit") |
| description | Text | Optional description for translators |
| project_id | Integer | Foreign key to projects table |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Update timestamp |

**Constraints:**
- Unique constraint on (project_id, key) - ensures key uniqueness within a project

### Translations Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| key_id | Integer | Foreign key to keys table |
| language | String(10) | Language code (e.g., "en", "ru", "de") |
| value | Text | Translated text |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Update timestamp |

**Constraints:**
- Unique constraint on (key_id, language) - ensures one translation per language per key

## Backend Structure

### Models

- **Key** (`app/models/key.py`): Main key model with relationship to project and translations
- **Translation** (`app/models/key.py`): Translation model with relationship to key

### Services

**KeyService** (`app/services/key_service.py`) provides methods for:

- `create_key()` - Create a new translation key
- `get_key_by_public_id()` - Get key by UUID
- `get_project_keys()` - Get all keys for a project
- `update_key()` - Update key name or description
- `delete_key()` - Delete key and all translations
- `set_translation()` - Set or update a translation
- `delete_translation()` - Delete a specific translation

### GraphQL API

**Queries:**
- `projectKeys(projectId: String!)` - Get all keys for a project
- `key(id: String!)` - Get a specific key by ID

**Mutations:**
- `createKey(input: CreateKeyInput!)` - Create new key
- `updateKey(input: UpdateKeyInput!)` - Update existing key
- `deleteKey(id: String!)` - Delete key
- `setTranslation(input: SetTranslationInput!)` - Set/update translation
- `deleteTranslation(input: DeleteTranslationInput!)` - Delete translation

**Types:**

```graphql
type KeyType {
  id: String!
  key: String!
  description: String
  translations: [TranslationType!]!
  createdAt: DateTime!
  updatedAt: DateTime
}

type TranslationType {
  language: String!
  value: String!
  createdAt: DateTime!
  updatedAt: DateTime
}
```

## Frontend Structure

### Types

`src/types/translationKey.ts` defines TypeScript interfaces:
- `TranslationKey` - Main key type
- `Translation` - Translation type
- `CreateKeyInput` - Input for creating keys
- `UpdateKeyInput` - Input for updating keys
- `SetTranslationInput` - Input for setting translations

### GraphQL Operations

`src/graphql/keys.ts` exports:
- `GET_PROJECT_KEYS` - Query for project keys
- `GET_KEY` - Query for single key
- `CREATE_KEY` - Mutation to create key
- `UPDATE_KEY` - Mutation to update key
- `DELETE_KEY` - Mutation to delete key
- `SET_TRANSLATION` - Mutation to set translation
- `DELETE_TRANSLATION` - Mutation to delete translation

### Components

**KeyList** (`src/components/key/KeyList.tsx`):
- Displays all keys for a project
- Shows translations in simple format:
  ```
  {key}
  ----
  {language} {translation}
  {language} {translation}
  ```
- Handles loading and error states

## Usage

### Creating a Key

```typescript
import { useMutation } from '@apollo/client';
import { CREATE_KEY } from '@/graphql/keys';

const [createKey] = useMutation(CREATE_KEY);

await createKey({
  variables: {
    input: {
      projectId: "project-uuid",
      key: "button.submit",
      description: "Submit button label",
      translations: {
        en: "Submit",
        ru: "Отправить"
      }
    }
  }
});
```

### Displaying Keys

```typescript
import { KeyList } from '@/components/key';

function ProjectPage() {
  return <KeyList projectId={projectId} />;
}
```

### Setting a Translation

```typescript
import { useMutation } from '@apollo/client';
import { SET_TRANSLATION } from '@/graphql/keys';

const [setTranslation] = useMutation(SET_TRANSLATION);

await setTranslation({
  variables: {
    input: {
      keyId: "key-uuid",
      language: "de",
      value: "Absenden"
    }
  }
});
```

## Migration

To create the database tables, run:

```bash
cd backend
source venv/bin/activate
python migrations/create_keys_tables.py
```

This will create:
- `keys` table
- `translations` table
- All necessary constraints and indexes

## Security

- All operations require authentication
- Users can only access keys from projects they own or are members of
- Only project owners and admin members can create/update/delete keys
- All IDs exposed via API are UUIDs (not internal IDs)

## Future Enhancements

- Bulk import/export of keys and translations
- Translation history and versioning
- Translation status tracking (untranslated, draft, approved)
- Translation suggestions and auto-translation
- Search and filtering in UI
- Inline editing of translations
- Translation memory and reuse
- Pluralization support
- Context variables/placeholders in translations

