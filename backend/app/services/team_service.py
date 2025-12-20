from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, selectinload
import uuid as uuid_lib
import logging

from app.models.team import Team, TeamMember
from app.models.team_invitation import TeamInvitation, InvitationStatus
from app.models.user import User
from app.models.activity_log import ActivityLog, ActionType

logger = logging.getLogger(__name__)


class TeamService:
    """
    Service for managing teams and team memberships.
    """

    @staticmethod
    async def create_team(
        db: AsyncSession,
        owner_id: int,
        name: str,
        description: Optional[str] = None
    ) -> Team:
        """
        Create a new team.
        
        Args:
            db: Database session
            owner_id: ID of the team owner
            name: Team name
            description: Team description
            
        Returns:
            Created team
        """
        team = Team(
            name=name,
            description=description,
            owner_id=owner_id
        )
        db.add(team)
        await db.flush()
        
        # Log team creation
        log = ActivityLog(
            team_id=team.id,
            user_id=owner_id,
            action=ActionType.TEAM_CREATE,
            field_name="name",
            new_value=name
        )
        db.add(log)
        
        await db.commit()
        
        # Reload with relationships to avoid lazy loading in async context
        result = await db.execute(
            select(Team)
            .options(
                joinedload(Team.owner),
                selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(Team.invitations).joinedload(TeamInvitation.invited_by)
            )
            .where(Team.id == team.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def get_team_by_public_id(db: AsyncSession, public_id: str) -> Optional[Team]:
        """
        Get a team by its public UUID.
        Uses eager loading to prevent N+1 query problems.
        
        Args:
            db: Database session
            public_id: Public UUID of the team
            
        Returns:
            Team or None
        """
        try:
            uuid_obj = uuid_lib.UUID(public_id)
            result = await db.execute(
                select(Team)
                .options(
                    joinedload(Team.owner),
                    selectinload(Team.members).joinedload(TeamMember.user),
                    selectinload(Team.invitations).joinedload(TeamInvitation.invited_by)
                )
                .where(Team.public_id == uuid_obj)
            )
            return result.unique().scalar_one_or_none()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    async def get_user_teams(db: AsyncSession, user_id: int) -> List[Team]:
        """
        Get all teams where user is owner or member.
        Uses eager loading to prevent N+1 query problems.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of teams
        """
        eager_options = [
            joinedload(Team.owner),
            selectinload(Team.members).joinedload(TeamMember.user),
            selectinload(Team.invitations).joinedload(TeamInvitation.invited_by),
        ]
        
        # Get teams where user is owner
        result = await db.execute(
            select(Team)
            .options(*eager_options)
            .where(Team.owner_id == user_id)
        )
        owned_teams = result.scalars().unique().all()
        owned_team_ids = {t.id for t in owned_teams}
        
        # Get teams where user is member
        result = await db.execute(
            select(Team)
            .options(*eager_options)
            .join(TeamMember, Team.id == TeamMember.team_id)
            .where(TeamMember.user_id == user_id)
        )
        member_teams = result.scalars().unique().all()
        
        # Combine and deduplicate
        all_teams = list(owned_teams)
        for team in member_teams:
            if team.id not in owned_team_ids:
                all_teams.append(team)
        
        return all_teams

    @staticmethod
    async def update_team(
        db: AsyncSession,
        public_id: str,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Team]:
        """
        Update a team. Only owner or admin members can update.
        
        Args:
            db: Database session
            public_id: Public UUID of the team
            user_id: User ID requesting the update
            name: New team name
            description: New team description
            
        Returns:
            Updated team or None if not found or no permission
        """
        team = await TeamService.get_team_by_public_id(db, public_id)
        if not team:
            return None
        
        # Check if user has permission to update
        if not await TeamService.can_user_manage_team(db, team.id, user_id):
            return None
        
        # Update fields if provided and log changes
        if name is not None and name != team.name:
            old_name = team.name
            team.name = name
            log = ActivityLog(
                team_id=team.id,
                user_id=user_id,
                action=ActionType.TEAM_UPDATE_NAME,
                field_name="name",
                old_value=old_name,
                new_value=name
            )
            db.add(log)
        
        if description is not None and description != team.description:
            old_description = team.description
            team.description = description
            log = ActivityLog(
                team_id=team.id,
                user_id=user_id,
                action=ActionType.TEAM_UPDATE_DESCRIPTION,
                field_name="description",
                old_value=old_description or '',
                new_value=description
            )
            db.add(log)
        
        await db.commit()
        
        # Reload with relationships
        result = await db.execute(
            select(Team)
            .options(
                joinedload(Team.owner),
                selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(Team.invitations).joinedload(TeamInvitation.invited_by)
            )
            .where(Team.id == team.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def delete_team(db: AsyncSession, public_id: str, user_id: int) -> bool:
        """
        Delete a team. Only owner can delete.
        
        Args:
            db: Database session
            public_id: Public UUID of the team
            user_id: User ID requesting the deletion
            
        Returns:
            True if deleted, False otherwise
        """
        team = await TeamService.get_team_by_public_id(db, public_id)
        if not team:
            return False
        
        # Only owner can delete
        if team.owner_id != user_id:
            return False
        
        # Log team deletion before deleting - use team name but no FK reference
        log = ActivityLog(
            team_id=None,  # Don't reference team being deleted
            user_id=user_id,
            action=ActionType.TEAM_DELETE,
            field_name="name",
            old_value=team.name
        )
        db.add(log)
        
        # Delete using execute to avoid issues with detached objects
        await db.execute(delete(Team).where(Team.id == team.id))
        await db.commit()
        return True

    @staticmethod
    async def get_team_by_id(db: AsyncSession, team_id: int) -> Optional[Team]:
        """
        Get a team by its internal ID.
        
        Args:
            db: Database session
            team_id: Internal ID of the team
            
        Returns:
            Team or None
        """
        result = await db.execute(
            select(Team)
            .options(
                joinedload(Team.owner),
                selectinload(Team.members).joinedload(TeamMember.user),
            )
            .where(Team.id == team_id)
        )
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def check_user_team_role(db: AsyncSession, team_id: int, user_id: int, role: str) -> bool:
        """
        Check if user has a specific role in a team.
        
        Args:
            db: Database session
            team_id: Internal team ID
            user_id: User ID
            role: Role to check (admin, editor, viewer, translator, reviewer)
            
        Returns:
            True if user has the role, False otherwise
        """
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.role == role
            )
        )
        member = result.scalar_one_or_none()
        return member is not None

    @staticmethod
    async def check_user_team_access(db: AsyncSession, team_id: int, user_id: int) -> bool:
        """
        Check if user has access to a team (owner or member).
        
        Args:
            db: Database session
            team_id: Internal team ID
            user_id: User ID
            
        Returns:
            True if user has access, False otherwise
        """
        result = await db.execute(select(Team).where(Team.id == team_id))
        team = result.scalar_one_or_none()
        if not team:
            return False
        
        # Check if owner
        if team.owner_id == user_id:
            return True
        
        # Check if member
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
        )
        member = result.scalar_one_or_none()
        
        return member is not None

    @staticmethod
    async def can_user_manage_team(db: AsyncSession, team_id: int, user_id: int) -> bool:
        """
        Check if user can manage a team (owner or admin member).
        
        Args:
            db: Database session
            team_id: Internal team ID
            user_id: User ID
            
        Returns:
            True if user can manage, False otherwise
        """
        result = await db.execute(select(Team).where(Team.id == team_id))
        team = result.scalar_one_or_none()
        if not team:
            return False
        
        # Owner can always manage
        if team.owner_id == user_id:
            return True
        
        # Check if admin member
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.role == "admin"
            )
        )
        member = result.scalar_one_or_none()
        
        return member is not None

    @staticmethod
    async def add_team_member_by_email(
        db: AsyncSession,
        team_public_id: str,
        user_email: str,
        role: str,
        added_by_user_id: int
    ) -> Optional[TeamInvitation]:
        """
        Create an invitation to join a team by email address.
        Both existing and new users receive invitations that must be accepted.
        
        Args:
            db: Database session
            team_public_id: Public UUID of the team
            user_email: Email of the user to invite
            role: Role for the new member (admin, editor, viewer, translator, reviewer)
            added_by_user_id: User ID who is sending the invitation
            
        Returns:
            TeamInvitation if created/updated, None if failed (for security - don't reveal details)
        """
        # Get team
        team = await TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return None
        
        # Check permission
        if not await TeamService.can_user_manage_team(db, team.id, added_by_user_id):
            return None
        
        email = user_email.lower().strip()
        
        # Check if user exists and is already a member
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            result = await db.execute(
                select(TeamMember).where(
                    TeamMember.team_id == team.id,
                    TeamMember.user_id == user.id
                )
            )
            existing_member = result.scalar_one_or_none()
            if existing_member:
                # Already a member - don't create invitation
                logger.info(f"User {email} is already a member of team {team.name}")
                return None
        
        # Check for existing pending invitation
        result = await db.execute(
            select(TeamInvitation).where(
                TeamInvitation.team_id == team.id,
                TeamInvitation.invited_email == email,
                TeamInvitation.status == InvitationStatus.PENDING
            )
        )
        existing_invitation = result.scalar_one_or_none()
        
        if existing_invitation:
            # Update existing invitation
            existing_invitation.role = role
            existing_invitation.invited_by_user_id = added_by_user_id
            if user:
                existing_invitation.invited_user_id = user.id
            
            await db.commit()
            await db.refresh(existing_invitation, ['team'])
            logger.info(f"Updated invitation for: {email}")
            return existing_invitation
        
        # Create new invitation
        invitation = TeamInvitation(
            team_id=team.id,
            invited_email=email,
            role=role,
            status=InvitationStatus.PENDING,
            invited_by_user_id=added_by_user_id,
            invited_user_id=user.id if user else None
        )
        db.add(invitation)
        await db.flush()
        
        # Log invitation
        log = ActivityLog(
            team_id=team.id,
            user_id=added_by_user_id,
            action=ActionType.TEAM_INVITE,
            field_name="email",
            new_value=f"{email} ({role})"
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(invitation, ['team'])
        logger.info(f"Created invitation for: {email}")
        return invitation

    @staticmethod
    async def get_invitation_by_public_id(db: AsyncSession, public_id: str) -> Optional[TeamInvitation]:
        """
        Get an invitation by its public UUID.
        
        Args:
            db: Database session
            public_id: Public UUID of the invitation
            
        Returns:
            TeamInvitation or None
        """
        try:
            uuid_obj = uuid_lib.UUID(public_id)
            result = await db.execute(
                select(TeamInvitation)
                .options(
                    joinedload(TeamInvitation.team).joinedload(Team.owner),
                    joinedload(TeamInvitation.invited_by)
                )
                .where(TeamInvitation.public_id == uuid_obj)
            )
            return result.unique().scalar_one_or_none()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    async def get_pending_invitations_for_email(db: AsyncSession, email: str) -> List[TeamInvitation]:
        """
        Get all pending invitations for a given email address.
        
        Args:
            db: Database session
            email: Email address to search for
            
        Returns:
            List of pending TeamInvitation objects
        """
        result = await db.execute(
            select(TeamInvitation)
            .options(
                joinedload(TeamInvitation.team).joinedload(Team.owner),
                joinedload(TeamInvitation.invited_by)
            )
            .where(
                TeamInvitation.invited_email == email.lower().strip(),
                TeamInvitation.status == InvitationStatus.PENDING
            )
        )
        return result.scalars().unique().all()

    @staticmethod
    async def accept_invitation(
        db: AsyncSession,
        invitation_public_id: str,
        user_id: int
    ) -> Optional[TeamMember]:
        """
        Accept a team invitation. Creates a TeamMember and updates invitation status.
        
        Args:
            db: Database session
            invitation_public_id: Public UUID of the invitation
            user_id: ID of the user accepting the invitation
            
        Returns:
            Created TeamMember or None if failed
        """
        # Get invitation
        invitation = await TeamService.get_invitation_by_public_id(db, invitation_public_id)
        if not invitation:
            logger.warning(f"Invitation not found: {invitation_public_id}")
            return None
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            logger.warning(f"Invitation {invitation_public_id} is not pending: {invitation.status}")
            return None
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
        
        # Verify email matches (case insensitive)
        if user.email.lower() != invitation.invited_email.lower():
            logger.warning(f"Email mismatch: user {user.email} vs invitation {invitation.invited_email}")
            return None
        
        # Check if already a member
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == invitation.team_id,
                TeamMember.user_id == user_id
            )
        )
        existing_member = result.scalar_one_or_none()
        
        if existing_member:
            # Already a member - just update invitation status
            invitation.status = InvitationStatus.ACCEPTED
            invitation.invited_user_id = user_id
            await db.commit()
            logger.info(f"User {user.email} was already a member, updated invitation status")
            return existing_member
        
        # Create team member
        member = TeamMember(
            team_id=invitation.team_id,
            user_id=user_id,
            role=invitation.role
        )
        db.add(member)
        
        # Update invitation status
        invitation.status = InvitationStatus.ACCEPTED
        invitation.invited_user_id = user_id
        
        # Log member addition
        log = ActivityLog(
            team_id=invitation.team_id,
            user_id=user_id,
            action=ActionType.MEMBER_ADD,
            field_name="role",
            new_value=invitation.role
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(member)
        logger.info(f"User {user.email} accepted invitation to team {invitation.team.name}")
        return member

    @staticmethod
    async def decline_invitation(
        db: AsyncSession,
        invitation_public_id: str,
        user_id: int
    ) -> bool:
        """
        Decline a team invitation.
        
        Args:
            db: Database session
            invitation_public_id: Public UUID of the invitation
            user_id: ID of the user declining the invitation
            
        Returns:
            True if declined, False otherwise
        """
        # Get invitation
        invitation = await TeamService.get_invitation_by_public_id(db, invitation_public_id)
        if not invitation:
            return False
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            return False
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        
        # Verify email matches
        if user.email.lower() != invitation.invited_email.lower():
            return False
        
        # Update invitation status
        invitation.status = InvitationStatus.DECLINED
        invitation.invited_user_id = user_id
        
        await db.commit()
        logger.info(f"User {user.email} declined invitation to team {invitation.team.name}")
        return True

    @staticmethod
    async def resend_invitation(
        db: AsyncSession,
        invitation_public_id: str,
        user_id: int
    ) -> Optional[TeamInvitation]:
        """
        Resend a team invitation email.
        Only team admins/owners can resend invitations.
        
        Args:
            db: Database session
            invitation_public_id: Public UUID of the invitation
            user_id: ID of the user requesting resend
            
        Returns:
            TeamInvitation if successful, None otherwise
        """
        # Get invitation
        invitation = await TeamService.get_invitation_by_public_id(db, invitation_public_id)
        if not invitation:
            logger.warning(f"Invitation not found: {invitation_public_id}")
            return None
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            logger.warning(f"Cannot resend non-pending invitation: {invitation.status}")
            return None
        
        # Check permission
        if not await TeamService.can_user_manage_team(db, invitation.team_id, user_id):
            logger.warning(f"User {user_id} cannot manage team {invitation.team_id}")
            return None
        
        logger.info(f"Resending invitation for {invitation.invited_email} to team {invitation.team.name}")
        return invitation

    @staticmethod
    async def add_team_member(
        db: AsyncSession,
        team_public_id: str,
        user_public_id: str,
        role: str,
        added_by_user_id: int
    ) -> Optional[TeamMember]:
        """
        Add a member to a team. Only owner or admin can add members.
        
        Args:
            db: Database session
            team_public_id: Public UUID of the team
            user_public_id: Public UUID of the user to add
            role: Role for the new member (admin, editor, viewer, translator, reviewer)
            added_by_user_id: User ID who is adding the member
            
        Returns:
            Created TeamMember or None if failed
        """
        # Get team
        team = await TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return None
        
        # Check permission
        if not await TeamService.can_user_manage_team(db, team.id, added_by_user_id):
            return None
        
        # Get user to add
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            result = await db.execute(select(User).where(User.public_id == uuid_obj))
            user = result.scalar_one_or_none()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Check if already a member
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user.id
            )
        )
        existing_member = result.scalar_one_or_none()
        
        if existing_member:
            # Update role if already exists
            old_role = existing_member.role
            existing_member.role = role
            
            # Log role change if different
            if old_role != role:
                log = ActivityLog(
                    team_id=team.id,
                    user_id=added_by_user_id,
                    affected_user_id=user.id,
                    action=ActionType.MEMBER_ROLE_CHANGE,
                    field_name="role",
                    old_value=old_role,
                    new_value=role
                )
                db.add(log)
            
            await db.commit()
            await db.refresh(existing_member)
            return existing_member
        
        # Create new member
        member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role=role
        )
        db.add(member)
        await db.flush()
        
        # Log member addition
        log = ActivityLog(
            team_id=team.id,
            user_id=added_by_user_id,
            affected_user_id=user.id,
            action=ActionType.MEMBER_ADD,
            field_name="role",
            new_value=role
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def remove_team_member(
        db: AsyncSession,
        team_public_id: str,
        user_public_id: str,
        removed_by_user_id: int
    ) -> bool:
        """
        Remove a member from a team. Only owner or admin can remove members.
        
        Args:
            db: Database session
            team_public_id: Public UUID of the team
            user_public_id: Public UUID of the user to remove
            removed_by_user_id: User ID who is removing the member
            
        Returns:
            True if removed, False otherwise
        """
        # Get team
        team = await TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return False
        
        # Check permission
        if not await TeamService.can_user_manage_team(db, team.id, removed_by_user_id):
            return False
        
        # Get user to remove
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            result = await db.execute(select(User).where(User.public_id == uuid_obj))
            user = result.scalar_one_or_none()
            if not user:
                return False
        except (ValueError, AttributeError):
            return False
        
        # Cannot remove owner
        if team.owner_id == user.id:
            return False
        
        # Find and remove member
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user.id
            )
        )
        member = result.scalar_one_or_none()
        
        if not member:
            return False
        
        # Log member removal
        log = ActivityLog(
            team_id=team.id,
            user_id=removed_by_user_id,
            affected_user_id=user.id,
            action=ActionType.MEMBER_REMOVE,
            field_name="role",
            old_value=member.role
        )
        db.add(log)
        
        db.delete(member)
        await db.commit()
        return True

    @staticmethod
    async def update_team_member_role(
        db: AsyncSession,
        team_public_id: str,
        user_public_id: str,
        role: str,
        updated_by_user_id: int
    ) -> Optional[TeamMember]:
        """
        Update a team member's role. Only owner or admin can update roles.
        
        Args:
            db: Database session
            team_public_id: Public UUID of the team
            user_public_id: Public UUID of the user
            role: New role (admin, editor, viewer, translator, reviewer)
            updated_by_user_id: User ID who is updating the role
            
        Returns:
            Updated TeamMember or None if failed
        """
        # Get team
        team = await TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return None
        
        # Check permission
        if not await TeamService.can_user_manage_team(db, team.id, updated_by_user_id):
            return None
        
        # Get user
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            result = await db.execute(select(User).where(User.public_id == uuid_obj))
            user = result.scalar_one_or_none()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Cannot change owner's role
        if team.owner_id == user.id:
            return None
        
        # Find and update member
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user.id
            )
        )
        member = result.scalar_one_or_none()
        
        if not member:
            return None
        
        # Log role change if different
        old_role = member.role
        member.role = role
        
        if old_role != role:
            log = ActivityLog(
                team_id=team.id,
                user_id=updated_by_user_id,
                affected_user_id=user.id,
                action=ActionType.MEMBER_ROLE_CHANGE,
                field_name="role",
                old_value=old_role,
                new_value=role
            )
            db.add(log)
        
        await db.commit()
        await db.refresh(member)
        return member
