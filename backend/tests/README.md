# Backend Tests

Comprehensive test suite for the authentication system.

## Setup

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_models.py
```

### Run specific test
```bash
pytest tests/test_models.py::TestUserModel::test_password_hashing
```

### Run with verbose output
```bash
pytest -v
```

### Run only fast tests (skip slow ones)
```bash
pytest -m "not slow"
```

## Test Structure

```
tests/
├── __init__.py              # Package init
├── conftest.py              # Pytest fixtures and configuration
├── test_models.py           # User model tests
├── test_services.py         # UserService tests
├── test_security.py         # JWT and security tests
└── README.md                # This file
```

## Test Coverage

### test_models.py
- User creation
- Password hashing and verification
- Long password truncation (72 bytes limit)
- Special characters and Unicode in passwords
- Unique email and username constraints

### test_services.py
- User CRUD operations
- Authentication (success and failure cases)
- Inactive user handling
- Non-existent user handling

### test_security.py
- JWT token creation
- Token decoding and validation
- Expired token handling
- Invalid token handling

## Fixtures

### Database Fixtures
- `db_engine`: Test database engine (SQLite in-memory)
- `db_session`: Test database session
- `sample_user_data`: Sample user data for testing
- `created_user`: Pre-created user in database

## Writing New Tests

1. Create a new file `test_<feature>.py`
2. Use fixtures from `conftest.py`
3. Follow naming convention: `test_<action>_<expected_result>`
4. Add docstrings to describe what test does

Example:
```python
def test_user_creation(db_session, sample_user_data):
    """
    Test creating a new user.
    """
    # Your test code here
    pass
```

## Continuous Integration

Tests should be run in CI/CD pipeline before deployment.
All tests must pass before merging to main branch.

