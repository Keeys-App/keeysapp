"""
GraphQL schema for GitHub integration.
GitHub connections are linked to Teams.
"""
import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy import select
import logging

from app.database import AsyncSessionLocal
from app.models.github_connection import GitHubConnection
from app.services.github_service import GitHubService
from app.services.user_service import UserService
from app.services.team_service import TeamService
from app.services.project_service import ProjectService
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


async def get_current_user_id(info: Info) -> int:
    """
    Get current user's internal ID from GraphQL context.
    
    Args:
        info: GraphQL info object
        
    Returns:
        Internal user ID
        
    Raises:
        AuthenticationError: If user is not authenticated
    """
    request = info.context.get("request")
    if not request:
        raise AuthenticationError()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError()
    
    token = auth_header.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if not payload:
        raise AuthenticationError()
    
    public_id = payload.get("sub")
    if not public_id:
        raise AuthenticationError()
    
    async with AsyncSessionLocal() as db:
        user = await UserService.get_user_by_public_id(db, public_id)
        if not user:
            raise AuthenticationError()
        return user.id


@strawberry.type
class GitHubConnectionType:
    """
    GraphQL type for GitHub connection.
    """
    id: str  # Public UUID
    github_username: str
    github_avatar_url: Optional[str]
    github_email: Optional[str]
    scope: Optional[str]
    connected_at: datetime
    connected_by_username: Optional[str]  # Username of who connected it


@strawberry.type
class GitHubAuthUrlResult:
    """
    Result type for getting GitHub authorization URL.
    """
    authorization_url: str
    state: str


@strawberry.type
class GitHubDisconnectResult:
    """
    Result type for disconnecting GitHub.
    """
    success: bool
    message: str


@strawberry.type
class GitHubInstallationType:
    """
    GraphQL type for GitHub App installation.
    """
    id: str
    account_login: str
    account_type: str  # "User" or "Organization"
    repository_selection: str  # "all" or "selected"


@strawberry.type
class GitHubAppInfoType:
    """
    GraphQL type for GitHub App information.
    """
    installation_url: Optional[str]
    installations: List[GitHubInstallationType]
    has_installation: bool


@strawberry.type
class GitHubRepoType:
    """
    GraphQL type for GitHub repository information.
    """
    id: str
    full_name: str
    name: str
    owner: str
    default_branch: str
    private: bool
    description: Optional[str]
    html_url: str


@strawberry.type
class RepositoryType:
    """
    GraphQL type for connected repository.
    """
    id: str  # Public UUID
    github_repo_id: str
    repo_owner: str
    repo_name: str
    full_name: str
    default_branch: str
    i18n_framework: Optional[str]
    source_patterns: List[str]
    locale_path: Optional[str]
    github_username: Optional[str]  # From connected GitHub account
    connected_at: datetime


@strawberry.type
class ConnectRepositoryResult:
    """
    Result type for connecting a repository.
    """
    success: bool
    message: str
    repository: Optional[RepositoryType] = None


