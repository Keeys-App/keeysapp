import { useQuery } from "@apollo/client";
import { useRef, useState, useEffect, useCallback } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { GET_PROJECT_KEYS } from "@/graphql/keys";
import type { TranslationKey } from "@/types/translationKey";
import { EmptyKeys } from "./EmptyKeys";
import { EmptySearchResults } from "./EmptySearchResults";
import { Key } from "./Key";
import { KeySkeleton } from "./KeySkeleton";
import { KeyControls } from "./KeyControls";
import type { Language, LanguageWithLocale } from "@/types/project";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { ErrorState } from "../blocks";
import { CustomScrollbar } from "@/components/ui/custom-scrollbar";
import { useKeysSearchStore } from "@/stores";

interface KeyListProps {
  projectId: string;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectKeysCount: number;
  onCreateKey: () => void;
  selectedKey?: TranslationKey | null;
  onSelectKey?: (key: TranslationKey) => void;
  editingTranslation?: {
    keyId: string;
    language: string;
  } | null;
  onEditingTranslationChange?: (translation: {
    keyId: string;
    language: string;
  } | null) => void;
}

const PAGE_SIZE = 20;

export function KeyList({
  projectId,
  projectLanguages,
  projectKeysCount,
  onCreateKey,
  selectedKey,
  onSelectKey,
  editingTranslation = null,
  onEditingTranslationChange,
}: KeyListProps) {
  const [loadingRanges, setLoadingRanges] = useState<Set<number>>(new Set());
  const [, forceUpdate] = useState({});
  const keysMapRef = useRef<Map<number, TranslationKey>>(new Map());
  const { search } = useKeysSearchStore();
  const previousSearchRef = useRef<string | undefined>(search);
  const previousKeysRef = useRef<(TranslationKey | undefined)[]>([]);
  const previousTotalCountRef = useRef<number>(0);

  const { data, loading, error, fetchMore } = useQuery(GET_PROJECT_KEYS, {
    variables: { 
      projectId,
      offset: 0,
      limit: PAGE_SIZE,
      search: search || undefined
    },
    skip: !projectId,
    fetchPolicy: 'cache-and-network',
    nextFetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: false,
  });

  const parentRef = useRef<HTMLDivElement>(null);
  
  // Extract keys from paginated response
  const initialKeys: TranslationKey[] = data?.projectKeys?.keys || [];
  const totalCount = data?.projectKeys?.totalCount || 0;

  // Clear cache only when project changes
  useEffect(() => {
    keysMapRef.current.clear();
    setLoadingRanges(new Set());
    previousKeysRef.current = [];
    previousTotalCountRef.current = 0;
  }, [projectId]);

  // Detect if search query changed
  const searchChanged = previousSearchRef.current !== search;
  
  // Update keys map with initial data and force re-render
  useEffect(() => {
    // If search changed and we got new data, clear the map and update previousSearchRef
    if (searchChanged && !loading) {
      keysMapRef.current.clear();
      setLoadingRanges(new Set());
      previousSearchRef.current = search;
      
      // Update map with new data
      initialKeys.forEach((key, index) => {
        keysMapRef.current.set(index, key);
      });
      
      // Save current state as previous
      const currentKeys = Array.from(
        { length: totalCount },
        (_, index) => keysMapRef.current.get(index)
      );
      previousKeysRef.current = currentKeys;
      previousTotalCountRef.current = totalCount;
      
      // Force re-render to show the loaded keys
      forceUpdate(() => ({}));
    } else if (!searchChanged && initialKeys.length > 0) {
      // Same search, just update with new data
      initialKeys.forEach((key, index) => {
        keysMapRef.current.set(index, key);
      });
      
      // Save current state as previous
      const currentKeys = Array.from(
        { length: totalCount },
        (_, index) => keysMapRef.current.get(index)
      );
      previousKeysRef.current = currentKeys;
      previousTotalCountRef.current = totalCount;
      
      // Force re-render to show the loaded keys
      forceUpdate(() => ({}));
    }
  }, [initialKeys, totalCount, loading, search, searchChanged]);

  // Convert map to array for rendering
  // Show previous results while loading new search
  const isSearching = searchChanged && loading;
  const keys: (TranslationKey | undefined)[] = isSearching 
    ? previousKeysRef.current
    : Array.from(
        { length: totalCount },
        (_, index) => keysMapRef.current.get(index)
      );
  const displayTotalCount = isSearching ? previousTotalCountRef.current : totalCount;

  // Load specific range of keys
  const loadKeysRange = useCallback(async (startIndex: number) => {
    const pageOffset = Math.floor(startIndex / PAGE_SIZE) * PAGE_SIZE;
    
    // Don't load if already loading this range
    if (loadingRanges.has(pageOffset)) {
      return;
    }

    // Don't load if all keys in this range are already loaded
    const rangeLoaded = Array.from(
      { length: PAGE_SIZE },
      (_, i) => keysMapRef.current.has(pageOffset + i)
    ).every(Boolean);

    if (rangeLoaded && pageOffset + PAGE_SIZE <= displayTotalCount) {
      return;
    }

    setLoadingRanges((prev) => new Set(prev).add(pageOffset));
    
    try {
      const result = await fetchMore({
        variables: {
          offset: pageOffset,
          limit: PAGE_SIZE,
          search: search || undefined,
        },
      });

      // Update keys map with new data
      const newKeys = result.data?.projectKeys?.keys || [];
      newKeys.forEach((key, index) => {
        keysMapRef.current.set(pageOffset + index, key);
      });

      // Remove loading state and force re-render
      setLoadingRanges((prev) => {
        const next = new Set(prev);
        next.delete(pageOffset);
        return next;
      });
      
      // Force re-render to show the loaded keys
      forceUpdate(() => ({}));
    } catch (err) {
      console.error("Failed to load keys range:", err);
      setLoadingRanges((prev) => {
        const next = new Set(prev);
        next.delete(pageOffset);
        return next;
      });
    }
  }, [fetchMore, displayTotalCount, loadingRanges, search]);

  // Calculate estimated size based on number of languages
  // Each language row is approximately 60px, plus some padding
  const estimateSize = () => {
    return projectLanguages.length * 60 + 40;
  };

  // Use displayTotalCount for virtualizer to show correct scrollbar proportions
  const virtualizer = useVirtualizer({
    count: displayTotalCount || keys.length,
    getScrollElement: () => parentRef.current,
    estimateSize,
    overscan: 5,
    measureElement:
      typeof window !== "undefined" &&
      navigator.userAgent.indexOf("Firefox") === -1
        ? (element) => element?.getBoundingClientRect().height
        : undefined,
  });

  // Check if we need to load more when scrolling
  const virtualItems = virtualizer.getVirtualItems();
  
  useEffect(() => {
    if (!virtualItems.length || loading || !displayTotalCount) {
      return;
    }

    // Check all visible items and load missing ranges
    const visibleIndices = virtualItems.map(item => item.index);
    const minIndex = Math.min(...visibleIndices);
    const maxIndex = Math.max(...visibleIndices);

    // Load ranges for all visible items that aren't loaded yet
    const indicesToCheck = Array.from(
      { length: maxIndex - minIndex + 1 },
      (_, i) => minIndex + i
    );

    // Also preload adjacent pages for smooth scrolling
    const preloadCount = PAGE_SIZE;
    const preloadBefore = Math.max(0, minIndex - preloadCount);
    const preloadAfter = Math.min(displayTotalCount - 1, maxIndex + preloadCount);

    const allIndicesToCheck = [
      ...Array.from({ length: minIndex - preloadBefore }, (_, i) => preloadBefore + i),
      ...indicesToCheck,
      ...Array.from({ length: preloadAfter - maxIndex }, (_, i) => maxIndex + 1 + i),
    ];

    // Find unique page offsets that need to be loaded
    const pagesToLoad = new Set(
      allIndicesToCheck
        .filter(index => !keysMapRef.current.has(index))
        .map(index => Math.floor(index / PAGE_SIZE) * PAGE_SIZE)
    );

    // Load all missing pages
    pagesToLoad.forEach(pageOffset => {
      loadKeysRange(pageOffset);
    });
  }, [virtualItems, loading, displayTotalCount, loadKeysRange]);

  if (error) {
    const errorMessage = getUserFriendlyErrorMessage(
      error,
      "Failed to load translation keys. Please try again."
    );
    return <ErrorState message={errorMessage} />;
  }

  // Show skeletons only on initial load (not during search)
  const isInitialLoading = loading && !search && keys.length === 0;
  // Show controls if project has any keys (regardless of search results)
  const hasKeys = projectKeysCount > 0;

  return (
    <div className="flex flex-col h-full">
      <KeyControls projectId={projectId} onCreateKey={onCreateKey} totalCount={displayTotalCount} isSearching={loading} hasKeys={hasKeys} />
      {isInitialLoading ? (
        <div className="flex-1 overflow-auto">
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
        </div>
      ) : keys.length === 0 ? (
        <div className="flex flex-col flex-1 min-h-[50vh]">
          {search ? (
            <EmptySearchResults searchQuery={search} />
          ) : (
            <EmptyKeys projectId={projectId} onCreateKey={onCreateKey} />
          )}
        </div>
      ) : (
        <div className="relative flex-1">
          <div
            ref={parentRef}
            className="absolute inset-0 overflow-auto pr-3 hide-scrollbar"
          >
            <div
              style={{
                paddingTop: virtualizer.getVirtualItems()[0]?.start || 0,
                paddingBottom:
                  virtualizer.getTotalSize() -
                  (virtualizer.getVirtualItems()[
                    virtualizer.getVirtualItems().length - 1
                  ]?.end || 0),
              }}
            >
              {virtualizer.getVirtualItems().map((virtualItem) => {
                const key = keys[virtualItem.index];
                
                // If key is not loaded yet, show skeleton
                if (!key) {
                  return (
                    <div
                      key={`skeleton-${virtualItem.index}`}
                      data-index={virtualItem.index}
                    >
                      <KeySkeleton languagesCount={projectLanguages.length || 5} />
                    </div>
                  );
                }
                
                return (
                  <div
                    key={key.id}
                    data-index={virtualItem.index}
                    ref={virtualizer.measureElement}
                  >
                    <Key
                      keyData={key}
                      projectId={projectId}
                      projectLanguages={projectLanguages}
                      isSelected={selectedKey?.id === key.id}
                      onSelect={onSelectKey}
                      editingLanguage={
                        editingTranslation?.keyId === key.id
                          ? editingTranslation.language
                          : null
                      }
                      onEditingLanguageChange={(language) => {
                        if (onEditingTranslationChange) {
                          onEditingTranslationChange(
                            language ? { keyId: key.id, language } : null
                          );
                        }
                      }}
                    />
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Custom scrollbar */}
          <CustomScrollbar
            scrollContainerRef={parentRef}
            totalItems={displayTotalCount}
            totalHeight={virtualizer.getTotalSize()}
          />
        </div>
      )}
    </div>
  );
}
