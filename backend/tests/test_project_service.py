"""
Tests for ProjectService.
"""
import pytest
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.services.project_service import ProjectService


def test_create_project(db_session, test_user):
    """
    Test creating a project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="Test Project",
        description="Test Description",
        languages=[
            {"code": "en", "locale": "en-US"},
            {"code": "ru", "locale": "ru-RU"}
        ],
        color="#FF0000",
        status="active"
    )
    
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert len(project.languages) == 2
    assert project.languages[0]['code'] == "en"
    assert project.languages[1]['code'] == "ru"
    assert project.color == "#FF0000"
    assert project.status == "active"
    assert project.owner_id == test_user.id
    assert project.public_id is not None


def test_get_project_by_public_id(db_session, test_user):
    """
    Test getting a project by public ID.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="Test Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    found_project = ProjectService.get_project_by_public_id(
        db=db_session,
        public_id=str(project.public_id)
    )
    
    assert found_project is not None
    assert found_project.id == project.id
    assert found_project.name == project.name


def test_get_project_by_invalid_public_id(db_session):
    """
    Test getting a project with invalid public ID returns None.
    """
    project = ProjectService.get_project_by_public_id(
        db=db_session,
        public_id="invalid-uuid"
    )
    
    assert project is None


def test_get_user_projects_as_owner(db_session, test_user):
    """
    Test getting projects where user is owner.
    """
    project1 = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="Project 1",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    project2 = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="Project 2",
        languages=[{"code": "ru", "locale": "ru-RU"}]
    )
    
    projects = ProjectService.get_user_projects(db=db_session, user_id=test_user.id)
    
    assert len(projects) == 2
    project_ids = [p.id for p in projects]
    assert project1.id in project_ids
    assert project2.id in project_ids


def test_get_user_projects_as_member(db_session, test_user):
    """
    Test getting projects where user is member.
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Shared Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Add test_user as member
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role="editor"
    )
    db_session.add(member)
    db_session.commit()
    
    projects = ProjectService.get_user_projects(db=db_session, user_id=test_user.id)
    
    assert len(projects) == 1
    assert projects[0].id == project.id


def test_update_project(db_session, test_user):
    """
    Test updating a project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="Original Name",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    updated_project = ProjectService.update_project(
        db=db_session,
        public_id=str(project.public_id),
        user_id=test_user.id,
        name="Updated Name",
        description="New Description",
        languages=[
            {"code": "en", "locale": "en-US"},
            {"code": "ru", "locale": "ru-RU"},
            {"code": "de", "locale": "de-DE"}
        ]
    )
    
    assert updated_project is not None
    assert updated_project.name == "Updated Name"
    assert updated_project.description == "New Description"
    assert len(updated_project.languages) == 3
    assert updated_project.languages[0]['code'] == "en"
    assert updated_project.languages[1]['code'] == "ru"
    assert updated_project.languages[2]['code'] == "de"


def test_update_project_without_permission(db_session, test_user):
    """
    Test that non-owner cannot update project.
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Owner's Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # test_user tries to update
    updated_project = ProjectService.update_project(
        db=db_session,
        public_id=str(project.public_id),
        user_id=test_user.id,
        name="Hacked Name"
    )
    
    assert updated_project is None


def test_delete_project(db_session, test_user):
    """
    Test deleting a project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="To Delete",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    result = ProjectService.delete_project(
        db=db_session,
        public_id=str(project.public_id),
        user_id=test_user.id
    )
    
    assert result is True
    
    # Verify project is deleted
    deleted_project = ProjectService.get_project_by_public_id(
        db=db_session,
        public_id=str(project.public_id)
    )
    assert deleted_project is None


def test_delete_project_without_permission(db_session, test_user):
    """
    Test that non-owner cannot delete project.
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Owner's Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # test_user tries to delete
    result = ProjectService.delete_project(
        db=db_session,
        public_id=str(project.public_id),
        user_id=test_user.id
    )
    
    assert result is False


def test_check_project_access_as_owner(db_session, test_user):
    """
    Test checking access for project owner.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="My Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    has_access = ProjectService.check_project_access(
        db=db_session,
        project_id=project.id,
        user_id=test_user.id
    )
    
    assert has_access is True


