/**
 * TypeScript types for project module.
 * Re-exports types from GraphQL operations for convenience.
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
 * Language configuration with all metadata, plural forms, and detection patterns.
 */
export type LanguageConfig = {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  locale: string;
  direction: 'ltr' | 'rtl';
  /**
   * Plural forms according to CLDR standard.
   * - zero: Used for zero quantity (e.g., Arabic)
   * - one: Singular form (e.g., 1 item)
   * - two: Dual form (e.g., Arabic for exactly 2)
   * - few: Paucal form (e.g., Russian 2-4)
   * - many: Large quantity form (e.g., Russian 5-20)
   * - other: General/default form (always present)
   */
  pluralForms: ('zero' | 'one' | 'two' | 'few' | 'many' | 'other')[];
  detectionPatterns: {
    // Filename patterns for auto-detection
    endPatterns: RegExp[];      // e.g., app-en.json
    middlePatterns: RegExp[];   // e.g., en-US.json
    startPatterns: RegExp[];    // e.g., en.translations.json
    fullNames: RegExp[];        // e.g., english.json
  };
};

export type Language = Pick<LanguageConfig, 'code' | 'name' | 'flag' | 'direction' | 'pluralForms'> & {
  default?: boolean;
};

/**
 * Extended language type with locale information for UI components.
 */
export interface LanguageWithLocale extends Language {
  locale: string;
}

/**
 * Complete language configurations with detection patterns.
 */
