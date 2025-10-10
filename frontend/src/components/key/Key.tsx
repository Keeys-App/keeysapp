import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TranslationEditor } from './TranslationEditor';
import type { TranslationKey } from '@/types/translationKey';

interface KeyProps {
  keyData: TranslationKey;
  projectId: string;
  projectLanguages: string[];
}

/**
 * Component for displaying a single translation key with its translations
 */
export function Key({ keyData, projectId, projectLanguages }: KeyProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-mono">{keyData.key}</CardTitle>
        {keyData.description ? (
          <p className="text-sm text-muted-foreground">{keyData.description}</p>
        ) : null}
      </CardHeader>
      <CardContent>
        <div className="border-t pt-4">
          {projectLanguages.length === 0 ? (
            <p className="text-sm text-muted-foreground">No languages configured in project</p>
          ) : (
            <div className="space-y-2">
              {projectLanguages.map((language) => {
                const translation = keyData.translations.find(t => t.language === language);
                return (
                  <TranslationEditor
                    key={language}
                    keyId={keyData.id}
                    language={language}
                    currentValue={translation?.value || ''}
                    projectId={projectId}
                  />
                );
              })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

