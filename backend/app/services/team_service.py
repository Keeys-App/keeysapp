from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
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
    def create_team(
        db: Session,
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
        db.flush()
        
        # Log team creation
        log = ActivityLog(
            team_id=team.id,
            user_id=owner_id,
            action=ActionType.TEAM_CREATE,
            field_name="name",
            new_value=name
        )
        db.add(log)
        
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def get_team_by_public_id(db: Session, public_id: str) -> Optional[Team]:
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
            return db.query(Team).options(
                joinedload(Team.owner),
                selectinload(Team.members).joinedload(TeamMember.user),
                selectinload(Team.invitations).joinedload(TeamInvitation.invited_by)
            ).filter(Team.public_id == uuid_obj).first()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def get_user_teams(db: Session, user_id: int) -> List[Team]:
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
        owned_teams = db.query(Team).options(
            *eager_options
        ).filter(
            Team.owner_id == user_id
        ).all()
        owned_team_ids = {t.id for t in owned_teams}
        
        # Get teams where user is member
        member_teams = db.query(Team).options(
            *eager_options
        ).join(
            TeamMember, Team.id == TeamMember.team_id
        ).filter(
            TeamMember.user_id == user_id
        ).all()
        
        # Combine and deduplicate
        all_teams = owned_teams.copy()
        for team in member_teams:
            if team.id not in owned_team_ids:
                all_teams.append(team)
        
        return all_teams

    @staticmethod
    def update_team(
        db: Session,
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
        team = TeamService.get_team_by_public_id(db, public_id)
        if not team:
            return None
        
        # Check if user has permission to update
        if not TeamService.can_user_manage_team(db, team.id, user_id):
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
        
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def delete_team(db: Session, public_id: str, user_id: int) -> bool:
        """
        Delete a team. Only owner can delete.
        
        Args:
            db: Database session
            public_id: Public UUID of the team
            user_id: User ID requesting the deletion
            
        Returns:
            True if deleted, False otherwise
        """
        team = TeamService.get_team_by_public_id(db, public_id)
        if not team:
            return False
        
        # Only owner can delete
        if team.owner_id != user_id:
            return False
        
        # Log team deletion before deleting
        log = ActivityLog(
            team_id=team.id,
            user_id=user_id,
            action=ActionType.TEAM_DELETE,
            field_name="name",
            old_value=team.name
        )
        db.add(log)
        
        db.delete(team)
        db.commit()
        return True

    @staticmethod
    def check_user_team_access(db: Session, team_id: int, user_id: int) -> bool:
        """
        Check if user has access to a team (owner or member).
        
        Args:
            db: Database session
            team_id: Internal team ID
            user_id: User ID
            
        Returns:
            True if user has access, False otherwise
        """
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return False
        
        # Check if owner
        if team.owner_id == user_id:
            return True
        
        # Check if member
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        
        return member is not None

    @staticmethod
    def can_user_manage_team(db: Session, team_id: int, user_id: int) -> bool:
        """
        Check if user can manage a team (owner or admin member).
        
        Args:
            db: Database session
            team_id: Internal team ID
            user_id: User ID
            
        Returns:
            True if user can manage, False otherwise
        """
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return False
        
        # Owner can always manage
        if team.owner_id == user_id:
            return True
        
        # Check if admin member
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.role == "admin"
        ).first()
        
        return member is not None

    @staticmethod
    def add_team_member_by_email(
        db: Session,
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
        team = TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return None
        
        # Check permission
        if not TeamService.can_user_manage_team(db, team.id, added_by_user_id):
            return None
        
        email = user_email.lower().strip()
        
        # Check if user exists and is already a member
        user = db.query(User).filter(User.email == email).first()
        if user:
            existing_member = db.query(TeamMember).filter(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user.id
            ).first()
            if existing_member:
                # Already a member - don't create invitation
                logger.info(f"User {email} is already a member of team {team.name}")
                return None
        
        # Check for existing pending invitation
        existing_invitation = db.query(TeamInvitation).filter(
            TeamInvitation.team_id == team.id,
            TeamInvitation.invited_email == email,
            TeamInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if existing_invitation:
            # Update existing invitation
            existing_invitation.role = role
            existing_invitation.invited_by_user_id = added_by_user_id
            if user:
                existing_invitation.invited_user_id = user.id
            
            db.commit()
            db.refresh(existing_invitation)
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
        db.flush()
        
        # Log invitation
        log = ActivityLog(
            team_id=team.id,
            user_id=added_by_user_id,
            action=ActionType.TEAM_INVITE,
            field_name="email",
            new_value=f"{email} ({role})"
        )
        db.add(log)
        
        db.commit()
        db.refresh(invitation)
        logger.info(f"Created invitation for: {email}")
        return invitation

    @staticmethod
    def get_invitation_by_public_id(db: Session, public_id: str) -> Optional[TeamInvitation]:
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
            return db.query(TeamInvitation).options(
                joinedload(TeamInvitation.team).joinedload(Team.owner),
                joinedload(TeamInvitation.invited_by)
            ).filter(TeamInvitation.public_id == uuid_obj).first()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def get_pending_invitations_for_email(db: Session, email: str) -> List[TeamInvitation]:
        """
        Get all pending invitations for a given email address.
        
        Args:
            db: Database session
            email: Email address to search for
            
        Returns:
            List of pending TeamInvitation objects
        """
        return db.query(TeamInvitation).options(
            joinedload(TeamInvitation.team).joinedload(Team.owner),
            joinedload(TeamInvitation.invited_by)
        ).filter(
            TeamInvitation.invited_email == email.lower().strip(),
            TeamInvitation.status == InvitationStatus.PENDING
        ).all()

    @staticmethod
    def accept_invitation(
        db: Session,
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
        invitation = TeamService.get_invitation_by_public_id(db, invitation_public_id)
        if not invitation:
            logger.warning(f"Invitation not found: {invitation_public_id}")
            return None
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            logger.warning(f"Invitation {invitation_public_id} is not pending: {invitation.status}")
            return None
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
        
        # Verify email matches (case insensitive)
        if user.email.lower() != invitation.invited_email.lower():
            logger.warning(f"Email mismatch: user {user.email} vs invitation {invitation.invited_email}")
            return None
        
        # Check if already a member
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == invitation.team_id,
            TeamMember.user_id == user_id
        ).first()
        
        if existing_member:
            # Already a member - just update invitation status
            invitation.status = InvitationStatus.ACCEPTED
            invitation.invited_user_id = user_id
            db.commit()
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
        
        db.commit()
        db.refresh(member)
        logger.info(f"User {user.email} accepted invitation to team {invitation.team.name}")
        return member

    @staticmethod
    def decline_invitation(
        db: Session,
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
        invitation = TeamService.get_invitation_by_public_id(db, invitation_public_id)
        if not invitation:
            return False
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            return False
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Verify email matches
        if user.email.lower() != invitation.invited_email.lower():
            return False
        
        # Update invitation status
        invitation.status = InvitationStatus.DECLINED
        invitation.invited_user_id = user_id
        
        db.commit()
        logger.info(f"User {user.email} declined invitation to team {invitation.team.name}")
        return True

    @staticmethod
    def resend_invitation(
        db: Session,
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
        invitation = TeamService.get_invitation_by_public_id(db, invitation_public_id)
        if not invitation:
            logger.warning(f"Invitation not found: {invitation_public_id}")
            return None
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            logger.warning(f"Cannot resend non-pending invitation: {invitation.status}")
            return None
        
        # Check permission
        if not TeamService.can_user_manage_team(db, invitation.team_id, user_id):
            logger.warning(f"User {user_id} cannot manage team {invitation.team_id}")
            return None
        
        logger.info(f"Resending invitation for {invitation.invited_email} to team {invitation.team.name}")
        return invitation

    @staticmethod
    def add_team_member(
        db: Session,
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
        team = TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return None
        
        # Check permission
        if not TeamService.can_user_manage_team(db, team.id, added_by_user_id):
            return None
        
        # Get user to add
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Check if already a member
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id
        ).first()
        
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
            
            db.commit()
            db.refresh(existing_member)
            return existing_member
        
        # Create new member
        member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role=role
        )
        db.add(member)
        db.flush()
        
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
        
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_team_member(
        db: Session,
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
        team = TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return False
        
        # Check permission
        if not TeamService.can_user_manage_team(db, team.id, removed_by_user_id):
            return False
        
        # Get user to remove
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return False
        except (ValueError, AttributeError):
            return False
        
        # Cannot remove owner
        if team.owner_id == user.id:
            return False
        
        # Find and remove member
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id
        ).first()
        
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
        db.commit()
        return True

    @staticmethod
    def update_team_member_role(
        db: Session,
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
        team = TeamService.get_team_by_public_id(db, team_public_id)
        if not team:
            return None
        
        # Check permission
        if not TeamService.can_user_manage_team(db, team.id, updated_by_user_id):
            return None
        
        # Get user
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Cannot change owner's role
        if team.owner_id == user.id:
            return None
        
        # Find and update member
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id
        ).first()
        
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
        
        db.commit()
        db.refresh(member)
        return member

