import { type FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import { KeyManagement } from "./KeyManagement";
import type { Language } from "@/types/project";
import { AutopilotCard } from "./AutopilotCard";

interface KeysAsidePanelProps {
  totalKeys: number;
  keysLoading: boolean;
  selectedKey: TranslationKey | null;
  selectedKeyId?: string | null;
  keyLoading?: boolean;
  projectId: string;
  availableTags?: string[];
  onKeyDeleted?: () => void;
  currentLanguage?: Language | null;
  currentLanguageValue?: string;
  defaultLanguage?: Language | null;
  defaultLanguageValue?: string;
}

/**
 * Component for managing a selected translation key
 */
export const KeysAsidePanel: FC<KeysAsidePanelProps> = ({
  totalKeys,
  keysLoading,
  selectedKey,
  selectedKeyId,
  keyLoading = false,
  projectId,
  availableTags = [],
  onKeyDeleted,
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  let content: React.ReactNode | null = null;
  let title = "Suggestions";

  if (selectedKeyId && totalKeys > 0) {
    title = "Key Management";
    content = (
      <KeyManagement
        selectedKey={selectedKey}
        keyLoading={keyLoading}
        projectId={projectId}
        availableTags={availableTags}
        onKeyDeleted={onKeyDeleted}
        currentLanguage={currentLanguage}
        currentLanguageValue={currentLanguageValue}
        defaultLanguage={defaultLanguage}
        defaultLanguageValue={defaultLanguageValue}
      />
    );
  } else if (!selectedKeyId && totalKeys > 0) {
    content = (
      <AutopilotCard
        title="Tip"
        isDisabled
        description="Click on any translation key from the list to view and manage it."
      />
    );
  }

  if (totalKeys === 0) {
    content = (
      <AutopilotCard
        title="Tip"
        isDisabled
        description="No translation keys yet. Create one or import existing translations."
      />
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 border-b h-12 box-border">
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      <div className="flex-1 overflow-auto p-4">{content}</div>
    </div>
  );
};
