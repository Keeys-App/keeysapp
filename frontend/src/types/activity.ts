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
  // Review actions
  | 'REVIEW_APPROVE'
  | 'REVIEW_REJECT'
  | 'REVIEW_DELETE';

