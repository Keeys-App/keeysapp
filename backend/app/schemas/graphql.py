import strawberry
from typing import Optional, List
from app.schemas.auth import AuthQuery, AuthMutation, OnboardingMutation, UserType
from app.schemas.project import ProjectQuery, ProjectMutation, ProjectType
from app.schemas.team import TeamQuery, TeamMutation, TeamType, InviteInfoType, PendingInviteType
from app.schemas.project_access import ProjectAccessMutation
from app.schemas.key import KeyQuery, KeyMutation, KeyType, KeysConnection, ActivityLogType
from app.schemas.ai import AIMutation


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
    
    # Include team queries
    teams: List[TeamType] = strawberry.field(resolver=TeamQuery.teams)
    team: Optional[TeamType] = strawberry.field(resolver=TeamQuery.team)
    team_activity: List[ActivityLogType] = strawberry.field(resolver=TeamQuery.team_activity)
    invite_info: Optional[InviteInfoType] = strawberry.field(resolver=TeamQuery.invite_info)
    my_pending_invites: List[PendingInviteType] = strawberry.field(resolver=TeamQuery.my_pending_invites)
    
    # Include project queries
    projects: List[ProjectType] = strawberry.field(resolver=ProjectQuery.projects)
    project: Optional[ProjectType] = strawberry.field(resolver=ProjectQuery.project)
    
    # Include key queries
    project_keys: KeysConnection = strawberry.field(resolver=KeyQuery.project_keys)
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
    complete_onboarding = strawberry.field(resolver=OnboardingMutation.complete_onboarding)
    
    # Include team mutations
    create_team = strawberry.field(resolver=TeamMutation.create_team)
    update_team = strawberry.field(resolver=TeamMutation.update_team)
    delete_team = strawberry.field(resolver=TeamMutation.delete_team)
    add_team_member = strawberry.field(resolver=TeamMutation.add_team_member)
    remove_team_member = strawberry.field(resolver=TeamMutation.remove_team_member)
    update_team_member_role = strawberry.field(resolver=TeamMutation.update_team_member_role)
    accept_invite = strawberry.field(resolver=TeamMutation.accept_invite)
    decline_invite = strawberry.field(resolver=TeamMutation.decline_invite)
    resend_invite = strawberry.field(resolver=TeamMutation.resend_invite)
    
    # Include project mutations
    create_project = strawberry.field(resolver=ProjectMutation.create_project)
    update_project = strawberry.field(resolver=ProjectMutation.update_project)
    delete_project = strawberry.field(resolver=ProjectMutation.delete_project)
    add_project_member = strawberry.field(resolver=ProjectMutation.add_project_member)
    
    # Include project access mutations
    grant_project_access = strawberry.field(resolver=ProjectAccessMutation.grant_project_access)
    revoke_project_access = strawberry.field(resolver=ProjectAccessMutation.revoke_project_access)
    update_project_access_role = strawberry.field(resolver=ProjectAccessMutation.update_project_access_role)
    
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
    
    # Include AI mutations
    ai_translate = strawberry.field(resolver=AIMutation.ai_translate)
    ai_rephrase = strawberry.field(resolver=AIMutation.ai_rephrase)
    ai_shorten = strawberry.field(resolver=AIMutation.ai_shorten)
    ai_suggest_variants = strawberry.field(resolver=AIMutation.ai_suggest_variants)


schema = strawberry.Schema(query=Query, mutation=Mutation)
