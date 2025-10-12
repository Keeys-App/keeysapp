from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
import uuid as uuid_lib
import logging

from app.models.team import Team, TeamMember
from app.models.user import User

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
                selectinload(Team.members).joinedload(TeamMember.user)
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
        
        # Update fields if provided
        if name is not None:
            team.name = name
        if description is not None:
            team.description = description
        
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
    ) -> Optional[TeamMember]:
        """
        Add a member to a team by email address. Only owner or admin can add members.
        
        Args:
            db: Database session
            team_public_id: Public UUID of the team
            user_email: Email of the user to add
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
        
        # Get user by email
        user = db.query(User).filter(User.email == user_email.lower().strip()).first()
        if not user:
            logger.warning(f"User with email {user_email} not found")
            return None
        
        # Check if already a member
        existing_member = db.query(TeamMember).filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id
        ).first()
        
        if existing_member:
            # Update role if already exists
            existing_member.role = role
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
        db.commit()
        db.refresh(member)
        return member

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
            existing_member.role = role
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
        
        member.role = role
        db.commit()
        db.refresh(member)
        return member

