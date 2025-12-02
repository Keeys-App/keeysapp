import { type FC } from 'react';
import type { BatchImportExtraData } from '@/types/activity';

interface BatchImportContentProps {
  extraData: BatchImportExtraData;
  language?: string;
}

/**
 * Content component for displaying batch import statistics
 */
export const BatchImportContent: FC<BatchImportContentProps> = ({
  extraData,
  language,
}) => {
  const { created_keys, updated_keys, total_processed, error_count, translations_count } = extraData;

  const parts: string[] = [];

  if (created_keys > 0) {
    parts.push(`${created_keys} created`);
  }

  if (updated_keys > 0) {
    parts.push(`${updated_keys} updated`);
  }

  if (translations_count && translations_count > 0) {
    parts.push(`${translations_count} translations`);
  }

  if (error_count > 0) {
    parts.push(`${error_count} failed`);
  }

  return (
    <div className="text-sm space-y-1">
      <div className="flex items-center gap-2">
        <span className="font-medium text-foreground">
          {total_processed} keys imported
        </span>
        {language ? (
          <span className="text-xs px-1.5 py-0.5 bg-muted rounded">
            {language}
          </span>
        ) : null}
      </div>
      {parts.length > 0 ? (
        <div className="text-muted-foreground">
          {parts.join(', ')}
        </div>
      ) : null}
    </div>
  );
};

