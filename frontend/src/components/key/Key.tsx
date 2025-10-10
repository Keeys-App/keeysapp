import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TranslationEditor } from "./TranslationEditor";
import type { TranslationKey } from "@/types/translationKey";
import type { Language } from "@/types/project";

interface KeyProps {
  keyData: TranslationKey;
  projectId: string;
  projectLanguages: Language[];
}

/**
 * Component for displaying a single translation key with its translations
 */
export function Key({ keyData, projectId, projectLanguages }: KeyProps) {
  return (
    <div className="border-b grid grid-cols-[minmax(300px,1fr)_minmax(300px,3fr)]">
      <div className="border-r py-2 px-4 ">
        <div className="font-mono">{keyData.key}</div>
        {keyData.description ? (
          <p className="text-sm text-muted-foreground">{keyData.description}</p>
        ) : null}
      </div>
      <div className="flex flex-col">
        <div className="">
          {projectLanguages.map((language) => {
            return (
              <div
                key={language.code}
                className="grid grid-cols-[120px_1fr] even:bg-muted border-b last:border-b-0"
              >
                <div className="flex flex-col border-r p-2">
                  <div className="">{language.name}</div>
                  <div className="text-muted-foreground text-sm">
                    {language.code}
                  </div>
                </div>
                <div className="text-sm p-2">
                  <TranslationEditor
                    keyId={keyData.id}
                    language={language.code}
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
