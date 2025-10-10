import type { TranslationKey } from "@/types/translationKey";

export type ExportFormat = "i18n";

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
    default:
      return "txt";
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

