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
      filesTotal
      filesScanned
      stringsFound
      errorMessage
      createdAt
      startedAt
      completedAt
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
      filesTotal
      filesScanned
      stringsFound
      errorMessage
      createdAt
      startedAt
      completedAt
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

// Mutation to start a repository scan
// Note: AI settings are taken from Team configuration on backend
export const START_REPOSITORY_SCAN_MUTATION = gql`
  mutation StartRepositoryScan($projectId: String!) {
    startRepositoryScan(projectId: $projectId) {
      success
      message
      scanSession {
        id
        status
        aiProvider
        aiModel
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
  createdAt: string;
}

export interface ScanSession {
  id: string;
  status: ScanStatus;
  aiProvider: AIProvider;
  aiModel: string;
  filesTotal: number;
  filesScanned: number;
  stringsFound: number;
  errorMessage: string | null;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
  foundStrings: FoundString[];
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

