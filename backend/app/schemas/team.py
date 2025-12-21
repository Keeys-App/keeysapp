import strawberry
import enum
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import AsyncSessionLocal
from app.services.team_service import TeamService
from app.services.user_service import UserService
from app.models.team import Team, TeamMember
from app.models.team_invitation import TeamInvitation
from app.core.exceptions import (
    UnauthorizedError,
    handle_database_exception
)
from app.schemas.auth import UserType

if TYPE_CHECKING:
    from app.schemas.key import ActivityLogType

logger = logging.getLogger(__name__)


@strawberry.type
class TeamMemberType:
    """
    GraphQL type for TeamMember.
    """
    user: UserType
    role: str
    created_at: datetime


@strawberry.type
class TeamInvitationType:
    """
    GraphQL type for TeamInvitation.
    """
    id: str  # UUID as string
    invited_email: str
    role: str
    status: str  # PENDING, ACCEPTED, DECLINED
    invited_by: Optional[UserType]
    created_at: datetime


@strawberry.type
class InviteInfoType:
    """
    Public information about an invitation (no auth required).
    """
    id: str  # UUID
    team_name: str
    team_description: Optional[str]
    inviter_name: str
    inviter_email: str
    role: str
    status: str
    invited_email: str
    created_at: datetime


@strawberry.type
class PendingInviteType:
    """
    Pending invitation for the current user.
    """
    id: str  # UUID
    team_name: str
    team_description: Optional[str]
    inviter_name: str
    role: str
    created_at: datetime


@strawberry.enum
class AIProviderEnum(str, enum.Enum):
    """Enum for AI provider types in GraphQL."""
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


@strawberry.type
class TeamType:
    """
    GraphQL type for Team.
    Uses public_id (UUID) instead of internal ID for security.
    """
    id: str  # UUID as string for public API
    name: str
    description: Optional[str]
    owner: UserType
    members: List[TeamMemberType]
    invitations: List[TeamInvitationType]  # Pending invitations
    can_manage: bool  # Whether current user can manage the team
    members_count: int
    # AI Settings - global LLM configuration
    ai_provider: Optional[str]  # OPENAI or ANTHROPIC
    ai_model: Optional[str]  # e.g., gpt-4o-mini, claude-haiku-4-5
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.input
class CreateTeamInput:
    """
    Input type for creating a team.
    """
    name: str
    description: Optional[str] = None


@strawberry.input
class UpdateTeamInput:
    """
    Input type for updating a team.
    """
    id: str  # UUID
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class AddTeamMemberInput:
    """
    Input type for adding a member to a team.
    """
    team_id: str  # UUID
    user_email: str  # Email address of user to add
    role: str  # admin, editor, viewer, translator, reviewer


@strawberry.input
class UpdateTeamMemberRoleInput:
    """
    Input type for updating a team member's role.
    """
    team_id: str  # UUID
    user_id: str  # UUID
    role: str  # admin, editor, viewer, translator, reviewer


@strawberry.input
class RemoveTeamMemberInput:
    """
    Input type for removing a member from a team.
    """
    team_id: str  # UUID
    user_id: str  # UUID


@strawberry.input
class UpdateTeamAISettingsInput:
    """
    Input type for updating a team's AI settings.
    """
    team_id: str  # UUID
    ai_provider: Optional[str] = None  # OPENAI or ANTHROPIC
    ai_model: Optional[str] = None  # e.g., gpt-4o-mini, claude-haiku-4-5


async def get_current_user_id(info: Info) -> Optional[int]:
    """
    Helper function to get current user ID from request context.
    
    Args:
        info: GraphQL info object
        
    Returns:
        User ID or None
    """
    try:
        from app.core.security import decode_access_token
        
        request = info.context.get("request")
        if not request:
            logger.warning("No request in GraphQL context")
            return None
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("No Authorization header in request")
            return None
            
        if not auth_header.startswith("Bearer "):
            logger.warning(f"Invalid Authorization header format")
            return None
        
        token = auth_header.replace("Bearer ", "")
        payload = decode_access_token(token)
        
        if not payload:
            logger.warning("Failed to decode access token")
            return None
        
        public_id = payload.get("sub")
        if not public_id:
            logger.warning("No 'sub' field in token payload")
            return None
        
        async with AsyncSessionLocal() as db:
            user = await UserService.get_user_by_public_id(db, public_id)
            if not user:
                logger.warning(f"User not found for public_id")
                return None
            return user.id
    except Exception as e:
        logger.error(f"Error getting current user: {type(e).__name__}: {str(e)}")
        return None


