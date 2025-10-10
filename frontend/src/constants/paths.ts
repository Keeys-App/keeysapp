/**
 * Application route paths constants.
 * Use these constants instead of hardcoded strings for type safety and easier refactoring.
 */

export const PATHS = {
  AUTH: '/auth',
  HOME: '/',
  DASHBOARD: '/',
  PROJECT: '/project/:id/keys',
  PROJECT_CREATE: '/project/create',
  PROJECT_EDIT: '/project/:id/edit',
  EXPORT: '/project/:id/export',
  IMPORT: '/project/:id/import',
} as const;

