import { type FC } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Item } from "@/components/ui/item";

/**
 * Loading skeleton for AI suggestions
 */
export const AutopilotSuggestionSkeleton: FC = () => {
  return (
    <Item variant="outline" className="w-full animate-in fade-in slide-in-from-bottom-2 duration-300 flex flex-col gap-5 border-border/50">
      <div className="flex gap-2 w-full">
        <Skeleton className="h-3 w-3 animate-pulse" />
        <Skeleton className="w-full h-3 animate-pulse" />
      </div>
      <div className="flex flex-col gap-2 w-full">
        <Skeleton className="h-2.5 w-full animate-pulse" />
        <Skeleton className="h-2.5 w-full animate-pulse" />
      </div>
      <div className="flex gap-2 w-full">
        <Skeleton className="h-8 w-24 animate-pulse" />
      </div>
    </Item>
  );
};

