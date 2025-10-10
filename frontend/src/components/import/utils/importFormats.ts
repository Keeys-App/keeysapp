export type ImportFormat = "i18n";

export interface ParsedTranslation {
  key: string;
  value: string;
}

export interface ParseResult {
  success: boolean;
  translations: ParsedTranslation[];
  error?: string;
}

/**
 * Parse i18n format (simple key-value JSON)
 * @example { "welcome": "Welcome!", "hello": "Hello" }
 */
export function parseI18nFormat(content: string): ParseResult {
  try {
    const data = JSON.parse(content);

    if (typeof data !== "object" || data === null || Array.isArray(data)) {
      return {
        success: false,
        translations: [],
        error: "Invalid format: Expected a JSON object with key-value pairs",
      };
    }

    const translations: ParsedTranslation[] = [];

    for (const [key, value] of Object.entries(data)) {
      if (typeof value !== "string") {
        return {
          success: false,
          translations: [],
          error: `Invalid value for key "${key}": Expected a string, got ${typeof value}`,
        };
      }

      translations.push({ key, value });
    }

    if (translations.length === 0) {
      return {
        success: false,
        translations: [],
        error: "No translations found in the file",
      };
    }

    return {
      success: true,
      translations,
    };
  } catch (error) {
    return {
      success: false,
      translations: [],
      error:
        error instanceof Error
          ? `Failed to parse JSON: ${error.message}`
          : "Failed to parse JSON",
    };
  }
}

/**
 * Parse import based on format
 */
export function parseImport(
  content: string,
  format: ImportFormat
): ParseResult {
  switch (format) {
    case "i18n":
      return parseI18nFormat(content);
    default:
      return {
        success: false,
        translations: [],
        error: `Unsupported format: ${format}`,
      };
  }
}

/**
 * Detect format from content
 */
export function detectFormat(content: string): ImportFormat | null {
  try {
    const trimmed = content.trim();
    if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
      const data = JSON.parse(trimmed);
      if (
        typeof data === "object" &&
        !Array.isArray(data) &&
        Object.values(data).every((v) => typeof v === "string")
      ) {
        return "i18n";
      }
    }
  } catch {
    // Failed to detect format
  }
  return null;
}

