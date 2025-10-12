import { memo } from "react";
import { TranslationEditor } from "./TranslationEditor";
import { LanguageHeader } from "./LanguageHeader";
import { KeyHeader } from "./KeyHeader";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";
import { cn } from "@/lib/utils";

interface KeyProps {
  keyData: TranslationKey;
  projectId: string;
  projectLanguages: (Language | LanguageWithLocale)[];
  isSelected?: boolean;
  onSelect?: (key: TranslationKey) => void;
  editingLanguage: string | null;
  onEditingLanguageChange: (language: string | null) => void;
}

/**
 * Component for displaying a single translation key with its translations
 */
export const Key = memo(
  function Key({
    keyData,
    projectId,
    projectLanguages,
    isSelected = false,
    onSelect,
    editingLanguage,
    onEditingLanguageChange,
  }: KeyProps) {
    const handleClick = () => {
      if (onSelect) {
        onSelect(keyData);
      }
    };

    return (
      <div
        className={cn(
          "border-b grid grid-cols-[220px_minmax(300px,3fr)] relative cursor-pointer transition-colors"
        )}
        onClick={handleClick}
      >
        <div className="border-r -mr-px relative">
          <KeyHeader
            keyName={keyData.key}
            description={keyData.description}
            isSelected={isSelected}
          />
        </div>
        <div className="flex flex-col">
          {projectLanguages.map((language) => (
            <div
              key={language.code}
              className="group grid grid-cols-[120px_1fr] even:bg-muted/50 border-b last:-mb-px"
            >
              <LanguageHeader
                language={language}
                translations={keyData.translations}
                keyId={keyData.id}
                projectId={projectId}
              />
              <TranslationEditor
                keyData={keyData}
                language={language}
                projectLanguages={projectLanguages}
                projectId={projectId}
                isEditing={editingLanguage === language.code}
                onEditingChange={(editing) => {
                  onEditingLanguageChange(editing ? language.code : null);
                }}
              />
            </div>
          ))}
        </div>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison function to prevent unnecessary re-renders
    // Only re-render if the key data actually changed
    if (
      prevProps.keyData.id !== nextProps.keyData.id ||
      prevProps.keyData.key !== nextProps.keyData.key ||
      prevProps.keyData.description !== nextProps.keyData.description ||
      prevProps.keyData.updatedAt !== nextProps.keyData.updatedAt ||
      prevProps.isSelected !== nextProps.isSelected ||
      prevProps.projectId !== nextProps.projectId ||
      prevProps.editingLanguage !== nextProps.editingLanguage
    ) {
      return false; // Re-render
    }

    // Check if translations changed (including reviewStatus)
    if (
      prevProps.keyData.translations.length !==
      nextProps.keyData.translations.length
    ) {
      return false; // Re-render
    }

    for (let i = 0; i < prevProps.keyData.translations.length; i++) {
      const prev = prevProps.keyData.translations[i];
      const next = nextProps.keyData.translations[i];

      if (
        prev.language !== next.language ||
        prev.value !== next.value ||
        prev.reviewStatus !== next.reviewStatus ||
        prev.updatedAt !== next.updatedAt
      ) {
        return false; // Re-render
      }
    }

    return true; // Don't re-render
  }
);
