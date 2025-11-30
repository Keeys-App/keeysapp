import { type FC } from 'react';

interface LanguageInfoContentProps {
  language: string;
}

/**
 * Content component for displaying language information
 */
export const LanguageInfoContent: FC<LanguageInfoContentProps> = ({
  language,
}) => {
  return (
    <div className="text-xs text-muted-foreground/70">
      Language:{' '}
      <span className="font-mono bg-muted px-1.5 py-0.5 rounded">
        {language}
      </span>
    </div>
  );
};

