"""
Tests for translation progress calculation.
"""
import pytest
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.key import Key, Translation
from app.models.user import User
from app.services.project_service import ProjectService
from app.services.key_service import KeyService
from app.schemas.project import build_project_type


def test_translation_progress_calculation(db_session: Session):
    """
    Test that translation progress is calculated correctly.
    Only non-empty translations should be counted.
    """
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="fake_hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create project with 2 languages
    project = ProjectService.create_project(
        db=db_session,
        owner_id=user.id,
        name="Test Project",
        languages=["en", "ru"]
    )
    
    # Create 2 keys
    key1 = KeyService.create_key(
        db=db_session,
        project_public_id=str(project.public_id),
        key="button.submit",
        user_id=user.id
    )
    
    key2 = KeyService.create_key(
        db=db_session,
        project_public_id=str(project.public_id),
        key="button.cancel",
        user_id=user.id
    )
    
    # Expected: 2 keys × 2 languages = 4 translations needed
    # Current: 0 translations
    # Progress: 0%
    db_session.refresh(project)
    project_type = build_project_type(project, user.id)
    assert project_type.translation_progress == 0, "Should be 0% with no translations"
    
    # Add 3 translations (one missing)
    KeyService.set_translation(db_session, str(key1.public_id), "en", "Submit", user.id)
    KeyService.set_translation(db_session, str(key1.public_id), "ru", "Отправить", user.id)
    KeyService.set_translation(db_session, str(key2.public_id), "en", "Cancel", user.id)
    # key2 "ru" is missing
    
    # Expected: 3/4 = 75%
    db_session.refresh(project)
    project_type = build_project_type(project, user.id)
    print(f"\nProgress with 3/4 translations: {project_type.translation_progress}%")
    assert project_type.translation_progress == 75, f"Should be 75%, got {project_type.translation_progress}%"
    
    # Add empty translation (should not count)
    KeyService.set_translation(db_session, str(key2.public_id), "ru", "   ", user.id)
    
    # Expected: still 3/4 = 75% (empty translation should be deleted)
    db_session.refresh(project)
    project_type = build_project_type(project, user.id)
    print(f"Progress after adding empty translation: {project_type.translation_progress}%")
    assert project_type.translation_progress == 75, f"Should still be 75%, got {project_type.translation_progress}%"
    
    # Check that empty translation was actually deleted
    empty_translation = db_session.query(Translation).filter(
        Translation.key_id == key2.id,
        Translation.language == "ru"
    ).first()
    assert empty_translation is None, "Empty translation should be deleted from DB"
    
    # Add the final translation
    KeyService.set_translation(db_session, str(key2.public_id), "ru", "Отмена", user.id)
    
    # Expected: 4/4 = 100%
    db_session.refresh(project)
    project_type = build_project_type(project, user.id)
    print(f"Progress with all 4/4 translations: {project_type.translation_progress}%")
    assert project_type.translation_progress == 100, f"Should be 100%, got {project_type.translation_progress}%"


def test_translation_with_whitespace_not_counted(db_session: Session):
    """
    Test that translations with only whitespace are not counted.
    """
    # Create test user
    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password="fake_hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create project with 1 language
    project = ProjectService.create_project(
        db=db_session,
        owner_id=user.id,
        name="Test Project 2",
        languages=["en"]
    )
    
    # Create 1 key
    key = KeyService.create_key(
        db=db_session,
        project_public_id=str(project.public_id),
        key="test.key",
        user_id=user.id
    )
    
    # Manually add translation with whitespace only
    translation = Translation(
        key_id=key.id,
        language="en",
        value="   "
    )
    db_session.add(translation)
    db_session.commit()
    
    # Expected: 0/1 = 0% (whitespace should not count)
    db_session.refresh(project)
    project_type = build_project_type(project, user.id)
    print(f"\nProgress with whitespace-only translation: {project_type.translation_progress}%")
    assert project_type.translation_progress == 0, f"Should be 0% with whitespace, got {project_type.translation_progress}%"


def test_empty_string_translation_not_counted(db_session: Session):
    """
    Test that translations with empty string are not counted.
    """
    # Create test user
    user = User(
        email="test3@example.com",
        username="testuser3",
        hashed_password="fake_hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create project with 1 language
    project = ProjectService.create_project(
        db=db_session,
        owner_id=user.id,
        name="Test Project 3",
        languages=["en"]
    )
    
    # Create 1 key
    key = KeyService.create_key(
        db=db_session,
        project_public_id=str(project.public_id),
        key="test.key",
        user_id=user.id
    )
    
    # Manually add translation with empty string
    translation = Translation(
        key_id=key.id,
        language="en",
        value=""
    )
    db_session.add(translation)
    db_session.commit()
    
    # Expected: 0/1 = 0% (empty string should not count)
    db_session.refresh(project)
    project_type = build_project_type(project, user.id)
    print(f"\nProgress with empty string translation: {project_type.translation_progress}%")
    assert project_type.translation_progress == 0, f"Should be 0% with empty string, got {project_type.translation_progress}%"

