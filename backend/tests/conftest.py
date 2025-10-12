"""
Pytest configuration and fixtures for tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User  # Import User so table is registered
from app.models.project import Project, ProjectMember  # Import Project models
from app.models.team import Team, TeamMember  # Import Team models
from app.models.team_invitation import TeamInvitation  # Import TeamInvitation model
from app.models.project_access import ProjectAccess  # Import ProjectAccess model
from app.models.key import Key, Translation  # Import Key models
from app.services.team_service import TeamService


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """
    Create a test database engine.
    """
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create a test database session.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.
    """
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }


@pytest.fixture
def created_user(db_session, sample_user_data):
    """
    Create a user in the database for testing.
    """
    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=User.get_password_hash(sample_user_data["password"])
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user(created_user):
    """
    Alias for created_user for project tests.
    """
    return created_user


@pytest.fixture
def test_team(db_session, test_user):
    """
    Create a test team for the test user.
    """
    team = TeamService.create_team(
        db=db_session,
        owner_id=test_user.id,
        name="Test Team",
        description="Team for testing"
    )
    return team

