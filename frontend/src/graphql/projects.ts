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

// Fragment for language config data
export const LANGUAGE_CONFIG_FRAGMENT = gql`
  fragment LanguageConfigFields on LanguageConfigType {
    code
    locale
    direction
    pluralForms
    default
  }
`;

// Fragment for project data
export const PROJECT_FRAGMENT = gql`
  fragment ProjectFields on ProjectType {
    id
    name
    description
    languages {
      ...LanguageConfigFields
    }
    defaultLanguage
    availableTags
    color
    status
    team {
      id
      name
      description
    }
    owner {
      ...UserFields
    }
    accessMembers {
      ...ProjectMemberFields
    }
    canEdit
    keysCount
    translationProgress
    languageProgress {
      code
      progress
      completed
      total
    }
    createdAt
    updatedAt
  }
  ${USER_FRAGMENT}
  ${PROJECT_MEMBER_FRAGMENT}
  ${LANGUAGE_CONFIG_FRAGMENT}
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

// Query to get all available languages (single source of truth)
export const GET_AVAILABLE_LANGUAGES = gql`
  query GetAvailableLanguages {
    availableLanguages {
      code
      name
      nativeName
      flag
      locale
      direction
      pluralForms
      detectionPatterns {
        endPatterns
        middlePatterns
        startPatterns
        fullNames
      }
    }
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
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
  createdAt: string;
}

export interface SimpleTeam {
  id: string;
  name: string;
  description?: string | null;
}

/**
 * Plural form categories according to CLDR standard.
 * - zero: Used for zero quantity (e.g., Arabic)
 * - one: Singular form (e.g., 1 item)
 * - two: Dual form (e.g., Arabic for exactly 2)
 * - few: Paucal form (e.g., Russian 2-4)
 * - many: Large quantity form (e.g., Russian 5-20)
 * - other: General/default form (always present)
 */
export type PluralForm = 'zero' | 'one' | 'two' | 'few' | 'many' | 'other';

export interface LanguageConfig {
  code: string;
  locale: string;
  direction: 'ltr' | 'rtl';
  pluralForms: PluralForm[];
  default?: boolean;
}

export interface LanguageConfigInput {
  code: string;
  locale: string;
  direction?: string;
  default?: boolean;
}

export interface LanguageProgress {
  code: string;
  progress: number;
  completed: number;
  total: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  languages: LanguageConfig[];
  defaultLanguage?: string | null;
  availableTags: string[];
  color: string;
  status: 'active' | 'archived' | 'draft';
  team: SimpleTeam;
  owner: User;
  accessMembers: ProjectMember[];
  canEdit: boolean;
  keysCount: number;
  translationProgress: number;
  languageProgress: LanguageProgress[];
  createdAt: string;
  updatedAt?: string | null;
}

export interface CreateProjectInput {
  name: string;
  teamId: string;
  description?: string | null;
  languages?: LanguageConfigInput[] | null;
  defaultLanguage?: string | null;
  color?: string | null;
  status?: 'active' | 'archived' | 'draft' | null;
}

export interface UpdateProjectInput {
  id: string;
  name?: string | null;
  description?: string | null;
  languages?: LanguageConfigInput[] | null;
  defaultLanguage?: string | null;
  color?: string | null;
  status?: 'active' | 'archived' | 'draft' | null;
}

export interface AddProjectMemberInput {
  projectId: string;
  userId: string;
  role: 'admin' | 'editor' | 'viewer' | 'translator' | 'reviewer';
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

// Available languages types (single source of truth from backend)

export interface DetectionPatterns {
  endPatterns: string[];
  middlePatterns: string[];
  startPatterns: string[];
  fullNames: string[];
}

export interface AvailableLanguage {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  locale: string;
  direction: 'ltr' | 'rtl';
  pluralForms: PluralForm[];
  detectionPatterns: DetectionPatterns;
}

export interface GetAvailableLanguagesData {
  availableLanguages: AvailableLanguage[];
}

