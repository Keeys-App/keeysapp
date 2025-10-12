import { useQuery } from "@apollo/client";
import { useRef, useState, useEffect, useCallback } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { GET_PROJECT_KEYS } from "@/graphql/keys";
import type { TranslationKey } from "@/types/translationKey";
import { EmptyKeys } from "./EmptyKeys";
import { Key } from "./Key";
import { KeySkeleton } from "./KeySkeleton";
import { KeyControls } from "./KeyControls";
import type { Language, LanguageWithLocale } from "@/types/project";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { ErrorState } from "../blocks";
import { CustomScrollbar } from "@/components/ui/custom-scrollbar";

interface KeyListProps {
  projectId: string;
  projectLanguages: (Language | LanguageWithLocale)[];
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
  onCreateKey,
  selectedKey,
  onSelectKey,
  editingTranslation = null,
  onEditingTranslationChange,
}: KeyListProps) {
  const [loadingRanges, setLoadingRanges] = useState<Set<number>>(new Set());
  const keysMapRef = useRef<Map<number, TranslationKey>>(new Map());

  const { data, loading, error, fetchMore } = useQuery(GET_PROJECT_KEYS, {
    variables: { 
      projectId,
      offset: 0,
      limit: PAGE_SIZE
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

  // Clear cache when project changes
  useEffect(() => {
    keysMapRef.current.clear();
    setLoadingRanges(new Set());
  }, [projectId]);

  // Update keys map with initial data
  useEffect(() => {
    if (initialKeys.length > 0) {
      initialKeys.forEach((key, index) => {
        keysMapRef.current.set(index, key);
      });
    }
  }, [initialKeys]);

  // Convert map to array for rendering
  const keys: (TranslationKey | undefined)[] = Array.from(
    { length: totalCount },
    (_, index) => keysMapRef.current.get(index)
  );

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

    if (rangeLoaded && pageOffset + PAGE_SIZE <= totalCount) {
      return;
    }

    setLoadingRanges((prev) => new Set(prev).add(pageOffset));
    
    try {
      const result = await fetchMore({
        variables: {
          offset: pageOffset,
          limit: PAGE_SIZE,
        },
      });

      // Update keys map with new data
      const newKeys = result.data?.projectKeys?.keys || [];
      newKeys.forEach((key, index) => {
        keysMapRef.current.set(pageOffset + index, key);
      });

      // Force re-render
      setLoadingRanges((prev) => {
        const next = new Set(prev);
        next.delete(pageOffset);
        return next;
      });
    } catch (err) {
      console.error("Failed to load keys range:", err);
      setLoadingRanges((prev) => {
        const next = new Set(prev);
        next.delete(pageOffset);
        return next;
      });
    }
  }, [fetchMore, totalCount, loadingRanges]);

  // Calculate estimated size based on number of languages
  // Each language row is approximately 60px, plus some padding
  const estimateSize = () => {
    return projectLanguages.length * 60 + 40;
  };

  // Use totalCount for virtualizer to show correct scrollbar proportions
  const virtualizer = useVirtualizer({
    count: totalCount || keys.length,
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
    if (!virtualItems.length || loading || !totalCount) {
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
    const preloadAfter = Math.min(totalCount - 1, maxIndex + preloadCount);

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
  }, [virtualItems, loading, totalCount, loadKeysRange]);

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <KeyControls projectId={projectId} onCreateKey={onCreateKey} />
        <div className="flex-1 overflow-auto">
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
          <KeySkeleton languagesCount={projectLanguages.length || 5} />
        </div>
      </div>
    );
  }

  if (error) {
    const errorMessage = getUserFriendlyErrorMessage(
      error,
      "Failed to load translation keys. Please try again."
    );
    return <ErrorState message={errorMessage} />;
  }

  return (
    <div className="flex flex-col h-full">
      <KeyControls projectId={projectId} onCreateKey={onCreateKey} />
      {keys.length === 0 ? (
        <div className="flex flex-col flex-1 min-h-[50vh]">
          <EmptyKeys projectId={projectId} onCreateKey={onCreateKey} />
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
            totalItems={totalCount}
            totalHeight={virtualizer.getTotalSize()}
          />
        </div>
      )}
    </div>
  );
}
