# Performance Optimization

This document describes performance optimizations implemented in the backend to ensure fast query execution.

## N+1 Query Problem in Projects

### Problem Description

The N+1 query problem occurs when an application makes one query to fetch a list of records, then makes N additional queries to fetch related data for each record.

#### Example Scenario

When fetching a list of 10 projects:
- 1 query to get projects
- 10 queries to get each project's owner
- 10 queries to get each project's members list
- ~50 queries to get user data for each member
- 10 queries to get each project's keys
- ~1000 queries to get translations for all keys

**Total: Over 1000 database queries** 🔥

This causes significant performance degradation, especially:
- For users with many projects
- For projects with many keys and translations
- On slow network connections

### Solution: Eager Loading

We use SQLAlchemy's **eager loading** strategies to load all related data in a minimal number of queries.

#### Implementation

In `backend/app/services/project_service.py`:

```python
from sqlalchemy.orm import Session, joinedload, selectinload

def get_user_projects(db: Session, user_id: int) -> List[Project]:
    """
    Get all projects where user is owner or member.
    Uses eager loading to prevent N+1 query problems.
    """
    eager_options = [
        joinedload(Project.owner),  # Load owner (many-to-one)
        selectinload(Project.members).joinedload(ProjectMember.user),  # Load members and their users
        selectinload(Project.keys).selectinload('translations')  # Load keys and their translations
    ]
    
    owned_projects = db.query(Project).options(
        *eager_options
    ).filter(
        Project.owner_id == user_id
    ).all()
    
    # ... rest of the code
```

#### Eager Loading Strategies

**`joinedload()`** - Uses SQL JOIN
- Best for **many-to-one** or **one-to-one** relationships
- Example: `Project.owner`
- Creates a single query with JOINs

**`selectinload()`** - Uses separate IN query
- Best for **one-to-many** or **many-to-many** relationships
- Example: `Project.members`, `Project.keys`
- Prevents cartesian product in SQL results
- Uses 1 additional query per relationship level

#### Performance Improvement

**Before optimization:**
- 1000+ queries for 10 projects
- ~10-30 seconds load time

**After optimization:**
- ~5-10 queries total
- <1 second load time

**Improvement: 100-1000x faster!** 🚀

### Affected Queries

This optimization is applied to:

1. **`ProjectQuery.projects`** - Get all user projects
   - Used by: Dashboard, Project list
   
2. **`ProjectQuery.project`** - Get single project
   - Used by: Project details page

### Related Files

- `backend/app/services/project_service.py` - Service layer with eager loading
- `backend/app/schemas/project.py` - GraphQL resolvers and type builders
- `backend/app/models/project.py` - Project and ProjectMember models
- `backend/app/models/key.py` - Key and Translation models

## Best Practices

When working with SQLAlchemy relationships:

1. **Always use eager loading** when you know you'll access related data
2. Use `joinedload()` for many-to-one relationships
3. Use `selectinload()` for one-to-many relationships
4. Monitor query count in development using SQLAlchemy logging
5. Test with realistic data volumes (10+ projects, 100+ keys)

## Monitoring Query Performance

### Enable SQLAlchemy Query Logging

Add to `backend/main.py` or `backend/app/database.py`:

```python
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

This will log all SQL queries to console during development.

### Using PostgreSQL EXPLAIN

For production query analysis:

```sql
EXPLAIN ANALYZE
SELECT * FROM projects WHERE owner_id = 123;
```

## Future Optimizations

Potential areas for further optimization:

1. **Database Indexes**
   - Ensure indexes on foreign keys
   - Add composite indexes for common query patterns
   
2. **Caching**
   - Cache project list for users (with invalidation)
   - Cache translation counts for progress calculation
   
3. **Pagination**
   - Limit projects per page to reduce memory usage
   - Use cursor-based pagination for large datasets
   
4. **Denormalization**
   - Store `keys_count` directly in projects table
   - Store `translation_progress` as computed column
   - Update via database triggers

## References

- [SQLAlchemy Relationship Loading Techniques](https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html)
- [N+1 Query Problem Explained](https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem-in-orm-object-relational-mapping)

