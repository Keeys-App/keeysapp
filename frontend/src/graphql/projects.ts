import { gql } from '@apollo/client';

/**
 * GraphQL operations for projects module.
 */

// Fragment for user data
export const USER_FRAGMENT = gql`
  fragment UserFields on UserType {
    id
    email
    username
    isActive
    isSuperuser
  }
`;

// Fragment for project member data
export const PROJECT_MEMBER_FRAGMENT = gql`
  fragment ProjectMemberFields on ProjectMemberType {
    user {
      ...UserFields
    }
    role
    createdAt
  }
  ${USER_FRAGMENT}
`;

// Fragment for project data
export const PROJECT_FRAGMENT = gql`
  fragment ProjectFields on ProjectType {
    id
    name
    description
    languages
    color
    status
    owner {
      ...UserFields
    }
    members {
      ...ProjectMemberFields
    }
    canEdit
    keysCount
    createdAt
    updatedAt
  }
  ${USER_FRAGMENT}
  ${PROJECT_MEMBER_FRAGMENT}
`;

// Query to get all projects
export const GET_PROJECTS = gql`
  query GetProjects {
    projects {
      ...ProjectFields
    }
  }
  ${PROJECT_FRAGMENT}
`;

// Query to get a single project
export const GET_PROJECT = gql`
  query GetProject($id: String!) {
    project(id: $id) {
      ...ProjectFields
    }
  }
  ${PROJECT_FRAGMENT}
`;

// Mutation to create a project
export const CREATE_PROJECT = gql`
  mutation CreateProject($input: CreateProjectInput!) {
    createProject(input: $input) {
      ...ProjectFields
    }
  }
  ${PROJECT_FRAGMENT}
`;

// Mutation to update a project
export const UPDATE_PROJECT = gql`
  mutation UpdateProject($input: UpdateProjectInput!) {
    updateProject(input: $input) {
      ...ProjectFields
    }
  }
  ${PROJECT_FRAGMENT}
`;

// Mutation to delete a project
export const DELETE_PROJECT = gql`
  mutation DeleteProject($id: String!) {
    deleteProject(id: $id)
  }
`;

// Mutation to add a project member
export const ADD_PROJECT_MEMBER = gql`
  mutation AddProjectMember($input: AddProjectMemberInput!) {
    addProjectMember(input: $input) {
      ...ProjectFields
    }
  }
  ${PROJECT_FRAGMENT}
`;

// TypeScript types for GraphQL operations

export interface User {
  id: string;
  email: string;
  username: string;
  isActive: boolean;
  isSuperuser: boolean;
}

export interface ProjectMember {
  user: User;
  role: 'admin' | 'editor' | 'viewer';
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  languages: string[];
  color: string;
  status: 'active' | 'archived' | 'draft';
  owner: User;
  members: ProjectMember[];
  canEdit: boolean;
  keysCount: number;
  createdAt: string;
  updatedAt?: string | null;
}

export interface CreateProjectInput {
  name: string;
  description?: string | null;
  languages?: string[] | null;
  color?: string | null;
  status?: 'active' | 'archived' | 'draft' | null;
}

export interface UpdateProjectInput {
  id: string;
  name?: string | null;
  description?: string | null;
  languages?: string[] | null;
  color?: string | null;
  status?: 'active' | 'archived' | 'draft' | null;
}

export interface AddProjectMemberInput {
  projectId: string;
  userId: string;
  role: 'admin' | 'editor' | 'viewer';
}

// Query result types
export interface GetProjectsData {
  projects: Project[];
}

export interface GetProjectData {
  project: Project | null;
}

export interface CreateProjectData {
  createProject: Project;
}

export interface UpdateProjectData {
  updateProject: Project | null;
}

export interface DeleteProjectData {
  deleteProject: boolean;
}

export interface AddProjectMemberData {
  addProjectMember: Project | null;
}