def build_team_type(team, current_user_id: int) -> TeamType:
    """
    Build TeamType from Team model.
    
    Args:
        team: Team model instance
        current_user_id: Current user's ID
        
    Returns:
        TeamType
    """
    # Build owner
    owner = UserType(
        id=str(team.owner.public_id),
        email=team.owner.email,
        username=team.owner.username,
        is_active=team.owner.is_active,
        is_superuser=team.owner.is_superuser,
        onboarding_completed=team.owner.onboarding_completed
    )
    
    # Build members
    members = []
    for member in team.members:
        members.append(TeamMemberType(
            user=UserType(
                id=str(member.user.public_id),
                email=member.user.email,
                username=member.user.username,
                is_active=member.user.is_active,
                is_superuser=member.user.is_superuser,
                onboarding_completed=member.user.onboarding_completed
            ),
            role=member.role,
            created_at=member.created_at
        ))
    
    # Build invitations (only pending ones)
    from app.models.team_invitation import InvitationStatus
    
    invitations = []
    for invitation in team.invitations:
        # Check status properly (it's an enum)
        if invitation.status == InvitationStatus.PENDING:
            invited_by_user = None
            if invitation.invited_by:
                invited_by_user = UserType(
                    id=str(invitation.invited_by.public_id),
                    email=invitation.invited_by.email,
                    username=invitation.invited_by.username,
                    is_active=invitation.invited_by.is_active,
                    is_superuser=invitation.invited_by.is_superuser,
                    onboarding_completed=invitation.invited_by.onboarding_completed
                )
            
            invitations.append(TeamInvitationType(
                id=str(invitation.public_id),
                invited_email=invitation.invited_email,
                role=invitation.role,
                status=invitation.status.value,
                invited_by=invited_by_user,
                created_at=invitation.created_at
            ))
    
    # Check if current user can manage
    can_manage = team.owner_id == current_user_id
    if not can_manage:
        for member in team.members:
            if member.user_id == current_user_id and member.role == "admin":
                can_manage = True
                break
    
    return TeamType(
        id=str(team.public_id),
        name=team.name,
        description=team.description,
        owner=owner,
        members=members,
        invitations=invitations,
        can_manage=can_manage,
        members_count=len(members) + len(invitations),  # Include invited users in count
        ai_provider=team.ai_provider,
        ai_model=team.ai_model,
        created_at=team.created_at,
        updated_at=team.updated_at
    )


