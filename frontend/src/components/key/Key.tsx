import { memo } from "react";
import { TranslationEditor } from "./TranslationEditor";
import { ReviewStatusButton } from "./ReviewStatusButton";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";
import { Badge } from "../ui";

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
        className="border-b grid grid-cols-[minmax(300px,300px)_minmax(300px,3fr)] relative cursor-pointer"
        onClick={handleClick}
      >
        <div className="border-r -mr-px relative">
          <div className="font-mono text-sm break-words sticky bg-background top-[2px] z-10 py-2 px-4">
            <span
              className={`transition-colors ${
                isSelected ? "bg-primary/10 text-primary py-0.5 rounded" : ""
              }`}
            >
              {keyData.key}
            </span>
          </div>
          {keyData.description ? (
            <p className="text-sm break-words text-muted-foreground px-4 py-2">
              {keyData.description}
            </p>
          ) : null}
        </div>
        <div className="flex flex-col">
          <div>
            {projectLanguages.map((language) => {
              const translation = keyData.translations.find(
                (t) => t.language === language.code
              );
              const translationValue = translation?.value || "";
              const hasTranslation = translationValue.trim() !== "";

              return (
                <div
                  key={language.code}
                  className="group grid grid-cols-[120px_1fr] even:bg-muted/50 border-b -mb-px"
                >
                  <div className="border-r -mr-px p-2 grid grid-rows-[auto_1fr] gap-1">
                    <div className="text-sm flex items-center gap-1.5">
                      <span>{language.name}</span>
                      {"default" in language && language.default ? (
                        <Badge variant="outline" className="text-xs">
                          Default
                        </Badge>
                      ) : null}
                    </div>
                    <div className="flex items-end justify-between">
                      <div className="text-muted-foreground text-xs">
                        {"locale" in language ? language.locale : language.code}
                      </div>
                      <div className="relative top-[5px] right-[-3px]">
                        {hasTranslation ? (
                          <ReviewStatusButton
                            keyId={keyData.id}
                            language={language.code}
                            reviewStatus={
                              translation?.reviewStatus || "NOT_REVIEWED"
                            }
                            projectId={projectId}
                          />
                        ) : null}
                      </div>
                    </div>
                  </div>
                  <div className="text-sm p-2">
                    <TranslationEditor
                      keyData={keyData}
                      language={language}
                      currentValue={translationValue}
                      projectId={projectId}
                      isEditing={editingLanguage === language.code}
                      onEditingChange={(editing) => {
                        onEditingLanguageChange(editing ? language.code : null);
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
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
