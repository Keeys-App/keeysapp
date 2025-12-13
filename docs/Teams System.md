# Teams System

## Overview

The Teams system is a core feature that enables collaborative work on localization projects. Teams serve as the central organizational unit, with projects belonging to teams and access controlled at both team and project levels.

## Architecture

### Data Models

#### Team
The main organizational unit that groups users and projects together.

**Model:** `backend/app/models/team.py`

```python
class Team:
    id: int                    # Internal ID
    public_id: UUID           # Public-facing UUID
    name: str                 # Team name
    description: str          # Optional description
    owner_id: int            # Team owner (creator)
    created_at: datetime
    updated_at: datetime
```

**Relationships:**
- `owner` → User (one-to-one)
- `members` → TeamMember[] (one-to-many)
- `invitations` → TeamInvitation[] (one-to-many)
- `projects` → Project[] (one-to-many)

#### TeamMember
Represents a user's membership in a team with a specific role.

**Model:** `backend/app/models/team.py`

```python
class TeamMember:
    id: int
    team_id: int
    user_id: int
    role: str                # admin, editor, viewer, translator, reviewer
    created_at: datetime
```

**Roles:**
- **admin** - Full access to team management and all projects
- **editor** - Can edit project content
- **viewer** - Read-only access
- **translator** - Can translate texts
- **reviewer** - Can review translations

#### TeamInvitation
Stores invitations to join a team, supporting invites to non-registered users.

**Model:** `backend/app/models/team_invitation.py`

```python
class TeamInvitation:
    id: int
    public_id: UUID
    team_id: int
    invited_email: str        # Email address (user may not exist yet)
    role: str
    status: InvitationStatus  # PENDING, ACCEPTED, DECLINED
    invited_by_user_id: int
    invited_user_id: int      # Set if user exists
    created_at: datetime
```

#### ProjectAccess
Manages granular access control to specific projects within a team.

**Model:** `backend/app/models/project_access.py`

```python
class ProjectAccess:
    id: int
    project_id: int
    user_id: int
    role: str                # admin, editor, viewer, translator, reviewer
    granted_by_user_id: int
    created_at: datetime
```

### Relationships

```
User
  ├── owned_teams → Team[]
  ├── team_memberships → TeamMember[]
  └── project_access → ProjectAccess[]

Team
  ├── owner → User
  ├── members → TeamMember[]
  ├── invitations → TeamInvitation[]
  └── projects → Project[]

Project
  ├── team → Team
  ├── owner → User
  └── access_members → ProjectAccess[]
```

## Key Features

### 1. Team Management

**Creating Teams:**
- Any authenticated user can create a team
- Creator becomes the team owner
- No limit on number of teams

**Updating Teams:**
- Only owner or admin members can update
- Can modify name and description

**Deleting Teams:**
- Only owner can delete
- Cascade deletes all team members, invitations, and projects

### 2. Team Membership

**Adding Members:**
- Owner or admin can add members
- Uses email-based invitation system
- If user exists → added immediately as TeamMember
- If user doesn't exist → creates TeamInvitation (PENDING)

**Security Note:**
- System NEVER reveals if a user exists or not
- Always shows "Invitation sent successfully"
- Prevents user enumeration attacks

**Roles and Permissions:**
- Owner: Full control (cannot be removed or changed)
- Admin: Can manage team and members
- Editor, Viewer, Translator, Reviewer: Team access only

**Removing Members:**
- Owner or admin can remove members
- Cannot remove owner
- Removes all project access when removed from team

### 3. Project Access Control

**Two-Level Access:**
1. **Team Level** - User must be in team (owner or member)
2. **Project Level** - User must have ProjectAccess entry

**Granting Project Access:**
- Only project owner or admin can grant access
- User must be in the team first
- Can specify role for the project

**Access Hierarchy:**
- Project owner: Always has full access
- ProjectAccess with admin role: Can manage access
- ProjectAccess with other roles: Limited by role

## API Reference

### GraphQL Queries

#### `teams`
Get all teams for current user (owned or member).

```graphql
query GetTeams {
  teams {
    id
    name
    description
    owner { ... }
    members { ... }
    invitations { ... }
    canManage
    membersCount
  }
}
```

#### `team(id: String!)`
Get a specific team by UUID.

