"""
Tests for TeamService and team-related functionality.
"""
import pytest
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.team_invitation import TeamInvitation, InvitationStatus
from app.services.team_service import TeamService


def test_create_team(db_session, test_user):
    """Test creating a team."""
    team = TeamService.create_team(
        db=db_session,
        owner_id=test_user.id,
        name="My Team",
        description="Test team"
    )
    
    assert team.id is not None
    assert team.name == "My Team"
    assert team.description == "Test team"
    assert team.owner_id == test_user.id
    assert team.public_id is not None


def test_get_team_by_public_id(db_session, test_team):
    """Test getting a team by public ID."""
    found_team = TeamService.get_team_by_public_id(db_session, str(test_team.public_id))
    
    assert found_team is not None
    assert found_team.id == test_team.id
    assert found_team.name == test_team.name


def test_get_team_by_invalid_public_id(db_session):
    """Test getting a team with invalid UUID."""
    team = TeamService.get_team_by_public_id(db_session, "invalid-uuid")
    assert team is None


def test_get_user_teams(db_session, test_user):
    """Test getting all teams for a user."""
    # Create teams
    team1 = TeamService.create_team(db_session, test_user.id, "Team 1")
    team2 = TeamService.create_team(db_session, test_user.id, "Team 2")
    
    teams = TeamService.get_user_teams(db_session, test_user.id)
    
    assert len(teams) >= 2
    team_ids = {t.id for t in teams}
    assert team1.id in team_ids
    assert team2.id in team_ids


def test_update_team(db_session, test_team, test_user):
    """Test updating a team."""
    updated_team = TeamService.update_team(
        db=db_session,
        public_id=str(test_team.public_id),
        user_id=test_user.id,
        name="Updated Name",
        description="Updated Description"
    )
    
    assert updated_team is not None
    assert updated_team.name == "Updated Name"
    assert updated_team.description == "Updated Description"


