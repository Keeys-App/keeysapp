export interface Translation {
  language: string;
  value: string;
  createdAt: string;
  updatedAt?: string;
}

export interface TranslationKey {
  id: string;
  key: string;
  description?: string;
  tags: string[];
  translations: Translation[];
  createdAt: string;
  updatedAt?: string;
}

export interface CreateKeyInput {
  projectId: string;
  key: string;
  description?: string;
  tags?: string[];
  translations?: Record<string, string>;
}

export interface UpdateKeyInput {
  id: string;
  key?: string;
  description?: string;
  tags?: string[];
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

