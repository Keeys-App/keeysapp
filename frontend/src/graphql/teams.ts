import { gql } from '@apollo/client';

// Fragment for Team fields
export const TEAM_FRAGMENT = gql`
  fragment TeamFields on TeamType {
    id
    name
    description
    owner {
      id
      email
      username
      isActive
      isSuperuser
    }
    members {
      user {
        id
        email
        username
        isActive
        isSuperuser
      }
      role
      createdAt
    }
    invitations {
      id
      invitedEmail
      role
      status
      invitedBy {
        id
        email
        username
      }
      createdAt
    }
    canManage
    membersCount
    createdAt
    updatedAt
  }
`;

// Query to get all teams for current user
export const GET_TEAMS = gql`
  ${TEAM_FRAGMENT}
  query GetTeams {
    teams {
      ...TeamFields
    }
  }
`;

// Query to get a specific team
export const GET_TEAM = gql`
  ${TEAM_FRAGMENT}
  query GetTeam($id: String!) {
    team(id: $id) {
      ...TeamFields
    }
  }
`;

// Mutation to create a team
export const CREATE_TEAM = gql`
  ${TEAM_FRAGMENT}
  mutation CreateTeam($input: CreateTeamInput!) {
    createTeam(input: $input) {
      ...TeamFields
    }
  }
`;

// Mutation to update a team
export const UPDATE_TEAM = gql`
  ${TEAM_FRAGMENT}
  mutation UpdateTeam($input: UpdateTeamInput!) {
    updateTeam(input: $input) {
      ...TeamFields
    }
  }
`;

// Mutation to delete a team
export const DELETE_TEAM = gql`
  mutation DeleteTeam($id: String!) {
    deleteTeam(id: $id)
  }
`;

// Mutation to add a team member
export const ADD_TEAM_MEMBER = gql`
  ${TEAM_FRAGMENT}
  mutation AddTeamMember($input: AddTeamMemberInput!) {
    addTeamMember(input: $input) {
      ...TeamFields
    }
  }
`;

// Mutation to remove a team member
export const REMOVE_TEAM_MEMBER = gql`
  ${TEAM_FRAGMENT}
  mutation RemoveTeamMember($input: RemoveTeamMemberInput!) {
    removeTeamMember(input: $input) {
      ...TeamFields
    }
  }
`;

// Mutation to update team member role
export const UPDATE_TEAM_MEMBER_ROLE = gql`
  ${TEAM_FRAGMENT}
  mutation UpdateTeamMemberRole($input: UpdateTeamMemberRoleInput!) {
    updateTeamMemberRole(input: $input) {
      ...TeamFields
    }
  }
`;

// TypeScript types

export interface User {
  id: string;
  email: string;
  username: string;
  isActive: boolean;
  isSuperuser: boolean;
}

export interface TeamMember {
  user: User;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
  createdAt: string;
}

export interface TeamInvitation {
  id: string;
  invitedEmail: string;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED';
  invitedBy?: User;
  createdAt: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  owner: User;
  members: TeamMember[];
  invitations: TeamInvitation[];
  canManage: boolean;
  membersCount: number;
  createdAt: string;
  updatedAt?: string;
}

export interface CreateTeamInput {
  name: string;
  description?: string;
}

export interface UpdateTeamInput {
  id: string;
  name?: string;
  description?: string;
}

export interface AddTeamMemberInput {
  teamId: string;
  userEmail: string;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
}

export interface RemoveTeamMemberInput {
  teamId: string;
  userId: string;
}

export interface UpdateTeamMemberRoleInput {
  teamId: string;
  userId: string;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
}

export interface GetTeamsResponse {
  teams: Team[];
}

export interface GetTeamResponse {
  team: Team | null;
}

export interface CreateTeamResponse {
  createTeam: Team;
}

export interface UpdateTeamResponse {
  updateTeam: Team | null;
}

export interface DeleteTeamResponse {
  deleteTeam: boolean;
}

export interface AddTeamMemberResponse {
  addTeamMember: Team | null;
}

export interface RemoveTeamMemberResponse {
  removeTeamMember: Team | null;
}

export interface UpdateTeamMemberRoleResponse {
  updateTeamMemberRole: Team | null;
}

// === Invite Queries and Mutations ===

// Query to get public invite info (no auth required)
export const INVITE_INFO_QUERY = gql`
  query InviteInfo($code: String!) {
    inviteInfo(code: $code) {
      id
      teamName
      teamDescription
      inviterName
      inviterEmail
      role
      status
      invitedEmail
      createdAt
    }
  }
`;

// Query to get current user's pending invites
export const MY_PENDING_INVITES_QUERY = gql`
  query MyPendingInvites {
    myPendingInvites {
      id
      teamName
      teamDescription
      inviterName
      role
      createdAt
    }
  }
`;

// Mutation to accept an invite
export const ACCEPT_INVITE_MUTATION = gql`
  ${TEAM_FRAGMENT}
  mutation AcceptInvite($code: String!) {
    acceptInvite(code: $code) {
      ...TeamFields
    }
  }
`;

// Mutation to decline an invite
export const DECLINE_INVITE_MUTATION = gql`
  mutation DeclineInvite($code: String!) {
    declineInvite(code: $code)
  }
`;

// Mutation to resend an invite
export const RESEND_INVITE_MUTATION = gql`
  mutation ResendInvite($invitationId: String!) {
    resendInvite(invitationId: $invitationId)
  }
`;

// TypeScript types for invites

export interface InviteInfo {
  id: string;
  teamName: string;
  teamDescription?: string;
  inviterName: string;
  inviterEmail: string;
  role: string;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED';
  invitedEmail: string;
  createdAt: string;
}

export interface PendingInvite {
  id: string;
  teamName: string;
  teamDescription?: string;
  inviterName: string;
  role: string;
  createdAt: string;
}

export interface InviteInfoResponse {
  inviteInfo: InviteInfo | null;
}

export interface MyPendingInvitesResponse {
  myPendingInvites: PendingInvite[];
}

export interface AcceptInviteResponse {
  acceptInvite: Team | null;
}

export interface DeclineInviteResponse {
  declineInvite: boolean;
}

export interface ResendInviteResponse {
  resendInvite: boolean;
}