```graphql
query GetTeam($id: String!) {
  team(id: $id) {
    id
    name
    # ... same fields as teams
  }
}
```

### GraphQL Mutations

#### `createTeam`
Create a new team.

```graphql
mutation CreateTeam($input: CreateTeamInput!) {
  createTeam(input: $input) {
    id
    name
    description
  }
}
```

**Input:**
```typescript
{
  name: string;
  description?: string;
}
```

#### `updateTeam`
Update team details (owner or admin only).

```graphql
mutation UpdateTeam($input: UpdateTeamInput!) {
  updateTeam(input: $input) {
    id
    name
    description
  }
}
```

#### `addTeamMember`
Add or invite a member by email.

```graphql
mutation AddTeamMember($input: AddTeamMemberInput!) {
  addTeamMember(input: $input) {
    id
    members { ... }
    invitations { ... }
  }
}
```

**Input:**
```typescript
{
  teamId: string;      // Team UUID
  userEmail: string;   // Email of user to add/invite
  role: string;        // admin, editor, viewer, translator, reviewer
}
```

**Behavior:**
- User exists → added as TeamMember immediately
- User doesn't exist → creates TeamInvitation (PENDING)
- User already member → updates role
- Always returns success (security)

#### `removeTeamMember`
Remove a member from team.

```graphql
mutation RemoveTeamMember($input: RemoveTeamMemberInput!) {
  removeTeamMember(input: $input) {
    id
    members { ... }
  }
}
```

#### `updateTeamMemberRole`
Change a member's role.

```graphql
mutation UpdateTeamMemberRole($input: UpdateTeamMemberRoleInput!) {
  updateTeamMemberRole(input: $input) {
    id
    members { ... }
  }
}
```

### Project Access Mutations

#### `grantProjectAccess`
Grant a user access to a specific project.

```graphql
mutation GrantProjectAccess($input: GrantProjectAccessInput!) {
  grantProjectAccess(input: $input)
}
```

**Input:**
```typescript
{
  projectId: string;  // Project UUID
  userId: string;     // User UUID
  role: string;       // admin, editor, viewer, translator, reviewer
}
```

**Requirements:**
- User must be in the team
- Current user must be project owner or admin

#### `revokeProjectAccess`
Remove user's access to a project.

```graphql
mutation RevokeProjectAccess($input: RevokeProjectAccessInput!) {
  revokeProjectAccess(input: $input)
}
```

#### `updateProjectAccessRole`
Change user's role in a project.

```graphql
mutation UpdateProjectAccessRole($input: UpdateProjectAccessRoleInput!) {
  updateProjectAccessRole(input: $input)
}
```

## Frontend Components

### Pages

**`TeamsPage.tsx`** - List all user's teams
- Shows team cards with member count
- "Create Team" button
- Click card → navigate to team details

**`TeamPage.tsx`** - Team details and member management
- Team information
- Members list with roles and status
- Add/remove members (admin only)
- Change member roles (admin only)
- Shows pending invitations

**`CreateTeamPage.tsx`** - Create new team
- Team name (required)
- Description (optional)

**`EditTeamPage.tsx`** - Edit team details
- Only accessible to owner/admin
- Update name and description

### Components

**`TeamSwitcher.tsx`** - Global team selector in header
- Dropdown with all user's teams
- Auto-selects first team on load
- Navigate to dashboard on team change
- "Create Team" quick action

**`TeamCard.tsx`** - Team card in teams list
- Team name, description, member count
- Admin badge if user can manage
- Actions menu (View, Settings)

**`TeamMembersList.tsx`** - Table of team members
- Shows owner, active members, pending invitations
- Visual distinction (Active vs Pending Invite)
- Role badges with colors
- Actions menu for each member (admin only)

**`AddTeamMemberDialog.tsx`** - Add member dialog
- Email input (no user enumeration)
- Role selection
- Always shows success (security)

**`UserSearchInput.tsx`** - Email input field
- Simple text input for email
- No autocomplete or user search
- Security-focused design

**`TeamSelector.tsx`** - Team selector for project creation
- Dropdown with user's teams
- Used in CreateProjectPage

## User Flows

### Creating and Managing a Team

1. **Create Team:**
   - Navigate to Teams → "Create Team"
   - Enter name and description
   - Team created with user as owner

2. **Add Members:**
   - Go to team page
   - Click "Add Member"
   - Enter member's email
   - Select role
   - Click "Add Member"
   - Result: Member added (if exists) or invited (if not)