export const LANGUAGE_CONFIGS: LanguageConfig[] = [
  // Germanic languages - one/other
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: '🇬🇧',
    locale: 'en-US',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]en\.(json|js|ts)$/i, /[-_.]en[-_.]/],
      middlePatterns: [/[-_.]en[-_.]/, /en[-_]US/i, /en[-_]GB/i],
      startPatterns: [/^en[-_.]/],
      fullNames: [/english/i],
    },
  },
  {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    flag: '🇩🇪',
    locale: 'de-DE',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]de\.(json|js|ts)$/i, /[-_.]de[-_.]/],
      middlePatterns: [/[-_.]de[-_.]/, /de[-_]DE/i],
      startPatterns: [/^de[-_.]/],
      fullNames: [/german/i, /deutsch/i],
    },
  },
  {
    code: 'nl',
    name: 'Dutch',
    nativeName: 'Nederlands',
    flag: '🇳🇱',
    locale: 'nl-NL',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]nl\.(json|js|ts)$/i, /[-_.]nl[-_.]/],
      middlePatterns: [/[-_.]nl[-_.]/, /nl[-_]NL/i],
      startPatterns: [/^nl[-_.]/],
      fullNames: [/dutch/i, /nederlands/i],
    },
  },
  {
    code: 'sv',
    name: 'Swedish',
    nativeName: 'Svenska',
    flag: '🇸🇪',
    locale: 'sv-SE',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]sv\.(json|js|ts)$/i, /[-_.]sv[-_.]/],
      middlePatterns: [/[-_.]sv[-_.]/, /sv[-_]SE/i],
      startPatterns: [/^sv[-_.]/],
      fullNames: [/swedish/i, /svenska/i],
    },
  },
  {
    code: 'no',
    name: 'Norwegian',
    nativeName: 'Norsk',
    flag: '🇳🇴',
    locale: 'no-NO',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]no\.(json|js|ts)$/i, /[-_.]no[-_.]/],
      middlePatterns: [/[-_.]no[-_.]/, /no[-_]NO/i, /nb[-_]NO/i],
      startPatterns: [/^no[-_.]/, /^nb[-_.]/],
      fullNames: [/norwegian/i, /norsk/i],
    },
  },
  {
    code: 'da',
    name: 'Danish',
    nativeName: 'Dansk',
    flag: '🇩🇰',
    locale: 'da-DK',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]da\.(json|js|ts)$/i, /[-_.]da[-_.]/],
      middlePatterns: [/[-_.]da[-_.]/, /da[-_]DK/i],
      startPatterns: [/^da[-_.]/],
      fullNames: [/danish/i, /dansk/i],
    },
  },
  // Romance languages - one/many/other
  {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    flag: '🇪🇸',
    locale: 'es-ES',
    direction: 'ltr',
    pluralForms: ['one', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]es\.(json|js|ts)$/i, /[-_.]es[-_.]/],
      middlePatterns: [/[-_.]es[-_.]/, /es[-_]ES/i],
      startPatterns: [/^es[-_.]/],
      fullNames: [/spanish/i, /español/i],
    },
  },
  {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    flag: '🇫🇷',
    locale: 'fr-FR',
    direction: 'ltr',
    pluralForms: ['one', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]fr\.(json|js|ts)$/i, /[-_.]fr[-_.]/],
      middlePatterns: [/[-_.]fr[-_.]/, /fr[-_]FR/i],
      startPatterns: [/^fr[-_.]/],
      fullNames: [/french/i, /français/i],
    },
  },
  {
    code: 'it',
    name: 'Italian',
    nativeName: 'Italiano',
    flag: '🇮🇹',
    locale: 'it-IT',
    direction: 'ltr',
    pluralForms: ['one', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]it\.(json|js|ts)$/i, /[-_.]it[-_.]/],
      middlePatterns: [/[-_.]it[-_.]/, /it[-_]IT/i],
      startPatterns: [/^it[-_.]/],
      fullNames: [/italian/i, /italiano/i],
    },
  },
  {
    code: 'pt',
    name: 'Portuguese',
    nativeName: 'Português',
    flag: '🇵🇹',
    locale: 'pt-PT',
    direction: 'ltr',
    pluralForms: ['one', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]pt\.(json|js|ts)$/i, /[-_.]pt[-_.]/],
      middlePatterns: [/[-_.]pt[-_.]/, /pt[-_]BR/i, /pt[-_]PT/i],
      startPatterns: [/^pt[-_.]/],
      fullNames: [/portuguese/i, /português/i],
    },
  },
  {
    code: 'ro',
    name: 'Romanian',
    nativeName: 'Română',
    flag: '🇷🇴',
    locale: 'ro-RO',
    direction: 'ltr',
    pluralForms: ['one', 'few', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]ro\.(json|js|ts)$/i, /[-_.]ro[-_.]/],
      middlePatterns: [/[-_.]ro[-_.]/, /ro[-_]RO/i],
      startPatterns: [/^ro[-_.]/],
      fullNames: [/romanian/i, /română/i],
    },
  },
  // Slavic languages - one/few/many/other
  {
    code: 'ru',
    name: 'Russian',
    nativeName: 'Русский',
    flag: '🇷🇺',
    locale: 'ru-RU',
    direction: 'ltr',
    pluralForms: ['one', 'few', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]ru\.(json|js|ts)$/i, /[-_.]ru[-_.]/],
      middlePatterns: [/[-_.]ru[-_.]/, /ru[-_]RU/i],
      startPatterns: [/^ru[-_.]/],
      fullNames: [/russian/i, /русский/i],
    },
  },
  {
    code: 'uk',
    name: 'Ukrainian',
    nativeName: 'Українська',
    flag: '🇺🇦',
    locale: 'uk-UA',
    direction: 'ltr',
    pluralForms: ['one', 'few', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]uk\.(json|js|ts)$/i, /[-_.]uk[-_.]/],
      middlePatterns: [/[-_.]uk[-_.]/, /uk[-_]UA/i],
      startPatterns: [/^uk[-_.]/],
      fullNames: [/ukrainian/i, /українська/i],
    },
  },
  {
    code: 'pl',
    name: 'Polish',
    nativeName: 'Polski',
    flag: '🇵🇱',
    locale: 'pl-PL',
    direction: 'ltr',
    pluralForms: ['one', 'few', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]pl\.(json|js|ts)$/i, /[-_.]pl[-_.]/],
      middlePatterns: [/[-_.]pl[-_.]/, /pl[-_]PL/i],
      startPatterns: [/^pl[-_.]/],
      fullNames: [/polish/i, /polski/i],
    },
  },
  {
    code: 'cs',
    name: 'Czech',
    nativeName: 'Čeština',
    flag: '🇨🇿',
    locale: 'cs-CZ',
    direction: 'ltr',
    pluralForms: ['one', 'few', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]cs\.(json|js|ts)$/i, /[-_.]cs[-_.]/],
      middlePatterns: [/[-_.]cs[-_.]/, /cs[-_]CZ/i],
      startPatterns: [/^cs[-_.]/],
      fullNames: [/czech/i, /čeština/i],
    },
  },
  // East Asian languages - only "other" (no plural forms)
  {
    code: 'zh',
    name: 'Chinese',
    nativeName: '中文',
    flag: '🇨🇳',
    locale: 'zh-CN',
    direction: 'ltr',
    pluralForms: ['other'],
    detectionPatterns: {
      endPatterns: [/[-_.]zh\.(json|js|ts)$/i, /[-_.]zh[-_.]/],
      middlePatterns: [/[-_.]zh[-_.]/, /zh[-_]CN/i, /zh[-_]TW/i],
      startPatterns: [/^zh[-_.]/],
      fullNames: [/chinese/i, /中文/],
    },
  },
  {
    code: 'ja',
    name: 'Japanese',
    nativeName: '日本語',
    flag: '🇯🇵',
    locale: 'ja-JP',
    direction: 'ltr',
    pluralForms: ['other'],
    detectionPatterns: {
      endPatterns: [/[-_.]ja\.(json|js|ts)$/i, /[-_.]ja[-_.]/],
      middlePatterns: [/[-_.]ja[-_.]/, /ja[-_]JP/i],
      startPatterns: [/^ja[-_.]/],
      fullNames: [/japanese/i, /日本語/],
    },
  },
  {
    code: 'ko',
    name: 'Korean',
    nativeName: '한국어',
    flag: '🇰🇷',
    locale: 'ko-KR',
    direction: 'ltr',
    pluralForms: ['other'],
    detectionPatterns: {
      endPatterns: [/[-_.]ko\.(json|js|ts)$/i, /[-_.]ko[-_.]/],
      middlePatterns: [/[-_.]ko[-_.]/, /ko[-_]KR/i],
      startPatterns: [/^ko[-_.]/],
      fullNames: [/korean/i, /한국어/],
    },
  },
  {
    code: 'vi',
    name: 'Vietnamese',
    nativeName: 'Tiếng Việt',
    flag: '🇻🇳',
    locale: 'vi-VN',
    direction: 'ltr',
    pluralForms: ['other'],
    detectionPatterns: {
      endPatterns: [/[-_.]vi\.(json|js|ts)$/i, /[-_.]vi[-_.]/],
      middlePatterns: [/[-_.]vi[-_.]/, /vi[-_]VN/i],
      startPatterns: [/^vi[-_.]/],
      fullNames: [/vietnamese/i, /tiếng việt/i],
    },
  },
  {
    code: 'th',
    name: 'Thai',
    nativeName: 'ไทย',
    flag: '🇹🇭',
    locale: 'th-TH',
    direction: 'ltr',
    pluralForms: ['other'],
    detectionPatterns: {
      endPatterns: [/[-_.]th\.(json|js|ts)$/i, /[-_.]th[-_.]/],
      middlePatterns: [/[-_.]th[-_.]/, /th[-_]TH/i],
      startPatterns: [/^th[-_.]/],
      fullNames: [/thai/i, /ไทย/],
    },
  },
  // Arabic - most complex: zero/one/two/few/many/other
  {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    flag: '🇸🇦',
    locale: 'ar-SA',
    direction: 'rtl',
    pluralForms: ['zero', 'one', 'two', 'few', 'many', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]ar\.(json|js|ts)$/i, /[-_.]ar[-_.]/],
      middlePatterns: [/[-_.]ar[-_.]/, /ar[-_]SA/i, /ar[-_]EG/i],
      startPatterns: [/^ar[-_.]/],
      fullNames: [/arabic/i, /العربية/],
    },
  },
  // Other languages - one/other
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    flag: '🇮🇳',
    locale: 'hi-IN',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]hi\.(json|js|ts)$/i, /[-_.]hi[-_.]/],
      middlePatterns: [/[-_.]hi[-_.]/, /hi[-_]IN/i],
      startPatterns: [/^hi[-_.]/],
      fullNames: [/hindi/i, /हिन्दी/],
    },
  },
  {
    code: 'tr',
    name: 'Turkish',
    nativeName: 'Türkçe',
    flag: '🇹🇷',
    locale: 'tr-TR',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]tr\.(json|js|ts)$/i, /[-_.]tr[-_.]/],
      middlePatterns: [/[-_.]tr[-_.]/, /tr[-_]TR/i],
      startPatterns: [/^tr[-_.]/],
      fullNames: [/turkish/i, /türkçe/i],
    },
  },
  {
    code: 'fi',
    name: 'Finnish',
    nativeName: 'Suomi',
    flag: '🇫🇮',
    locale: 'fi-FI',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]fi\.(json|js|ts)$/i, /[-_.]fi[-_.]/],
      middlePatterns: [/[-_.]fi[-_.]/, /fi[-_]FI/i],
      startPatterns: [/^fi[-_.]/],
      fullNames: [/finnish/i, /suomi/i],
    },
  },
  {
    code: 'hu',
    name: 'Hungarian',
    nativeName: 'Magyar',
    flag: '🇭🇺',
    locale: 'hu-HU',
    direction: 'ltr',
    pluralForms: ['one', 'other'],
    detectionPatterns: {
      endPatterns: [/[-_.]hu\.(json|js|ts)$/i, /[-_.]hu[-_.]/],
      middlePatterns: [/[-_.]hu[-_.]/, /hu[-_]HU/i],
      startPatterns: [/^hu[-_.]/],
      fullNames: [/hungarian/i, /magyar/i],
    },
  },
];

/**
 * Simple language list for UI selectors (backward compatibility).
 */
export const COMMON_LANGUAGES: Language[] = LANGUAGE_CONFIGS.map(
  ({ code, name, flag, direction, pluralForms }) => ({ code, name, flag, direction, pluralForms })
);

