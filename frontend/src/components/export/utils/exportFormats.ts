import type { TranslationKey } from "@/types/translationKey";

export type ExportFormat = "i18n" | "ios-strings";

export interface ExportOptions {
  format: ExportFormat;
  language: string;
  indent: number;
  sortKeys: boolean;
  /** If true, use source language value when target translation is empty */
  fillEmptyFromSource: boolean;
  /** Source/default language code */
  sourceLanguage?: string;
}

/**
 * Get translation value for a key, optionally falling back to source language
 * Always returns a string (empty string if no translation)
 */
function getTranslationValue(
  keyData: TranslationKey,
  language: string,
  fillEmptyFromSource: boolean,
  sourceLanguage?: string
): string {
  const translation = keyData.translations.find((t) => t.language === language);
  const translationValue = translation?.value || '';
  
  // If we have a value, return it
  if (translationValue) {
    return translationValue;
  }
  
  // If no value and fillEmptyFromSource is enabled, use source language
  if (fillEmptyFromSource && sourceLanguage && sourceLanguage !== language) {
    const sourceTranslation = keyData.translations.find((t) => t.language === sourceLanguage);
    if (sourceTranslation?.value) {
      return sourceTranslation.value;
    }
  }
  
  // Return empty string (key will still be exported)
  return '';
}

/**
 * Generate i18n format (simple key-value JSON)
 * @example { "welcome": "Welcome!", "hello": "Hello" }
 */
export function generateI18nFormat(
  keys: TranslationKey[],
  language: string,
  options: { indent: number; sortKeys: boolean; fillEmptyFromSource?: boolean; sourceLanguage?: string }
): string {
  const translations: Record<string, string> = {};

  keys.forEach((keyData) => {
    const value = getTranslationValue(
      keyData,
      language,
      options.fillEmptyFromSource ?? false,
      options.sourceLanguage
    );
    // Always include the key, even with empty value
    translations[keyData.key] = value;
  });

  // Sort keys alphabetically if requested
  const sortedTranslations = options.sortKeys
    ? Object.keys(translations)
        .sort()
        .reduce((acc, key) => {
          acc[key] = translations[key];
          return acc;
        }, {} as Record<string, string>)
    : translations;

  return JSON.stringify(sortedTranslations, null, options.indent);
}

/**
 * Escape value for iOS Strings format
 * Escapes: " -> \", \ -> \\, newline -> \n, tab -> \t
 */
function escapeIosStringsValue(value: string): string {
  return value
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\t/g, '\\t');
}

/**
 * Convert i18n variables {name} to iOS Strings format %@
 * Single variable: {name} -> %@
 * Multiple variables: {name} {count} -> %1$@ %2$@
 * Returns converted string and variable names for comment
 */
function convertVariablesToIosFormat(value: string): { converted: string; variables: string[] } {
  const variableRegex = /\{([^}]+)\}/g;
  const variables: string[] = [];
  let match;
  
  // Collect all variable names
  while ((match = variableRegex.exec(value)) !== null) {
    variables.push(match[1]);
  }
  
  if (variables.length === 0) {
    return { converted: value, variables: [] };
  }
  
  // Single variable - use simple %@
  if (variables.length === 1) {
    const converted = value.replace(variableRegex, '%@');
    return { converted, variables };
  }
  
  // Multiple variables - use positional %1$@, %2$@, etc.
  let position = 0;
  const converted = value.replace(variableRegex, () => {
    position++;
    return `%${position}$@`;
  });
  
  return { converted, variables };
}

/**
 * Generate iOS Strings format (.strings files)
 * @example "key.name" = "Translation value";
 * 
 * Format used by iOS/macOS apps for localization.
 * Each line contains: "key" = "value";
 * 
 * Variables are converted from i18n format to iOS format:
 * - {name} -> %@ (single variable)
 * - {name} {count} -> %1$@ %2$@ (multiple variables)
 */
export function generateIosStringsFormat(
  keys: TranslationKey[],
  language: string,
  options: { sortKeys: boolean; fillEmptyFromSource?: boolean; sourceLanguage?: string }
): string {
  const translations: Array<{ key: string; value: string; description?: string }> = [];

  keys.forEach((keyData) => {
    const value = getTranslationValue(
      keyData,
      language,
      options.fillEmptyFromSource ?? false,
      options.sourceLanguage
    );
    // Always include the key, even with empty value
    translations.push({
      key: keyData.key,
      value: value,
      description: keyData.description,
    });
  });

  // Sort keys alphabetically if requested
  if (options.sortKeys) {
    translations.sort((a, b) => a.key.localeCompare(b.key));
  }

  const lines: string[] = [];
  
  for (const item of translations) {
    // Convert i18n variables to iOS format
    const { converted, variables } = convertVariablesToIosFormat(item.value);
    
    // Add description as comment if available
    if (item.description) {
      lines.push(`/* ${item.description} */`);
    }
    
    // Add variable mapping comment if there are variables
    if (variables.length > 0) {
      const varMapping = variables.map((v, i) => 
        variables.length === 1 ? `%@ = {${v}}` : `%${i + 1}$@ = {${v}}`
      ).join(', ');
      lines.push(`/* Variables: ${varMapping} */`);
    }
    
    const escapedKey = escapeIosStringsValue(item.key);
    const escapedValue = escapeIosStringsValue(converted);
    lines.push(`"${escapedKey}" = "${escapedValue}";`);
    
    // Add empty line after each entry for readability
    lines.push('');
  }

  return lines.join('\n').trim();
}

/**
 * Generate export based on format
 */
export function generateExport(
  keys: TranslationKey[],
  options: ExportOptions
): string {
  switch (options.format) {
    case "i18n":
      return generateI18nFormat(keys, options.language, {
        indent: options.indent,
        sortKeys: options.sortKeys,
        fillEmptyFromSource: options.fillEmptyFromSource,
        sourceLanguage: options.sourceLanguage,
      });
    case "ios-strings":
      return generateIosStringsFormat(keys, options.language, {
        sortKeys: options.sortKeys,
        fillEmptyFromSource: options.fillEmptyFromSource,
        sourceLanguage: options.sourceLanguage,
      });
    default:
      throw new Error(`Unsupported format: ${options.format}`);
  }
}

/**
 * Get file extension for export format
 */
export function getFileExtension(format: ExportFormat): string {
  switch (format) {
    case "i18n":
      return "json";
    case "ios-strings":
      return "strings";
    default:
      return "txt";
  }
}

/**
 * Get MIME type for export format
 */
export function getMimeType(format: ExportFormat): string {
  switch (format) {
    case "i18n":
      return "application/json";
    case "ios-strings":
      return "text/plain;charset=utf-8";
    default:
      return "text/plain";
  }
}

/**
 * Get filename for export
 */
export function getExportFilename(
  projectName: string,
  language: string,
  format: ExportFormat
): string {
  const extension = getFileExtension(format);
  const sanitizedProjectName = projectName.toLowerCase().replace(/\s+/g, "-");
  return `${sanitizedProjectName}-${language}.${extension}`;
}

