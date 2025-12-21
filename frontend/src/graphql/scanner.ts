import { gql } from '@apollo/client';

/**
 * GraphQL queries and mutations for repository scanning
 */

// Query to get a scan session with found strings
export const SCAN_SESSION_QUERY = gql`
  query ScanSession($scanSessionId: String!) {
    scanSession(scanSessionId: $scanSessionId) {
      id
      status
      aiProvider
      aiModel
      scanPath
      keyNamingStyle
      keyNamingDelimiter
      filesTotal
      filesScanned
      stringsFound
      errorMessage
      createdAt
      startedAt
      completedAt
      prBranchName
      prNumber
      prUrl
      prCreatedAt
      foundStrings {
        id
        filePath
        lineNumber
        originalText
        suggestedKey
        context
        confidence
        status
        keyId
        matchedKeyId
        matchedKeyName
        fileType
        fileLanguage
        fileFramework
        createdAt
      }
    }
  }
`;

// Query to get scan sessions for a project
export const PROJECT_SCAN_SESSIONS_QUERY = gql`
  query ProjectScanSessions($projectId: String!, $limit: Int) {
    projectScanSessions(projectId: $projectId, limit: $limit) {
      id
      status
      aiProvider
      aiModel
      scanPath
      keyNamingStyle
      keyNamingDelimiter
      filesTotal
      filesScanned
      stringsFound
      errorMessage
      createdAt
      startedAt
      completedAt
      prBranchName
      prNumber
      prUrl
      prCreatedAt
      foundStrings {
        id
        filePath
        lineNumber
        originalText
        suggestedKey
        context
        confidence
        status
        keyId
        matchedKeyId
        matchedKeyName
        fileType
        fileLanguage
        fileFramework
        createdAt
      }
    }
  }
`;

// Query to get team token usage statistics
export const TEAM_TOKEN_USAGE_QUERY = gql`
  query TeamTokenUsage($teamId: String!, $days: Int) {
    teamTokenUsage(teamId: $teamId, days: $days) {
      totalInputTokens
      totalOutputTokens
      totalTokens
      operationsCount
    }
  }
`;

// Query to get repository directories for autocomplete
export const REPOSITORY_DIRECTORIES_QUERY = gql`
  query RepositoryDirectories($projectId: String!, $prefix: String) {
    repositoryDirectories(projectId: $projectId, prefix: $prefix) {
      path
      name
      isRecommended
    }
  }
`;

// Mutation to start a repository scan
// Note: AI settings are taken from Team configuration on backend
export const START_REPOSITORY_SCAN_MUTATION = gql`
  mutation StartRepositoryScan(
    $projectId: String!
    $scanPath: String
    $keyNamingStyle: String
    $keyNamingDelimiter: String
  ) {
    startRepositoryScan(
      projectId: $projectId
      scanPath: $scanPath
      keyNamingStyle: $keyNamingStyle
      keyNamingDelimiter: $keyNamingDelimiter
    ) {
      success
      message
      scanSession {
        id
        status
        aiProvider
        aiModel
        scanPath
        keyNamingStyle
        keyNamingDelimiter
        filesTotal
        filesScanned
        stringsFound
        createdAt
        startedAt
      }
    }
  }
`;

// Mutation to cancel a scan
export const CANCEL_SCAN_MUTATION = gql`
  mutation CancelScan($scanSessionId: String!) {
    cancelScan(scanSessionId: $scanSessionId) {
      success
      message
      scanSession {
        id
        status
        completedAt
      }
    }
  }
`;

// Mutation to update found string status
export const UPDATE_FOUND_STRING_STATUS_MUTATION = gql`
  mutation UpdateFoundStringStatus($foundStringId: String!, $status: FoundStringStatusEnum!) {
    updateFoundStringStatus(foundStringId: $foundStringId, status: $status) {
      success
      message
      foundString {
        id
        filePath
        lineNumber
        originalText
        suggestedKey
        context
        confidence
        status
        keyId
        matchedKeyId
        matchedKeyName
        fileType
        fileLanguage
        fileFramework
        createdAt
      }
    }
  }
`;

