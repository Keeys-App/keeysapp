/**
 * Application route paths constants.
 * Use these constants instead of hardcoded strings for type safety and easier refactoring.
 */

export const PATHS = {
  AUTH: '/auth',
  HOME: '/',
  DASHBOARD: '/',
  TEAMS: '/teams',
  TEAM: '/team/:id',
  TEAM_CREATE: '/team/create',
  TEAM_EDIT: '/team/:id/edit',
  PROJECT: '/project/:id',
  PROJECT_KEYS: '/project/:id/keys',
  PROJECT_CREATE: '/project/create',
  PROJECT_EDIT: '/project/:id/edit',
  EXPORT: '/project/:id/export',
  IMPORT: '/project/:id/import',
} as const;

