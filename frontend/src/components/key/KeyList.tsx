import { useQuery } from '@apollo/client';
import { GET_PROJECT_KEYS } from '@/graphql/keys';
import type { TranslationKey } from '@/types/translationKey';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { TranslationEditor } from './TranslationEditor';
import { EmptyKeys } from './EmptyKeys';

interface KeyListProps {
  projectId: string;
  projectLanguages: string[];
  onCreateKey: () => void;
}

export function KeyList({ projectId, projectLanguages, onCreateKey }: KeyListProps) {
  const { data, loading, error } = useQuery(GET_PROJECT_KEYS, {
    variables: { projectId },
    skip: !projectId,
  });

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load keys: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  const keys: TranslationKey[] = data?.projectKeys || [];

  if (keys.length === 0) {
    return (
      <div className="flex flex-col h-full min-h-[50vh]">
        <EmptyKeys onCreateKey={onCreateKey} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {keys.map((key) => {
        return (
          <Card key={key.id}>
            <CardHeader>
              <CardTitle className="text-lg font-mono">{key.key}</CardTitle>
              {key.description ? (
                <p className="text-sm text-muted-foreground">{key.description}</p>
              ) : null}
            </CardHeader>
            <CardContent>
              <div className="border-t pt-4">
                {projectLanguages.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No languages configured in project</p>
                ) : (
                  <div className="space-y-2">
                    {projectLanguages.map((language) => {
                      const translation = key.translations.find(t => t.language === language);
                      return (
                        <TranslationEditor
                          key={language}
                          keyId={key.id}
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
      })}
    </div>
  );
}

