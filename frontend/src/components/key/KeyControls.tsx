import type { FC } from "react";
import { Button } from "@/components/ui/button";
import { KeysSearch } from "./KeysSearch";

interface KeyControlsProps {
  projectId: string;
  onCreateKey: () => void;
  totalCount?: number;
  isSearching?: boolean;
  hasKeys?: boolean;
}

export const KeyControls: FC<KeyControlsProps> = ({
  projectId,
  onCreateKey,
  totalCount,
  isSearching = false,
  hasKeys = true,
}) => {
  return (
    <div className="h-12 py-1 px-2 grid grid-cols-2 gap-2 items-center justify-end bg-muted border-b">
      {hasKeys ? (
        <>
          <div className="flex justify-start">
            <KeysSearch resultsCount={totalCount} isLoading={isSearching} />
          </div>
          <div className="flex justify-end">
            <Button size="sm" onClick={onCreateKey}>
              Add key
            </Button>
          </div>
        </>
      ) : null}
    </div>
  );
};
