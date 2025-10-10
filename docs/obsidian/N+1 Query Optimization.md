# N+1 Query Optimization

## Problem

The GraphQL query `GetProjectKeys` was taking ~500ms due to the classic N+1 query problem.

### What is N+1 Query Problem?

When loading a list of entities with relationships, ORMs by default use lazy loading:
1. **1 query** to get all parent entities (keys)
2. **N queries** to get related entities for each parent (translations for each key)

Example: Loading 100 keys with translations = 1 + 100 = **101 queries**!

## Solution

Use SQLAlchemy's **eager loading** with `joinedload()` to load all data in a single JOIN query.

### Changes Made

#### 1. Updated `KeyService.get_project_keys()`

```python
# Before (N+1 problem)
keys = db.query(Key).filter(Key.project_id == project.id).order_by(Key.key).all()

# After (optimized)
keys = db.query(Key).options(
    joinedload(Key.translations)
).filter(Key.project_id == project.id).order_by(Key.key).all()
```

#### 2. Updated `KeyService.get_key_by_public_id()`

Added optional eager loading parameter:

```python
def get_key_by_public_id(db: Session, public_id: str, eager_load_translations: bool = True):
    query = db.query(Key)
    if eager_load_translations:
        query = query.options(joinedload(Key.translations))
    return query.filter(Key.public_id == uuid_obj).first()
```

#### 3. Updated `KeyService.batch_import_translations()`

```python
existing_keys = db.query(Key).options(
    joinedload(Key.translations)
).filter(Key.project_id == project.id).all()
```

## Performance Results

### Test Results (20 keys, 3 languages each = 60 translations)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total queries | ~23 | **6** | **↓ 74%** |
| Response time | ~500ms | **~50-100ms** | **↓ 80-90%** |

### Query Breakdown (After Optimization)

For `get_project_keys()` with 20 keys:
1. Get project by UUID
2. Check user access
3. Verify project existence
4. Check project membership
5. Verify project again
6. **Get keys with translations** (single JOIN query)

Total: **6 queries** regardless of number of keys!

### Performance Tests

Created comprehensive performance tests in `tests/test_key_performance.py`:

```python
def test_get_project_keys_no_n_plus_one(self, db_session, project_with_keys):
    """
    Verifies that loading 20 keys with translations uses <= 10 queries
    (without optimization it would be 23+ queries)
    """
```

## When to Use Eager Loading

### ✅ Use `joinedload()` when:
- You KNOW you'll access the related data
- Loading a collection of entities (list of keys)
- Data is needed immediately in the response

### ❌ Don't use eager loading when:
- Relationship might not be accessed
- Loading single entity where relationship is optional
- Very large relationships (thousands of related records)

## Related Documentation

- [SQLAlchemy Eager Loading](https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html)
- [Performance Optimization](./Performance%20Optimization.md)
- [Testing Guide](./Testing%20Guide.md)

## Monitoring

To monitor query performance in production:

1. Enable SQLAlchemy query logging:
```python
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

2. Use the query counter helper in tests to verify query counts

3. Monitor API response times for the `/graphql` endpoint

## Future Optimizations

Consider these additional optimizations:

1. **Pagination** - Add limit/offset for projects with thousands of keys
2. **Caching** - Cache project keys for read-heavy operations
3. **Database Indexes** - Verify indexes on `project_id`, `key_id`, `language`
4. **GraphQL DataLoader** - For more complex nested queries

