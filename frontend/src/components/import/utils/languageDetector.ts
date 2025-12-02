/**
 * Language detection utilities for import files using centralized language configs.
 */

import { getLanguageConfigs, type LanguageConfig } from "@/stores";

export interface LanguageMatch {
  code: string;
  confidence: number; // 0-1, where 1 is highest confidence
}

/**
 * Detect language from filename using centralized language configurations.
 * @param filename - The name of the file
 * @returns Array of possible language matches sorted by confidence
 */
export function detectLanguageFromFilename(filename: string): LanguageMatch[] {
  const matches: LanguageMatch[] = [];
  const lowerFilename = filename.toLowerCase();
  const languageConfigs: LanguageConfig[] = getLanguageConfigs();

  for (const langConfig of languageConfigs) {
    const { code, detectionPatterns } = langConfig;
    let maxConfidence = 0;

    // Check end patterns (highest confidence)
    for (const pattern of detectionPatterns.endPatterns) {
      if (pattern.test(lowerFilename)) {
        maxConfidence = Math.max(maxConfidence, 0.9);
      }
    }

    // Check middle patterns (high confidence)
    for (const pattern of detectionPatterns.middlePatterns) {
      if (pattern.test(lowerFilename)) {
        maxConfidence = Math.max(maxConfidence, 0.8);
      }
    }

    // Check start patterns (medium confidence)
    for (const pattern of detectionPatterns.startPatterns) {
      if (pattern.test(lowerFilename)) {
        maxConfidence = Math.max(maxConfidence, 0.7);
      }
    }

    // Check full name patterns (lower confidence)
    for (const pattern of detectionPatterns.fullNames) {
      if (pattern.test(lowerFilename)) {
        maxConfidence = Math.max(maxConfidence, 0.6);
      }
    }

    // Add to matches if found
    if (maxConfidence > 0) {
      matches.push({ code, confidence: maxConfidence });
    }
  }

  // Sort by confidence (highest first)
  return matches.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Get best language match from filename.
 * @param filename - The name of the file
 * @returns Language code or null if no match found
 */
export function getBestLanguageMatch(filename: string): string | null {
  const matches = detectLanguageFromFilename(filename);
  return matches.length > 0 ? matches[0].code : null;
}