@strawberry.type
class TeamQuery:
    """
    GraphQL queries for teams.
    """

    @strawberry.field
    async def teams(self, info: Info) -> List[TeamType]:
        """
        Get all teams for current user (owned or member).
        
        Args:
            info: GraphQL info object
            
        Returns:
            List of teams
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to access teams")
            
            async with AsyncSessionLocal() as db:
                teams = await TeamService.get_user_teams(db, current_user_id)
                return [build_team_type(team, current_user_id) for team in teams]
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in teams query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    async def team(self, info: Info, id: str) -> Optional[TeamType]:
        """
        Get a specific team by ID.
        
        Args:
            info: GraphQL info object
            id: Team UUID
            
        Returns:
            Team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                return None
            
            async with AsyncSessionLocal() as db:
                team = await TeamService.get_team_by_public_id(db, id)
                if not team:
                    return None
                
                # Check access
                if not await TeamService.check_user_team_access(db, team.id, current_user_id):
                    return None
                
                return build_team_type(team, current_user_id)
        except Exception as e:
            logger.error(f"Error in team query: {type(e).__name__}: {str(e)}")
            return None

    @strawberry.field
    async def invite_info(self, info: Info, code: str) -> Optional[InviteInfoType]:
        """
        Get public information about an invitation.
        This query does NOT require authentication.
        
        Args:
            info: GraphQL info object
            code: Invitation UUID code
            
        Returns:
            InviteInfoType or None if not found
        """
        async with AsyncSessionLocal() as db:
            try:
                invitation = await TeamService.get_invitation_by_public_id(db, code)
                if not invitation:
                    return None
                
                inviter_name = "Unknown"
                inviter_email = ""
                if invitation.invited_by:
                    inviter_name = invitation.invited_by.username
                    inviter_email = invitation.invited_by.email
                
                return InviteInfoType(
                    id=str(invitation.public_id),
                    team_name=invitation.team.name,
                    team_description=invitation.team.description,
                    inviter_name=inviter_name,
                    inviter_email=inviter_email,
                    role=invitation.role,
                    status=invitation.status.value,
                    invited_email=invitation.invited_email,
                    created_at=invitation.created_at
                )
            except Exception as e:
                logger.error(f"Error in invite_info query: {type(e).__name__}: {str(e)}")
                return None

    @strawberry.field
    async def my_pending_invites(self, info: Info) -> List[PendingInviteType]:
        """
        Get all pending invitations for the current user.
        
        Args:
            info: GraphQL info object
            
        Returns:
            List of pending invitations
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required")
            
            async with AsyncSessionLocal() as db:
                # Get current user email
                user = await UserService.get_user_by_id(db, current_user_id)
                if not user:
                    return []
                
                invitations = await TeamService.get_pending_invitations_for_email(db, user.email)
                
                result = []
                for inv in invitations:
                    inviter_name = "Unknown"
                    if inv.invited_by:
                        inviter_name = inv.invited_by.username
                    
                    result.append(PendingInviteType(
                        id=str(inv.public_id),
                        team_name=inv.team.name,
                        team_description=inv.team.description,
                        inviter_name=inviter_name,
                        role=inv.role,
                        created_at=inv.created_at
                    ))
                
                return result
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in my_pending_invites query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    async def team_activity(self, info: Info, team_id: str, limit: Optional[int] = 100) -> List['ActivityLogType']:
        """
        Get all activity logs for all projects in a team.
        
        Args:
            info: GraphQL info object
            team_id: Team UUID
            limit: Maximum number of logs to return (default: 100)
            
        Returns:
            List of activity logs ordered by created_at DESC
            
        Raises:
            UnauthorizedError: If user is not authenticated or doesn't have access
        """
        # Import here to avoid circular dependency
        from app.schemas.key import ActivityLogType, build_activity_log_type
        from app.models.activity_log import ActivityLog, ActionType
        from app.models.project import Project
        
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to view activity")
            
            async with AsyncSessionLocal() as db:
                # Get team to check access
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    return []
                
                # Check access
                if not await TeamService.check_user_team_access(db, team.id, current_user_id):
                    raise UnauthorizedError("You don't have access to this team")
                
                # Get all project IDs in this team
                result = await db.execute(select(Project).where(Project.team_id == team.id))
                projects = result.scalars().all()
                project_ids = [p.id for p in projects]
                logger.info(f"team_activity: team_id={team.id}, project_ids={project_ids}")
                
                # Define project and team level actions (exclude key/translation/review actions)
                team_and_project_actions = [
                    # Team lifecycle
                    ActionType.TEAM_CREATE,
                    ActionType.TEAM_UPDATE_NAME,
                    ActionType.TEAM_UPDATE_DESCRIPTION,
                    ActionType.TEAM_DELETE,
                    # Project actions
                    ActionType.PROJECT_CREATE,
                    ActionType.PROJECT_UPDATE_NAME,
                    ActionType.PROJECT_UPDATE_DESCRIPTION,
                    ActionType.PROJECT_UPDATE_LANGUAGES,
                    ActionType.PROJECT_UPDATE_DEFAULT_LANGUAGE,
                    ActionType.PROJECT_UPDATE_COLOR,
                    ActionType.PROJECT_UPDATE_STATUS,
                    ActionType.PROJECT_DELETE,
                    ActionType.PROJECT_EXPORT,
                    ActionType.PROJECT_IMPORT,
                    # Batch import
                    ActionType.KEYS_BATCH_IMPORT,
                    # Team management
                    ActionType.MEMBER_ADD,
                    ActionType.MEMBER_REMOVE,
                    ActionType.MEMBER_ROLE_CHANGE,
                    ActionType.TEAM_INVITE,
                    # Scan actions
                    ActionType.SCAN_START,
                    ActionType.SCAN_COMPLETE,
                    ActionType.SCAN_FAILED,
                    ActionType.SCAN_CANCELLED,
                    # PR actions
                    ActionType.PR_STARTED,
                    ActionType.PR_CREATED,
                    ActionType.PR_FAILED,
                    ActionType.PR_CANCELLED,
                ]
                
                # Get all logs for this team (team_id) or its projects (project_id)
                from sqlalchemy import or_
                
                # Build filter conditions
                filter_conditions = [ActivityLog.team_id == team.id]
                if project_ids:
                    filter_conditions.append(ActivityLog.project_id.in_(project_ids))
                
                result = await db.execute(
                    select(ActivityLog)
                    .options(
                        joinedload(ActivityLog.user),
                        joinedload(ActivityLog.affected_user),
                        joinedload(ActivityLog.project),
                        joinedload(ActivityLog.team)
                    )
                    .where(
                        or_(*filter_conditions),
                        ActivityLog.action.in_(team_and_project_actions)
                    )
                    .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
                    .limit(limit or 100)
                )
                logs = result.scalars().all()
                
                logger.info(f"team_activity: found {len(logs)} logs")
                for log in list(logs)[:3]:
                    logger.info(f"  Log: id={log.id}, action={log.action}, team_id={log.team_id}, project_id={log.project_id}")
                
                return [build_activity_log_type(log) for log in logs]
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in team_activity query: {type(e).__name__}: {str(e)}")
            return []


@strawberry.type
class TeamMutation:
    """
    GraphQL mutations for teams.
    """

    @strawberry.mutation
    async def create_team(self, input: CreateTeamInput, info: Info) -> TeamType:
        """
        Create a new team.
        
        Args:
            input: Team creation input
            info: GraphQL info object
            
        Returns:
            Created team
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to create teams")
        
        async with AsyncSessionLocal() as db:
            try:
                team = await TeamService.create_team(
                    db=db,
                    owner_id=current_user_id,
                    name=input.name,
                    description=input.description
                )
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "team creation")
            except Exception as e:
                handle_database_exception(e, "team creation")

    @strawberry.mutation
    async def update_team(self, input: UpdateTeamInput, info: Info) -> Optional[TeamType]:
        """
        Update an existing team.
        
        Args:
            input: Team update input
            info: GraphQL info object
            
        Returns:
            Updated team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update teams")
        
        async with AsyncSessionLocal() as db:
            try:
                team = await TeamService.update_team(
                    db=db,
                    public_id=input.id,
                    user_id=current_user_id,
                    name=input.name,
                    description=input.description
                )
                
                if not team:
                    return None
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "team update")
            except Exception as e:
                handle_database_exception(e, "team update")

    @strawberry.mutation
    async def delete_team(self, id: str, info: Info) -> bool:
        """
        Delete a team.
        
        Args:
            id: Team UUID
            info: GraphQL info object
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete teams")
        
        async with AsyncSessionLocal() as db:
            try:
                return await TeamService.delete_team(db, id, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "team deletion")
            except Exception as e:
                handle_database_exception(e, "team deletion")

    @strawberry.mutation
    async def add_team_member(self, input: AddTeamMemberInput, info: Info) -> Optional[TeamType]:
        """
        Add a member to a team by email address.
        Creates an invitation that must be accepted by the user.
        
        Args:
            input: Add member input
            info: GraphQL info object
            
        Returns:
            Updated team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        from app.services.email_service import send_team_invitation_email_background
        
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to add team members")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get current user for inviter name
                current_user = await UserService.get_user_by_id(db, current_user_id)
                if not current_user:
                    raise UnauthorizedError("User not found")
                
                # Create invitation
                invitation = await TeamService.add_team_member_by_email(
                    db=db,
                    team_public_id=input.team_id,
                    user_email=input.user_email,
                    role=input.role,
                    added_by_user_id=current_user_id
                )
                
                # Send invitation email if invitation was created
                if invitation:
                    send_team_invitation_email_background(
                        email=invitation.invited_email,
                        team_name=invitation.team.name,
                        inviter_name=current_user.username,
                        invite_code=str(invitation.public_id),
                        role=invitation.role
                    )
                
                # Always return updated team
                team = await TeamService.get_team_by_public_id(db, input.team_id)
                if not team:
                    return None
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "adding team member")
            except Exception as e:
                handle_database_exception(e, "adding team member")

    @strawberry.mutation
    async def remove_team_member(self, input: RemoveTeamMemberInput, info: Info) -> Optional[TeamType]:
        """
        Remove a member from a team.
        
        Args:
            input: Remove member input
            info: GraphQL info object
            
        Returns:
            Updated team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to remove team members")
        
        async with AsyncSessionLocal() as db:
            try:
                success = await TeamService.remove_team_member(
                    db=db,
                    team_public_id=input.team_id,
                    user_public_id=input.user_id,
                    removed_by_user_id=current_user_id
                )
                
                if not success:
                    return None
                
                # Get updated team
                team = await TeamService.get_team_by_public_id(db, input.team_id)
                if not team:
                    return None
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "removing team member")
            except Exception as e:
                handle_database_exception(e, "removing team member")

    @strawberry.mutation
    async def update_team_member_role(self, input: UpdateTeamMemberRoleInput, info: Info) -> Optional[TeamType]:
        """
        Update a team member's role.
        
        Args:
            input: Update role input
            info: GraphQL info object
            
        Returns:
            Updated team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update team member roles")
        
        async with AsyncSessionLocal() as db:
            try:
                member = await TeamService.update_team_member_role(
                    db=db,
                    team_public_id=input.team_id,
                    user_public_id=input.user_id,
                    role=input.role,
                    updated_by_user_id=current_user_id
                )
                
                if not member:
                    return None
                
                # Get updated team
                team = await TeamService.get_team_by_public_id(db, input.team_id)
                if not team:
                    return None
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "updating team member role")
            except Exception as e:
                handle_database_exception(e, "updating team member role")

    @strawberry.mutation
    async def accept_invite(self, code: str, info: Info) -> Optional[TeamType]:
        """
        Accept a team invitation.
        
        Args:
            code: Invitation UUID code
            info: GraphQL info object
            
        Returns:
            Team that user joined or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("Authentication required to accept invitations")
        
        async with AsyncSessionLocal() as db:
            try:
                member = await TeamService.accept_invitation(
                    db=db,
                    invitation_public_id=code,
                    user_id=current_user_id
                )
                
                if not member:
                    return None
                
                # Get the team
                result = await db.execute(
                    select(Team)
                    .options(
                        joinedload(Team.owner),
                        selectinload(Team.members).joinedload(TeamMember.user),
                        selectinload(Team.invitations).joinedload(TeamInvitation.invited_by)
                    )
                    .where(Team.id == member.team_id)
                )
                team = result.scalar_one_or_none()
                
                if not team:
                    return None
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "accepting invitation")
            except Exception as e:
                handle_database_exception(e, "accepting invitation")

    @strawberry.mutation
    async def decline_invite(self, code: str, info: Info) -> bool:
        """
        Decline a team invitation.
        
        Args:
            code: Invitation UUID code
            info: GraphQL info object
            
        Returns:
            True if declined successfully
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("Authentication required to decline invitations")
        
        async with AsyncSessionLocal() as db:
            try:
                return await TeamService.decline_invitation(
                    db=db,
                    invitation_public_id=code,
                    user_id=current_user_id
                )
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "declining invitation")
            except Exception as e:
                handle_database_exception(e, "declining invitation")

    @strawberry.mutation
    async def resend_invite(self, invitation_id: str, info: Info) -> bool:
        """
        Resend a team invitation email.
        
        Args:
            invitation_id: Invitation UUID
            info: GraphQL info object
            
        Returns:
            True if resent successfully
            
        Raises:
            UnauthorizedError: If user is not authenticated or not authorized
        """
        from app.services.email_service import send_team_invitation_email_background
        
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("Authentication required to resend invitations")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get current user for inviter name
                current_user = await UserService.get_user_by_id(db, current_user_id)
                if not current_user:
                    raise UnauthorizedError("User not found")
                
                invitation = await TeamService.resend_invitation(
                    db=db,
                    invitation_public_id=invitation_id,
                    user_id=current_user_id
                )
                
                if not invitation:
                    return False
                
                # Send the email
                send_team_invitation_email_background(
                    email=invitation.invited_email,
                    team_name=invitation.team.name,
                    inviter_name=current_user.username,
                    invite_code=str(invitation.public_id),
                    role=invitation.role
                )
                
                return True
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "resending invitation")
            except Exception as e:
                handle_database_exception(e, "resending invitation")

    @strawberry.mutation
    async def update_team_ai_settings(
        self, input: UpdateTeamAISettingsInput, info: Info
    ) -> Optional[TeamType]:
        """
        Update a team's AI settings (provider and model).
        
        Args:
            input: AI settings update input
            info: GraphQL info object
            
        Returns:
            Updated team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated or not authorized
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update team AI settings")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get team and check access
                team = await TeamService.get_team_by_public_id(db, input.team_id)
                if not team:
                    return None
                
                # Check if user can manage the team
                can_manage = team.owner_id == current_user_id
                if not can_manage:
                    for member in team.members:
                        if member.user_id == current_user_id and member.role == "admin":
                            can_manage = True
                            break
                
                if not can_manage:
                    raise UnauthorizedError("You don't have permission to update team AI settings")
                
                # Validate provider if provided
                valid_providers = ["OPENAI", "ANTHROPIC"]
                if input.ai_provider and input.ai_provider not in valid_providers:
                    raise ValueError(f"Invalid AI provider. Must be one of: {', '.join(valid_providers)}")
                
                # Update team AI settings
                if input.ai_provider is not None:
                    team.ai_provider = input.ai_provider if input.ai_provider else None
                if input.ai_model is not None:
                    team.ai_model = input.ai_model if input.ai_model else None
                
                await db.commit()
                await db.refresh(team)
                
                return build_team_type(team, current_user_id)
            except (UnauthorizedError, ValueError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "updating team AI settings")
            except Exception as e:
                handle_database_exception(e, "updating team AI settings")

