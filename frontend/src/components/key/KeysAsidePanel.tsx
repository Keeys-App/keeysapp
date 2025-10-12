import { type FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import { KeyManagement } from "./KeyManagement";

interface KeysAsidePanelProps {
  selectedKey: TranslationKey | null;
  projectId: string;
  availableTags?: string[];
  onKeyDeleted?: () => void;
}

/**
 * Component for managing a selected translation key
 */
export const KeysAsidePanel: FC<KeysAsidePanelProps> = ({
  selectedKey,
  projectId,
  availableTags = [],
  onKeyDeleted,
}) => {
  console.log('KeysAsidePanel - selectedKey:', selectedKey);
  
  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 border-b h-12 box-border">
        <h2 className="text-base font-semibold">
          {selectedKey?.key ? "Key Management" : "Activity"}
        </h2>
      </div>
      <div className="flex-1 overflow-auto">
        {!selectedKey ? (
          <p className="text-muted-foreground text-sm p-4">
            Click on any translation key from the list to view and manage it
          </p>
        ) : (
          <KeyManagement
            selectedKey={selectedKey}
            projectId={projectId}
            availableTags={availableTags}
            onKeyDeleted={onKeyDeleted}
          />
        )}
      </div>
    </div>
  );
};
