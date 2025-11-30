import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import get_db
from app.services.team_service import TeamService
from app.services.user_service import UserService
from app.core.exceptions import (
    UnauthorizedError,
    handle_database_exception
)
from app.schemas.auth import UserType

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


def get_current_user_id(info: Info) -> Optional[int]:
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
        
        db: Session = next(get_db())
        try:
            user = UserService.get_user_by_public_id(db, public_id)
            if not user:
                logger.warning(f"User not found for public_id")
                return None
            return user.id
        finally:
            db.close()
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
        created_at=team.created_at,
        updated_at=team.updated_at
    )


@strawberry.type
class TeamQuery:
    """
    GraphQL queries for teams.
    """

    @strawberry.field
    def teams(self, info: Info) -> List[TeamType]:
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
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to access teams")
            
            db: Session = next(get_db())
            try:
                teams = TeamService.get_user_teams(db, current_user_id)
                return [build_team_type(team, current_user_id) for team in teams]
            finally:
                db.close()
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in teams query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    def team(self, info: Info, id: str) -> Optional[TeamType]:
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
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                return None
            
            db: Session = next(get_db())
            try:
                team = TeamService.get_team_by_public_id(db, id)
                if not team:
                    return None
                
                # Check access
                if not TeamService.check_user_team_access(db, team.id, current_user_id):
                    return None
                
                return build_team_type(team, current_user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in team query: {type(e).__name__}: {str(e)}")
            return None


@strawberry.type
class TeamMutation:
    """
    GraphQL mutations for teams.
    """

    @strawberry.mutation
    def create_team(self, input: CreateTeamInput, info: Info) -> TeamType:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to create teams")
        
        db: Session = next(get_db())
        
        try:
            team = TeamService.create_team(
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
        finally:
            db.close()

    @strawberry.mutation
    def update_team(self, input: UpdateTeamInput, info: Info) -> Optional[TeamType]:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update teams")
        
        db: Session = next(get_db())
        
        try:
            team = TeamService.update_team(
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
        finally:
            db.close()

    @strawberry.mutation
    def delete_team(self, id: str, info: Info) -> bool:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete teams")
        
        db: Session = next(get_db())
        
        try:
            return TeamService.delete_team(db, id, current_user_id)
        except (UnauthorizedError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "team deletion")
        except Exception as e:
            handle_database_exception(e, "team deletion")
        finally:
            db.close()

    @strawberry.mutation
    def add_team_member(self, input: AddTeamMemberInput, info: Info) -> Optional[TeamType]:
        """
        Add a member to a team by email address.
        
        Args:
            input: Add member input
            info: GraphQL info object
            
        Returns:
            Updated team or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to add team members")
        
        db: Session = next(get_db())
        
        try:
            # Add member (may return dummy for security if user not found)
            TeamService.add_team_member_by_email(
                db=db,
                team_public_id=input.team_id,
                user_email=input.user_email,
                role=input.role,
                added_by_user_id=current_user_id
            )
            
            # Always return updated team (even if user wasn't added)
            # This prevents enumeration attacks
            team = TeamService.get_team_by_public_id(db, input.team_id)
            if not team:
                return None
            
            return build_team_type(team, current_user_id)
        except (UnauthorizedError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "adding team member")
        except Exception as e:
            handle_database_exception(e, "adding team member")
        finally:
            db.close()

    @strawberry.mutation
    def remove_team_member(self, input: RemoveTeamMemberInput, info: Info) -> Optional[TeamType]:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to remove team members")
        
        db: Session = next(get_db())
        
        try:
            success = TeamService.remove_team_member(
                db=db,
                team_public_id=input.team_id,
                user_public_id=input.user_id,
                removed_by_user_id=current_user_id
            )
            
            if not success:
                return None
            
            # Get updated team
            team = TeamService.get_team_by_public_id(db, input.team_id)
            if not team:
                return None
            
            return build_team_type(team, current_user_id)
        except (UnauthorizedError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "removing team member")
        except Exception as e:
            handle_database_exception(e, "removing team member")
        finally:
            db.close()

    @strawberry.mutation
    def update_team_member_role(self, input: UpdateTeamMemberRoleInput, info: Info) -> Optional[TeamType]:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update team member roles")
        
        db: Session = next(get_db())
        
        try:
            member = TeamService.update_team_member_role(
                db=db,
                team_public_id=input.team_id,
                user_public_id=input.user_id,
                role=input.role,
                updated_by_user_id=current_user_id
            )
            
            if not member:
                return None
            
            # Get updated team
            team = TeamService.get_team_by_public_id(db, input.team_id)
            if not team:
                return None
            
            return build_team_type(team, current_user_id)
        except (UnauthorizedError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "updating team member role")
        except Exception as e:
            handle_database_exception(e, "updating team member role")
        finally:
            db.close()

