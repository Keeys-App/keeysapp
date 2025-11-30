import { type FC } from 'react';
import { InlineDiff } from '@/components/key/InlineDiff';

interface DiffContentProps {
  oldValue?: string;
  newValue?: string;
  language?: string;
}

/**
 * Content component for displaying diff between old and new values
 */
export const DiffContent: FC<DiffContentProps> = ({
  oldValue,
  newValue,
  language,
}) => {
  return (
    <InlineDiff
      oldValue={oldValue || ''}
      newValue={newValue || ''}
      language={language || undefined}
    />
  );
};

