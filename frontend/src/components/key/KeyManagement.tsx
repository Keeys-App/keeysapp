import type { FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";

interface KeyManagementProps {
  selectedKey: TranslationKey | null;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectId: string;
}

/**
 * Component for managing a selected translation key
 */
export const KeyManagement: FC<KeyManagementProps> = ({
  selectedKey,
  projectLanguages,
  projectId,
}) => {
  if (!selectedKey) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center">
          <p className="text-lg">Select a key to manage</p>
          <p className="text-sm mt-2">
            Click on any translation key from the list to view and manage it
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4">
        <h2 className="text-lg font-semibold">Key Management</h2>
        <p className="text-sm text-muted-foreground font-mono">{selectedKey.key}</p>
      </div>
      <div className="flex-1 p-4">
        <p className="text-muted-foreground">Management panel content will be here</p>
      </div>
    </div>
  );
};

