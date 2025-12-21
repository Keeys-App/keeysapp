export interface ActivityUser {
  id: string;
  email: string;
  username: string;
}

export interface ActivityProject {
  id: string;
  name: string;
  color?: string;
}

export interface BatchImportExtraData {
  created_keys: number;
  updated_keys: number;
  total_processed: number;
  error_count: number;
  translations_count?: number;
}

export interface ScanExtraData {
  repository?: string;
  files_scanned?: number;
  strings_found?: number;
  error?: string;
}

export type ExtraData = BatchImportExtraData | ScanExtraData;

export interface ActivityLog {
  id: number;
  projectId: number | null;
  keyId: number | null;
  userId: number | null;
  affectedUserId: number | null;
  user: ActivityUser | null;
  affectedUser: ActivityUser | null;
  project?: ActivityProject | null;
  action: string;
  fieldName: string | null;
  language: string | null;
  oldValue: string | null;
  newValue: string | null;
  extraData: ExtraData | null;
  createdAt: string;
}

export type ActionType =
  // Team lifecycle
  | 'TEAM_CREATE'
  | 'TEAM_UPDATE_NAME'
  | 'TEAM_UPDATE_DESCRIPTION'
  | 'TEAM_DELETE'
  // Project actions
  | 'PROJECT_CREATE'
  | 'PROJECT_UPDATE_NAME'
  | 'PROJECT_UPDATE_DESCRIPTION'
  | 'PROJECT_UPDATE_LANGUAGES'
  | 'PROJECT_UPDATE_DEFAULT_LANGUAGE'
  | 'PROJECT_UPDATE_COLOR'
  | 'PROJECT_UPDATE_STATUS'
  | 'PROJECT_DELETE'
  | 'PROJECT_EXPORT'
  | 'PROJECT_IMPORT'
  // Team management
  | 'MEMBER_ADD'
  | 'MEMBER_REMOVE'
  | 'MEMBER_ROLE_CHANGE'
  | 'TEAM_INVITE'
  // Key actions
  | 'KEY_CREATE'
  | 'KEY_UPDATE'
  | 'KEY_UPDATE_DESCRIPTION'
  | 'KEY_DELETE'
  // Translation actions
  | 'TRANSLATION_UPDATE'
  | 'TRANSLATION_AI_UPDATE'
  | 'TRANSLATION_DELETE'
  | 'TRANSLATION_IMPORT'
  // Batch import action
  | 'KEYS_BATCH_IMPORT'
  // Review actions
  | 'REVIEW_APPROVE'
  | 'REVIEW_REJECT'
  | 'REVIEW_DELETE'
  // Scan actions
  | 'SCAN_START'
  | 'SCAN_COMPLETE'
  | 'SCAN_FAILED'
  | 'SCAN_CANCELLED';

