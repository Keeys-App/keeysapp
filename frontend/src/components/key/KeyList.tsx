import { useQuery } from "@apollo/client";
import { GET_PROJECT_KEYS } from "@/graphql/keys";
import type { TranslationKey } from "@/types/translationKey";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { EmptyKeys } from "./EmptyKeys";
import { Key } from "./Key";
import { KeyControls } from "./KeyControls";
import type { Language } from "@/types/project";
import { getUserFriendlyErrorMessage } from "@/lib/utils";

interface KeyListProps {
  projectId: string;
  projectLanguages: Language[];
  onCreateKey: () => void;
}

export function KeyList({
  projectId,
  projectLanguages,
  onCreateKey,
}: KeyListProps) {
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
    const errorMessage = getUserFriendlyErrorMessage(error, 'Failed to load translation keys. Please try again.');
    return (
      <Alert variant="destructive">
        <AlertDescription>
          {errorMessage}
        </AlertDescription>
      </Alert>
    );
  }

  const keys: TranslationKey[] = data?.projectKeys || [];

  if (keys.length === 0) {
    return (
      <div className="flex flex-col h-full min-h-[50vh]">
        <EmptyKeys projectId={projectId} onCreateKey={onCreateKey} />
      </div>
    );
  }

  return (
    <div>
      <KeyControls projectId={projectId} onCreateKey={onCreateKey} />
      {keys.map((key) => (
        <Key
          key={key.id}
          keyData={key}
          projectId={projectId}
          projectLanguages={projectLanguages}
        />
      ))}
    </div>
  );
}
