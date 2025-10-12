import { type FC } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Item } from "@/components/ui/item";

/**
 * Loading skeleton for AI suggestions
 */
export const AutopilotSuggestionSkeleton: FC = () => {
  return (
    <Item variant="outline" className="w-full animate-in animate-out flex flex-col gap-5 border-border/50">
      <div className="flex gap-2 w-full">
        <Skeleton className="h-3 w-3" />
        <Skeleton className="w-full h-3" />
      </div>
      <div className="flex flex-col gap-2 w-full">
        <Skeleton className="h-2.5 w-full" />
        <Skeleton className="h-2.5 w-full" />
      </div>
      <div className="flex gap-2 w-full">
        <Skeleton className="h-8 w-24" />
      </div>
    </Item>
  );
};

