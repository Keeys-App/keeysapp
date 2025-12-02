/**
 * Hook to initialize languages from API on app startup.
 * Call this hook once in a top-level component (e.g., Layout).
 */

import { useEffect } from 'react';
import { useQuery } from '@apollo/client';
import {
  GET_AVAILABLE_LANGUAGES,
  type GetAvailableLanguagesData,
} from '@/graphql/projects';
import { useLanguagesStore, toLanguageConfig } from '@/stores';

export function useLanguagesInit(): void {
  const { setLanguages, setLoading, setError, isLoaded } = useLanguagesStore();

  const { data, loading, error } = useQuery<GetAvailableLanguagesData>(
    GET_AVAILABLE_LANGUAGES,
    {
      skip: isLoaded,
      fetchPolicy: 'cache-first',
    }
  );

  useEffect(() => {
    setLoading(loading);
  }, [loading, setLoading]);

  useEffect(() => {
    if (error) {
      console.error('Failed to load languages:', error);
      setError(error.message);
    }
  }, [error, setError]);

  useEffect(() => {
    if (data?.availableLanguages) {
      const languages = data.availableLanguages.map(toLanguageConfig);
      setLanguages(languages);
    }
  }, [data, setLanguages]);
}

