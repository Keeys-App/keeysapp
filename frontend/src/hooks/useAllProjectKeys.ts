import { useEffect, useState } from 'react';
import { useQuery } from '@apollo/client';
import { GET_PROJECT_KEYS } from '@/graphql/keys';
import type { TranslationKey } from '@/types/translationKey';

interface UseAllProjectKeysResult {
  keys: TranslationKey[];
  loading: boolean;
  error: Error | undefined;
  totalCount: number;
}

const PAGE_SIZE = 100;

/**
 * Hook to fetch all project keys using pagination
 * Automatically loads all pages until hasMore is false
 */
export function useAllProjectKeys(projectId: string): UseAllProjectKeysResult {
  const [allKeys, setAllKeys] = useState<TranslationKey[]>([]);
  const [isLoadingAll, setIsLoadingAll] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  const { data, loading, error, fetchMore } = useQuery(GET_PROJECT_KEYS, {
    variables: {
      projectId,
      offset: 0,
      limit: PAGE_SIZE,
    },
    skip: !projectId,
    fetchPolicy: 'network-only', // Always fetch fresh data for export/import
  });

  // Reset state when projectId changes
  useEffect(() => {
    setAllKeys([]);
    setIsLoadingAll(true);
    setTotalCount(0);
  }, [projectId]);

  useEffect(() => {
    const loadAllKeys = async () => {
      if (!data?.projectKeys) {
        return;
      }

      // Reset when we get fresh data from the first page
      if (data.projectKeys.keys) {
        setAllKeys([]); // Clear before loading to ensure fresh data
      }

      let currentKeys = [...(data.projectKeys.keys || [])];
      let hasMore = data.projectKeys.hasMore;
      let currentOffset = currentKeys.length;
      const total = data.projectKeys.totalCount || 0;

      setTotalCount(total);

      // Load all remaining pages
      while (hasMore && currentOffset < total) {
        try {
          const result = await fetchMore({
            variables: {
              offset: currentOffset,
              limit: PAGE_SIZE,
            },
          });

          if (result.data?.projectKeys) {
            const newKeys = result.data.projectKeys.keys || [];
            currentKeys = [...currentKeys, ...newKeys];
            hasMore = result.data.projectKeys.hasMore;
            currentOffset = currentKeys.length;
          } else {
            break;
          }
        } catch (err) {
          console.error('Error loading more keys:', err);
          break;
        }
      }

      setAllKeys(currentKeys);
      setIsLoadingAll(false);
    };

    if (!loading && data) {
      loadAllKeys();
    }
  }, [data, loading, fetchMore]);

  return {
    keys: allKeys,
    loading: loading || isLoadingAll,
    error: error,
    totalCount,
  };
}

