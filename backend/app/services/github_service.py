"""
GitHub OAuth Service for handling GitHub integration.
GitHub connections are linked to Teams, not individual Users.
"""
import secrets
import logging
import httpx
from typing import Optional, TypedDict
from urllib.parse import urlencode
from cryptography.fernet import Fernet

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID

from app.core.config import settings
from app.models.github_connection import GitHubConnection
from app.models.repository import Repository

logger = logging.getLogger(__name__)

# GitHub OAuth URLs
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"

# Required scopes for repository access
GITHUB_SCOPES = "repo read:user user:email"


class GitHubUserInfo(TypedDict):
    """Type definition for GitHub user information."""
    id: str
    login: str
    avatar_url: str
    email: Optional[str]


class GitHubTokenInfo(TypedDict):
    """Type definition for GitHub token information."""
    access_token: str
    token_type: str
    scope: str


class GitHubRepoInfo(TypedDict):
    """Type definition for GitHub repository information."""
    id: str
    full_name: str
    name: str
    owner: str
    default_branch: str
    private: bool
    description: Optional[str]
    html_url: str


class GitHubService:
    """
    Service for GitHub OAuth and API operations.
    GitHub connections are linked to Teams, allowing all team members
    to use them for repository operations.
    """
    
    @staticmethod
    def _get_fernet() -> Optional[Fernet]:
        """
        Get Fernet cipher for token encryption.
        
        Returns:
            Fernet cipher instance or None if encryption key not configured.
        """
        if not settings.token_encryption_key:
            logger.warning("TOKEN_ENCRYPTION_KEY not configured, using base64 encoding (not secure for production!)")
            return None
        try:
            return Fernet(settings.token_encryption_key.encode())
        except Exception as e:
            logger.error(f"Failed to initialize Fernet: {type(e).__name__}")
            return None
    
    @staticmethod
    def encrypt_token(token: str) -> str:
        """
        Encrypt a token for secure storage.
        
        Args:
            token: Plain text token
            
        Returns:
            Encrypted token string
        """
        fernet = GitHubService._get_fernet()
        if fernet:
            return fernet.encrypt(token.encode()).decode()
        # Fallback: base64 encoding (NOT SECURE - only for development)
        import base64
        return base64.b64encode(token.encode()).decode()
    
    @staticmethod
    def decrypt_token(encrypted_token: str) -> str:
        """
        Decrypt a stored token.
        
        Args:
            encrypted_token: Encrypted token string
            
        Returns:
            Plain text token
        """
        fernet = GitHubService._get_fernet()
        if fernet:
            return fernet.decrypt(encrypted_token.encode()).decode()
        # Fallback: base64 decoding
        import base64
        return base64.b64decode(encrypted_token.encode()).decode()
    
    @staticmethod
    def generate_state() -> str:
        """
        Generate a random state parameter for OAuth flow.
        
        Returns:
            Random URL-safe string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_authorization_url(state: str) -> str:
        """
        Generate GitHub OAuth authorization URL.
        
        Args:
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        if not settings.github_client_id:
            raise ValueError("GITHUB_CLIENT_ID not configured")
        
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_callback_url,
            "scope": GITHUB_SCOPES,
            "state": state,
        }
        
        return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Optional[GitHubTokenInfo]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from GitHub callback
            
        Returns:
            Token information or None if exchange failed
        """
        if not settings.github_client_id or not settings.github_client_secret:
            logger.error("GitHub OAuth not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GITHUB_TOKEN_URL,
                    data={
                        "client_id": settings.github_client_id,
                        "client_secret": settings.github_client_secret,
                        "code": code,
                        "redirect_uri": settings.github_callback_url,
                    },
                    headers={
                        "Accept": "application/json",
                    },
                    timeout=30.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub token exchange failed: {response.status_code}")
                    return None
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"GitHub OAuth error: {data.get('error_description', data.get('error'))}")
                    return None
                
                return GitHubTokenInfo(
                    access_token=data["access_token"],
                    token_type=data.get("token_type", "bearer"),
                    scope=data.get("scope", ""),
                )
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {type(e).__name__}")
            return None
    
    @staticmethod
    async def get_user_info(access_token: str) -> Optional[GitHubUserInfo]:
        """
        Fetch GitHub user information using access token.
        
        Args:
            access_token: GitHub access token
            
        Returns:
            User information or None if request failed
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get user profile
                response = await client.get(
                    f"{GITHUB_API_URL}/user",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub API error: {response.status_code}")
                    return None
                
                user_data = response.json()
                
                # Get user email if not public
                email = user_data.get("email")
                if not email:
                    email_response = await client.get(
                        f"{GITHUB_API_URL}/user/emails",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28",
                        },
                        timeout=30.0,
                    )
                    
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        # Get primary email
                        for e in emails:
                            if e.get("primary"):
                                email = e.get("email")
                                break
                
                return GitHubUserInfo(
                    id=str(user_data["id"]),
                    login=user_data["login"],
                    avatar_url=user_data.get("avatar_url", ""),
                    email=email,
                )
        except Exception as e:
            logger.error(f"Failed to get user info: {type(e).__name__}")
            return None
    
    @staticmethod
    async def create_connection(
        db: AsyncSession,
        team_id: int,
        connected_by_user_id: int,
        token_info: GitHubTokenInfo,
        user_info: GitHubUserInfo,
    ) -> GitHubConnection:
        """
        Create or update a GitHub connection for a team.
        
        Args:
            db: Database session
            team_id: Internal team ID
            connected_by_user_id: ID of user who connected the account
            token_info: Token information from OAuth
            user_info: User information from GitHub API
            
        Returns:
            Created or updated GitHubConnection
        """
        # Check if connection already exists for this GitHub user in this team
        result = await db.execute(
            select(GitHubConnection).where(
                GitHubConnection.team_id == team_id,
                GitHubConnection.github_user_id == user_info["id"],
            )
        )
        existing = result.scalar_one_or_none()
        
        encrypted_token = GitHubService.encrypt_token(token_info["access_token"])
        
        if existing:
            # Update existing connection
            existing.access_token = encrypted_token
            existing.token_type = token_info["token_type"]
            existing.scope = token_info["scope"]
            existing.github_username = user_info["login"]
            existing.github_avatar_url = user_info["avatar_url"]
            existing.github_email = user_info["email"]
            existing.connected_by_user_id = connected_by_user_id
            
            await db.commit()
            await db.refresh(existing)
            
            logger.info(f"Updated GitHub connection for team {team_id}, GitHub user {user_info['login']}")
            return existing
        
        # Create new connection
        connection = GitHubConnection(
            team_id=team_id,
            connected_by_user_id=connected_by_user_id,
            access_token=encrypted_token,
            token_type=token_info["token_type"],
            scope=token_info["scope"],
            github_user_id=user_info["id"],
            github_username=user_info["login"],
            github_avatar_url=user_info["avatar_url"],
            github_email=user_info["email"],
        )
        
        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        
        logger.info(f"Created GitHub connection for team {team_id}, GitHub user {user_info['login']}")
        return connection
    
    @staticmethod
    async def get_connections_by_team(
        db: AsyncSession,
        team_id: int,
    ) -> list[GitHubConnection]:
        """
        Get all GitHub connections for a team.
        
        Args:
            db: Database session
            team_id: Internal team ID
            
        Returns:
            List of GitHubConnection objects
        """
        result = await db.execute(
            select(GitHubConnection)
            .where(GitHubConnection.team_id == team_id)
            .order_by(GitHubConnection.connected_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_connection_by_public_id(
        db: AsyncSession,
        public_id: str,
    ) -> Optional[GitHubConnection]:
        """
        Get a GitHub connection by public ID.
        
        Args:
            db: Database session
            public_id: Public UUID of the connection
            
        Returns:
            GitHubConnection or None
        """
        try:
            uuid_obj = UUID(public_id)
            result = await db.execute(
                select(GitHubConnection).where(GitHubConnection.public_id == uuid_obj)
            )
            return result.scalar_one_or_none()
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    async def delete_connection_by_public_id(
        db: AsyncSession,
        public_id: str,
        team_id: int,
    ) -> bool:
        """
        Delete a GitHub connection by public ID.
        
        Args:
            db: Database session
            public_id: Public UUID of the connection
            team_id: Internal team ID (for authorization check)
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            uuid_obj = UUID(public_id)
            result = await db.execute(
                delete(GitHubConnection)
                .where(
                    GitHubConnection.public_id == uuid_obj,
                    GitHubConnection.team_id == team_id,
                )
                .returning(GitHubConnection.id)
            )
            
            deleted = result.scalar_one_or_none()
            
            if deleted:
                await db.commit()
                logger.info(f"Deleted GitHub connection {public_id} for team {team_id}")
                return True
            
            return False
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def get_decrypted_token(connection: GitHubConnection) -> str:
        """
        Get decrypted access token from a connection.
        
        Args:
            connection: GitHubConnection object
            
        Returns:
            Decrypted access token
        """
        return GitHubService.decrypt_token(connection.access_token)
    
    @staticmethod
    async def list_user_repositories(access_token: str) -> list[GitHubRepoInfo]:
        """
        List all repositories accessible by the authenticated user.
        
        Args:
            access_token: GitHub access token
            
        Returns:
            List of repository information
        """
        repos: list[GitHubRepoInfo] = []
        page = 1
        per_page = 100
        
        try:
            async with httpx.AsyncClient() as client:
                while True:
                    response = await client.get(
                        f"{GITHUB_API_URL}/user/repos",
                        params={
                            "per_page": per_page,
                            "page": page,
                            "sort": "updated",
                            "direction": "desc",
                            "affiliation": "owner,collaborator,organization_member",
                        },
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28",
                        },
                        timeout=30.0,
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"GitHub API error: {response.status_code}")
                        break
                    
                    data = response.json()
                    
                    if not data:
                        break
                    
                    for repo in data:
                        repos.append(GitHubRepoInfo(
                            id=str(repo["id"]),
                            full_name=repo["full_name"],
                            name=repo["name"],
                            owner=repo["owner"]["login"],
                            default_branch=repo.get("default_branch", "main"),
                            private=repo.get("private", False),
                            description=repo.get("description"),
                            html_url=repo.get("html_url", ""),
                        ))
                    
                    # Check if there are more pages
                    if len(data) < per_page:
                        break
                    
                    page += 1
                    
                    # Safety limit
                    if page > 10:
                        break
            
            return repos
        except Exception as e:
            logger.error(f"Failed to list repositories: {type(e).__name__}")
            return []
    
    @staticmethod
    async def get_repository_by_project(
        db: AsyncSession,
        project_id: int,
    ) -> Optional[Repository]:
        """
        Get repository linked to a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            
        Returns:
            Repository or None
        """
        result = await db.execute(
            select(Repository).where(Repository.project_id == project_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_repository_by_public_id(
        db: AsyncSession,
        public_id: str,
    ) -> Optional[Repository]:
        """
        Get repository by public ID.
        
        Args:
            db: Database session
            public_id: Public UUID of the repository
            
        Returns:
            Repository or None
        """
        try:
            uuid_obj = UUID(public_id)
            result = await db.execute(
                select(Repository).where(Repository.public_id == uuid_obj)
            )
            return result.scalar_one_or_none()
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    async def connect_repository(
        db: AsyncSession,
        project_id: int,
        github_connection_id: int,
        repo_info: GitHubRepoInfo,
        i18n_framework: Optional[str] = None,
        source_patterns: Optional[list[str]] = None,
        locale_path: Optional[str] = None,
    ) -> Repository:
        """
        Connect a GitHub repository to a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            github_connection_id: Internal GitHub connection ID
            repo_info: Repository information from GitHub
            i18n_framework: Optional i18n framework name
            source_patterns: Optional source file patterns
            locale_path: Optional path to locale files
            
        Returns:
            Created or updated Repository
        """
        # Check if repository already exists for this project
        result = await db.execute(
            select(Repository).where(Repository.project_id == project_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing repository
            existing.github_connection_id = github_connection_id
            existing.github_repo_id = repo_info["id"]
            existing.repo_owner = repo_info["owner"]
            existing.repo_name = repo_info["name"]
            existing.default_branch = repo_info["default_branch"]
            
            if i18n_framework is not None:
                existing.i18n_framework = i18n_framework
            if source_patterns is not None:
                existing.source_patterns = source_patterns
            if locale_path is not None:
                existing.locale_path = locale_path
            
            await db.commit()
            await db.refresh(existing)
            
            logger.info(f"Updated repository {repo_info['full_name']} for project {project_id}")
            return existing
        
        # Create new repository
        repository = Repository(
            project_id=project_id,
            github_connection_id=github_connection_id,
            github_repo_id=repo_info["id"],
            repo_owner=repo_info["owner"],
            repo_name=repo_info["name"],
            default_branch=repo_info["default_branch"],
            i18n_framework=i18n_framework,
            source_patterns=source_patterns or [],
            locale_path=locale_path,
        )
        
        db.add(repository)
        await db.commit()
        await db.refresh(repository)
        
        logger.info(f"Connected repository {repo_info['full_name']} to project {project_id}")
        return repository
    
    @staticmethod
    async def disconnect_repository(
        db: AsyncSession,
        repository_id: int,
    ) -> bool:
        """
        Disconnect a repository from a project.
        
        Args:
            db: Database session
            repository_id: Internal repository ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await db.execute(
            delete(Repository)
            .where(Repository.id == repository_id)
            .returning(Repository.id)
        )
        
        deleted = result.scalar_one_or_none()
        
        if deleted:
            await db.commit()
            logger.info(f"Disconnected repository {repository_id}")
            return True
        
        return False
