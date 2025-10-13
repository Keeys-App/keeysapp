import { gql } from '@apollo/client';

// Mutation to grant project access
export const GRANT_PROJECT_ACCESS = gql`
  mutation GrantProjectAccess($input: GrantProjectAccessInput!) {
    grantProjectAccess(input: $input)
  }
`;

// Mutation to revoke project access
export const REVOKE_PROJECT_ACCESS = gql`
  mutation RevokeProjectAccess($input: RevokeProjectAccessInput!) {
    revokeProjectAccess(input: $input)
  }
`;

// Mutation to update project access role
export const UPDATE_PROJECT_ACCESS_ROLE = gql`
  mutation UpdateProjectAccessRole($input: UpdateProjectAccessRoleInput!) {
    updateProjectAccessRole(input: $input)
  }
`;

// TypeScript types

export interface GrantProjectAccessInput {
  projectId: string;
  userId: string;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
}

export interface RevokeProjectAccessInput {
  projectId: string;
  userId: string;
}

export interface UpdateProjectAccessRoleInput {
  projectId: string;
  userId: string;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
}

export interface GrantProjectAccessResponse {
  grantProjectAccess: boolean;
}

export interface RevokeProjectAccessResponse {
  revokeProjectAccess: boolean;
}

export interface UpdateProjectAccessRoleResponse {
  updateProjectAccessRole: boolean;
}

