export type ReviewStatus = 'NOT_REVIEWED' | 'PENDING' | 'APPROVED' | 'REJECTED';

export interface Translation {
  language: string;
  value: string;
  reviewStatus: ReviewStatus;
  createdAt: string;
  updatedAt?: string;
}

export interface TranslationKey {
  id: string;
  key: string;
  description?: string;
  tags: string[];
  isPlural?: boolean;
  translations: Translation[];
  createdAt: string;
  updatedAt?: string;
}

export interface CreateKeyInput {
  projectId: string;
  key: string;
  description?: string;
  tags?: string[];
  isPlural?: boolean;
  translations?: Record<string, string>;
}

export interface UpdateKeyInput {
  id: string;
  key?: string;
  description?: string;
  tags?: string[];
  isPlural?: boolean;
}

export interface SetTranslationInput {
  keyId: string;
  language: string;
  value: string;
}

export interface DeleteTranslationInput {
  keyId: string;
  language: string;
}

