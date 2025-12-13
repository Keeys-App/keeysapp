# Scripts / Utilities

Helper scripts for application management.

## Usage

All scripts run from `backend` folder:

```bash
cd backend
source venv/bin/activate
python scripts/<script_name>.py
```

## Available Scripts

### list_users.py
Shows list of all users in database.

```bash
python scripts/list_users.py
```

**Outputs:**
- User ID
- Email
- Username
- Status (active/inactive)
- Permissions (superuser)
- Creation date

### clear_users.py
Deletes all users from database.

```bash
python scripts/clear_users.py
```

**⚠️ Warning:** Script will ask for confirmation before deletion!

**When to use:**
- After changes in User model schema
- To clean test data
- When resetting application to initial state

---

*For DB migrations see `migrations/` folder*
