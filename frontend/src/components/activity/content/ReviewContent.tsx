import { type FC } from 'react';

interface ReviewContentProps {
  action: string;
  language?: string;
  newValue?: string;
}

/**
 * Content component for review actions (approve, reject, delete)
 */
export const ReviewContent: FC<ReviewContentProps> = ({
  action,
  language,
  newValue,
}) => {
  return (
    <>
      {language ? (
        <div className="text-xs text-muted-foreground/70 mb-1">
          Language:{' '}
          <span className="font-mono bg-muted px-1.5 py-0.5 rounded font-medium">
            {language.toUpperCase()}
          </span>
        </div>
      ) : null}
      {newValue && action !== 'REVIEW_DELETE' ? (
        <div className="text-sm whitespace-pre-wrap">{newValue}</div>
      ) : null}
    </>
  );
};

