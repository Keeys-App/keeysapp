import { memo, useState } from "react";
import { ReviewStatusButton } from "./ReviewStatusButton";
import type { Language, LanguageWithLocale } from "@/types/project";
import type { Translation } from "@/types/translationKey";
import { cn } from "@/lib/utils";

interface LanguageHeaderProps {
  language: Language | LanguageWithLocale;
  translations: Translation[];
  keyId: string;
  projectId: string;
}

/**
 * Component for displaying language information in key translation table
 * Shows language name, code/locale, default language indicator and review status
 */
export const LanguageHeader = memo(function LanguageHeader({
  language,
  translations,
  keyId,
  projectId,
}: LanguageHeaderProps) {
  const [isReviewOpen, setIsReviewOpen] = useState(false);

  // Find translation for this language
  const translation = translations.find((t) => t.language === language.code);
  const translationValue = translation?.value || "";
  const hasTranslation = translationValue.trim() !== "";

  return (
    <div className="border-r -mr-px p-2 grid grid-rows-[auto_1fr] gap-1 relative">
      <div className="text-sm flex items-center gap-1.5">
        <span>{language.name}</span>
      </div>
      <div className="flex items-end justify-between">
        <div className="text-muted-foreground text-xs">
          {"locale" in language ? language.locale : language.code}
        </div>
        <div className="relative top-[1px] right-[-3px] h-5">
          {hasTranslation && (
            <div
              className={isReviewOpen ? "block" : "hidden group-hover:block"}
            >
              <ReviewStatusButton
                keyId={keyId}
                language={language.code}
                reviewStatus={translation?.reviewStatus || "NOT_REVIEWED"}
                projectId={projectId}
                onOpenChange={setIsReviewOpen}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
