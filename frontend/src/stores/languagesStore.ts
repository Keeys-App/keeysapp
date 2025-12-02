/**
 * Languages store - single source of truth for language configuration.
 * 
 * This store fetches language data from the backend API and provides
 * synchronous access to language configuration across the application.
 */

import { create } from 'zustand';
import type { PluralForm } from '@/graphql/projects';

/**
 * Detection patterns with compiled RegExp for file language detection.
 */
export interface DetectionPatterns {
  endPatterns: RegExp[];
  middlePatterns: RegExp[];
  startPatterns: RegExp[];
  fullNames: RegExp[];
}

/**
 * Full language configuration with compiled detection patterns.
 */
export interface LanguageConfig {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  locale: string;
  direction: 'ltr' | 'rtl';
  pluralForms: PluralForm[];
  detectionPatterns: DetectionPatterns;
}

/**
 * Simple language type for UI components (backward compatibility).
 */
export interface Language {
  code: string;
  name: string;
  flag: string;
  direction: 'ltr' | 'rtl';
  pluralForms: PluralForm[];
  default?: boolean;
}

interface LanguagesState {
  /** Full language configurations with detection patterns */
  languageConfigs: LanguageConfig[];
  /** Simple language list for UI selectors */
  commonLanguages: Language[];
  /** Whether languages have been loaded */
  isLoaded: boolean;
  /** Whether languages are currently loading */
  isLoading: boolean;
  /** Error if loading failed */
  error: string | null;
  /** Set languages from API response */
  setLanguages: (languages: LanguageConfig[]) => void;
  /** Set loading state */
  setLoading: (loading: boolean) => void;
  /** Set error state */
  setError: (error: string | null) => void;
  /** Get language config by code */
  getLanguageConfig: (code: string) => LanguageConfig | undefined;
  /** Get simple language by code */
  getLanguage: (code: string) => Language | undefined;
}

/**
 * Compile regex pattern strings to RegExp objects.
 */
function compilePatterns(patterns: string[]): RegExp[] {
  return patterns.map((pattern) => {
    try {
      return new RegExp(pattern, 'i');
    } catch {
      console.warn(`Invalid regex pattern: ${pattern}`);
      return /^$/;
    }
  });
}

/**
 * Convert API language data to full config with compiled patterns.
 */
export function toLanguageConfig(lang: {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  locale: string;
  direction: string;
  pluralForms: PluralForm[];
  detectionPatterns: {
    endPatterns: string[];
    middlePatterns: string[];
    startPatterns: string[];
    fullNames: string[];
  };
}): LanguageConfig {
  return {
    code: lang.code,
    name: lang.name,
    nativeName: lang.nativeName,
    flag: lang.flag,
    locale: lang.locale,
    direction: lang.direction as 'ltr' | 'rtl',
    pluralForms: lang.pluralForms,
    detectionPatterns: {
      endPatterns: compilePatterns(lang.detectionPatterns.endPatterns),
      middlePatterns: compilePatterns(lang.detectionPatterns.middlePatterns),
      startPatterns: compilePatterns(lang.detectionPatterns.startPatterns),
      fullNames: compilePatterns(lang.detectionPatterns.fullNames),
    },
  };
}

/**
 * Convert language config to simple language for UI components.
 */
function toSimpleLanguage(lang: LanguageConfig): Language {
  return {
    code: lang.code,
    name: lang.name,
    flag: lang.flag,
    direction: lang.direction,
    pluralForms: lang.pluralForms,
  };
}

export const useLanguagesStore = create<LanguagesState>((set, get) => ({
  languageConfigs: [],
  commonLanguages: [],
  isLoaded: false,
  isLoading: false,
  error: null,

  setLanguages: (languages) => {
    set({
      languageConfigs: languages,
      commonLanguages: languages.map(toSimpleLanguage),
      isLoaded: true,
      isLoading: false,
      error: null,
    });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error, isLoading: false });
  },

  getLanguageConfig: (code) => {
    return get().languageConfigs.find((l) => l.code === code);
  },

  getLanguage: (code) => {
    return get().commonLanguages.find((l) => l.code === code);
  },
}));

// Non-hook accessors for utilities (synchronous access)

/**
 * Get all language configurations (for use in non-React code).
 */
export function getLanguageConfigs(): LanguageConfig[] {
  return useLanguagesStore.getState().languageConfigs;
}

/**
 * Get all simple languages (for use in non-React code).
 */
export function getCommonLanguages(): Language[] {
  return useLanguagesStore.getState().commonLanguages;
}

/**
 * Get language config by code (for use in non-React code).
 */
export function getLanguageConfigByCode(code: string): LanguageConfig | undefined {
  return useLanguagesStore.getState().languageConfigs.find((l) => l.code === code);
}

/**
 * Detect language from filename using detection patterns.
 */
export function detectLanguageFromFilename(filename: string): string | null {
  const languages = useLanguagesStore.getState().languageConfigs;
  
  for (const lang of languages) {
    const { detectionPatterns } = lang;
    
    // Check patterns in order of specificity
    if (detectionPatterns.fullNames.some((p) => p.test(filename))) {
      return lang.code;
    }
    if (detectionPatterns.endPatterns.some((p) => p.test(filename))) {
      return lang.code;
    }
    if (detectionPatterns.middlePatterns.some((p) => p.test(filename))) {
      return lang.code;
    }
    if (detectionPatterns.startPatterns.some((p) => p.test(filename))) {
      return lang.code;
    }
  }
  
  return null;
}