3. **Manage Roles:**
   - On team page, click ⋮ on member row
   - Select "Change Role"
   - Choose new role
   - Role updated immediately

4. **Remove Members:**
   - Click ⋮ on member row
   - Select "Remove"
   - Confirm removal
   - Member removed from team and all projects

### Working with Projects in Teams

1. **Create Project:**
   - Select team from header switcher
   - Click "Create Project"
   - Fill project details
   - Project created in selected team

2. **Filter Projects by Team:**
   - Use team switcher in header
   - Dashboard automatically shows only selected team's projects

3. **Grant Project Access:**
   - Navigate to project
   - Access "Project Access" section (admin only)
   - Select team member
   - Grant access with specific role

## Security Considerations

### User Enumeration Prevention

**Problem:** Revealing whether a user exists in the system allows attackers to enumerate users.

**Solution:**
1. **No user search** - Cannot browse/search all users
2. **Email-only input** - Must know exact email
3. **Consistent responses** - Always "Invitation sent successfully"
4. **Backend logging** - Real results logged for admins only

**Example:**
```typescript
// User enters: "unknown@example.com"
// Response: "Invitation sent successfully" ✅

// Backend log: "Team invitation sent to non-existent email: unknown@example.com"
```

### Access Control

**Team Access:**
```python
def can_user_manage_team(team_id, user_id):
    # Owner can always manage
    if team.owner_id == user_id:
        return True
    
    # Admin members can manage
    if member.role == "admin":
        return True
    
    return False
```

**Project Access:**
```python
def check_project_access(project_id, user_id):
    # Owner always has access
    if project.owner_id == user_id:
        return True
    
    # Check ProjectAccess entry
    if ProjectAccess.exists(project_id, user_id):
        return True
    
    return False
```

### UUID Usage

All public-facing IDs use UUIDs instead of sequential integers:
- Prevents enumeration attacks
- Makes brute-force impractical
- Better security for public APIs

## Database Schema

### Tables

