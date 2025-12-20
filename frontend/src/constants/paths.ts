/**
 * Application route paths constants.
 * Use these constants instead of hardcoded strings for type safety and easier refactoring.
 */

export const PATHS = {
  AUTH: '/auth',
  HOME: '/',
  DASHBOARD: '/',
  ONBOARDING: '/onboarding',
  INVITE: '/invite/:code',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password/:token',
  PROFILE: '/profile',
  TEAMS: '/teams',
  TEAM: '/team/:id',
  TEAM_LOGS: '/team/:id/logs',
  TEAM_USAGE: '/team/:id/usage',
  TEAM_CREATE: '/team/create',
  TEAM_EDIT: '/team/:id/edit',
  PROJECT: '/project/:id',
  PROJECT_KEYS: '/project/:id/keys',
  PROJECT_CREATE: '/project/create',
  PROJECT_EDIT: '/project/:id/edit',
  PROJECT_REPOSITORY: '/project/:id/repository',
  PROJECT_SCANNER: '/project/:id/scanner',
  EXPORT: '/project/:id/export',
  IMPORT: '/project/:id/import',
  // GitHub integration
  GITHUB_CALLBACK: '/github/callback',
} as const;

