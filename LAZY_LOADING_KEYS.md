# Lazy Loading for Keys List

## Overview

Implemented lazy loading feature for translation keys with pagination at GraphQL level and infinite scroll on frontend. This significantly improves performance when working with projects containing large number of keys.

## Backend Changes

### 1. GraphQL Schema (`backend/app/schemas/key.py` and `backend/app/schemas/graphql.py`)

#### New type `KeysConnection`
```python
@strawberry.type
class KeysConnection:
    """
    Paginated response type for keys.
    """
    keys: List[KeyType]
    total_count: int
    has_more: bool
```

#### Updated Query `project_keys`
```python
@strawberry.field
def project_keys(
    self, 
    info: Info, 
    project_id: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 50
) -> KeysConnection
```

**Parameters:**
- `project_id` - project UUID
- `offset` - number of keys to skip (default: 0)
- `limit` - maximum number of returned keys (default: 50, maximum: 200)

**Returns:**
- `keys` - list of keys
- `total_count` - total number of keys in project
- `has_more` - flag indicating additional keys available for loading

#### Registration in Root Schema (`backend/app/schemas/graphql.py`)
```python
from app.schemas.key import KeyQuery, KeyMutation, KeyType, KeysConnection, ActivityLogType

@strawberry.type
class Query:
    # Include key queries
    project_keys: KeysConnection = strawberry.field(resolver=KeyQuery.project_keys)
```

**Important:** Return type must be `KeysConnection`, not `List[KeyType]`!

### 2. Key Service (`backend/app/services/key_service.py`)

#### New method `get_project_keys_paginated`
```python
@staticmethod
def get_project_keys_paginated(
    db: Session, 
    project_public_id: str, 
    user_id: int,
    offset: int = 0,
    limit: int = 50
) -> Optional[Dict[str, any]]
```

**Features:**
- Uses SQL `OFFSET` and `LIMIT` for efficient pagination
- Eager loading of translations via `joinedload` to prevent N+1 problem
- Returns both key list and total count
- Checks user access rights to project

## Frontend Changes

### 1. GraphQL Query (`frontend/src/graphql/keys.ts`)

#### Updated query `GET_PROJECT_KEYS`
```graphql
query GetProjectKeys($projectId: String!, $offset: Int, $limit: Int) {
  projectKeys(projectId: $projectId, offset: $offset, limit: $limit) {
    keys {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
    totalCount
    hasMore
  }
}
```

### 2. KeyList Component (`frontend/src/components/key/KeyList.tsx`)

#### Main changes:

**Constants:**
```typescript
const PAGE_SIZE = 50; // Page size for loading
```

**State:**
```typescript
const [isLoadingMore, setIsLoadingMore] = useState(false);
```

**Function for loading additional keys:**
```typescript
const loadMoreKeys = useCallback(async () => {
  if (isLoadingMore || !hasMore) {
    return;
  }

  setIsLoadingMore(true);
  try {
    await fetchMore({
      variables: {
        offset: keys.length,
        limit: PAGE_SIZE,
      },
      updateQuery: (prev, { fetchMoreResult }) => {
        // Merge previous and new keys
        return {
          projectKeys: {
            ...fetchMoreResult.projectKeys,
            keys: [
              ...(prev.projectKeys?.keys || []),
              ...(fetchMoreResult.projectKeys?.keys || []),
            ],
          },
        };
      },
    });
  } finally {
    setIsLoadingMore(false);
  }
}, [fetchMore, keys.length, hasMore, isLoadingMore]);
```

**Automatic loading on scroll:**
```typescript
useEffect(() => {
  const [lastItem] = [...virtualizer.getVirtualItems()].reverse();

  if (!lastItem) {
    return;
  }

  if (
    lastItem.index >= keys.length - 1 &&
    hasMore &&
    !isLoadingMore &&
    !loading
  ) {
    loadMoreKeys();
  }
}, [
  hasMore,
  loadMoreKeys,
  keys.length,
  isLoadingMore,
  loading,
  virtualizer.getVirtualItems(),
]);
```

