# Migrations / Database Migrations

Scripts for database schema migration.

## Usage

All migrations run from `backend` folder:

```bash
cd backend
source venv/bin/activate
python migrations/<migration_name>.py
```

## Available Migrations

### create_projects_tables.py
Creates tables for projects module.

```bash
python migrations/create_projects_tables.py
```

**What it does:**
1. Creates `projects` table (id, public_id, name, description, languages, color, status, owner_id, timestamps)
2. Creates `project_members` table (id, project_id, user_id, role, created_at)
3. Sets up foreign key constraints

**When to use:**
- On first installation of projects module
- If tables exist, will offer to recreate them

**⚠️ Warning:** 
- Recreating tables will delete all project data!

### migrate_add_public_id.py
Adds `public_id` column (UUID) to users table.

```bash
python migrations/migrate_add_public_id.py
```

**What it does:**
1. Adds `public_id` column of UUID type
2. Generates UUIDs for all existing users
3. Makes column NOT NULL
4. Adds UNIQUE constraint
5. Creates index for performance

**When to use:**
- When transitioning from integer IDs to UUIDs
- Once after code update

**⚠️ Warning:** 
- Make database backup before running!
- Script will ask for confirmation

### recreate_tables.py
Drops and recreates all database tables.

```bash
python migrations/recreate_tables.py
```

**⚠️ DANGEROUS:** Deletes ALL data!

**What it does:**
1. Drops all tables (`DROP TABLE`)
2. Recreates tables with current schema

**When to use:**
- In development environment
- When need to completely reset DB
- For critical schema changes

**Requires confirmation:** Need to enter `DELETE ALL DATA`

### add_default_language.py
Adds `default_language` column to projects table.

```bash
python migrations/add_default_language.py
```

**What it does:**
1. Adds `default_language` column of VARCHAR(10) type
2. Column is nullable, can be NULL for existing projects

**When to use:**
- When upgrading to version with default language support
- Once after code update

## Migration History

| Date | Migration | Description |
|------|----------|----------|
| 2025-10-10 | add_default_language | Added default language for projects |
| 2025-10-09 | migrate_add_public_id | Added UUID for security |
| 2025-10-09 | create_projects_tables | Created projects module |

## Best Practices

1. **Backup** - Always backup before migration
2. **Testing** - Test migrations on DB copy
3. **Rollback** - Have rollback plan
4. **Documentation** - Document each migration
5. **Production** - Be especially careful in production

## Future

In future recommended to switch to Alembic for automatic migrations:

```bash
pip install alembic
alembic init alembic
```

---

*For management utilities see `scripts/` folder*
