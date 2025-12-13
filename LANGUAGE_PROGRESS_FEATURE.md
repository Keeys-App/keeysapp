# Language Progress Bars Feature

## Overview
Added ability to display translation progress for each language separately on project page.

## Changes

### Backend

#### 1. New method in ProjectService (`backend/app/services/project_service.py`)
```python
@staticmethod
def get_language_progress(db: Session, project_id: int) -> dict:
    """
    Get translation progress for each language in the project.
    
    Returns:
        Dict mapping language code to progress percentage and counts
    """
```

Method efficiently calculates progress for each language using single SQL query:
- Gets total key count
- Counts completed translations for each language
- Calculates completion percentage

#### 2. New GraphQL type (`backend/app/schemas/project.py`)
```python
@strawberry.type
class LanguageProgressType:
    """
    GraphQL type for language translation progress.
    """
    code: str              # Language code (en, ru, de, etc.)
    progress: int          # Completion percentage (0-100)
    completed: int         # Number of completed translations
    total: int            # Total number of keys
```

#### 3. Updated ProjectType
Added new field:
```python
language_progress: List[LanguageProgressType]
```

#### 4. Updated build_project_type function
- Added parameter `db: Optional[Session]`
- When DB session available, calls `get_language_progress()`
- Creates `LanguageProgressType` objects for all configured languages
- If language has no translations, returns 0% progress

### Frontend

#### 1. Updated GraphQL query (`frontend/src/graphql/projects.ts`)
```graphql
languageProgress {
  code
  progress
  completed
  total
}
```

#### 2. Added new TypeScript type
```typescript
export interface LanguageProgress {
  code: string;
  progress: number;
  completed: number;
  total: number;
}
```

#### 3. Updated Project interface
```typescript
interface Project {
  // ... existing fields
  languageProgress: LanguageProgress[];
}
```

#### 4. Updated ProjectPage component (`frontend/src/pages/ProjectPage.tsx`)
"Languages" card now displays for each language:
- Flag and language name
- "Default" badge for default language
- Language code and locale
- **Progress bar** with completion percentage
- Number of completed translations out of total

## UI Changes

### Before:
```
🇬🇧 English                    [Default]
    en · en-US
```

### After:
```
🇬🇧 English [Default]          20%
    en · en-US
    [████░░░░░░░░░░░░░░░░] 
    5 of 25 translations
```

## Performance

- Uses efficient SQL query with GROUP BY
- Data loads only when detailed project information requested
- Doesn't affect project list speed
- All calculations performed database-side

## Compatibility

- ✅ Backward compatible with existing projects
- ✅ Correctly handles projects without translations (0%)
- ✅ Correctly handles new languages without translations
- ✅ All changes covered by TypeScript types

## Testing

Recommended tests:
1. Project without keys (all languages should show 0%)
2. Project with partially filled translations
3. Project with fully filled translations (100%)
4. Adding new language to existing project
5. Deleting translations and updating progress
