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

// Query to search users
export const SEARCH_USERS = gql`
  query SearchUsers($query: String!, $limit: Int) {
    searchUsers(query: $query, limit: $limit) {
      id
      email
      username
      isActive
      isSuperuser
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

export interface Team {
  id: string;
  name: string;
  description?: string;
  owner: User;
  members: TeamMember[];
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
  userId: string;
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

export interface SearchUsersResponse {
  searchUsers: User[];
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

