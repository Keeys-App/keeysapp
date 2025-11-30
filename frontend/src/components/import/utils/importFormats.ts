export type ImportFormat = "i18n" | "ios-strings";

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
 * Unescape iOS Strings value
 * Handles: \" -> ", \\ -> \, \n -> newline, \t -> tab
 */
function unescapeIosStringsValue(value: string): string {
  return value
    .replace(/\\"/g, '"')
    .replace(/\\n/g, '\n')
    .replace(/\\t/g, '\t')
    .replace(/\\\\/g, '\\');
}

/**
 * Convert iOS Strings variables to i18n format
 * Positional: %1$@, %2$d -> {var1}, {var2}
 * Simple: %@, %d, %f -> {var1}, {var2}, {var3}
 * 
 * Supported iOS formats:
 * - %@ - string
 * - %d, %i - integer
 * - %f - float
 * - %ld, %li - long integer
 * - %1$@, %2$d - positional arguments
 */
function convertIosVariablesToI18n(value: string): string {
  // First, handle positional arguments like %1$@, %2$d
  const positionalRegex = /%(\d+)\$[@disfl]/g;
  let hasPositional = false;
  let result = value.replace(positionalRegex, (_, position) => {
    hasPositional = true;
    return `{var${position}}`;
  });
  
  // If we had positional args, we're done
  if (hasPositional) {
    return result;
  }
  
  // Handle simple format specifiers: %@, %d, %i, %f, %ld, %li, %s
  const simpleRegex = /%(?:l?[disf]|@|s)/g;
  let varIndex = 0;
  result = result.replace(simpleRegex, () => {
    varIndex++;
    return `{var${varIndex}}`;
  });
  
  return result;
}

/**
 * Parse iOS Strings format (.strings files)
 * @example "key.name" = "Translation value";
 * 
 * Format:
 * - Lines starting with // or /* are comments
 * - Each translation line: "key" = "value";
 * - Supports escaped quotes: \"
 * - Supports multiline values with \n
 */
export function parseIosStringsFormat(content: string): ParseResult {
  try {
    const translations: ParsedTranslation[] = [];
    const lines = content.split('\n');
    
    // Regex to match: "key" = "value";
    // Handles escaped quotes inside key and value
    const lineRegex = /^\s*"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;?\s*$/;
    
    let inBlockComment = false;
    
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      
      // Handle block comments /* ... */
      if (inBlockComment) {
        if (line.includes('*/')) {
          inBlockComment = false;
          // Get content after block comment end
          line = line.substring(line.indexOf('*/') + 2).trim();
          if (!line) {
            continue;
          }
        } else {
          continue;
        }
      }
      
      // Check for start of block comment
      if (line.includes('/*')) {
        // Check if it ends on the same line
        if (line.includes('*/')) {
          // Single line block comment - extract content after it
          const afterComment = line.substring(line.indexOf('*/') + 2).trim();
          if (!afterComment) {
            continue;
          }
          line = afterComment;
        } else {
          inBlockComment = true;
          continue;
        }
      }
      
      // Skip empty lines and single-line comments
      if (!line || line.startsWith('//')) {
        continue;
      }
      
      // Try to match translation line
      const match = line.match(lineRegex);
      if (match) {
        const key = unescapeIosStringsValue(match[1]);
        const rawValue = unescapeIosStringsValue(match[2]);
        // Convert iOS format specifiers to i18n variables
        const value = convertIosVariablesToI18n(rawValue);
        translations.push({ key, value });
      }
    }
    
    if (translations.length === 0) {
      return {
        success: false,
        translations: [],
        error: "No translations found. Expected format: \"key\" = \"value\";",
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
          ? `Failed to parse iOS Strings: ${error.message}`
          : "Failed to parse iOS Strings",
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
    case "ios-strings":
      return parseIosStringsFormat(content);
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
 * Check if content looks like iOS Strings format
 */
function looksLikeIosStrings(content: string): boolean {
  const lines = content.split('\n');
  const lineRegex = /^\s*"[^"]*"\s*=\s*"[^"]*"\s*;?\s*$/;
  
  let translationLines = 0;
  for (const line of lines) {
    const trimmed = line.trim();
    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) {
      continue;
    }
    if (lineRegex.test(trimmed)) {
      translationLines++;
    }
  }
  
  return translationLines > 0;
}

/**
 * Detect format from content
 */
export function detectFormat(content: string): ImportFormat | null {
  try {
    const trimmed = content.trim();
    
    // Check for JSON format first
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
    
    // Check for iOS Strings format
    if (looksLikeIosStrings(trimmed)) {
      return "ios-strings";
    }
  } catch {
    // If JSON parse fails, try iOS Strings
    if (looksLikeIosStrings(content.trim())) {
      return "ios-strings";
    }
  }
  return null;
}

