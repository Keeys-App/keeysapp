import { useQuery } from '@apollo/client';
import { GET_PROJECT_KEYS } from '@/graphql/keys';
import type { TranslationKey } from '@/types/translationKey';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface KeyListProps {
  projectId: string;
}

export function KeyList({ projectId }: KeyListProps) {
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
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">
            No keys found. Create your first translation key.
          </p>
        </CardContent>
      </Card>
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
                {key.translations.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No translations yet</p>
                ) : (
                  <div className="space-y-2">
                    {key.translations.map((translation) => {
                      return (
                        <div
                          key={translation.language}
                          className="flex gap-4 items-start"
                        >
                          <span className="font-medium text-sm w-12 shrink-0">
                            {translation.language}
                          </span>
                          <span className="text-sm flex-1">
                            {translation.value}
                          </span>
                        </div>
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

