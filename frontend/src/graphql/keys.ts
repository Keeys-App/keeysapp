import { gql } from '@apollo/client';

export const GET_PROJECT_KEYS = gql`
  query GetProjectKeys($projectId: String!) {
    projectKeys(projectId: $projectId) {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
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
      tags
      translations {
        language
        value
        reviewStatus
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const CHECK_KEY_EXISTS = gql`
  query CheckKeyExists($projectId: String!, $key: String!) {
    checkKeyExists(projectId: $projectId, key: $key)
  }
`;

export const CREATE_KEY = gql`
  mutation CreateKey($input: CreateKeyInput!) {
    createKey(input: $input) {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
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
      tags
      translations {
        language
        value
        reviewStatus
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

export const GET_KEY_LOGS = gql`
  query GetKeyLogs($keyId: String!, $limit: Int) {
    keyLogs(keyId: $keyId, limit: $limit) {
      id
      keyId
      userId
      user {
        id
        username
        email
      }
      action
      fieldName
      language
      oldValue
      newValue
      createdAt
    }
  }
`;

export const APPROVE_TRANSLATION = gql`
  mutation ApproveTranslation($input: ApproveTranslationInput!) {
    approveTranslation(input: $input) {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const REJECT_TRANSLATION = gql`
  mutation RejectTranslation($input: RejectTranslationInput!) {
    rejectTranslation(input: $input) {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

export const DELETE_TRANSLATION_REVIEW = gql`
  mutation DeleteTranslationReview($keyId: String!, $language: String!) {
    deleteTranslationReview(keyId: $keyId, language: $language) {
      id
      key
      description
      tags
      translations {
        language
        value
        reviewStatus
        createdAt
        updatedAt
      }
      createdAt
      updatedAt
    }
  }
`;

