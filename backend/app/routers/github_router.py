"""
GitHub OAuth Router for handling OAuth flow.
GitHub connections are linked to Teams.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.database import async_get_db
from app.services.github_service import GitHubService
from app.services.user_service import UserService
from app.services.team_service import TeamService
from app.core.security import decode_access_token
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/github", tags=["github"])

# In-memory state storage (for production, use Redis or database)
# Format: {state: {"user_public_id": str, "team_public_id": str}}
_oauth_states: dict[str, dict[str, str]] = {}


@router.get("/callback")
async def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: AsyncSession = Depends(async_get_db),
):
    """
    Handle GitHub OAuth callback.
    
    Exchanges authorization code for access token and creates/updates
    the GitHub connection for the team.
    
    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF verification
        db: Database session
        
    Returns:
        Redirect to frontend with success/error
    """
    # Verify state parameter
    state_data = _oauth_states.pop(state, None)
    
    if not state_data:
        logger.warning(f"Invalid OAuth state: {state}")
        error_url = f"{settings.app_url}/github/callback?error=invalid_state"
        return RedirectResponse(url=error_url)
    
    user_public_id = state_data.get("user_public_id")
    team_public_id = state_data.get("team_public_id")
    
    if not user_public_id or not team_public_id:
        logger.warning("Missing user or team in state data")
        error_url = f"{settings.app_url}/github/callback?error=invalid_state"
        return RedirectResponse(url=error_url)
    
    # Get user
    user = await UserService.get_user_by_public_id(db, user_public_id)
    if not user:
        logger.warning(f"User not found for public_id: {user_public_id}")
        error_url = f"{settings.app_url}/github/callback?error=user_not_found"
        return RedirectResponse(url=error_url)
    
    # Get team
    team = await TeamService.get_team_by_public_id(db, team_public_id)
    if not team:
        logger.warning(f"Team not found for public_id: {team_public_id}")
        error_url = f"{settings.app_url}/github/callback?error=team_not_found"
        return RedirectResponse(url=error_url)
    
    # Check if user has permission to manage team (admin or owner)
    is_owner = team.owner_id == user.id
    is_admin = await TeamService.check_user_team_role(db, team.id, user.id, "admin")
    
    if not is_owner and not is_admin:
        logger.warning(f"User {user.id} doesn't have permission to connect GitHub for team {team.id}")
        error_url = f"{settings.app_url}/github/callback?error=permission_denied"
        return RedirectResponse(url=error_url)
    
    # Exchange code for token
    token_info = await GitHubService.exchange_code_for_token(code)
    if not token_info:
        logger.error("Failed to exchange code for token")
        error_url = f"{settings.app_url}/github/callback?error=token_exchange_failed"
        return RedirectResponse(url=error_url)
    
    # Get GitHub user info
    user_info = await GitHubService.get_user_info(token_info["access_token"])
    if not user_info:
        logger.error("Failed to get GitHub user info")
        error_url = f"{settings.app_url}/github/callback?error=user_info_failed"
        return RedirectResponse(url=error_url)
    
    try:
        # Create/update connection for team
        connection = await GitHubService.create_connection(
            db=db,
            team_id=team.id,
            connected_by_user_id=user.id,
            token_info=token_info,
            user_info=user_info,
        )
        
        logger.info(f"GitHub connection created/updated for team {team.name}: {user_info['login']}")
        
        # Redirect to frontend with success
        success_url = f"{settings.app_url}/github/callback?success=true&username={user_info['login']}&team={team_public_id}"
        return RedirectResponse(url=success_url)
        
    except Exception as e:
        logger.error(f"Failed to create GitHub connection: {type(e).__name__}")
        error_url = f"{settings.app_url}/github/callback?error=connection_failed"
        return RedirectResponse(url=error_url)
