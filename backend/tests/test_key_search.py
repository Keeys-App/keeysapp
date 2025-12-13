"""
Tests for key search functionality.
"""
import pytest
from app.services.key_service import KeyService
from app.services.project_service import ProjectService
from app.models.key import Key, Translation


@pytest.fixture
def test_project(db_session, test_user, test_team):
    """
    Create a test project with keys and translations.
    """
    project = ProjectService.create_project(
        db=db_session,
        owner_id=test_user.id,
        name="Test Project",
        description="Project for search testing",
        default_language="en",
        languages=["en", "ru", "es"],
        team_id=test_team.id
    )
    
    # Create keys with different content for search testing
    keys_data = [
        {
            "key": "button.submit",
            "description": "Submit button text",
            "translations": {
                "en": "Submit",
                "fr": "Soumettre",
                "es": "Enviar"
            }
        },
        {
            "key": "button.cancel",
            "description": "Cancel button text",
            "translations": {
                "en": "Cancel",
                "fr": "Annuler",
                "es": "Cancelar"
            }
        },
        {
            "key": "admin.title",
            "description": "Admin panel title",
            "translations": {
                "en": "Administration",
                "fr": "Administration",
                "es": "Administración"
            }
        },
        {
            "key": "user.greeting",
            "description": "User greeting message",
            "translations": {
                "en": "Hello, user!",
                "fr": "Bonjour, utilisateur!",
                "es": "¡Hola, usuario!"
            }
        },
        {
            "key": "error.not_found",
            "description": "Error message for not found",
            "translations": {
                "en": "Not found",
                "fr": "Non trouvé",
                "es": "No encontrado"
            }
        }
    ]
    
    for key_data in keys_data:
        KeyService.create_key(
            db=db_session,
            project_public_id=str(project.public_id),
            key=key_data["key"],
            description=key_data["description"],
            translations=key_data["translations"],
            tags=[],
            user_id=test_user.id
        )
    
    return project


class TestKeySearch:
    """
    Test key search functionality.
    """
    
    def test_search_by_key_name(self, db_session, test_user, test_project):
        """
        Test searching keys by key name.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="button"
        )
        
        assert result is not None
        assert result['total_count'] == 2  # button.submit and button.cancel
        assert all('button' in key.key.lower() for key in result['keys'])
    
    def test_search_by_description(self, db_session, test_user, test_project):
        """
        Test searching keys by description.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="admin"
        )
        
        assert result is not None
        assert result['total_count'] == 1  # admin.title
        assert 'admin' in result['keys'][0].key.lower()
    
    def test_search_by_translation_value(self, db_session, test_user, test_project):
        """
        Test searching keys by translation value.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="Soumettre"
        )
        
        assert result is not None
        assert result['total_count'] == 1  # button.submit with Russian translation
        assert result['keys'][0].key == "button.submit"
    
    def test_search_case_insensitive(self, db_session, test_user, test_project):
        """
        Test that search is case-insensitive.
        """
        # Search with uppercase
        result_upper = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="BUTTON"
        )
        
        # Search with lowercase
        result_lower = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="button"
        )
        
        assert result_upper is not None
        assert result_lower is not None
        assert result_upper['total_count'] == result_lower['total_count'] == 2
    
    def test_search_partial_match(self, db_session, test_user, test_project):
        """
        Test that search works with partial matches.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="err"
        )
        
        assert result is not None
        assert result['total_count'] == 1  # error.not_found
        assert 'error' in result['keys'][0].key.lower()
    
    def test_search_no_results(self, db_session, test_user, test_project):
        """
        Test searching with a query that returns no results.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="nonexistent"
        )
        
        assert result is not None
        assert result['total_count'] == 0
        assert len(result['keys']) == 0
    
    def test_search_with_pagination(self, db_session, test_user, test_project):
        """
        Test that search works correctly with pagination.
        """
        # Get first page with limit 2
        result_page1 = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=2,
            search="."  # Search for all keys (all contain '.')
        )
        
        # Get second page
        result_page2 = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=2,
            limit=2,
            search="."
        )
        
        assert result_page1 is not None
        assert result_page2 is not None
        assert result_page1['total_count'] == 5  # All keys
        assert len(result_page1['keys']) == 2
        assert len(result_page2['keys']) == 2
        # Ensure different keys in different pages
        page1_keys = [k.key for k in result_page1['keys']]
        page2_keys = [k.key for k in result_page2['keys']]
        assert not set(page1_keys).intersection(set(page2_keys))
    
    def test_search_empty_query(self, db_session, test_user, test_project):
        """
        Test that empty search query returns all keys.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search=""
        )
        
        assert result is not None
        assert result['total_count'] == 5  # All keys
    
    def test_search_whitespace_query(self, db_session, test_user, test_project):
        """
        Test that whitespace-only search query returns all keys.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="   "
        )
        
        assert result is not None
        assert result['total_count'] == 5  # All keys
    
    def test_search_multiple_languages(self, db_session, test_user, test_project):
        """
        Test searching across multiple language translations.
        """
        # Search for English word
        result_en = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="Hello"
        )
        
        # Search for Russian word
        result_ru = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="Bonjour"
        )
        
        assert result_en is not None
        assert result_ru is not None
        assert result_en['total_count'] == 1
        assert result_ru['total_count'] == 1
        # Both should find the same key
        assert result_en['keys'][0].key == result_ru['keys'][0].key == "user.greeting"
    
    def test_search_unauthorized_user(self, db_session, test_project):
        """
        Test that unauthorized users cannot search keys.
        """
        # Create a different user who doesn't have access
        from app.models.user import User
        unauthorized_user = User(
            email="unauthorized@example.com",
            username="unauthorized",
            hashed_password=User.get_password_hash("password")
        )
        db_session.add(unauthorized_user)
        db_session.commit()
        db_session.refresh(unauthorized_user)
        
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=unauthorized_user.id,
            offset=0,
            limit=50,
            search="button"
        )
        
        assert result is None  # No access
    
    def test_search_with_special_characters(self, db_session, test_user, test_project):
        """
        Test searching with special characters.
        """
        result = KeyService.get_project_keys_paginated(
            db=db_session,
            project_public_id=str(test_project.public_id),
            user_id=test_user.id,
            offset=0,
            limit=50,
            search="not_found"
        )
        
        assert result is not None
        assert result['total_count'] == 1
        assert result['keys'][0].key == "error.not_found"