def test_update_team_without_permission(db_session, test_team):
    """Test that non-admin cannot update team."""
    # Create another user
    other_user = User(
        email="other@test.com",
        username="other",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(other_user)
    db_session.commit()
    
    updated_team = TeamService.update_team(
        db=db_session,
        public_id=str(test_team.public_id),
        user_id=other_user.id,
        name="Hacked Name"
    )
    
    assert updated_team is None


def test_delete_team(db_session, test_user):
    """Test deleting a team."""
    team = TeamService.create_team(db_session, test_user.id, "To Delete")
    
    success = TeamService.delete_team(
        db=db_session,
        public_id=str(team.public_id),
        user_id=test_user.id
    )
    
    assert success is True
    
    # Verify team is deleted
    found = TeamService.get_team_by_public_id(db_session, str(team.public_id))
    assert found is None


def test_delete_team_without_permission(db_session, test_team):
    """Test that non-owner cannot delete team."""
    other_user = User(
        email="other@test.com",
        username="other",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(other_user)
    db_session.commit()
    
    success = TeamService.delete_team(
        db=db_session,
        public_id=str(test_team.public_id),
        user_id=other_user.id
    )
    
    assert success is False


def test_add_team_member_by_email_existing_user(db_session, test_team, test_user):
    """Test adding an existing user to a team by email."""
    # Create another user
    new_user = User(
        email="newmember@test.com",
        username="newmember",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(new_user)
    db_session.commit()
    
    # Add member by email
    result = TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="newmember@test.com",
        role="editor",
        added_by_user_id=test_user.id
    )
    
    assert result is True  # Always returns True for security
    
    # Verify member was added
    member = db_session.query(TeamMember).filter(
        TeamMember.team_id == test_team.id,
        TeamMember.user_id == new_user.id
    ).first()
    
    assert member is not None
    assert member.role == "editor"


def test_add_team_member_by_email_non_existing_user(db_session, test_team, test_user):
    """Test inviting a non-existing user creates invitation."""
    result = TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="nonexistent@test.com",
        role="translator",
        added_by_user_id=test_user.id
    )
    
    assert result is True  # Always returns True for security
    
    # Verify invitation was created
    invitation = db_session.query(TeamInvitation).filter(
        TeamInvitation.team_id == test_team.id,
        TeamInvitation.invited_email == "nonexistent@test.com"
    ).first()
    
    assert invitation is not None
    assert invitation.role == "translator"
    assert invitation.status == InvitationStatus.PENDING


def test_add_team_member_case_insensitive_email(db_session, test_team, test_user):
    """Test that email matching is case-insensitive."""
    # Create user with lowercase email
    new_user = User(
        email="casetest@example.com",
        username="casetest",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(new_user)
    db_session.commit()
    
    # Add member with uppercase email
    result = TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="CASETEST@EXAMPLE.COM",
        role="viewer",
        added_by_user_id=test_user.id
    )
    
    assert result is True
    
    # Verify member was added (not invitation)
    member = db_session.query(TeamMember).filter(
        TeamMember.team_id == test_team.id,
        TeamMember.user_id == new_user.id
    ).first()
    
    assert member is not None


def test_remove_team_member(db_session, test_team, test_user):
    """Test removing a team member."""
    # Create and add another user
    member_user = User(
        email="member@test.com",
        username="member",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(member_user)
    db_session.commit()
    
    # Add as member
    TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="member@test.com",
        role="viewer",
        added_by_user_id=test_user.id
    )
    
    # Remove member
    success = TeamService.remove_team_member(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_public_id=str(member_user.public_id),
        removed_by_user_id=test_user.id
    )
    
    assert success is True
    
    # Verify member was removed
    member = db_session.query(TeamMember).filter(
        TeamMember.team_id == test_team.id,
        TeamMember.user_id == member_user.id
    ).first()
    
    assert member is None


def test_cannot_remove_owner(db_session, test_team, test_user):
    """Test that owner cannot be removed from team."""
    success = TeamService.remove_team_member(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_public_id=str(test_user.public_id),
        removed_by_user_id=test_user.id
    )
    
    assert success is False


def test_update_team_member_role(db_session, test_team, test_user):
    """Test updating a team member's role."""
    # Create and add member
    member_user = User(
        email="member@test.com",
        username="member",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(member_user)
    db_session.commit()
    
    TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="member@test.com",
        role="viewer",
        added_by_user_id=test_user.id
    )
    
    # Update role
    updated_member = TeamService.update_team_member_role(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_public_id=str(member_user.public_id),
        role="admin",
        updated_by_user_id=test_user.id
    )
    
    assert updated_member is not None
    assert updated_member.role == "admin"


def test_check_user_team_access(db_session, test_team, test_user):
    """Test checking user access to team."""
    # Owner has access
    has_access = TeamService.check_user_team_access(
        db=db_session,
        team_id=test_team.id,
        user_id=test_user.id
    )
    assert has_access is True
    
    # Non-member has no access
    other_user = User(
        email="other@test.com",
        username="other",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(other_user)
    db_session.commit()
    
    has_access = TeamService.check_user_team_access(
        db=db_session,
        team_id=test_team.id,
        user_id=other_user.id
    )
    assert has_access is False


def test_can_user_manage_team_as_owner(db_session, test_team, test_user):
    """Test that owner can manage team."""
    can_manage = TeamService.can_user_manage_team(
        db=db_session,
        team_id=test_team.id,
        user_id=test_user.id
    )
    assert can_manage is True


def test_can_user_manage_team_as_admin(db_session, test_team, test_user):
    """Test that admin member can manage team."""
    # Create admin member
    admin_user = User(
        email="admin@test.com",
        username="admin",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(admin_user)
    db_session.commit()
    
    TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="admin@test.com",
        role="admin",
        added_by_user_id=test_user.id
    )
    
    can_manage = TeamService.can_user_manage_team(
        db=db_session,
        team_id=test_team.id,
        user_id=admin_user.id
    )
    assert can_manage is True


def test_can_user_manage_team_as_viewer(db_session, test_team, test_user):
    """Test that viewer member cannot manage team."""
    # Create viewer member
    viewer_user = User(
        email="viewer@test.com",
        username="viewer",
        hashed_password=User.get_password_hash("password123")
    )
    db_session.add(viewer_user)
    db_session.commit()
    
    TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="viewer@test.com",
        role="viewer",
        added_by_user_id=test_user.id
    )
    
    can_manage = TeamService.can_user_manage_team(
        db=db_session,
        team_id=test_team.id,
        user_id=viewer_user.id
    )
    assert can_manage is False


def test_invitation_system_security(db_session, test_team, test_user):
    """
    Test that invitation system doesn't reveal user existence.
    All calls should return True regardless of user existence.
    """
    # Add existing user
    result1 = TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email=test_user.email,  # Existing user (owner)
        role="admin",
        added_by_user_id=test_user.id
    )
    
    # Add non-existing user
    result2 = TeamService.add_team_member_by_email(
        db=db_session,
        team_public_id=str(test_team.public_id),
        user_email="nonexistent@example.com",
        role="viewer",
        added_by_user_id=test_user.id
    )
    
    # Both should return True (security)
    assert result1 is True
    assert result2 is True

