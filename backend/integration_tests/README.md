# Integration Tests

Integration tests that verify entire system through HTTP API.

## Difference from Unit Tests

**Unit tests (`tests/`):**
- Test individual functions/classes
- Use in-memory SQLite
- Fast (~7 seconds)
- Run automatically: `pytest`

**Integration tests (`integration_tests/`):**
- Test real API
- Use real PostgreSQL DB
- Require running backend
- Run manually

## Usage

### 1. Start Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

### 2. Run Integration Tests

```bash
# In another terminal
cd backend
source venv/bin/activate
python integration_tests/<test_name>.py
```

## Available Tests

### check_error_safety.py
Verifies that technical errors NEVER shown to users.

```bash
python integration_tests/check_error_safety.py
```

**What it tests:**
- ✅ Duplicate email error is safe
- ✅ Wrong credentials error is safe
- ✅ User ID uses UUID (not integer)
- ✅ No SQL details in responses
- ✅ No stack traces
- ✅ No file paths

**Example output:**
```
============================================================
  TESTING ERROR SAFETY
  Verifying that technical errors never reach users
============================================================

✅ Backend is running

TEST: Register with duplicate email
User sees: 'Email already registered'
✅ PASS: Error message is safe for users

...

Total: 3/3 tests passed
🎉 ALL TESTS PASSED!
```

## Adding New Tests

1. Create file `test_<feature>.py` (WITHOUT `test_` prefix if you don't want pytest to pick it up)
2. Use `requests` for HTTP requests
3. Check real API responses
4. Make sure backend is running

Example:
```python
import requests

def test_my_feature():
    response = requests.post(
        "http://localhost:8000/graphql",
        json={"query": "..."}
    )
    data = response.json()
    # Checks...
```

## When to Run

- After error handling changes
- Before production deploy
- When adding new API endpoints
- When changing database schema

## CI/CD

For automation in CI/CD:

```yaml
# Example for GitHub Actions
- name: Run integration tests
  run: |
    cd backend
    python main.py &
    sleep 5
    python integration_tests/check_error_safety.py
```

---

*For unit tests see `tests/` folder*
