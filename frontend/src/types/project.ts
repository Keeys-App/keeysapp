/**
 * TypeScript types for project module.
 * Re-exports types from GraphQL operations for convenience.
 * 
 * NOTE: Language configurations are now fetched from the backend API.
 * Use `useLanguagesStore()` hook or `getLanguageConfigs()` function from @/stores
 * to access language data.
 */

export type {
  User,
  ProjectMember,
  Project,
  CreateProjectInput,
  UpdateProjectInput,
  AddProjectMemberInput,
  GetProjectsData,
  GetProjectData,
  CreateProjectData,
  UpdateProjectData,
  DeleteProjectData,
  AddProjectMemberData,
  LanguageConfig as ProjectLanguageConfig,
  PluralForm,
  AvailableLanguage,
  DetectionPatterns,
  GetAvailableLanguagesData,
} from '../graphql/projects';

/**
 * Project status constants.
 */
export const ProjectStatus = {
  ACTIVE: 'active',
  ARCHIVED: 'archived',
  DRAFT: 'draft',
} as const;

export type ProjectStatusType = typeof ProjectStatus[keyof typeof ProjectStatus];

/**
 * Project member role constants.
 */
export const ProjectMemberRole = {
  ADMIN: 'admin',
  EDITOR: 'editor',
  VIEWER: 'viewer',
} as const;

export type ProjectMemberRoleType = typeof ProjectMemberRole[keyof typeof ProjectMemberRole];

/**
 * Project color with name.
 */
export interface ProjectColor {
  hex: string;
  name: string;
}

/**
 * Available project colors with their names.
 */
export const PROJECT_COLORS: ProjectColor[] = [
  { hex: '#6366f1', name: 'Indigo' },
  { hex: '#8b5cf6', name: 'Violet' },
  { hex: '#ec4899', name: 'Pink' },
  { hex: '#f43f5e', name: 'Rose' },
  { hex: '#f97316', name: 'Orange' },
  { hex: '#eab308', name: 'Yellow' },
  { hex: '#22c55e', name: 'Green' },
  { hex: '#14b8a6', name: 'Teal' },
  { hex: '#06b6d4', name: 'Cyan' },
  { hex: '#3b82f6', name: 'Blue' },
];

/**
 * Default project colors (hex values only for backward compatibility).
 */
export const DEFAULT_PROJECT_COLORS = PROJECT_COLORS.map(c => c.hex);

/**
 * Get color name by hex value.
 */
export const getColorName = (hex?: string): string | undefined => {
  if (!hex) {
    return undefined;
  }
  return PROJECT_COLORS.find(c => c.hex.toLowerCase() === hex.toLowerCase())?.name;
};

/**
 * Re-export language types from stores for convenience.
 * 
 * Usage:
 * ```typescript
 * import { useLanguagesStore, getLanguageConfigs, getCommonLanguages } from '@/stores';
 * 
 * // In React components - use the hook
 * const { languageConfigs, commonLanguages, getLanguage } = useLanguagesStore();
 * 
 * // In non-React code - use the sync functions
 * const languages = getLanguageConfigs();
 * const simpleLanguages = getCommonLanguages();
 * ```
 */
export type {
  LanguageConfig,
  Language,
  DetectionPatterns as CompiledDetectionPatterns,
} from '@/stores/languagesStore';

/**
 * Extended language type with locale information for UI components.
 */
export interface LanguageWithLocale {
  code: string;
  name: string;
  flag: string;
  direction: 'ltr' | 'rtl';
  pluralForms: ('zero' | 'one' | 'two' | 'few' | 'many' | 'other')[];
  locale: string;
  default?: boolean;
}
