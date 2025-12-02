/**
 * ICU MessageFormat Plural utilities
 *
 * Handles parsing and building ICU plural format strings:
 * {count, plural, one {{count} item} other {{count} items}}
 */

export type PluralForm = 'zero' | 'one' | 'two' | 'few' | 'many' | 'other';

export interface PluralForms {
  zero?: string;
  one?: string;
  two?: string;
  few?: string;
  many?: string;
  other: string; // 'other' is always required
}

export interface ParsedPlural {
  variable: string;
  forms: PluralForms;
}

/**
 * Plural forms configuration for different languages based on CLDR rules.
 * @see https://cldr.unicode.org/index/cldr-spec/plural-rules
 */
export const LANGUAGE_PLURAL_FORMS: Record<string, PluralForm[]> = {
  // East Asian languages - no plural distinction
  zh: ['other'],
  ja: ['other'],
  ko: ['other'],
  vi: ['other'],
  th: ['other'],

  // Germanic/Romance - one/other
  en: ['one', 'other'],
  es: ['one', 'other'],
  fr: ['one', 'other'],
  de: ['one', 'other'],
  it: ['one', 'other'],
  pt: ['one', 'other'],
  nl: ['one', 'other'],
  sv: ['one', 'other'],
  no: ['one', 'other'],
  da: ['one', 'other'],
  fi: ['one', 'other'],
  hu: ['one', 'other'],
  tr: ['one', 'other'],
  hi: ['one', 'other'],

  // Romanian - one/few/other
  ro: ['one', 'few', 'other'],

  // Slavic languages - one/few/many/other
  ru: ['one', 'few', 'many', 'other'],
  uk: ['one', 'few', 'many', 'other'],
  pl: ['one', 'few', 'many', 'other'],
  cs: ['one', 'few', 'many', 'other'],

  // Arabic - zero/one/two/few/many/other
  ar: ['zero', 'one', 'two', 'few', 'many', 'other'],
};

/**
 * Get plural forms for a language code.
 *
 * @param langCode - Language code (e.g., 'en', 'ru')
 * @returns Array of plural form names for the language
 */
export function getPluralFormsForLanguage(langCode: string): PluralForm[] {
  return LANGUAGE_PLURAL_FORMS[langCode] || ['one', 'other'];
}

/**
 * Check if a string is in ICU plural format.
 *
 * @param value - String to check
 * @returns true if the string is in ICU plural format
 */
