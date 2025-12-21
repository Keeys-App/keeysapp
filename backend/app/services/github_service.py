"""
GitHub OAuth Service for handling GitHub integration.
GitHub connections are linked to Teams, not individual Users.
"""
import secrets
import logging
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, TypedDict
from urllib.parse import urlencode
from cryptography.fernet import Fernet

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from uuid import UUID

from app.core.config import settings
from app.models.github_connection import GitHubConnection
from app.models.repository import Repository

logger = logging.getLogger(__name__)

# Shared OAuth state storage (for production, use Redis or database)
# Format: {state: {"user_public_id": str, "team_public_id": str}}
oauth_states: dict[str, dict[str, str]] = {}

# GitHub OAuth URLs
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"
GITHUB_APP_INSTALL_URL = "https://github.com/apps"

# Required scopes for repository access
GITHUB_SCOPES = "repo read:user user:email"


class GitHubUserInfo(TypedDict):
    """Type definition for GitHub user information."""
    id: str
    login: str
    avatar_url: str
    email: Optional[str]


class GitHubTokenInfo(TypedDict, total=False):
    """Type definition for GitHub token information."""
    access_token: str  # Required
    token_type: str  # Required
    scope: str  # Required
    refresh_token: Optional[str]  # Present if token expiration is enabled
    expires_in: Optional[int]  # Seconds until access_token expires


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
        
        For GitHub Apps, this uses the same OAuth flow but the App's
        client_id/secret. The installed App determines which repos are accessible.
        
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
    def get_app_installation_url(state: Optional[str] = None) -> Optional[str]:
        """
        Get GitHub App installation URL for manual installation.
        
        Args:
            state: Optional state parameter (e.g., team_public_id) for redirect after installation
        
        Returns:
            Installation URL or None if app slug not configured
        """
        if not settings.github_app_slug:
            return None
        base_url = f"{GITHUB_APP_INSTALL_URL}/{settings.github_app_slug}/installations/new"
        if state:
            return f"{base_url}?state={state}"
        return base_url
    
    @staticmethod
    async def get_user_installations(access_token: str) -> list[dict]:
        """
        Get list of GitHub App installations for the authenticated user.
        
        Args:
            access_token: GitHub user access token
            
        Returns:
            List of installation objects
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GITHUB_API_URL}/user/installations",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                logger.info(f"GET /user/installations: status={response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Failed to get installations: {response.status_code} - {response.text}")
                    return []
                
                data = response.json()
                installations = data.get("installations", [])
                logger.info(f"Found {len(installations)} installations: {[i.get('account', {}).get('login') for i in installations]}")
                if installations:
                    # Log first installation to debug html_url
                    logger.info(f"First installation keys: {list(installations[0].keys())}")
                    logger.info(f"First installation html_url: {installations[0].get('html_url')}")
                return installations
        except Exception as e:
            logger.error(f"Error getting installations: {type(e).__name__}: {str(e)}")
            return []
    
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
                
                token_info: GitHubTokenInfo = {
                    "access_token": data["access_token"],
                    "token_type": data.get("token_type", "bearer"),
                    "scope": data.get("scope", ""),
                }
                
                # Include refresh_token and expires_in if present (expiring tokens enabled)
                if "refresh_token" in data:
                    token_info["refresh_token"] = data["refresh_token"]
                    logger.info("GitHub OAuth returned refresh_token (expiring tokens enabled)")
                
                if "expires_in" in data:
                    token_info["expires_in"] = int(data["expires_in"])
                    logger.info(f"GitHub token expires in {data['expires_in']} seconds")
                
                return token_info
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
    async def validate_token(access_token: str) -> bool:
        """
        Validate if a GitHub access token is still valid.
        
        Args:
            access_token: GitHub access token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GITHUB_API_URL}/user",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate token: {type(e).__name__}")
            return False
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Optional[GitHubTokenInfo]:
        """
        Refresh an expired access token using the refresh token.
        
        Args:
            refresh_token: Refresh token from GitHub OAuth
            
        Returns:
            New token information or None if refresh failed
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
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    },
                    headers={
                        "Accept": "application/json",
                    },
                    timeout=30.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub token refresh failed: {response.status_code}")
                    return None
                
                data = response.json()
                
                if "error" in data:
                    logger.error(f"GitHub OAuth refresh error: {data.get('error_description', data.get('error'))}")
                    return None
                
                token_info: GitHubTokenInfo = {
                    "access_token": data["access_token"],
                    "token_type": data.get("token_type", "bearer"),
                    "scope": data.get("scope", ""),
                }
                
                # Include new refresh_token if provided (GitHub rotates refresh tokens)
                if "refresh_token" in data:
                    token_info["refresh_token"] = data["refresh_token"]
                
                if "expires_in" in data:
                    token_info["expires_in"] = int(data["expires_in"])
                
                logger.info("Successfully refreshed GitHub access token")
                return token_info
        except Exception as e:
            logger.error(f"Failed to refresh access token: {type(e).__name__}")
            return None
    
    @staticmethod
    async def get_valid_access_token(
        db: AsyncSession,
        connection: GitHubConnection,
    ) -> Optional[str]:
        """
        Get a valid access token for a connection, refreshing if needed.
        
        This method checks if the token is expired and automatically refreshes it
        using the refresh_token if available.
        
        Args:
            db: Database session
            connection: GitHubConnection object
            
        Returns:
            Valid access token or None if refresh failed
        """
        access_token = GitHubService.decrypt_token(connection.access_token)
        
        # Check if token has expiration time set
        if connection.token_expires_at is not None:
            # Refresh 5 minutes before expiration to avoid race conditions
            refresh_threshold = datetime.now(timezone.utc) + timedelta(minutes=5)
            
            if connection.token_expires_at <= refresh_threshold:
                logger.info(f"Token expired or expiring soon for connection {connection.id}, attempting refresh")
                
                # Check if we have a refresh token
                if not connection.refresh_token:
                    logger.warning(f"No refresh token available for connection {connection.id}")
                    return None
                
                # Decrypt and use refresh token
                decrypted_refresh_token = GitHubService.decrypt_token(connection.refresh_token)
                new_token_info = await GitHubService.refresh_access_token(decrypted_refresh_token)
                
                if not new_token_info:
                    logger.error(f"Failed to refresh token for connection {connection.id}")
                    return None
                
                # Update connection with new tokens
                encrypted_access = GitHubService.encrypt_token(new_token_info["access_token"])
                
                update_values = {
                    "access_token": encrypted_access,
                }
                
                # Update refresh token if GitHub rotated it
                if new_token_info.get("refresh_token"):
                    update_values["refresh_token"] = GitHubService.encrypt_token(new_token_info["refresh_token"])
                
                # Update expiration time
                if new_token_info.get("expires_in"):
                    update_values["token_expires_at"] = datetime.now(timezone.utc) + timedelta(
                        seconds=new_token_info["expires_in"]
                    )
                
                await db.execute(
                    update(GitHubConnection)
                    .where(GitHubConnection.id == connection.id)
                    .values(**update_values)
                )
                await db.commit()
                
                logger.info(f"Successfully refreshed and updated token for connection {connection.id}")
                return new_token_info["access_token"]
        
        return access_token
    
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
        
        # Encrypt refresh_token if present
        encrypted_refresh = None
        if token_info.get("refresh_token"):
            encrypted_refresh = GitHubService.encrypt_token(token_info["refresh_token"])
        
        # Calculate token expiration time if expires_in is provided
        token_expires_at = None
        if token_info.get("expires_in"):
            token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_info["expires_in"])
        
        if existing:
            # Update existing connection
            existing.access_token = encrypted_token
            existing.token_type = token_info["token_type"]
            existing.scope = token_info["scope"]
            existing.github_username = user_info["login"]
            existing.github_avatar_url = user_info["avatar_url"]
            existing.github_email = user_info["email"]
            existing.connected_by_user_id = connected_by_user_id
            
            # Update refresh token fields
            if encrypted_refresh is not None:
                existing.refresh_token = encrypted_refresh
            if token_expires_at is not None:
                existing.token_expires_at = token_expires_at
            
            await db.commit()
            await db.refresh(existing)
            
            logger.info(f"Updated GitHub connection for team {team_id}, GitHub user {user_info['login']}")
            return existing
        
        # Create new connection
        connection = GitHubConnection(
            team_id=team_id,
            connected_by_user_id=connected_by_user_id,
            access_token=encrypted_token,
            refresh_token=encrypted_refresh,
            token_expires_at=token_expires_at,
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
        List repositories accessible via GitHub App installations.
        Only returns repositories that the GitHub App has been granted access to.
        
        Args:
            access_token: GitHub access token
            
        Returns:
            List of repository information
        """
        repos: list[GitHubRepoInfo] = []
        seen_repo_ids: set[str] = set()
        
        try:
            # First, get all installations for the user
            installations = await GitHubService.get_user_installations(access_token)
            
            if not installations:
                logger.warning("No GitHub App installations found, no repositories available")
                return []
            
            async with httpx.AsyncClient() as client:
                # For each installation, get accessible repositories
                for installation in installations:
                    installation_id = installation.get("id")
                    if not installation_id:
                        continue
                    
                    account_login = installation.get("account", {}).get("login", "unknown")
                    logger.info(f"Fetching repos for installation {installation_id} ({account_login})")
                    
                    page = 1
                    per_page = 100
                    
                    while True:
                        response = await client.get(
                            f"{GITHUB_API_URL}/user/installations/{installation_id}/repositories",
                            params={
                                "per_page": per_page,
                                "page": page,
                            },
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "Accept": "application/vnd.github+json",
                                "X-GitHub-Api-Version": "2022-11-28",
                            },
                            timeout=30.0,
                        )
                        
                        if response.status_code != 200:
                            logger.error(f"GitHub API error for installation {installation_id}: {response.status_code} - {response.text}")
                            break
                        
                        data = response.json()
                        repositories = data.get("repositories", [])
                        
                        if not repositories:
                            break
                        
                        for repo in repositories:
                            repo_id = str(repo["id"])
                            # Avoid duplicates if same repo is accessible via multiple installations
                            if repo_id not in seen_repo_ids:
                                seen_repo_ids.add(repo_id)
                                repos.append(GitHubRepoInfo(
                                    id=repo_id,
                                    full_name=repo["full_name"],
                                    name=repo["name"],
                                    owner=repo["owner"]["login"],
                                    default_branch=repo.get("default_branch", "main"),
                                    private=repo.get("private", False),
                                    description=repo.get("description"),
                                    html_url=repo.get("html_url", ""),
                                ))
                        
                        logger.info(f"Installation {account_login} page {page}: {len(repositories)} repos, total unique: {len(repos)}")
                        
                        # Check if there are more pages
                        total_count = data.get("total_count", 0)
                        if len(repos) >= total_count or len(repositories) < per_page:
                            break
                        
                        page += 1
                        
                        # Safety limit
                        if page > 50:
                            logger.warning(f"Hit page limit for installation {installation_id}")
                            break
                
                # Sort by full_name for consistent ordering
                repos.sort(key=lambda r: r["full_name"].lower())
                logger.info(f"Total repositories fetched from {len(installations)} installations: {len(repos)}")
            
            return repos
        except Exception as e:
            logger.error(f"Failed to list repositories: {type(e).__name__}: {str(e)}")
            return []
    
    @staticmethod
    async def search_repositories(access_token: str, query: str) -> list[GitHubRepoInfo]:
        """
        Search for repositories by filtering accessible repos locally.
        Only searches within repositories the GitHub App has access to.
        
        Args:
            access_token: GitHub access token
            query: Search query (filters by full_name, name, or owner)
            
        Returns:
            List of repository information matching the query
        """
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        
        try:
            # Get all accessible repos and filter
            all_repos = await GitHubService.list_user_repositories(access_token)
            
            matched_repos: list[GitHubRepoInfo] = []
            for repo in all_repos:
                full_name = repo["full_name"].lower()
                name = repo["name"].lower()
                owner = repo["owner"].lower()
                
                # Match if query is found in full_name, name, or owner
                if query_lower in full_name or query_lower in name or query_lower in owner:
                    matched_repos.append(repo)
            
            logger.info(f"Search complete: found {len(matched_repos)} repos matching '{query}' out of {len(all_repos)} accessible")
            return matched_repos
        except Exception as e:
            logger.error(f"Failed to search repositories: {type(e).__name__}: {str(e)}")
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
        branch: Optional[str] = None,
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
            branch: Branch to use for scanning (defaults to repo's default branch)
            i18n_framework: Optional i18n framework name
            source_patterns: Optional source file patterns
            locale_path: Optional path to locale files
            
        Returns:
            Created or updated Repository
        """
        # Use provided branch or default branch from repo
        selected_branch = branch or repo_info["default_branch"]
        
        # Check if repository already exists for this project
        result = await db.execute(
            select(Repository).where(Repository.project_id == project_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing repository (repo_info is TypedDict)
            existing.github_connection_id = github_connection_id
            existing.github_repo_id = repo_info["id"]
            existing.repo_owner = repo_info["owner"]
            existing.repo_name = repo_info["name"]
            existing.default_branch = selected_branch
            
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
        
        # Create new repository (repo_info is TypedDict)
        repository = Repository(
            project_id=project_id,
            github_connection_id=github_connection_id,
            github_repo_id=repo_info["id"],
            repo_owner=repo_info["owner"],
            repo_name=repo_info["name"],
            default_branch=selected_branch,
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

    @staticmethod
    async def get_repository_branches(
        access_token: str,
        owner: str,
        repo: str,
    ) -> list[dict]:
        """
        Get list of branches for a repository.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of branches with name and commit info
        """
        try:
            branches = []
            page = 1
            per_page = 100
            
            async with httpx.AsyncClient() as client:
                while True:
                    response = await client.get(
                        f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches",
                        params={"per_page": per_page, "page": page},
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28",
                        },
                        timeout=30.0,
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"Failed to get branches: {response.status_code}")
                        break
                    
                    page_branches = response.json()
                    if not page_branches:
                        break
                    
                    branches.extend(page_branches)
                    
                    # Check if there are more pages
                    if len(page_branches) < per_page:
                        break
                    page += 1
            
            logger.info(f"Found {len(branches)} branches for {owner}/{repo}")
            return branches
            
        except Exception as e:
            logger.error(f"Error getting branches: {type(e).__name__}: {str(e)}")
            return []

    @staticmethod
    async def get_repository_tree(
        access_token: str,
        owner: str,
        repo: str,
        branch: str = "main",
        recursive: bool = True,
    ) -> list[dict]:
        """
        Get the file tree of a repository.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            branch: Branch name (default: main)
            recursive: Whether to get recursive tree (default: True)
            
        Returns:
            List of tree entries with path, type, sha, etc.
        """
        try:
            async with httpx.AsyncClient() as client:
                # First, get the branch's commit SHA
                branch_response = await client.get(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches/{branch}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if branch_response.status_code != 200:
                    logger.error(f"Failed to get branch info: {branch_response.status_code}")
                    return []
                
                branch_data = branch_response.json()
                tree_sha = branch_data.get("commit", {}).get("commit", {}).get("tree", {}).get("sha")
                
                if not tree_sha:
                    logger.error("Could not get tree SHA from branch")
                    return []
                
                # Get the tree
                params = {"recursive": "1"} if recursive else {}
                tree_response = await client.get(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/{tree_sha}",
                    params=params,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=60.0,
                )
                
                if tree_response.status_code != 200:
                    logger.error(f"Failed to get tree: {tree_response.status_code}")
                    return []
                
                tree_data = tree_response.json()
                tree = tree_data.get("tree", [])
                
                logger.info(f"Got repository tree with {len(tree)} entries")
                return tree
                
        except Exception as e:
            logger.error(f"Failed to get repository tree: {type(e).__name__}: {str(e)}")
            return []
    
    @staticmethod
    async def get_file_content(
        access_token: str,
        owner: str,
        repo: str,
        path: str,
        branch: str = "main",
    ) -> Optional[str]:
        """
        Get the content of a file from a repository.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            path: Path to the file
            branch: Branch name (default: main)
            
        Returns:
            File content as string, or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}",
                    params={"ref": branch},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get file content: {response.status_code} - {path}")
                    return None
                
                data = response.json()
                
                # Check if it's a file (not directory)
                if data.get("type") != "file":
                    logger.warning(f"Path is not a file: {path}")
                    return None
                
                # Content is base64 encoded
                import base64
                content_b64 = data.get("content", "")
                
                if not content_b64:
                    return ""
                
                # Decode base64 content
                try:
                    content = base64.b64decode(content_b64).decode("utf-8")
                    return content
                except Exception as e:
                    logger.error(f"Failed to decode file content: {type(e).__name__}")
                    return None
                
        except Exception as e:
            logger.error(f"Failed to get file content: {type(e).__name__}: {str(e)}")
            return None
    
    @staticmethod
    def filter_files_by_patterns(
        tree: list[dict],
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Filter repository tree entries by file patterns.
        
        Args:
            tree: List of tree entries from get_repository_tree
            include_patterns: List of patterns to include (e.g., ["*.tsx", "*.vue"])
            exclude_patterns: List of patterns to exclude (e.g., ["*.test.*", "node_modules/*"])
            
        Returns:
            Filtered list of tree entries (files only, not directories)
        """
        import fnmatch
        
        # Default patterns if not specified
        if include_patterns is None:
            include_patterns = ["*.tsx", "*.jsx", "*.vue", "*.svelte", "*.ts", "*.js"]
        
        if exclude_patterns is None:
            exclude_patterns = [
                "*.test.*", "*.spec.*", "*.stories.*",
                "node_modules/*", "dist/*", "build/*", ".next/*",
                "*.d.ts", "*.config.*", "*.min.*",
                "__tests__/*", "__mocks__/*",
            ]
        
        filtered = []
        
        for entry in tree:
            # Only process files (blob type)
            if entry.get("type") != "blob":
                continue
            
            path = entry.get("path", "")
            
            # Check exclude patterns first
            excluded = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"**/{pattern}"):
                    excluded = True
                    break
            
            if excluded:
                continue
            
            # Check include patterns
            included = False
            for pattern in include_patterns:
                # Get just the filename for extension matching
                filename = path.split("/")[-1]
                if fnmatch.fnmatch(filename, pattern):
                    included = True
                    break
            
            if included:
                filtered.append(entry)
        
            logger.info(f"Filtered {len(tree)} entries to {len(filtered)} files")
        return filtered
    
    @staticmethod
    async def create_branch(
        access_token: str,
        owner: str,
        repo: str,
        branch_name: str,
        source_branch: str = "main",
    ) -> Optional[str]:
        """
        Create a new branch in a repository.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            branch_name: Name for the new branch
            source_branch: Source branch to base off (default: main)
            
        Returns:
            SHA of the new branch ref, or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get source branch SHA
                ref_response = await client.get(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/ref/heads/{source_branch}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if ref_response.status_code != 200:
                    logger.error(f"Failed to get source branch ref: {ref_response.status_code}")
                    return None
                
                ref_data = ref_response.json()
                source_sha = ref_data.get("object", {}).get("sha")
                
                if not source_sha:
                    logger.error("Could not get source branch SHA")
                    return None
                
                # Create new branch
                create_response = await client.post(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/refs",
                    json={
                        "ref": f"refs/heads/{branch_name}",
                        "sha": source_sha,
                    },
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if create_response.status_code in (201, 200):
                    logger.info(f"Created branch {branch_name} from {source_branch}")
                    return source_sha
                elif create_response.status_code == 422:
                    # Branch might already exist
                    logger.info(f"Branch {branch_name} may already exist")
                    return source_sha
                else:
                    logger.error(f"Failed to create branch: {create_response.status_code} - {create_response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to create branch: {type(e).__name__}: {str(e)}")
            return None
    
    @staticmethod
    async def get_file_sha(
        access_token: str,
        owner: str,
        repo: str,
        path: str,
        branch: str = "main",
    ) -> Optional[str]:
        """
        Get the SHA of a file in the repository.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            path: Path to the file
            branch: Branch name (default: main)
            
        Returns:
            File SHA or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}",
                    params={"ref": branch},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                return data.get("sha")
                
        except Exception as e:
            logger.error(f"Failed to get file SHA: {type(e).__name__}: {str(e)}")
            return None
    
    @staticmethod
    async def update_file(
        access_token: str,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        file_sha: Optional[str] = None,
    ) -> bool:
        """
        Update or create a file in the repository.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            path: Path to the file
            content: New file content
            message: Commit message
            branch: Branch to commit to
            file_sha: Current file SHA (required for updates)
            
        Returns:
            True if successful, False otherwise
        """
        import base64
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": message,
                    "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                    "branch": branch,
                }
                
                if file_sha:
                    payload["sha"] = file_sha
                
                response = await client.put(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if response.status_code in (200, 201):
                    logger.info(f"Updated file {path} on branch {branch}")
                    return True
                else:
                    logger.error(f"Failed to update file: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update file: {type(e).__name__}: {str(e)}")
            return False
    
    @staticmethod
    async def create_pull_request(
        access_token: str,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> Optional[dict]:
        """
        Create a pull request.
        
        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo: Repository name
            title: PR title
            body: PR description
            head: Source branch name
            base: Target branch name (default: main)
            
        Returns:
            PR data dict with 'number', 'html_url', etc. or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls",
                    json={
                        "title": title,
                        "body": body,
                        "head": head,
                        "base": base,
                    },
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 201:
                    pr_data = response.json()
                    logger.info(f"Created PR #{pr_data.get('number')}: {title}")
                    return {
                        "number": pr_data.get("number"),
                        "html_url": pr_data.get("html_url"),
                        "id": pr_data.get("id"),
                        "state": pr_data.get("state"),
                    }
                elif response.status_code == 422:
                    # PR might already exist
                    error_data = response.json()
                    logger.warning(f"PR creation returned 422: {error_data}")
                    return None
                else:
                    logger.error(f"Failed to create PR: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to create PR: {type(e).__name__}: {str(e)}")
            return None