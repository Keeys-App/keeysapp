# Keys Search Feature

## Overview

Implemented translation key search feature with support for searching by key name, description and translation values.

## Architecture

### Backend

#### GraphQL Schema (`backend/app/schemas/key.py`)

Added `search` parameter to `project_keys` query:

```python
@strawberry.field
def project_keys(
    self, 
    info: Info, 
    project_id: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 50,
    search: Optional[str] = None
) -> KeysConnection:
```

#### Service Layer (`backend/app/services/key_service.py`)

Method `get_project_keys_paginated` updated to support search:

```python
def get_project_keys_paginated(
    db: Session, 
    project_public_id: str, 
    user_id: int,
    offset: int = 0,
    limit: int = 50,
    search: Optional[str] = None
) -> Optional[Dict[str, any]]:
```

**Search performed by:**
- Key name (`key.key`)
- Key description (`key.description`)
- Translation values (`translation.value`)

Uses case-insensitive search via `ilike()` with pattern `%search%`.

### Frontend

#### Store (`frontend/src/stores/useKeysSearchStore.ts`)

Created Zustand store for search state management:

```typescript
interface KeysSearchState {
  search: string;
  setSearch: (search: string) => void;
  clearSearch: () => void;
}
```

#### GraphQL Query (`frontend/src/graphql/keys.ts`)

Updated `GET_PROJECT_KEYS` query:

```graphql
query GetProjectKeys($projectId: String!, $offset: Int, $limit: Int, $search: String) {
  projectKeys(projectId: $projectId, offset: $offset, limit: $limit, search: $search) {
    # ...
  }
}
```

#### Components

##### `KeysSearch` (`frontend/src/components/key/KeysSearch.tsx`)

- Input field with debounce (300ms)
- Clear search button (X icon)
- Results count display
- Integration with `useKeysSearchStore`

Features:
- Local state for instant UI responsiveness
- Debounce to minimize server requests
- Synchronization with global store

##### `KeyList` (`frontend/src/components/key/KeyList.tsx`)

Updated to:
- Use `search` parameter from store
- Clear cache on search query change
- Pass `search` to GraphQL queries (initial + fetchMore)

##### `EmptySearchResults` (`frontend/src/components/key/EmptySearchResults.tsx`)

New component for displaying empty state when no search results:
- Displays search query text
- Clear search button
- Uses `Empty` component from UI library

##### `KeyControls` (`frontend/src/components/key/KeyControls.tsx`)

Updated to pass `totalCount` to `KeysSearch` for results count display.

## Security

### 🚨 CRITICAL: Error Handling

**Problem:** On errors SQL details could be exposed to users, violating project RULE #1.

**Solution:**
1. **Backend**: All errors are caught and logged with full details, but users only receive `DatabaseError` with generic message: "An error occurred. Please try again later."
2. **Technical details** (SQL queries, stack traces, table names) are logged only on server and NEVER passed to client
3. **Frontend**: Uses `getUserFriendlyErrorMessage()` for additional filtering

```python
# Backend error handling (backend/app/schemas/key.py)
except Exception as e:
    # Log technical details (only in server logs)
    logger.error(f"Error in project_keys query: {type(e).__name__}: {str(e)}", exc_info=True)
    # Raise user-friendly error (user sees this)
    raise DatabaseError(internal_message=f"Error loading keys: {type(e).__name__}: {str(e)}")
```

### SQL Query Optimization

Used subquery approach to avoid issues with `DISTINCT` on JSON fields:
- First get key IDs via subquery with `Translation.key_id.distinct()`
- Then load full key data by these IDs
- This solves "could not identify an equality operator for type json" problem

## Usage

### For Users

1. On project keys page enter text in search field
2. Results will update automatically after 300ms
3. Number of found results is displayed
4. Click X to clear search

### For Developers

**Backend:**
```python
# Search is performed automatically in KeyService.get_project_keys_paginated
# when passing search parameter
```

**Frontend:**
```typescript
import { useKeysSearchStore } from '@/stores';

const { search, setSearch, clearSearch } = useKeysSearchStore();

// Set search query
setSearch('button');

// Clear search
clearSearch();
```

## Performance

- **Debounce**: 300ms to minimize requests
- **Cache invalidation**: Cache cleared on search query change
- **Database indexing**: Uses existing index on `keys.key`
- **Lazy loading**: List virtualization works with search results

## Limitations

- Case-insensitive search
- Minimum query length: no restriction (can search by 1 character)
- Search performed by full substring match (LIKE %search%)

## Possible Improvements

1. **Full-text search**: Use PostgreSQL Full-Text Search for more relevant search
2. **Filters**: Add filters by tags, translation status, languages
3. **Search history**: Save recent search queries
4. **Highlighting**: Highlight found matches in results
5. **Sorting**: Sort results by relevance

## Testing

### Backend

Comprehensive search tests implemented in `backend/tests/test_key_search.py`:

```bash
# Run all search tests
cd backend
source venv/bin/activate
python -m pytest tests/test_key_search.py -v
```

**Test Coverage:**

✅ **12 tests** cover following scenarios:

1. **`test_search_by_key_name`** - Search by key name (e.g., "button")
2. **`test_search_by_description`** - Search by key description
3. **`test_search_by_translation_value`** - Search by translation value (any language)
4. **`test_search_case_insensitive`** - Case-insensitive search check
5. **`test_search_partial_match`** - Partial match (e.g., "err" finds "error")
6. **`test_search_no_results`** - Search with no results
7. **`test_search_with_pagination`** - Search results pagination
8. **`test_search_empty_query`** - Empty query returns all keys
9. **`test_search_whitespace_query`** - Whitespace-only query
10. **`test_search_multiple_languages`** - Search in different languages
11. **`test_search_unauthorized_user`** - Access check
12. **`test_search_with_special_characters`** - Search with special characters

**Results:**
```
12 passed in 2.52s ✅
```

### Frontend

Frontend tests can be added for components:

```bash
# TODO: Add E2E tests for search UI
yarn test KeysSearch
```

**Test scenarios for frontend:**
- Debounce works (300ms delay)
- Loading indicator shows on input
- Results counter updates
- Clear button works
- State syncs with store

## Loading Indicator

### UX Improvements

Instead of showing skeletons during search, loading indicator is displayed **in the search field itself**:

- ⚡ **Instant feedback**: spinner appears when typing
- 🔄 **Two states**: 
  - `isTyping` - user is typing (300ms debounce)
  - `isLoading` - GraphQL query executing
- 🎯 **Minimalist UI**: no distracting skeletons
- 👁️ **Always visible**: indicator in search field is in view

```typescript
// KeysSearch.tsx
const showLoading = isLoading || isTyping;

<InputGroupButton>
  {showLoading ? <Spinner /> : <Search />}
</InputGroupButton>
```

**Display logic:**
- Skeletons shown **only** on first page load
- During search: only spinner in search field + list update
- If list already loaded: smooth replacement without skeletons

## Related Files

### Backend
- `backend/app/services/key_service.py` - Search logic with subqueries
- `backend/app/schemas/key.py` - GraphQL resolver with error handling
- `backend/tests/test_key_search.py` - **12 tests** for search

### Frontend
- `frontend/src/stores/useKeysSearchStore.ts` - Zustand store for search state
- `frontend/src/components/key/KeysSearch.tsx` - Search field with debounce and indicator
- `frontend/src/components/key/KeyList.tsx` - Virtualized list with search
- `frontend/src/components/key/EmptySearchResults.tsx` - Empty state for search
- `frontend/src/components/key/KeyControls.tsx` - Keys control panel
- `frontend/src/graphql/keys.ts` - GraphQL queries