// Mutation to replace existing key with found string
export const REPLACE_FOUND_STRING_MUTATION = gql`
  mutation ReplaceFoundString($foundStringId: String!) {
    replaceFoundString(foundStringId: $foundStringId) {
      success
      message
      foundString {
        id
        filePath
        lineNumber
        originalText
        suggestedKey
        context
        confidence
        status
        keyId
        matchedKeyId
        matchedKeyName
        fileType
        fileLanguage
        fileFramework
        createdAt
      }
    }
  }
`;

// Mutation to convert approved strings to keys
export const CONVERT_FOUND_STRINGS_TO_KEYS_MUTATION = gql`
  mutation ConvertFoundStringsToKeys($scanSessionId: String!) {
    convertFoundStringsToKeys(scanSessionId: $scanSessionId) {
      success
      message
      keysCreated
    }
  }
`;

// Mutation to create a pull request with key replacements
export const CREATE_LOCALIZATION_PR_MUTATION = gql`
  mutation CreateLocalizationPR($scanSessionId: String!, $translationFunction: String) {
    createLocalizationPr(scanSessionId: $scanSessionId, translationFunction: $translationFunction) {
      success
      message
      prUrl
      prNumber
      branchName
      filesModified
    }
  }
`;

// TypeScript types
export const ScanStatus = {
  PENDING: 'PENDING',
  SCANNING: 'SCANNING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  CANCELLED: 'CANCELLED',
} as const;
export type ScanStatus = (typeof ScanStatus)[keyof typeof ScanStatus];

export const AIProvider = {
  OPENAI: 'OPENAI',
  ANTHROPIC: 'ANTHROPIC',
} as const;
export type AIProvider = (typeof AIProvider)[keyof typeof AIProvider];

export const FoundStringStatus = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  SKIPPED: 'SKIPPED',
  CONVERTED: 'CONVERTED',
  MATCHED: 'MATCHED',
} as const;
export type FoundStringStatus = (typeof FoundStringStatus)[keyof typeof FoundStringStatus];

export interface FoundString {
  id: string;
  filePath: string;
  lineNumber: number | null;
  originalText: string;
  suggestedKey: string;
  context: string | null;
  confidence: number;
  status: FoundStringStatus;
  keyId: string | null;
  matchedKeyId: string | null;
  matchedKeyName: string | null;
  fileType: string | null;
  fileLanguage: string | null;
  fileFramework: string | null;
  createdAt: string;
}

export const KeyNamingStyle = {
  UPPERCASE: 'UPPERCASE',
  snake_case: 'snake_case',
  camelCase: 'camelCase',
} as const;
export type KeyNamingStyle = (typeof KeyNamingStyle)[keyof typeof KeyNamingStyle];

export const KeyNamingDelimiter = {
  UNDERSCORE: '_',
  DOT: '.',
  COLON: ':',
  DOUBLE_COLON: '::',
} as const;
export type KeyNamingDelimiter = (typeof KeyNamingDelimiter)[keyof typeof KeyNamingDelimiter];

export interface ScanSession {
  id: string;
  status: ScanStatus;
  aiProvider: AIProvider;
  aiModel: string;
  scanPath: string | null;
  keyNamingStyle: string | null;
  keyNamingDelimiter: string | null;
  filesTotal: number;
  filesScanned: number;
  stringsFound: number;
  errorMessage: string | null;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
  foundStrings: FoundString[];
  // PR information
  prBranchName: string | null;
  prNumber: number | null;
  prUrl: string | null;
  prCreatedAt: string | null;
}

export interface RepositoryDirectory {
  path: string;
  name: string;
  isRecommended: boolean;
}

export interface TokenUsageStats {
  totalInputTokens: number;
  totalOutputTokens: number;
  totalTokens: number;
  operationsCount: number;
}

export interface StartScanResult {
  success: boolean;
  message: string;
  scanSession: ScanSession | null;
}

export interface UpdateFoundStringResult {
  success: boolean;
  message: string;
  foundString: FoundString | null;
}

export interface ConvertStringsResult {
  success: boolean;
  message: string;
  keysCreated: number;
}

export interface ReplaceFoundStringResult {
  success: boolean;
  message: string;
  foundString: FoundString | null;
}

export interface CreatePRResult {
  success: boolean;
  message: string;
  prUrl: string | null;
  prNumber: number | null;
  branchName: string | null;
  filesModified: number;
}

