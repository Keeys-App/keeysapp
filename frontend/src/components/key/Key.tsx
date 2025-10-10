import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TranslationEditor } from "./TranslationEditor";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";

interface KeyProps {
  keyData: TranslationKey;
  projectId: string;
  projectLanguages: (Language | LanguageWithLocale)[];
  isSelected?: boolean;
  onSelect?: (key: TranslationKey) => void;
}

/**
 * Component for displaying a single translation key with its translations
 */
export function Key({ 
  keyData, 
  projectId, 
  projectLanguages,
  isSelected = false,
  onSelect,
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
      <div className="border-r relative">
        <div className="font-mono text-sm break-words sticky bg-background top-[2px] z-10 py-2 px-4">
          <span className={`transition-colors px-1 ${
            isSelected ? 'bg-primary/10 text-primary py-0.5 rounded' : ''
          }`}>
            {keyData.key}
          </span>
        </div>
        {keyData.description ? (
          <p className="text-sm text-muted-foreground px-4 py-2">{keyData.description}</p>
        ) : null}
      </div>
      <div className="flex flex-col">
        <div className="">
          {projectLanguages.map((language) => {
            return (
              <div
                key={language.code}
                className="grid grid-cols-[120px_1fr] even:bg-muted/50 border-b"
              >
                <div className="flex flex-col border-r p-2">
                  <div className="text-sm">{language.name}</div>
                  <div className="text-muted-foreground text-xs">
                    {'locale' in language ? (
                      language.locale
                    ) : (
                      language.code
                    )}
                  </div>
                </div>
                <div className="text-sm p-2">
                  <TranslationEditor
                    keyData={keyData}
                    language={language}
                    currentValue={
                      keyData.translations.find(
                        (t) => t.language === language.code
                      )?.value || ""
                    }
                    projectId={projectId}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