@strawberry.type
class GitHubQuery:
    """
    GraphQL queries for GitHub integration.
    """
    
    @strawberry.field
    async def github_app_info(
        self,
        info: Info,
        team_id: str,
    ) -> GitHubAppInfoType:
        """
        Get GitHub App installation info for the team.
        
        Args:
            info: GraphQL info object
            team_id: Public UUID of the team
            
        Returns:
            GitHub App information including installation URL and status
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get team and verify access
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    return GitHubAppInfoType(
                        installation_url=GitHubService.get_app_installation_url(),
                        installations=[],
                        has_installation=False,
                    )
                
                # Get GitHub connections for this team
                connections = await GitHubService.get_connections_by_team(db, team.id)
                
                if not connections:
                    return GitHubAppInfoType(
                        installation_url=GitHubService.get_app_installation_url(),
                        installations=[],
                        has_installation=False,
                    )
                
                # Check installations using the first connection's token
                access_token = GitHubService.get_decrypted_token(connections[0])
                raw_installations = await GitHubService.get_user_installations(access_token)
                
                installations = [
                    GitHubInstallationType(
                        id=str(inst.get("id", "")),
                        account_login=inst.get("account", {}).get("login", ""),
                        account_type=inst.get("account", {}).get("type", "User"),
                        repository_selection=inst.get("repository_selection", "selected"),
                    )
                    for inst in raw_installations
                ]
                
                return GitHubAppInfoType(
                    installation_url=GitHubService.get_app_installation_url(),
                    installations=installations,
                    has_installation=len(installations) > 0,
                )
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error getting GitHub App info: {type(e).__name__}")
            return GitHubAppInfoType(
                installation_url=GitHubService.get_app_installation_url(),
                installations=[],
                has_installation=False,
            )
    
    @strawberry.field
    async def available_github_repositories(
        self,
        info: Info,
        team_id: str,
    ) -> List[GitHubRepoType]:
        """
        Get available repositories from team's GitHub connections.
        
        Args:
            info: GraphQL info object
            team_id: Public UUID of the team
            
        Returns:
            List of available repositories
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get team and verify access
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    return []
                
                # Check if user has access to team
                has_access = await TeamService.check_user_team_access(db, team.id, user_id)
                if not has_access and team.owner_id != user_id:
                    return []
                
                # Get all GitHub connections for the team
                connections = await GitHubService.get_connections_by_team(db, team.id)
                
                if not connections:
                    return []
                
                # Get repositories from all connections
                all_repos: List[GitHubRepoType] = []
                seen_repo_ids = set()
                
                for conn in connections:
                    try:
                        access_token = GitHubService.get_decrypted_token(conn)
                        repos = await GitHubService.list_user_repositories(access_token)
                        
                        for repo in repos:
                            if repo["id"] not in seen_repo_ids:
                                seen_repo_ids.add(repo["id"])
                                all_repos.append(GitHubRepoType(
                                    id=repo["id"],
                                    full_name=repo["full_name"],
                                    name=repo["name"],
                                    owner=repo["owner"],
                                    default_branch=repo["default_branch"],
                                    private=repo["private"],
                                    description=repo["description"],
                                    html_url=repo["html_url"],
                                ))
                    except Exception as e:
                        logger.error(f"Error fetching repos from connection {conn.id}: {type(e).__name__}")
                        continue
                
                return all_repos
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching available repositories: {type(e).__name__}")
            return []
    
    @strawberry.field
    async def project_repository(
        self,
        info: Info,
        project_id: str,
    ) -> Optional[RepositoryType]:
        """
        Get repository linked to a project.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            
        Returns:
            Repository or None
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get project
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return None
                
                # Verify user has access
                has_access = await ProjectService.check_project_access(db, project.id, user_id)
                if not has_access:
                    return None
                
                # Get repository
                repository = await GitHubService.get_repository_by_project(db, project.id)
                if not repository:
                    return None
                
                # Get GitHub username from connection
                github_username = None
                if repository.github_connection_id:
                    result = await db.execute(
                        select(GitHubConnection).where(
                            GitHubConnection.id == repository.github_connection_id
                        )
                    )
                    connection = result.scalar_one_or_none()
                    if connection:
                        github_username = connection.github_username
                
                return RepositoryType(
                    id=str(repository.public_id),
                    github_repo_id=repository.github_repo_id,
                    repo_owner=repository.repo_owner,
                    repo_name=repository.repo_name,
                    full_name=f"{repository.repo_owner}/{repository.repo_name}",
                    default_branch=repository.default_branch or "main",
                    i18n_framework=repository.i18n_framework,
                    source_patterns=repository.source_patterns or [],
                    locale_path=repository.locale_path,
                    github_username=github_username,
                    connected_at=repository.connected_at,
                )
        except AuthenticationError:
            raise
        except Exception as e:
            import traceback
            logger.error(f"Error fetching project repository: {type(e).__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @strawberry.field
    async def search_github_repositories(
        self,
        info: Info,
        team_id: str,
        query: str,
    ) -> List[GitHubRepoType]:
        """
        Search for repositories using GitHub Search API.
        Use this when a repo is not found in the main list.
        
        Args:
            info: GraphQL info object
            team_id: Public UUID of the team
            query: Search query
            
        Returns:
            List of matching repositories
        """
        try:
            if not query or len(query) < 2:
                return []
            
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get team and verify access
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    return []
                
                # Check if user has access to team
                has_access = await TeamService.check_user_team_access(db, team.id, user_id)
                if not has_access and team.owner_id != user_id:
                    return []
                
                # Get first GitHub connection for the team
                connections = await GitHubService.get_connections_by_team(db, team.id)
                
                if not connections:
                    return []
                
                # Use first connection for search
                conn = connections[0]
                access_token = GitHubService.get_decrypted_token(conn)
                repos = await GitHubService.search_repositories(access_token, query)
                
                return [
                    GitHubRepoType(
                        id=repo["id"],
                        full_name=repo["full_name"],
                        name=repo["name"],
                        owner=repo["owner"],
                        default_branch=repo["default_branch"],
                        private=repo["private"],
                        description=repo["description"],
                        html_url=repo["html_url"],
                    )
                    for repo in repos
                ]
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error searching repositories: {type(e).__name__}")
            return []
    
    @strawberry.field
    async def team_github_connections(
        self,
        info: Info,
        team_id: str,
    ) -> List[GitHubConnectionType]:
        """
        Get all GitHub connections for a team.
        
        Args:
            info: GraphQL info object
            team_id: Public UUID of the team
            
        Returns:
            List of GitHub connections
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get team and verify access
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    return []
                
                # Check if user has access to team
                has_access = await TeamService.check_user_team_access(db, team.id, user_id)
                if not has_access and team.owner_id != user_id:
                    return []
                
                connections = await GitHubService.get_connections_by_team(db, team.id)
                
                result = []
                for conn in connections:
                    # Get username of who connected it
                    connected_by_username = None
                    if conn.connected_by_user_id:
                        connected_by_user = await UserService.get_user_by_id(db, conn.connected_by_user_id)
                        if connected_by_user:
                            connected_by_username = connected_by_user.username
                    
                    result.append(GitHubConnectionType(
                        id=str(conn.public_id),
                        github_username=conn.github_username,
                        github_avatar_url=conn.github_avatar_url,
                        github_email=conn.github_email,
                        scope=conn.scope,
                        connected_at=conn.connected_at,
                        connected_by_username=connected_by_username,
                    ))
                
                return result
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching GitHub connections: {type(e).__name__}")
            return []
    
    @strawberry.field
    async def github_connection(
        self,
        info: Info,
        connection_id: str,
    ) -> Optional[GitHubConnectionType]:
        """
        Get a specific GitHub connection by ID.
        
        Args:
            info: GraphQL info object
            connection_id: Public UUID of the connection
            
        Returns:
            GitHub connection or None
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                connection = await GitHubService.get_connection_by_public_id(db, connection_id)
                
                if not connection:
                    return None
                
                # Check if user has access to the team
                team = await TeamService.get_team_by_id(db, connection.team_id)
                if not team:
                    return None
                
                has_access = await TeamService.check_user_team_access(db, team.id, user_id)
                if not has_access and team.owner_id != user_id:
                    return None
                
                # Get username of who connected it
                connected_by_username = None
                if connection.connected_by_user_id:
                    connected_by_user = await UserService.get_user_by_id(db, connection.connected_by_user_id)
                    if connected_by_user:
                        connected_by_username = connected_by_user.username
                
                return GitHubConnectionType(
                    id=str(connection.public_id),
                    github_username=connection.github_username,
                    github_avatar_url=connection.github_avatar_url,
                    github_email=connection.github_email,
                    scope=connection.scope,
                    connected_at=connection.connected_at,
                    connected_by_username=connected_by_username,
                )
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching GitHub connection: {type(e).__name__}")
            return None


# In-memory state storage (shared with router)
# For production, use Redis or database


@strawberry.type
class GitHubMutation:
    """
    GraphQL mutations for GitHub integration.
    """
    
    @strawberry.mutation
    async def get_github_auth_url(
        self,
        info: Info,
        team_id: str,
    ) -> GitHubAuthUrlResult:
        """
        Get GitHub OAuth authorization URL for a team.
        
        Args:
            info: GraphQL info object
            team_id: Public UUID of the team to connect GitHub to
            
        Returns:
            Authorization URL and state
        """
        try:
            # Get user's public_id
            request = info.context.get("request")
            if not request:
                raise AuthenticationError()
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationError()
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            
            if not payload:
                raise AuthenticationError()
            
            user_public_id = payload.get("sub")
            if not user_public_id:
                raise AuthenticationError()
            
            # Verify user has permission to manage team
            async with AsyncSessionLocal() as db:
                user = await UserService.get_user_by_public_id(db, user_public_id)
                if not user:
                    raise AuthenticationError()
                
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    raise Exception("Team not found")
                
                # Check if user is owner or admin
                is_owner = team.owner_id == user.id
                is_admin = await TeamService.check_user_team_role(db, team.id, user.id, "admin")
                
                if not is_owner and not is_admin:
                    raise Exception("Permission denied. Only team owner or admin can connect GitHub.")
            
            # Generate state and authorization URL
            state = GitHubService.generate_state()
            auth_url = GitHubService.get_authorization_url(state)
            
            # Store state -> user+team mapping (shared with router)
            from app.services.github_service import oauth_states
            oauth_states[state] = {
                "user_public_id": user_public_id,
                "team_public_id": team_id,
            }
            
            logger.info(f"Stored OAuth state '{state}' for user {user_public_id}, team {team_id}. Total states: {len(oauth_states)}")
            
            return GitHubAuthUrlResult(
                authorization_url=auth_url,
                state=state,
            )
        except AuthenticationError:
            raise
        except ValueError as e:
            logger.error(f"GitHub OAuth not configured: {e}")
            raise Exception("GitHub OAuth not configured")
        except Exception as e:
            logger.error(f"Error getting auth URL: {type(e).__name__}: {str(e)}")
            raise Exception(str(e) if str(e) else "Failed to get authorization URL")
    
    @strawberry.mutation
    async def disconnect_github(
        self,
        info: Info,
        connection_id: str,
    ) -> GitHubDisconnectResult:
        """
        Disconnect a GitHub connection from a team.
        
        Args:
            info: GraphQL info object
            connection_id: Public UUID of the connection to disconnect
            
        Returns:
            Result with success status and message
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get connection to find team
                connection = await GitHubService.get_connection_by_public_id(db, connection_id)
                if not connection:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Connection not found",
                    )
                
                # Check if user has permission to manage team
                team = await TeamService.get_team_by_id(db, connection.team_id)
                if not team:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Team not found",
                    )
                
                is_owner = team.owner_id == user_id
                is_admin = await TeamService.check_user_team_role(db, team.id, user_id, "admin")
                
                if not is_owner and not is_admin:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Permission denied. Only team owner or admin can disconnect GitHub.",
                    )
                
                deleted = await GitHubService.delete_connection_by_public_id(
                    db=db,
                    public_id=connection_id,
                    team_id=team.id,
                )
                
                if deleted:
                    return GitHubDisconnectResult(
                        success=True,
                        message="GitHub connection removed successfully",
                    )
                else:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Connection not found or already removed",
                    )
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error disconnecting GitHub: {type(e).__name__}")
            return GitHubDisconnectResult(
                success=False,
                message="Failed to disconnect GitHub. Please try again.",
            )
    
    @strawberry.mutation
    async def connect_repository(
        self,
        info: Info,
        project_id: str,
        github_repo_id: str,
        github_connection_id: str,
    ) -> ConnectRepositoryResult:
        """
        Connect a GitHub repository to a project.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            github_repo_id: GitHub repository ID
            github_connection_id: Public UUID of the GitHub connection to use
            
        Returns:
            Result with success status and repository info
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get project
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return ConnectRepositoryResult(
                        success=False,
                        message="Project not found",
                    )
                
                # Verify user has access to project
                has_access = await ProjectService.check_project_access(db, project.id, user_id)
                if not has_access:
                    return ConnectRepositoryResult(
                        success=False,
                        message="Access denied",
                    )
                
                # Get GitHub connection
                connection = await GitHubService.get_connection_by_public_id(db, github_connection_id)
                if not connection:
                    return ConnectRepositoryResult(
                        success=False,
                        message="GitHub connection not found",
                    )
                
                # Verify connection belongs to the project's team
                if connection.team_id != project.team_id:
                    return ConnectRepositoryResult(
                        success=False,
                        message="GitHub connection doesn't belong to project's team",
                    )
                
                # Fetch repository info from GitHub
                access_token = GitHubService.get_decrypted_token(connection)
                repos = await GitHubService.list_user_repositories(access_token)
                
                logger.info(f"Looking for repo with id={github_repo_id} in {len(repos)} repos")
                
                # Find the repository (GitHubRepoInfo is TypedDict, access as dict)
                repo_info = None
                for repo in repos:
                    if repo["id"] == github_repo_id:
                        repo_info = repo
                        break
                
                if not repo_info:
                    logger.warning(f"Repository {github_repo_id} not found in user repos")
                    return ConnectRepositoryResult(
                        success=False,
                        message="Repository not found or not accessible",
                    )
                
                logger.info(f"Found repo: {repo_info['full_name']}")
                
                # Connect repository
                repository = await GitHubService.connect_repository(
                    db=db,
                    project_id=project.id,
                    github_connection_id=connection.id,
                    repo_info=repo_info,
                )
                
                return ConnectRepositoryResult(
                    success=True,
                    message="Repository connected successfully",
                    repository=RepositoryType(
                        id=str(repository.public_id),
                        github_repo_id=repository.github_repo_id,
                        repo_owner=repository.repo_owner,
                        repo_name=repository.repo_name,
                        full_name=f"{repository.repo_owner}/{repository.repo_name}",
                        default_branch=repository.default_branch or "main",
                        i18n_framework=repository.i18n_framework,
                        source_patterns=repository.source_patterns or [],
                        locale_path=repository.locale_path,
                        github_username=connection.github_username,
                        connected_at=repository.connected_at,
                    ),
                )
        except AuthenticationError:
            raise
        except Exception as e:
            import traceback
            logger.error(f"Error connecting repository: {type(e).__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return ConnectRepositoryResult(
                success=False,
                message="Failed to connect repository. Please try again.",
            )
    
    @strawberry.mutation
    async def disconnect_repository(
        self,
        info: Info,
        project_id: str,
    ) -> GitHubDisconnectResult:
        """
        Disconnect repository from a project.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            
        Returns:
            Result with success status and message
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get project
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Project not found",
                    )
                
                # Verify user has access
                has_access = await ProjectService.check_project_access(db, project.id, user_id)
                if not has_access:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Access denied",
                    )
                
                # Get repository
                repository = await GitHubService.get_repository_by_project(db, project.id)
                if not repository:
                    return GitHubDisconnectResult(
                        success=False,
                        message="No repository connected",
                    )
                
                # Disconnect
                deleted = await GitHubService.disconnect_repository(db, repository.id)
                
                if deleted:
                    return GitHubDisconnectResult(
                        success=True,
                        message="Repository disconnected successfully",
                    )
                else:
                    return GitHubDisconnectResult(
                        success=False,
                        message="Failed to disconnect repository",
                    )
        except AuthenticationError:
            raise
        except Exception as e:
            import traceback
            logger.error(f"Error disconnecting repository: {type(e).__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return GitHubDisconnectResult(
                success=False,
                message="Failed to disconnect repository. Please try again.",
            )
