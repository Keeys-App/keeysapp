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
}

const PAGE_SIZE = 20;

export function KeyList({
  projectId,
  projectLanguages,
  onCreateKey,
  selectedKey,
  onSelectKey,
}: KeyListProps) {
  const [editingTranslation, setEditingTranslation] = useState<{
    keyId: string;
    language: string;
  } | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

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
  const keys: TranslationKey[] = data?.projectKeys?.keys || [];
  const totalCount = data?.projectKeys?.totalCount || 0;
  const hasMore = data?.projectKeys?.hasMore || false;

  // Load more keys when scrolling near the end
  const loadMoreKeys = useCallback(async () => {
    if (isLoadingMore || !hasMore) {
      return;
    }

    setIsLoadingMore(true);
    try {
      await fetchMore({
        variables: {
          offset: keys.length,
          limit: PAGE_SIZE,
        },
        updateQuery: (prev, { fetchMoreResult }) => {
          if (!fetchMoreResult) {
            return prev;
          }

          return {
            projectKeys: {
              ...fetchMoreResult.projectKeys,
              keys: [
                ...(prev.projectKeys?.keys || []),
                ...(fetchMoreResult.projectKeys?.keys || []),
              ],
            },
          };
        },
      });
    } catch (err) {
      console.error("Failed to load more keys:", err);
    } finally {
      setIsLoadingMore(false);
    }
  }, [fetchMore, keys.length, hasMore, isLoadingMore]);

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
    if (!virtualItems.length) {
      return;
    }

    // Check if any visible item is not loaded yet
    const lastVisibleIndex = virtualItems[virtualItems.length - 1].index;
    
    // Load more if we're viewing items beyond what's loaded
    if (
      lastVisibleIndex >= keys.length - 10 && // Start loading 10 items before the end
      hasMore &&
      !isLoadingMore &&
      !loading
    ) {
      loadMoreKeys();
    }
  }, [
    hasMore,
    loadMoreKeys,
    keys.length,
    isLoadingMore,
    loading,
    virtualItems,
  ]);

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
                height: virtualizer.getTotalSize(),
                width: "100%",
                position: "relative",
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
                      style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        width: "100%",
                        transform: `translateY(${virtualItem.start}px)`,
                      }}
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
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      transform: `translateY(${virtualItem.start}px)`,
                    }}
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
                        setEditingTranslation(
                          language ? { keyId: key.id, language } : null
                        );
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
            loadedItems={keys.length}
            itemHeight={estimateSize()}
          />
        </div>
      )}
    </div>
  );
}
