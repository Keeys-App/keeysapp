import { gql } from '@apollo/client';

export const AI_TRANSLATE = gql`
  mutation AiTranslate($input: TranslateInput!) {
    aiTranslate(input: $input) {
      text
      success
      error
      reason
    }
  }
`;

export const AI_REPHRASE = gql`
  mutation AiRephrase($input: RephraseInput!) {
    aiRephrase(input: $input) {
      text
      success
      error
      reason
    }
  }
`;

export const AI_SHORTEN = gql`
  mutation AiShorten($input: ShortenInput!) {
    aiShorten(input: $input) {
      text
      success
      error
      reason
    }
  }
`;

export const AI_SUGGEST_VARIANTS = gql`
  mutation AiSuggestVariants($input: SuggestVariantsInput!) {
    aiSuggestVariants(input: $input) {
      variants
      success
      error
      reason
    }
  }
`;

// Types
export interface TranslationResult {
  text: string;
  success: boolean;
  error?: string | null;
  reason?: string | null;
}

export interface VariantsResult {
  variants: string[];
  success: boolean;
  error?: string | null;
  reason?: string | null;
}

export interface TranslateInput {
  text: string;
  targetLanguage: string;
  sourceLanguage?: string;
  context?: string;
  teamId?: string;
}

export interface RephraseInput {
  text: string;
  language: string;
  context?: string;
  teamId?: string;
}

export interface ShortenInput {
  text: string;
  language: string;
  context?: string;
  teamId?: string;
}

export interface SuggestVariantsInput {
  text: string;
  language: string;
  context?: string;
  count?: number;
  teamId?: string;
}

export interface AiTranslateData {
  aiTranslate: TranslationResult;
}

export interface AiRephraseData {
  aiRephrase: TranslationResult;
}

export interface AiShortenData {
  aiShorten: TranslationResult;
}

export interface AiSuggestVariantsData {
  aiSuggestVariants: VariantsResult;
}

