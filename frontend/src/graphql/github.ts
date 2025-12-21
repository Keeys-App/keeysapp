import { gql } from '@apollo/client';

/**
 * GraphQL queries and mutations for GitHub integration
 * GitHub connections are linked to Teams
 */

// Query to get all GitHub connections for a team
export const TEAM_GITHUB_CONNECTIONS_QUERY = gql`
  query TeamGitHubConnections($teamId: String!, $validate: Boolean) {
    teamGithubConnections(teamId: $teamId, validate: $validate) {
      id
      githubUsername
      githubAvatarUrl
      githubEmail
      scope
      connectedAt
      connectedByUsername
      isValid
    }
  }
`;

// Query to get a specific GitHub connection
export const GITHUB_CONNECTION_QUERY = gql`
  query GitHubConnection($connectionId: String!) {
    githubConnection(connectionId: $connectionId) {
      id
      githubUsername
      githubAvatarUrl
      githubEmail
      scope
      connectedAt
      connectedByUsername
    }
  }
`;

// Mutation to get GitHub OAuth authorization URL for a team
export const GET_GITHUB_AUTH_URL_MUTATION = gql`
  mutation GetGitHubAuthUrl($teamId: String!) {
    getGithubAuthUrl(teamId: $teamId) {
      authorizationUrl
      state
    }
  }
`;

// Mutation to disconnect GitHub from a team
export const DISCONNECT_GITHUB_MUTATION = gql`
  mutation DisconnectGitHub($connectionId: String!) {
    disconnectGithub(connectionId: $connectionId) {
      success
      message
    }
  }
`;

// Query to get GitHub App installation info
export const GITHUB_APP_INFO_QUERY = gql`
  query GitHubAppInfo($teamId: String!) {
    githubAppInfo(teamId: $teamId) {
      installationUrl
      hasInstallation
      installations {
        id
        accountLogin
        accountType
        repositorySelection
        htmlUrl
      }
    }
  }
`;

// Query to get available repositories from team's GitHub connections
export const AVAILABLE_GITHUB_REPOS_QUERY = gql`
  query AvailableGitHubRepositories($teamId: String!) {
    availableGithubRepositories(teamId: $teamId) {
      id
      fullName
      name
      owner
      defaultBranch
      private
      description
      htmlUrl
    }
  }
`;

// Query to search repositories via GitHub Search API
export const SEARCH_GITHUB_REPOS_QUERY = gql`
  query SearchGitHubRepositories($teamId: String!, $query: String!) {
    searchGithubRepositories(teamId: $teamId, query: $query) {
      id
      fullName
      name
      owner
      defaultBranch
      private
      description
      htmlUrl
    }
  }
`;

// Query to get repository linked to a project
export const PROJECT_REPOSITORY_QUERY = gql`
  query ProjectRepository($projectId: String!) {
    projectRepository(projectId: $projectId) {
      id
      githubRepoId
      repoOwner
      repoName
      fullName
      defaultBranch
      i18nFramework
      sourcePatterns
      localePath
      githubUsername
      connectedAt
    }
  }
`;

// Mutation to connect a repository to a project
export const CONNECT_REPOSITORY_MUTATION = gql`
  mutation ConnectRepository($projectId: String!, $githubRepoId: String!, $githubConnectionId: String!) {
    connectRepository(projectId: $projectId, githubRepoId: $githubRepoId, githubConnectionId: $githubConnectionId) {
      success
      message
      repository {
        id
        githubRepoId
        repoOwner
        repoName
        fullName
        defaultBranch
        githubUsername
        connectedAt
      }
    }
  }
`;

// Mutation to disconnect a repository from a project
export const DISCONNECT_REPOSITORY_MUTATION = gql`
  mutation DisconnectRepository($projectId: String!) {
    disconnectRepository(projectId: $projectId) {
      success
      message
    }
  }
`;

// Types for TypeScript
export interface GitHubConnection {
  id: string;
  githubUsername: string;
  githubAvatarUrl: string | null;
  githubEmail: string | null;
  scope: string | null;
  connectedAt: string;
  connectedByUsername: string | null;
  isValid: boolean | null;
}

export interface GitHubRepo {
  id: string;
  fullName: string;
  name: string;
  owner: string;
  defaultBranch: string;
  private: boolean;
  description: string | null;
  htmlUrl: string;
}

export interface Repository {
  id: string;
  githubRepoId: string;
  repoOwner: string;
  repoName: string;
  fullName: string;
  defaultBranch: string;
  i18nFramework: string | null;
  sourcePatterns: string[];
  localePath: string | null;
  githubUsername: string | null;
  connectedAt: string;
}

export interface GitHubInstallation {
  id: string;
  accountLogin: string;
  accountType: string;
  repositorySelection: string;
  htmlUrl: string | null;
}

export interface GitHubAppInfo {
  installationUrl: string | null;
  hasInstallation: boolean;
  installations: GitHubInstallation[];
}

export interface GitHubAuthUrlResult {
  authorizationUrl: string;
  state: string;
}

export interface DisconnectGitHubResult {
  success: boolean;
  message: string;
}

export interface ConnectRepositoryResult {
  success: boolean;
  message: string;
  repository: Repository | null;
}
