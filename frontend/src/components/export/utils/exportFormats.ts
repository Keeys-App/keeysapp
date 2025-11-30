import type { TranslationKey } from "@/types/translationKey";

export type ExportFormat = "i18n" | "ios-strings";

export interface ExportOptions {
  format: ExportFormat;
  language: string;
  indent: number;
  sortKeys: boolean;
}

/**
 * Generate i18n format (simple key-value JSON)
 * @example { "welcome": "Welcome!", "hello": "Hello" }
 */
export function generateI18nFormat(
  keys: TranslationKey[],
  language: string,
  options: { indent: number; sortKeys: boolean }
): string {
  const translations: Record<string, string> = {};

  keys.forEach((keyData) => {
    const translation = keyData.translations.find((t) => t.language === language);
    if (translation) {
      translations[keyData.key] = translation.value;
    }
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
 * Generate iOS Strings format (.strings files)
 * @example "key.name" = "Translation value";
 * 
 * Format used by iOS/macOS apps for localization.
 * Each line contains: "key" = "value";
 */
export function generateIosStringsFormat(
  keys: TranslationKey[],
  language: string,
  options: { sortKeys: boolean }
): string {
  const translations: Array<{ key: string; value: string; description?: string }> = [];

  keys.forEach((keyData) => {
    const translation = keyData.translations.find((t) => t.language === language);
    if (translation) {
      translations.push({
        key: keyData.key,
        value: translation.value,
        description: keyData.description,
      });
    }
  });

  // Sort keys alphabetically if requested
  if (options.sortKeys) {
    translations.sort((a, b) => a.key.localeCompare(b.key));
  }

  const lines: string[] = [];
  
  for (const item of translations) {
    // Add description as comment if available
    if (item.description) {
      lines.push(`/* ${item.description} */`);
    }
    
    const escapedKey = escapeIosStringsValue(item.key);
    const escapedValue = escapeIosStringsValue(item.value);
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
      });
    case "ios-strings":
      return generateIosStringsFormat(keys, options.language, {
        sortKeys: options.sortKeys,
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

