# Database Enums and Migrations

## Overview

This guide explains how to work with PostgreSQL enum types in the application and how to properly add new enum values.

## Enum Value Format

**CRITICAL**: All enum values in the database must be in **UPPERCASE**.

### Example: KeyActionType

```python
class KeyActionType(str, enum.Enum):
    """Enum for different types of key actions that can be logged"""
    CREATE = "CREATE"
    UPDATE_KEY = "UPDATE_KEY"
    UPDATE_DESCRIPTION = "UPDATE_DESCRIPTION"
    UPDATE_TRANSLATION = "UPDATE_TRANSLATION"
    DELETE_TRANSLATION = "DELETE_TRANSLATION"
    DELETE = "DELETE"
    IMPORT = "IMPORT"
```

**Why uppercase?**
- All existing enum values in the database are uppercase
- PostgreSQL enums are case-sensitive
- Consistency across the codebase

## Adding New Enum Values

When you need to add a new value to an existing enum (e.g., `KeyActionType`):

### Step 1: Update Python Model

Update the enum class in the model file:

```python
# backend/app/models/key_log.py
class KeyActionType(str, enum.Enum):
    # ... existing values
    NEW_ACTION = "NEW_ACTION"  # Add in UPPERCASE
```

### Step 2: Update GraphQL Schema

Update the GraphQL enum to match:

```python
# backend/app/schemas/key.py
class KeyActionTypeEnum(str, enum.Enum):
    # ... existing values
    NEW_ACTION = "NEW_ACTION"  # Must match model
```

### Step 3: Update action_map in build_key_log_type

```python
# backend/app/schemas/key.py
def build_key_log_type(log) -> KeyLogType:
    action_map = {
        # ... existing mappings
        "NEW_ACTION": KeyActionTypeEnum.NEW_ACTION,
    }
```

### Step 4: Add Migration to auto_migrate.py

**ALWAYS add a migration function** to `backend/migrations/auto_migrate.py`:

```python
def migrate_add_new_enum_value_if_needed():
    """
    Add NEW_ACTION value to keyactiontype enum if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        with engine.connect() as connection:
            # Check if value already exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_enum 
                    WHERE enumlabel = 'NEW_ACTION' 
                    AND enumtypid = (
                        SELECT oid 
                        FROM pg_type 
                        WHERE typname = 'keyactiontype'
                    )
                );
            """))
            
            exists = result.scalar()
            
            if exists:
                logger.info("✅ Migration: NEW_ACTION already exists, skipping")
                return True
            
            logger.info("🔄 Migration: Adding NEW_ACTION to keyactiontype enum")
            
            # Add value to enum
            connection.execute(text("ALTER TYPE keyactiontype ADD VALUE 'NEW_ACTION'"))
            connection.commit()
            
            logger.info("✅ Migration: NEW_ACTION added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def run_all_migrations():
    migrations = [
        # ... existing migrations
        ("add_new_enum_value", migrate_add_new_enum_value_if_needed),
    ]
```

### Step 5: Update Frontend

Add the new action to frontend mappings:

```typescript
// frontend/src/components/key/KeyLogsTimeline.tsx

const actionLabels: Record<string, string> = {
  // ... existing labels
  NEW_ACTION: "New Action Label",
};

const actionIcons: Record<string, typeof History> = {
  // ... existing icons
  NEW_ACTION: SomeIcon,
};

const actionColors: Record<string, string> = {
  // ... existing colors
  NEW_ACTION: "bg-color-500",
};
```

## Testing

After adding a new enum value:

1. **Run the migration manually first** to test it:
   ```bash
   cd backend
   source venv/bin/activate
   PYTHONPATH=/path/to/backend python migrations/add_new_enum_value.py
   ```

2. **Verify in database**:
   ```python
   from sqlalchemy import text
   from app.database import get_db
   
   db = next(get_db())
   result = db.execute(text("""
       SELECT enumlabel 
       FROM pg_enum 
       WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'keyactiontype')
       ORDER BY enumsortorder;
   """))
   for row in result:
       print(row[0])
   ```

3. **Restart backend** - Code changes only take effect after restart

4. **Test the functionality** that uses the new enum value

## Common Mistakes

### ❌ DON'T: Use lowercase
```python
IMPORT = "import"  # Wrong! Database has uppercase values
```

### ✅ DO: Use uppercase
```python
IMPORT = "IMPORT"  # Correct!
```

### ❌ DON'T: Forget to update action_map
```python
# If you add IMPORT to enum but forget to update action_map,
# all IMPORT actions will be mapped to UPDATE_KEY (default)
```

### ✅ DO: Always update action_map
```python
action_map = {
    "IMPORT": KeyActionTypeEnum.IMPORT,  # Must add!
}
```

### ❌ DON'T: Skip the migration
If you add enum value to Python code but don't run migration, you'll get:
```
psycopg.errors.InvalidTextRepresentation: 
invalid input value for enum keyactiontype: "IMPORT"
```

### ✅ DO: Always add to auto_migrate.py
This ensures the migration runs automatically on deployment.

## Rollback

**Warning**: PostgreSQL does NOT support removing enum values in a simple way.

If you need to remove an enum value:
1. It must not be used in any existing rows
2. Requires recreating the enum type
3. Usually safer to keep deprecated values and just not use them

## Related Files

- **Models**: `backend/app/models/key_log.py`
- **GraphQL Schema**: `backend/app/schemas/key.py`
- **Services**: `backend/app/services/key_service.py`
- **Migrations**: `backend/migrations/auto_migrate.py`
- **Frontend**: `frontend/src/components/key/KeyLogsTimeline.tsx`

## Current Enum Values

As of this writing, `KeyActionType` has:
- `CREATE` - Key created
- `UPDATE_KEY` - Key name changed
- `UPDATE_DESCRIPTION` - Description changed
- `UPDATE_TRANSLATION` - Translation manually updated
- `DELETE_TRANSLATION` - Translation deleted
- `DELETE` - Key deleted
- `IMPORT` - Imported via batch import or project import

