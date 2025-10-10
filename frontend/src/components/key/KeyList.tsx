import { useQuery } from "@apollo/client";
import { useRef, useMemo } from "react";
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

interface KeyListProps {
  projectId: string;
  projectLanguages: (Language | LanguageWithLocale)[];
  onCreateKey: () => void;
  selectedKey?: TranslationKey | null;
  onSelectKey?: (key: TranslationKey) => void;
}

export function KeyList({
  projectId,
  projectLanguages,
  onCreateKey,
  selectedKey,
  onSelectKey,
}: KeyListProps) {
  const { data, loading, error } = useQuery(GET_PROJECT_KEYS, {
    variables: { projectId },
    skip: !projectId,
    fetchPolicy: 'cache-first', // Use cache when available
    nextFetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: false, // Don't trigger re-renders on network status changes
  });

  const parentRef = useRef<HTMLDivElement>(null);
  
  // Memoize keys array to prevent unnecessary re-renders
  // Only update if the array length or individual key IDs/updatedAt changed
  const keys: TranslationKey[] = useMemo(() => {
    const projectKeys = data?.projectKeys || [];
    return projectKeys;
  }, [
    data?.projectKeys?.length,
    // Create a stable key based on IDs and update times
    data?.projectKeys?.map((k) => `${k.id}-${k.updatedAt}`).join(','),
  ]);

  // Calculate estimated size based on number of languages
  // Each language row is approximately 60px, plus some padding
  const estimateSize = () => {
    return projectLanguages.length * 60 + 40;
  };

  const virtualizer = useVirtualizer({
    count: keys.length,
    getScrollElement: () => parentRef.current,
    estimateSize,
    overscan: 5,
    measureElement:
      typeof window !== "undefined" &&
      navigator.userAgent.indexOf("Firefox") === -1
        ? (element) => element?.getBoundingClientRect().height
        : undefined,
  });

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
        <div
          ref={parentRef}
          className="flex-1 overflow-auto"
        >
          <div
            style={{
              paddingTop: virtualizer.getVirtualItems()[0]?.start || 0,
              paddingBottom: 
                virtualizer.getTotalSize() - 
                (virtualizer.getVirtualItems()[virtualizer.getVirtualItems().length - 1]?.end || 0),
            }}
          >
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const key = keys[virtualItem.index];
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
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
