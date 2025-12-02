import { useQuery } from '@apollo/client';
import { useMemo } from 'react';
import {
  GET_AVAILABLE_LANGUAGES,
  type GetAvailableLanguagesData,
  type AvailableLanguage,
  type PluralForm,
} from '@/graphql/projects';

/**
 * Language configuration with compiled RegExp patterns for file detection.
 */
export interface LanguageConfigWithPatterns {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  locale: string;
  direction: 'ltr' | 'rtl';
  pluralForms: PluralForm[];
  detectionPatterns: {
    endPatterns: RegExp[];
    middlePatterns: RegExp[];
    startPatterns: RegExp[];
    fullNames: RegExp[];
  };
}

/**
 * Simple language type for UI components (without detection patterns).
 */
export interface SimpleLanguage {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  locale: string;
  direction: 'ltr' | 'rtl';
  pluralForms: PluralForm[];
}

/**
 * Compile regex pattern strings to RegExp objects.
 * Patterns are case-insensitive by default.
 */
function compilePatterns(patterns: string[]): RegExp[] {
  return patterns.map((pattern) => {
    try {
      return new RegExp(pattern, 'i');
    } catch {
      // If pattern is invalid, return a regex that never matches
      console.warn(`Invalid regex pattern: ${pattern}`);
      return /^$/;
    }
  });
}

/**
 * Convert API language data to full config with compiled RegExp patterns.
 */
function toLanguageConfigWithPatterns(
  lang: AvailableLanguage
): LanguageConfigWithPatterns {
  return {
    code: lang.code,
    name: lang.name,
    nativeName: lang.nativeName,
    flag: lang.flag,
    locale: lang.locale,
    direction: lang.direction,
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
 * Convert API language data to simple language (without patterns).
 */
function toSimpleLanguage(lang: AvailableLanguage): SimpleLanguage {
  return {
    code: lang.code,
    name: lang.name,
    nativeName: lang.nativeName,
    flag: lang.flag,
    locale: lang.locale,
    direction: lang.direction,
    pluralForms: lang.pluralForms,
  };
}

interface UseAvailableLanguagesResult {
  /** All languages with compiled detection patterns */
  languages: LanguageConfigWithPatterns[];
  /** Simple language list for UI selectors */
  simpleLanguages: SimpleLanguage[];
  /** Get language by code */
  getLanguage: (code: string) => LanguageConfigWithPatterns | undefined;
  /** Get simple language by code */
  getSimpleLanguage: (code: string) => SimpleLanguage | undefined;
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: Error | undefined;
}

/**
 * Hook to get available languages from the backend (single source of truth).
 * 
 * - Fetches language data via GraphQL
 * - Caches results in Apollo cache
 * - Compiles regex patterns for file detection
 * - Provides both full configs and simple language lists
 * 
 * @example
 * ```tsx
 * const { languages, simpleLanguages, getLanguage } = useAvailableLanguages();
 * 
 * // Use simple list for dropdowns
 * <Select options={simpleLanguages.map(l => ({ value: l.code, label: l.name }))} />
 * 
 * // Use full config for file detection
 * const config = getLanguage('en');
 * if (config?.detectionPatterns.endPatterns.some(p => p.test(filename))) {
 *   // File matches English pattern
 * }
 * ```
 */
export function useAvailableLanguages(): UseAvailableLanguagesResult {
  const { data, loading, error } = useQuery<GetAvailableLanguagesData>(
    GET_AVAILABLE_LANGUAGES,
    {
      // Cache languages for the session - they rarely change
      fetchPolicy: 'cache-first',
    }
  );

  // Memoize compiled languages to avoid recompiling on every render
  const languages = useMemo(() => {
    if (!data?.availableLanguages) {
      return [];
    }
    return data.availableLanguages.map(toLanguageConfigWithPatterns);
  }, [data?.availableLanguages]);

  // Memoize simple languages for UI components
  const simpleLanguages = useMemo(() => {
    if (!data?.availableLanguages) {
      return [];
    }
    return data.availableLanguages.map(toSimpleLanguage);
  }, [data?.availableLanguages]);

  // Memoize lookup maps for O(1) access
  const languageMap = useMemo(() => {
    return new Map(languages.map((l) => [l.code, l]));
  }, [languages]);

  const simpleLanguageMap = useMemo(() => {
    return new Map(simpleLanguages.map((l) => [l.code, l]));
  }, [simpleLanguages]);

  const getLanguage = useMemo(() => {
    return (code: string) => languageMap.get(code);
  }, [languageMap]);

  const getSimpleLanguage = useMemo(() => {
    return (code: string) => simpleLanguageMap.get(code);
  }, [simpleLanguageMap]);

  return {
    languages,
    simpleLanguages,
    getLanguage,
    getSimpleLanguage,
    loading,
    error: error as Error | undefined,
  };
}

/**
 * Detect language from filename using detection patterns.
 * 
 * @param filename - The filename to analyze
 * @param languages - Language configs with compiled patterns
 * @returns Detected language code or null
 */
export function detectLanguageFromFilename(
  filename: string,
  languages: LanguageConfigWithPatterns[]
): string | null {
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