export function isICUPlural(value: string): boolean {
  if (!value) {
    return false;
  }
  // Match pattern: {variable, plural, ...forms...}
  const pluralPattern = /^\s*\{[^,]+,\s*plural\s*,/;
  return pluralPattern.test(value);
}

/**
 * Parse an ICU plural format string into structured data.
 *
 * @param value - ICU plural format string
 * @returns Parsed plural data or null if parsing fails
 *
 * @example
 * parseICUPlural('{count, plural, one {{count} item} other {{count} items}}')
 * // Returns: { variable: 'count', forms: { one: '{count} item', other: '{count} items' } }
 */
export function parseICUPlural(value: string): ParsedPlural | null {
  if (!value || !isICUPlural(value)) {
    return null;
  }

  try {
    // Extract the variable name
    const variableMatch = value.match(/^\s*\{([^,]+),\s*plural\s*,/);
    if (!variableMatch) {
      return null;
    }
    const variable = variableMatch[1].trim();

    // Remove the outer wrapper to get the forms content
    // {count, plural, one {...} other {...}} -> one {...} other {...}
    const formsStart = value.indexOf('plural,') + 'plural,'.length;
    let formsContent = value.substring(formsStart);

    // Remove the final closing brace
    const lastBraceIndex = formsContent.lastIndexOf('}');
    if (lastBraceIndex !== -1) {
      formsContent = formsContent.substring(0, lastBraceIndex);
    }

    // Parse individual forms
    const forms: PluralForms = { other: '' };
    const formPattern =
      /\b(zero|one|two|few|many|other)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}/g;

    let match;
    while ((match = formPattern.exec(formsContent)) !== null) {
      const [, formName, formValue] = match;
      forms[formName as PluralForm] = formValue.trim();
    }

    // Ensure 'other' form exists
    if (!forms.other && !forms.one) {
      return null;
    }

    return { variable, forms };
  } catch {
    return null;
  }
}

/**
 * Build an ICU plural format string from structured data.
 *
 * @param variable - Variable name (e.g., 'count')
 * @param forms - Plural forms object
 * @returns ICU plural format string
 *
 * @example
 * buildICUPlural('count', { one: '{count} item', other: '{count} items' })
 * // Returns: '{count, plural, one {{count} item} other {{count} items}}'
 */
export function buildICUPlural(variable: string, forms: PluralForms): string {
  const formParts: string[] = [];

  // Add forms in a consistent order
  const formOrder: PluralForm[] = ['zero', 'one', 'two', 'few', 'many', 'other'];

  for (const form of formOrder) {
    const value = forms[form];
    if (value !== undefined && value !== '') {
      formParts.push(`${form} {${value}}`);
    }
  }

  return `{${variable}, plural, ${formParts.join(' ')}}`;
}

/**
 * Get a human-readable label for a plural form.
 *
 * @param form - Plural form name
 * @returns Human-readable label
 */
export function getPluralFormLabel(form: PluralForm): string {
  const labels: Record<PluralForm, string> = {
    zero: 'Zero (0)',
    one: 'One (1)',
    two: 'Two (2)',
    few: 'Few (2-4)',
    many: 'Many (5+)',
    other: 'Other',
  };
  return labels[form] || form;
}

/**
 * Get example numbers for a plural form based on language.
 *
 * @param form - Plural form name
 * @param langCode - Language code
 * @returns Example numbers string
 */
export function getPluralFormExamples(form: PluralForm, langCode: string): string {
  // Examples based on CLDR rules
  const examples: Record<string, Record<PluralForm, string>> = {
    en: {
      zero: '0',
      one: '1',
      two: '2',
      few: '',
      many: '',
      other: '0, 2, 3, 4, 5...',
    },
    ru: {
      zero: '0',
      one: '1, 21, 31...',
      two: '',
      few: '2, 3, 4, 22, 23...',
      many: '0, 5-20, 25-30...',
      other: '1.5, 2.5...',
    },
    ar: {
      zero: '0',
      one: '1',
      two: '2',
      few: '3-10, 103-110...',
      many: '11-99, 111-199...',
      other: '100-102, 200-202...',
    },
    pl: {
      zero: '0',
      one: '1',
      two: '',
      few: '2-4, 22-24...',
      many: '0, 5-21, 25-31...',
      other: '1.5, 2.5...',
    },
  };

  const langExamples = examples[langCode] || examples['en'];
  return langExamples?.[form] || '';
}

/**
 * Validate plural forms for a language.
 *
 * @param forms - Plural forms to validate
 * @param langCode - Language code
 * @returns Array of validation errors (empty if valid)
 */
export function validatePluralForms(
  forms: Partial<PluralForms>,
  langCode: string
): string[] {
  const errors: string[] = [];
  const requiredForms = getPluralFormsForLanguage(langCode);

  // Check that 'other' is always present
  if (!forms.other?.trim()) {
    errors.push("The 'other' form is required");
  }

  // Check required forms for the language (except 'other' which we already checked)
  for (const form of requiredForms) {
    if (form !== 'other' && !forms[form]?.trim()) {
      errors.push(`The '${form}' form is required for ${langCode}`);
    }
  }

  return errors;
}

/**
 * Create empty plural forms for a language.
 *
 * @param langCode - Language code
 * @param variable - Variable name to use in placeholders (e.g., 'count')
 * @returns Empty plural forms object with placeholders
 */
export function createEmptyPluralForms(
  langCode: string,
  variable: string = 'count'
): PluralForms {
  const requiredForms = getPluralFormsForLanguage(langCode);
  const forms: PluralForms = { other: `{${variable}}` };

  for (const form of requiredForms) {
    if (form !== 'other') {
      forms[form] = `{${variable}}`;
    }
  }

  return forms;
}

