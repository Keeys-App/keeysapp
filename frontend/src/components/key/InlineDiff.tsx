import { type FC, useMemo } from 'react';
import { diffWords } from 'diff';

interface InlineDiffProps {
  oldValue: string;
  newValue: string;
  language?: string;
}

/**
 * Component for displaying inline word-level diff with highlighted changes
 */
export const InlineDiff: FC<InlineDiffProps> = ({ oldValue, newValue, language }) => {
  const diffParts = useMemo(() => {
    return diffWords(oldValue, newValue);
  }, [oldValue, newValue]);

  // Check if this is a creation (no old value) or deletion (no new value)
  const isCreation = !oldValue && newValue;
  const isDeletion = oldValue && !newValue;

  return (
    <div className="mt-2 space-y-1">
      {language ? (
        <div className="text-xs text-muted-foreground/70">
          Language: <span className="font-mono bg-muted px-1.5 py-0.5 rounded">{language}</span>
        </div>
      ) : null}
      
      <div className="bg-muted/50 border border-border rounded px-3 py-2 text-sm font-mono break-words leading-relaxed">
        {isCreation ? (
          // Only new value - show all in green
          <span className="bg-green-500/20 text-green-700 dark:text-green-400 px-0.5 rounded">
            {newValue}
          </span>
        ) : isDeletion ? (
          // Only old value - show all in red with strikethrough
          <span className="bg-red-500/20 text-red-700 dark:text-red-400 line-through px-0.5 rounded">
            {oldValue}
          </span>
        ) : (
          // Show diff
          diffParts.map((part, index) => {
            if (part.added) {
              return (
                <span
                  key={index}
                  className="bg-green-500/20 text-green-700 dark:text-green-400 px-0.5 rounded"
                >
                  {part.value}
                </span>
              );
            }
            
            if (part.removed) {
              return (
                <span
                  key={index}
                  className="bg-red-500/20 text-red-700 dark:text-red-400 line-through px-0.5 rounded"
                >
                  {part.value}
                </span>
              );
            }
            
            return <span key={index}>{part.value}</span>;
          })
        )}
      </div>
    </div>
  );
};