def test_check_project_access_as_member(db_session, test_user):
    """
    Test checking access for project member.
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Shared Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Add test_user as member
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role="viewer"
    )
    db_session.add(member)
    db_session.commit()
    
    has_access = ProjectService.check_project_access(
        db=db_session,
        project_id=project.id,
        user_id=test_user.id
    )
    
    assert has_access is True


def test_check_project_access_no_permission(db_session, test_user):
    """
    Test checking access for user with no permission.
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Private Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    has_access = ProjectService.check_project_access(
        db=db_session,
        project_id=project.id,
        user_id=test_user.id
    )
    
    assert has_access is False


def test_can_user_edit_project_as_owner(db_session, test_user):
    """
    Test that owner can edit project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="My Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    can_edit = ProjectService.can_user_edit_project(
        db=db_session,
        project_id=project.id,
        user_id=test_user.id
    )
    
    assert can_edit is True


def test_can_user_edit_project_as_admin(db_session, test_user):
    """
    Test that admin member can edit project.
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Shared Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Add test_user as admin
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role="admin"
    )
    db_session.add(member)
    db_session.commit()
    
    can_edit = ProjectService.can_user_edit_project(
        db=db_session,
        project_id=project.id,
        user_id=test_user.id
    )
    
    assert can_edit is True


def test_can_user_edit_project_as_editor(db_session, test_user):
    """
    Test that editor member cannot edit project settings (only owner/admin can).
    """
    # Create another user who owns the project
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Shared Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Add test_user as editor
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user.id,
        role="editor"
    )
    db_session.add(member)
    db_session.commit()
    
    can_edit = ProjectService.can_user_edit_project(
        db=db_session,
        project_id=project.id,
        user_id=test_user.id
    )
    
    assert can_edit is False


def test_add_project_member(db_session, test_user):
    """
    Test adding a member to a project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="My Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Create another user to add as member
    new_member = User(
        email="member@test.com",
        username="member",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(new_member)
    db_session.commit()
    
    member = ProjectService.add_project_member(
        db=db_session,
        project_public_id=str(project.public_id),
        user_public_id=str(new_member.public_id),
        role="editor",
        added_by_user_id=test_user.id
    )
    
    assert member is not None
    assert member.project_id == project.id
    assert member.user_id == new_member.id
    assert member.role == "editor"


def test_add_project_member_without_permission(db_session, test_user):
    """
    Test that non-admin cannot add members.
    """
    # Create owner
    owner = User(
        email="owner@test.com",
        username="owner",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(owner)
    db_session.commit()
    
    project = ProjectService.create_project(
        db=db_session,
        owner_id=owner.id,
        name="Owner's Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Create user to add
    new_member = User(
        email="member@test.com",
        username="member",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(new_member)
    db_session.commit()
    
    # test_user (not owner/admin) tries to add member
    member = ProjectService.add_project_member(
        db=db_session,
        project_public_id=str(project.public_id),
        user_public_id=str(new_member.public_id),
        role="editor",
        added_by_user_id=test_user.id
    )
    
    assert member is None


def test_remove_project_member(db_session, test_user):
    """
    Test removing a member from a project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="My Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Create and add a member
    member_user = User(
        email="member@test.com",
        username="member",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(member_user)
    db_session.commit()
    
    member = ProjectMember(
        project_id=project.id,
        user_id=member_user.id,
        role="editor"
    )
    db_session.add(member)
    db_session.commit()
    
    # Remove member
    result = ProjectService.remove_project_member(
        db=db_session,
        project_public_id=str(project.public_id),
        user_public_id=str(member_user.public_id),
        removed_by_user_id=test_user.id
    )
    
    assert result is True
    
    # Verify member is removed
    has_access = ProjectService.check_project_access(
        db=db_session,
        project_id=project.id,
        user_id=member_user.id
    )
    assert has_access is False


def test_cannot_remove_owner(db_session, test_user):
    """
    Test that owner cannot be removed from project.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="My Project",
        languages=[{"code": "en", "locale": "en-US"}]
    )
    
    # Try to remove owner
    result = ProjectService.remove_project_member(
        db=db_session,
        project_public_id=str(project.public_id),
        user_public_id=str(test_user.public_id),
        removed_by_user_id=test_user.id
    )
    
    assert result is False