**teams**
```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    public_id UUID UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**team_members**
```sql
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(team_id, user_id)
);
```

**team_invitations**
```sql
CREATE TABLE team_invitations (
    id SERIAL PRIMARY KEY,
    public_id UUID UNIQUE NOT NULL,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    invited_email VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL,
    status invitation_status NOT NULL DEFAULT 'PENDING',
    invited_by_user_id INTEGER REFERENCES users(id),
    invited_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(team_id, invited_email)
);
```

**project_access**
```sql
CREATE TABLE project_access (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    granted_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(project_id, user_id)
);
```

### Migrations

**Migration Files:**
1. `create_teams_system.py` - Creates teams, team_members, project_access tables
2. Migration adds `team_id` to projects table

**Running Migrations:**
```bash
cd backend
python -m migrations.create_teams_system
```

**Migration handles:**
- Creating new tables with indexes
- Adding team_id column to projects
- Dropping old project_members table
- Setting up foreign key constraints

## Implementation Details

### Backend Services

**TeamService** (`backend/app/services/team_service.py`)
- `create_team()` - Create new team
- `get_team_by_public_id()` - Fetch team with eager loading
- `get_user_teams()` - Get all teams for user
- `update_team()` - Update team details
- `delete_team()` - Delete team (owner only)
- `add_team_member_by_email()` - Add/invite member by email
- `remove_team_member()` - Remove member
- `update_team_member_role()` - Change member role
- `check_user_team_access()` - Verify team access
- `can_user_manage_team()` - Check management permissions

**ProjectAccessService** (`backend/app/services/project_access_service.py`)
- `grant_project_access()` - Give user access to project
- `revoke_project_access()` - Remove user access
- `update_project_access_role()` - Change user's project role
- `get_project_members()` - List all project members
- `check_project_access()` - Verify project access
- `get_user_role_in_project()` - Get user's role

### Frontend State Management

**TeamStore** (`frontend/src/stores/teamStore.ts`)
- Manages currently selected team
- Persists selection in localStorage
- Used for filtering projects by team

**Usage:**
```typescript
const { selectedTeamId, setSelectedTeamId } = useTeamStore();
```

### Navigation

**Routes:**
- `/teams` - List all teams
- `/team/create` - Create new team
- `/team/:id` - View team details
- `/team/:id/edit` - Edit team (admin only)

**Updated Routes:**
- All project creation requires team selection
- Dashboard filters by selected team
- Import projects into selected team

## UI/UX Patterns

### Team Selection Flow

1. User logs in
2. TeamSwitcher auto-selects first team
3. Dashboard shows projects from selected team
4. User can switch teams via header dropdown
5. Switching team navigates to dashboard

### Adding Team Members

**User exists in system:**
```
Enter email → Select role → Click Add
→ User added to team immediately
→ Shows "Invitation sent successfully"
→ User appears in Active members list
```

**User doesn't exist:**
```
Enter email → Select role → Click Add
→ Invitation created in database
→ Shows "Invitation sent successfully"
→ Email appears in Pending Invitations list
```

**User already in team:**
```
Enter email → Select role → Click Add
→ Role updated silently
→ Shows "Invitation sent successfully"
→ No error message (security)
```

### Visual Indicators

**Active Members:**
- Green "Active" badge
- Full username and email
- Normal background
- Full action menu

**Pending Invitations:**
- Yellow "Pending Invite" badge
- Email only (with mail icon)
- Muted background
- Cancel button only

**Current User:**
- Small "You" badge next to name
- Works for both owner and members

## Performance Optimizations

### Apollo Client Caching

All queries use optimized fetch policies:
```typescript
{
  fetchPolicy: 'cache-and-network',    // Use cache first, then network
  nextFetchPolicy: 'cache-first',      // Subsequent queries from cache
}
```

**Benefits:**
- Instant page loads from cache
- Background updates keep data fresh
- Reduced server load
- No loading spinners on repeat visits

### React Optimizations

**BreadcrumbContext:**
- `useCallback` for stable function references
- `useMemo` for context value
- Prevents unnecessary re-renders

**ProjectList:**
- `useMemo` for project filtering
- Only recomputes when data or team changes

**Conditional Loading:**
```typescript
if (loading && !data) {
  return <Spinner />;  // Only if no cached data
}
```

### Navigation

All navigation uses React Router `<Link>` or `navigate()`:
- No page reloads
- Preserves application state
- Maintains Apollo cache
- Smooth transitions

## Testing

### Manual Testing Checklist

**Team Management:**
- [ ] Create team
- [ ] Update team name/description
- [ ] Delete team (verify cascade)

**Member Management:**
- [ ] Add existing user by email
- [ ] Add non-existing user (creates invitation)
- [ ] Add user already in team (updates role)
- [ ] Remove team member
- [ ] Change member role

**Project Access:**
- [ ] Create project in team
- [ ] Grant project access to team member
- [ ] Revoke project access
- [ ] Change project access role

**Security:**
- [ ] Try adding invalid email → still shows success
- [ ] Try adding non-existent user → shows success, creates invitation
- [ ] Verify no user enumeration possible

**Navigation:**
- [ ] Switch teams via header → navigates to dashboard
- [ ] Click logo → navigates without reload
- [ ] Click breadcrumbs → navigates without reload
- [ ] No page flashing on navigation

## Troubleshooting

### Teams not showing
- Check if user is owner or member of any team
- Verify teams table has data
- Check GraphQL response for errors

### Members not appearing after adding
- If user exists → should appear immediately in Active members
- If user doesn't exist → should appear in Pending Invitations
- Check team_members or team_invitations table

### Projects not filtered by team
- Ensure team is selected in header
- Check selectedTeamId in teamStore
- Verify project.team_id is set in database

### Import project fails
- Ensure team is selected before importing
- Verify user has access to team
- Check backend logs for actual error

## Future Enhancements

### Planned Features

1. **Invitation Acceptance Flow**
   - Email notifications
   - Accept/decline invitation page
   - Auto-join team on registration

2. **Team Settings**
   - Team visibility (public/private)
   - Default project permissions
   - Team avatar/logo

3. **Advanced Access Control**
   - Custom roles
   - Permission templates
   - Bulk access management

4. **Team Analytics**
   - Member activity
   - Project statistics
   - Translation progress by team

## Related Documentation

- [[Project Structure]] - Overall application architecture
- [[Authentication Setup]] - User authentication system
- [[Security Best Practices]] - Security guidelines
- [[Error Handling Best Practices]] - Error handling patterns
- [[Performance Optimization]] - General performance tips

