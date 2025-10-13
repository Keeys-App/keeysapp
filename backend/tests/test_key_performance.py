"""
Performance tests for KeyService to verify N+1 query optimization.
"""
import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.services.key_service import KeyService
from app.services.project_service import ProjectService
from app.models.key import Key, Translation


class QueryCounter:
    """
    Helper class to count SQL queries executed during a test.
    """
    def __init__(self):
        self.count = 0
        self.queries = []

    def __enter__(self):
        event.listen(Engine, "before_cursor_execute", self.callback)
        return self

    def __exit__(self, *args):
        event.remove(Engine, "before_cursor_execute", self.callback)

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1
        self.queries.append(statement)


class TestKeyPerformance:
    """
    Performance tests for KeyService.
    """

    @pytest.fixture
    def project_with_keys(self, db_session, created_user, test_team):
        """
        Create a project with multiple keys and translations.
        """
        # Create project
        project = ProjectService.create_project(
            db=db_session,
            owner_id=created_user.id,
            team_id=test_team.id,
            name="Performance Test Project",
            languages=[
                {"code": "en", "locale": "en-US"},
                {"code": "ru", "locale": "ru-RU"},
                {"code": "de", "locale": "de-DE"}
            ]
        )

        # Create 20 keys with translations in 3 languages
        for i in range(20):
            key = Key(
                key=f"test.key.{i}",
                description=f"Test key {i}",
                tags=["test", f"group{i % 3}"],
                project_id=project.id
            )
            db_session.add(key)
            db_session.flush()

            # Add translations for each language
            for lang in ["en", "ru", "de"]:
                translation = Translation(
                    key_id=key.id,
                    language=lang,
                    value=f"Translation {i} in {lang}"
                )
                db_session.add(translation)

        db_session.commit()
        return project, created_user

    def test_get_project_keys_no_n_plus_one(self, db_session, project_with_keys):
        """
        Test that get_project_keys doesn't have N+1 query problem.
        With eager loading, we should have a constant number of queries
        regardless of the number of keys.
        """
        project, user = project_with_keys
        
        # Count queries
        with QueryCounter() as counter:
            keys = KeyService.get_project_keys(
                db=db_session,
                project_public_id=str(project.public_id),
                user_id=user.id
            )
            
            # Access translations to ensure they're loaded
            for key in keys:
                for translation in key.translations:
                    _ = translation.value

        # With joinedload, we should have approximately:
        # 1. Get project by public_id
        # 2. Check project access (check membership)
        # 3. Get keys with translations (single query with JOIN)
        # Total: ~3-5 queries (depending on SQLAlchemy's internals)
        # 
        # Without joinedload, it would be:
        # 1. Get project
        # 2. Check access
        # 3. Get keys (1 query)
        # 4. Get translations for each key (20 queries for 20 keys)
        # Total: ~23 queries
        
        print(f"\n=== Query Performance Test ===")
        print(f"Number of keys: {len(keys)}")
        print(f"Number of queries executed: {counter.count}")
        print(f"\nQueries executed:")
        for i, query in enumerate(counter.queries, 1):
            # Clean up query for readability
            clean_query = ' '.join(query.split())
            if len(clean_query) > 100:
                clean_query = clean_query[:100] + "..."
            print(f"{i}. {clean_query}")
        
        # Assert we loaded 20 keys
        assert len(keys) == 20
        
        # Assert each key has 3 translations
        for key in keys:
            assert len(key.translations) == 3
        
        # With proper eager loading, queries should be <= 10
        # (being generous to account for SQLAlchemy internals)
        # Without eager loading, it would be 23+ queries
        assert counter.count <= 10, (
            f"Too many queries! Expected <= 10, got {counter.count}. "
            f"This suggests N+1 query problem is not fixed."
        )
        
        print(f"\n✓ Performance test passed! Only {counter.count} queries for 20 keys.")

    def test_get_key_by_public_id_eager_loading(self, db_session, project_with_keys):
        """
        Test that get_key_by_public_id with eager loading works correctly.
        """
        project, user = project_with_keys
        
        # Get first key
        first_key = db_session.query(Key).filter(
            Key.project_id == project.id
        ).first()
        
        with QueryCounter() as counter:
            key = KeyService.get_key_by_public_id(
                db=db_session,
                public_id=str(first_key.public_id),
                eager_load_translations=True
            )
            
            # Access translations
            for translation in key.translations:
                _ = translation.value
        
        print(f"\n=== Single Key Query Test ===")
        print(f"Number of queries: {counter.count}")
        
        # Should be just 1-2 queries (get key with translations)
        assert counter.count <= 2
        assert len(key.translations) == 3
        
        print(f"✓ Single key test passed! Only {counter.count} queries.")

    def test_get_key_by_public_id_lazy_loading(self, db_session, project_with_keys):
        """
        Test get_key_by_public_id without eager loading.
        """
        project, user = project_with_keys
        
        # Get first key
        first_key = db_session.query(Key).filter(
            Key.project_id == project.id
        ).first()
        
        with QueryCounter() as counter:
            key = KeyService.get_key_by_public_id(
                db=db_session,
                public_id=str(first_key.public_id),
                eager_load_translations=False
            )
            
            # Access translations (will trigger lazy loading)
            for translation in key.translations:
                _ = translation.value
        
        print(f"\n=== Lazy Loading Test ===")
        print(f"Number of queries: {counter.count}")
        
        # With lazy loading, should be 2 queries:
        # 1. Get key
        # 2. Get translations (when accessed)
        assert counter.count >= 2
        
        print(f"✓ Lazy loading works as expected: {counter.count} queries.")

