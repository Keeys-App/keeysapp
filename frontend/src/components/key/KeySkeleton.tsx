import type { FC } from "react";
import { Skeleton } from "@/components/ui/skeleton";

interface KeySkeletonProps {
  languagesCount?: number;
}

/**
 * Skeleton loader that matches the structure of the Key component
 */
export const KeySkeleton: FC<KeySkeletonProps> = ({ languagesCount = 5 }) => {
  return (
    <div className="border-b grid grid-cols-[minmax(300px,300px)_minmax(300px,3fr)]">
      {/* Left column: Key name and description */}
      <div className="border-r relative">
        <div className="sticky bg-background top-[2px] z-10 py-2 px-4">
          <Skeleton className="h-5 w-3/4" />
        </div>
        <div className="px-4 py-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3 mt-1" />
        </div>
      </div>

      {/* Right column: Translations */}
      <div className="flex flex-col">
        {Array.from({ length: languagesCount }).map((_, index) => {
          return (
            <div
              key={index}
              className="grid grid-cols-[120px_1fr] even:bg-muted/50 border-b"
            >
              {/* Language name and code */}
              <div className="flex flex-col border-r p-2 gap-1">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-3 w-12" />
              </div>

              {/* Translation value */}
              <div className="p-2">
                <Skeleton className="h-4 w-full" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

