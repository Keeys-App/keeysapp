import { gql } from '@apollo/client';

export const GET_PROJECT_KEYS = gql`
  query GetProjectKeys($projectId: String!) {
    projectKeys(projectId: $projectId) {
      id
      key
      description
      translations {
        language
        value
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const GET_KEY = gql`
  query GetKey($id: String!) {
    key(id: $id) {
      id
      key
      description
      translations {
        language
        value
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const CREATE_KEY = gql`
  mutation CreateKey($input: CreateKeyInput!) {
    createKey(input: $input) {
      id
      key
      description
      translations {
        language
        value
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const UPDATE_KEY = gql`
  mutation UpdateKey($input: UpdateKeyInput!) {
    updateKey(input: $input) {
      id
      key
      description
      translations {
        language
        value
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const DELETE_KEY = gql`
  mutation DeleteKey($id: String!) {
    deleteKey(id: $id)
  }
`;

export const SET_TRANSLATION = gql`
  mutation SetTranslation($input: SetTranslationInput!) {
    setTranslation(input: $input) {
      language
      value
      createdAt
      updatedAt
    }
  }
`;

export const DELETE_TRANSLATION = gql`
  mutation DeleteTranslation($input: DeleteTranslationInput!) {
    deleteTranslation(input: $input)
  }
`;

export const BATCH_IMPORT_TRANSLATIONS = gql`
  mutation BatchImportTranslations($input: BatchImportInput!) {
    batchImportTranslations(input: $input) {
      successCount
      errorCount
      createdKeys
      updatedKeys
      errors
    }
  }
`;