**UI indicators:**
- Loading skeleton when loading additional keys
- Message "Loaded all {totalCount} keys" when all keys are loaded

## Benefits

### Performance
- **Reduced initial load time**: Instead of loading all keys at once, only first page loads (50 keys)
- **Less DB load**: SQL queries with LIMIT execute faster
- **Less client memory**: Only visible part of list renders in DOM thanks to virtualization

### Scalability
- **Support for large projects**: Projects with thousands of keys now load instantly
- **Adaptive loading**: Keys load as needed
- **Maximum page size limit**: Protection against abuse (max 200 keys per request)

### UX
- **Smooth scrolling**: Virtualization + lazy loading work together
- **Visual feedback**: Loading indicators and counter of loaded keys
- **No unnecessary waiting**: User can start working immediately after first page loads

## Compatibility

- Old method `get_project_keys` preserved for backward compatibility
- Apollo Client caching works correctly with paginated queries
- Virtualization (@tanstack/react-virtual) continues to work with dynamic list

## Technical Details

### Backend
- **ORM**: SQLAlchemy with eager loading
- **GraphQL**: Strawberry
- **Security**: Parameter validation, access checks, maximum limit restriction

### Frontend
- **Apollo Client**: `fetchMore` for data loading
- **React Hooks**: `useCallback`, `useEffect` for optimization
- **Virtualization**: @tanstack/react-virtual for rendering only visible elements

## Testing

### Functionality check:
1. Open project with large number of keys (>50)
2. Verify that only first 50 keys load
3. Scroll list down
4. Check automatic loading of next page
5. Verify loading indicator display
6. Wait for all keys to load and check final message

### Performance check:
```bash
# Backend tests (if available)
cd backend
python -m pytest tests/test_key_performance.py

# Check GraphQL queries
# Open GraphQL Playground and execute:
query {
  projectKeys(projectId: "...", offset: 0, limit: 50) {
    keys { id key }
    totalCount
    hasMore
  }
}
```

## Custom Scrollbar

### Problem
When using lazy loading, native scrollbar changes size as new elements load, creating poor UX - user doesn't understand real element count.

### Solution
Implemented custom scrollbar (`CustomScrollbar` component) that:

1. **Shows real proportions**: Scrollbar size and position calculated based on `totalCount`, not loaded elements
2. **Progress indicator**: Inside handle, loading progress displays (blue color fills proportionally to loaded elements)
3. **Loading percentage**: Text indicator of loaded keys percentage displays
4. **Interactivity**: Supports track click and drag & drop of handle

### Implementation Features

**Virtualization with totalCount:**
```typescript
const virtualizer = useVirtualizer({
  count: totalCount || keys.length, // Use totalCount, not keys.length
  // ...
});
```

**Rendering unloaded elements:**
```typescript
const key = keys[virtualItem.index];

// If key not yet loaded, show skeleton
if (!key) {
  return <KeySkeleton />;
}
```

**Hiding native scrollbar:**
```css
.hide-scrollbar {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}
.hide-scrollbar::-webkit-scrollbar {
  display: none; /* Chrome, Safari and Opera */
}
```

### Components

- **`CustomScrollbar`** (`frontend/src/components/ui/custom-scrollbar.tsx`) - Custom scrollbar
- **Updated** `KeyList.tsx` - Integration of custom scrollbar and virtualization with totalCount

## Possible Improvements

1. ~~**Custom scrollbar with correct proportions**~~ ✅ Implemented
2. **Preloading**: Start loading next page in advance (at 80% of list) - partially implemented (loads 10 elements before end)
3. **Service Worker caching**: For offline support
4. **Virtual scrolling with bidirectional loading**: Loading in both directions when scrolling
5. **Search and filtering**: Adapt pagination to work with filters
6. **Metrics**: Add analytics to track page load times

## Migration

Changes are backward compatible. If old code calls `projectKeys` without `offset` and `limit` parameters, they will use default values (0 and 50).

Update doesn't require database migration - all changes are at logic level only.

**After updating code, backend server must be restarted** for GraphQL schema to update with new `KeysConnection` type.
