import { type FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import { KeyManagement } from "./KeyManagement";
import type { Language } from "@/types/project";

interface KeysAsidePanelProps {
  totalKeys: number;
  keysLoading: boolean;
  selectedKey: TranslationKey | null;
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
  projectId,
  availableTags = [],
  onKeyDeleted,
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  let content: React.ReactNode | null = null;

  if (selectedKey && totalKeys > 0) {
    content = (
      <KeyManagement
        selectedKey={selectedKey}
        projectId={projectId}
        availableTags={availableTags}
        onKeyDeleted={onKeyDeleted}
        currentLanguage={currentLanguage}
        currentLanguageValue={currentLanguageValue}
        defaultLanguage={defaultLanguage}
        defaultLanguageValue={defaultLanguageValue}
      />
    );
  }

  if (!selectedKey && totalKeys > 0) {
    content = (
      <p className="text-muted-foreground text-sm p-4">
        Click on any translation key from the list to view and manage it.
      </p>
    );
  }

  if (totalKeys === 0) {
    content = (
      <p className="text-muted-foreground text-sm p-4">
        No translation keys found, create your first translation key to get
        started or import your existing translations.
      </p>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 border-b h-12 box-border">
        <h2 className="text-base font-semibold">
          {selectedKey?.key ? "Key Management" : "Activity"}
        </h2>
      </div>
      <div className="flex-1 overflow-auto">{content}</div>
    </div>
  );
};
