/**
 * Language detection utilities for import files
 */

export interface LanguageMatch {
  code: string;
  confidence: number; // 0-1, where 1 is highest confidence
}

/**
 * Common language code patterns in filenames
 */
const LANGUAGE_PATTERNS = [
  // Format: pattern, language code
  { pattern: /[-_.]en[-_.]/, code: 'en' },
  { pattern: /[-_.]ru[-_.]/, code: 'ru' },
  { pattern: /[-_.]de[-_.]/, code: 'de' },
  { pattern: /[-_.]es[-_.]/, code: 'es' },
  { pattern: /[-_.]fr[-_.]/, code: 'fr' },
  { pattern: /[-_.]it[-_.]/, code: 'it' },
  { pattern: /[-_.]pt[-_.]/, code: 'pt' },
  { pattern: /[-_.]ja[-_.]/, code: 'ja' },
  { pattern: /[-_.]zh[-_.]/, code: 'zh' },
  { pattern: /[-_.]ko[-_.]/, code: 'ko' },
  { pattern: /[-_.]ar[-_.]/, code: 'ar' },
  { pattern: /[-_.]hi[-_.]/, code: 'hi' },
  { pattern: /[-_.]tr[-_.]/, code: 'tr' },
  { pattern: /[-_.]pl[-_.]/, code: 'pl' },
  { pattern: /[-_.]nl[-_.]/, code: 'nl' },
  { pattern: /[-_.]sv[-_.]/, code: 'sv' },
  { pattern: /[-_.]da[-_.]/, code: 'da' },
  { pattern: /[-_.]fi[-_.]/, code: 'fi' },
  { pattern: /[-_.]no[-_.]/, code: 'no' },
  { pattern: /[-_.]cs[-_.]/, code: 'cs' },
  { pattern: /[-_.]uk[-_.]/, code: 'uk' },
  
  // End patterns (more specific)
  { pattern: /[-_.]en\.(json|js|ts)$/i, code: 'en' },
  { pattern: /[-_.]ru\.(json|js|ts)$/i, code: 'ru' },
  { pattern: /[-_.]de\.(json|js|ts)$/i, code: 'de' },
  { pattern: /[-_.]es\.(json|js|ts)$/i, code: 'es' },
  { pattern: /[-_.]fr\.(json|js|ts)$/i, code: 'fr' },
  { pattern: /[-_.]it\.(json|js|ts)$/i, code: 'it' },
  { pattern: /[-_.]pt\.(json|js|ts)$/i, code: 'pt' },
  { pattern: /[-_.]ja\.(json|js|ts)$/i, code: 'ja' },
  { pattern: /[-_.]zh\.(json|js|ts)$/i, code: 'zh' },
  { pattern: /[-_.]ko\.(json|js|ts)$/i, code: 'ko' },
  
  // Start patterns
  { pattern: /^en[-_.]/, code: 'en' },
  { pattern: /^ru[-_.]/, code: 'ru' },
  { pattern: /^de[-_.]/, code: 'de' },
  { pattern: /^es[-_.]/, code: 'es' },
  { pattern: /^fr[-_.]/, code: 'fr' },
  
  // Full name patterns
  { pattern: /english/i, code: 'en' },
  { pattern: /russian/i, code: 'ru' },
  { pattern: /german/i, code: 'de' },
  { pattern: /spanish/i, code: 'es' },
  { pattern: /french/i, code: 'fr' },
  { pattern: /italian/i, code: 'it' },
  { pattern: /portuguese/i, code: 'pt' },
  { pattern: /japanese/i, code: 'ja' },
  { pattern: /chinese/i, code: 'zh' },
  { pattern: /korean/i, code: 'ko' },
];

/**
 * Detect language from filename
 * @param filename - The name of the file
 * @returns Array of possible language matches sorted by confidence
 */
export function detectLanguageFromFilename(filename: string): LanguageMatch[] {
  const matches: LanguageMatch[] = [];
  const lowerFilename = filename.toLowerCase();

  for (const { pattern, code } of LANGUAGE_PATTERNS) {
    if (pattern.test(lowerFilename)) {
      // Higher confidence for end patterns
      const confidence = pattern.source.includes('$') ? 0.9 : 0.7;
      
      // Check if already added
      const existing = matches.find((m) => m.code === code);
      if (!existing) {
        matches.push({ code, confidence });
      } else if (confidence > existing.confidence) {
        existing.confidence = confidence;
      }
    }
  }

  // Sort by confidence
  return matches.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Get best language match from filename
 * @param filename - The name of the file
 * @returns Language code or null if no match found
 */
export function getBestLanguageMatch(filename: string): string | null {
  const matches = detectLanguageFromFilename(filename);
  return matches.length > 0 ? matches[0].code : null;
}

