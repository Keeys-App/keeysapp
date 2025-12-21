import strawberry
from typing import Optional, List
from app.schemas.auth import (
    AuthQuery,
    AuthMutation,
    OnboardingMutation,
    ProfileMutation,
    UserType,
    PasswordResetResult,
    ProfileUpdateResult,
    UpdateProfileInput,
    ChangePasswordInput,
)
from app.schemas.project import ProjectQuery, ProjectMutation, ProjectType, AvailableLanguageType
from app.schemas.team import TeamQuery, TeamMutation, TeamType, InviteInfoType, PendingInviteType
from app.schemas.project_access import ProjectAccessMutation
from app.schemas.key import KeyQuery, KeyMutation, KeyType, KeysConnection, ActivityLogType
from app.schemas.ai import AIQuery, AIMutation, AIProviderModels
from app.schemas.github import (
    GitHubQuery,
    GitHubMutation,
    GitHubConnectionType,
    GitHubRepoType,
    RepositoryType,
    ConnectRepositoryResult,
    GitHubDisconnectResult,
    GitHubAppInfoType,
)
from app.schemas.scanner import (
    ScannerQuery,
    ScannerMutation,
    ScanSessionType,
    FoundStringType,
    TokenUsageStatsType,
    StartScanResult,
    UpdateFoundStringResult,
    ConvertStringsResult,
    RepositoryDirectoryType,
)


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
    available_languages: List[AvailableLanguageType] = strawberry.field(resolver=ProjectQuery.available_languages)
    
    # Include key queries
    project_keys: KeysConnection = strawberry.field(resolver=KeyQuery.project_keys)
    key: Optional[KeyType] = strawberry.field(resolver=KeyQuery.key)
    check_key_exists: bool = strawberry.field(resolver=KeyQuery.check_key_exists)
    
    # Activity logs
    key_logs: List[ActivityLogType] = strawberry.field(resolver=KeyQuery.key_logs)
    project_activity: List[ActivityLogType] = strawberry.field(resolver=KeyQuery.project_activity)
    
    # GitHub integration
    team_github_connections: List[GitHubConnectionType] = strawberry.field(resolver=GitHubQuery.team_github_connections)
    github_connection: Optional[GitHubConnectionType] = strawberry.field(resolver=GitHubQuery.github_connection)
    github_app_info: GitHubAppInfoType = strawberry.field(resolver=GitHubQuery.github_app_info)
    available_github_repositories: List[GitHubRepoType] = strawberry.field(resolver=GitHubQuery.available_github_repositories)
    search_github_repositories: List[GitHubRepoType] = strawberry.field(resolver=GitHubQuery.search_github_repositories)
    project_repository: Optional[RepositoryType] = strawberry.field(resolver=GitHubQuery.project_repository)
    
    # Scanner
    scan_session: Optional[ScanSessionType] = strawberry.field(resolver=ScannerQuery.scan_session)
    project_scan_sessions: List[ScanSessionType] = strawberry.field(resolver=ScannerQuery.project_scan_sessions)
    team_token_usage: TokenUsageStatsType = strawberry.field(resolver=ScannerQuery.team_token_usage)
    repository_directories: List[RepositoryDirectoryType] = strawberry.field(resolver=ScannerQuery.repository_directories)
    
    # AI
    available_ai_models: List[AIProviderModels] = strawberry.field(resolver=AIQuery.available_ai_models)


@strawberry.type
class Mutation:
    """
    Root GraphQL Mutation.
    """
    
    # Include auth mutations
    register = strawberry.field(resolver=AuthMutation.register)
    login = strawberry.field(resolver=AuthMutation.login)
    complete_onboarding = strawberry.field(resolver=OnboardingMutation.complete_onboarding)
    request_password_reset: PasswordResetResult = strawberry.field(resolver=AuthMutation.request_password_reset)
    reset_password: PasswordResetResult = strawberry.field(resolver=AuthMutation.reset_password)
    
    # Include profile mutations
    update_profile: ProfileUpdateResult = strawberry.field(resolver=ProfileMutation.update_profile)
    change_password: ProfileUpdateResult = strawberry.field(resolver=ProfileMutation.change_password)
    
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
    update_team_ai_settings = strawberry.field(resolver=TeamMutation.update_team_ai_settings)
    
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
    
    # Include GitHub mutations
    get_github_auth_url = strawberry.field(resolver=GitHubMutation.get_github_auth_url)
    disconnect_github = strawberry.field(resolver=GitHubMutation.disconnect_github)
    connect_repository: ConnectRepositoryResult = strawberry.field(resolver=GitHubMutation.connect_repository)
    disconnect_repository: GitHubDisconnectResult = strawberry.field(resolver=GitHubMutation.disconnect_repository)
    
    # Include Scanner mutations
    start_repository_scan: StartScanResult = strawberry.field(resolver=ScannerMutation.start_repository_scan)
    cancel_scan: StartScanResult = strawberry.field(resolver=ScannerMutation.cancel_scan)
    update_found_string_status: UpdateFoundStringResult = strawberry.field(resolver=ScannerMutation.update_found_string_status)
    convert_found_strings_to_keys: ConvertStringsResult = strawberry.field(resolver=ScannerMutation.convert_found_strings_to_keys)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    types=[UpdateProfileInput, ChangePasswordInput, ProfileUpdateResult],
)
