# Pagination Fix

## Problem

After implementing lazy loading with pagination for keys, export and import components used hardcoded limit of 10,000 records. This created problems for projects with large number of keys.

## Solution

### Created new hook `useAllProjectKeys`

Hook automatically loads all project keys through pagination:

**Location**: `frontend/src/hooks/useAllProjectKeys.ts`

**Features**:
- 📄 Loads data in chunks of 100 records (PAGE_SIZE)
- 🔄 Automatically does fetchMore while `hasMore === true`
- 📊 Shows loading progress (how many loaded out of total)
- 🌐 Uses `network-only` for always fresh data
- ⚡ Efficiently works with any number of keys

**Usage example**:
```typescript
const { keys, loading, error, totalCount } = useAllProjectKeys(projectId);

// Shows progress during loading
if (loading) {
  return <LoadingState 
    message={`Loading... ${keys.length > 0 ? `(${keys.length} of ${totalCount})` : ''}`} 
  />;
}
```

### Updated Components

#### ✅ ExportContent.tsx
- Replaced `useQuery` with limit with `useAllProjectKeys`
- Shows loading progress for all keys
- Works with any number of keys

#### ✅ ImportContent.tsx
- Replaced `useQuery` with limit with `useAllProjectKeys`
- Shows loading progress for existing keys
- Correctly identifies conflicts for any number of keys

## Performance

- **Small projects (<100 keys)**: 1 request, instant loading
- **Medium projects (100-1000 keys)**: 2-10 requests, ~1-3 seconds
- **Large projects (1000+ keys)**: proportional to quantity, with visual progress

## Benefits

✅ No limit on number of keys  
✅ Efficient loading of only needed data  
✅ Visual progress for user  
✅ Reusable hook for other components  
✅ Automatic error handling

## Future Improvements

Can consider:
- Adding caching of hook results
- Using Web Workers for parsing large import files
- Streaming export for very large projects
