# Testing Guide

> [!check] Authentication system testing guide

## Overview

Comprehensive test suite for authentication system.

**Statistics:**
- ✅ 28 tests
- ✅ Coverage ~95%
- ✅ Execution time ~6 seconds

## Installation

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Testing dependencies:
- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- `pytest-asyncio` - Async support

## Running Tests

### All Tests
```bash
pytest
```

### With Verbose Output
```bash
pytest -v
```

### With Code Coverage
```bash
pytest --cov=app --cov-report=html
```

HTML report will be in `htmlcov/index.html`

### Specific File
```bash
pytest tests/test_models.py
```

### Specific Test
```bash
pytest tests/test_models.py::TestUserModel::test_password_hashing
```

### Only Fast Tests
```bash
pytest -m "not slow"
```

### Coverage Script
```bash
./run_tests.sh
```

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Fixtures and pytest configuration
├── test_models.py           # User model tests
├── test_services.py         # UserService tests
├── test_security.py         # JWT and security tests
└── README.md                # Test documentation
```

## Test Coverage

### test_models.py (10 tests)

#### Creation and Management
- ✅ `test_user_creation` - User creation
- ✅ `test_user_unique_email` - Email uniqueness
- ✅ `test_user_unique_username` - Username uniqueness

#### Passwords
- ✅ `test_password_hashing` - Password hashing
- ✅ `test_password_verification_success` - Successful verification
- ✅ `test_password_verification_failure` - Failed verification
- ✅ `test_long_password_truncation` - Truncation to 72 bytes
- ✅ `test_password_with_special_characters` - Special characters
- ✅ `test_unicode_password` - Unicode passwords
- ✅ `test_empty_password` - Empty passwords

### test_services.py (11 tests)

#### CRUD Operations
- ✅ `test_create_user` - Creation via service
- ✅ `test_get_user_by_email` - Search by email
- ✅ `test_get_user_by_email_not_found` - User not found
- ✅ `test_get_user_by_username` - Search by username
- ✅ `test_get_user_by_username_not_found` - Username not found
- ✅ `test_get_user_by_id` - Search by ID
- ✅ `test_get_user_by_id_not_found` - ID not found

#### Authentication
- ✅ `test_authenticate_user_success` - Successful authentication
- ✅ `test_authenticate_user_wrong_password` - Wrong password
- ✅ `test_authenticate_user_wrong_email` - Wrong email
- ✅ `test_authenticate_inactive_user` - Inactive user

### test_security.py (7 tests)

#### JWT Tokens
- ✅ `test_create_access_token` - Token creation
- ✅ `test_create_access_token_with_expiration` - Custom expiration
- ✅ `test_decode_valid_token` - Valid token decoding
- ✅ `test_decode_invalid_token` - Invalid token
- ✅ `test_decode_expired_token` - Expired token
- ✅ `test_token_contains_expiration` - Expiration presence
- ✅ `test_different_tokens_for_same_data` - Different tokens for same data

## Fixtures

### Database Fixtures

#### `db_engine`
Creates test DB engine (SQLite in-memory).

```python
@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
```

#### `db_session`
Creates test DB session.

```python
@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
```

### Data Fixtures

#### `sample_user_data`
Sample user data for tests.

```python
@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
```

#### `created_user`
Created user in DB.

```python
@pytest.fixture
def created_user(db_session, sample_user_data):
    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=User.get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

## Writing New Tests

### Test Template

```python
def test_feature_name(db_session, sample_user_data):
    """
    Description of what this test checks.
    """
    # Arrange - data preparation
    user_data = sample_user_data
    
    # Act - execute action
    result = some_function(user_data)
    
    # Assert - check result
    assert result is not None
    assert result.email == user_data["email"]
```

### Model Test Example

```python
def test_user_creation(db_session, sample_user_data):
    """
    Test creating a new user.
    """
    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=User.get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == sample_user_data["email"]
    assert user.is_active is True
```

### Service Test Example

```python
def test_authenticate_user_success(db_session, created_user, sample_user_data):
    """
    Test successful user authentication.
    """
    user = UserService.authenticate_user(
        db_session,
        sample_user_data["email"],
        sample_user_data["password"]
    )

    assert user is not None
    assert user.id == created_user.id
```

## Conventions

### Naming
- Files: `test_<feature>.py`
- Classes: `Test<Feature>`
- Methods: `test_<action>_<expected_result>`

### Test Structure
1. **Docstring** - test description
2. **Arrange** - data preparation
3. **Act** - execute action
4. **Assert** - check result

### Documentation
- Always add docstring
- Describe what is being tested
- Specify expected result

## Continuous Integration

### Pre-commit

Before commit run tests:

```bash
pytest
```

### CI/CD Pipeline

```yaml
# Example for GitHub Actions
- name: Run tests
  run: |
    cd backend
    source venv/bin/activate
    pytest --cov=app --cov-report=xml
```

## Code Coverage

### Current Coverage

```
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                           0      0   100%
app/core/config.py                       15      0   100%
app/core/security.py                     20      0   100%
app/models/__init__.py                    2      0   100%
app/models/base.py                        3      0   100%
app/models/user.py                       25      0   100%
app/services/user_service.py             45      0   100%
app/schemas/auth.py                      60      2    97%
---------------------------------------------------------
TOTAL                                   170      2    99%
```

### View Report

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### DB Problems

```python
# Problem: Table not created
# Solution: Make sure User is imported in conftest.py
from app.models.user import User  # Important!
```

### Fixture Problems

```python
# Problem: Fixture not found
# Solution: Check that conftest.py is in correct folder
tests/
├── conftest.py  # Should be here
└── test_models.py
```

### Slow Tests

```python
# Mark slow test
@pytest.mark.slow
def test_slow_operation():
    # Long operation
    pass

# Skip slow tests
pytest -m "not slow"
```

## Best Practices

1. **Isolation** - Each test is independent
2. **Readability** - Clear names and docstrings
3. **Coverage** - Aim for >90%
4. **Speed** - Tests should be fast
5. **Relevance** - Update when code changes

## Related Documents

- [[Authentication Setup]] - Authentication system
- [[Authentication Cheatsheet]] - Quick reference
- [[Quick Start]] - Quick start

---

*Updated: 2025-10-09*
