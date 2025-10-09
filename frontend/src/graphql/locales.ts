import { gql } from '@apollo/client';

export interface Locale {
  id: number;
  key: string;
  value: string;
  language: string;
  namespace: string;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
}

export interface LocaleFilter {
  language?: string;
  namespace?: string;
  isActive?: boolean;
}

export interface LocaleCreateInput {
  key: string;
  value: string;
  language: string;
  namespace?: string;
  isActive?: boolean;
}

export interface LocaleUpdateInput {
  key?: string;
  value?: string;
  language?: string;
  namespace?: string;
  isActive?: boolean;
}

// Queries
export const GET_LOCALES = gql`
  query GetLocales($filter: LocaleFilter, $skip: Int, $limit: Int) {
    locales(filter: $filter, skip: $skip, limit: $limit) {
      id
      key
      value
      language
      namespace
      isActive
      createdAt
      updatedAt
    }
  }
`;

export const GET_LOCALE = gql`
  query GetLocale($id: Int!) {
    locale(id: $id) {
      id
      key
      value
      language
      namespace
      isActive
      createdAt
      updatedAt
    }
  }
`;

export const EXPORT_LOCALES = gql`
  query ExportLocales($language: String!, $namespace: String) {
    exportLocales(language: $language, namespace: $namespace)
  }
`;

// Mutations
export const CREATE_LOCALE = gql`
  mutation CreateLocale($input: LocaleCreateInput!) {
    createLocale(input: $input) {
      id
      key
      value
      language
      namespace
      isActive
      createdAt
      updatedAt
    }
  }
`;

export const UPDATE_LOCALE = gql`
  mutation UpdateLocale($id: Int!, $input: LocaleUpdateInput!) {
    updateLocale(id: $id, input: $input) {
      id
      key
      value
      language
      namespace
      isActive
      createdAt
      updatedAt
    }
  }
`;

export const DELETE_LOCALE = gql`
  mutation DeleteLocale($id: Int!) {
    deleteLocale(id: $id) {
      success
      message
    }
  }
`;
