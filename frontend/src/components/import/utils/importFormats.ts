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
 * Recursively flatten nested JSON object into dot-notation keys
 * @example { "AUTH": { "LOGIN": "Login" } } => [{ key: "AUTH.LOGIN", value: "Login" }]
 */
function flattenObject(
  obj: Record<string, unknown>,
  prefix = ""
): ParsedTranslation[] {
  const translations: ParsedTranslation[] = [];

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (typeof value === "string") {
      // String value - add as translation
      translations.push({ key: fullKey, value });
    } else if (
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(value)
    ) {
      // Nested object - recursively flatten
      translations.push(...flattenObject(value as Record<string, unknown>, fullKey));
    } else if (value !== null && value !== undefined) {
      // Skip null/undefined, but warn about other types
      console.warn(
        `Skipping key "${fullKey}" with unsupported type: ${typeof value}`
      );
    }
  }

  return translations;
}

/**
 * Parse i18n format (simple key-value JSON with nested object support)
 * @example { "welcome": "Welcome!", "AUTH": { "LOGIN": "Login" } }
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

    const translations = flattenObject(data);

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
 * Check if value is a valid translation value (string or nested object)
 */
function isValidTranslationValue(value: unknown): boolean {
  if (typeof value === "string") {
    return true;
  }
  if (typeof value === "object" && value !== null && !Array.isArray(value)) {
    // Check if nested object contains only valid translation values
    return Object.values(value).every((v) => isValidTranslationValue(v));
  }
  return false;
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
        Object.values(data).every((v) => isValidTranslationValue(v))
      ) {
        return "i18n";
      }
    }
  } catch {
    // Failed to detect format
  }
  return null;
}

