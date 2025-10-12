import strawberry
from typing import Optional, List
from app.schemas.auth import AuthQuery, AuthMutation, UserType
from app.schemas.project import ProjectQuery, ProjectMutation, ProjectType
from app.schemas.key import KeyQuery, KeyMutation, KeyType, ActivityLogType


@strawberry.type
class Query:
    """
    Root GraphQL Query.
    """
    
    @strawberry.field
    def hello(self) -> str:
        """
        Simple hello query for testing.
        """
        return "Hello from GraphQL!"
    
    # Include auth queries
    me: Optional[UserType] = strawberry.field(resolver=AuthQuery.me)
    
    # Include project queries
    projects: List[ProjectType] = strawberry.field(resolver=ProjectQuery.projects)
    project: Optional[ProjectType] = strawberry.field(resolver=ProjectQuery.project)
    
    # Include key queries
    project_keys: List[KeyType] = strawberry.field(resolver=KeyQuery.project_keys)
    key: Optional[KeyType] = strawberry.field(resolver=KeyQuery.key)
    check_key_exists: bool = strawberry.field(resolver=KeyQuery.check_key_exists)
    
    # Activity logs
    key_logs: List[ActivityLogType] = strawberry.field(resolver=KeyQuery.key_logs)
    project_activity: List[ActivityLogType] = strawberry.field(resolver=KeyQuery.project_activity)


@strawberry.type
class Mutation:
    """
    Root GraphQL Mutation.
    """
    
    # Include auth mutations
    register = strawberry.field(resolver=AuthMutation.register)
    login = strawberry.field(resolver=AuthMutation.login)
    
    # Include project mutations
    create_project = strawberry.field(resolver=ProjectMutation.create_project)
    update_project = strawberry.field(resolver=ProjectMutation.update_project)
    delete_project = strawberry.field(resolver=ProjectMutation.delete_project)
    add_project_member = strawberry.field(resolver=ProjectMutation.add_project_member)
    
    # Include key mutations
    create_key = strawberry.field(resolver=KeyMutation.create_key)
    update_key = strawberry.field(resolver=KeyMutation.update_key)
    delete_key = strawberry.field(resolver=KeyMutation.delete_key)
    set_translation = strawberry.field(resolver=KeyMutation.set_translation)
    delete_translation = strawberry.field(resolver=KeyMutation.delete_translation)
    batch_import_translations = strawberry.field(resolver=KeyMutation.batch_import_translations)
    
    # Include review mutations
    approve_translation = strawberry.field(resolver=KeyMutation.approve_translation)
    reject_translation = strawberry.field(resolver=KeyMutation.reject_translation)
    delete_translation_review = strawberry.field(resolver=KeyMutation.delete_translation_review)


schema = strawberry.Schema(query=Query, mutation=Mutation)
