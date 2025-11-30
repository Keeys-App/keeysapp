import { type FC } from 'react';

interface ColorChangeContentProps {
  oldValue?: string;
  newValue?: string;
}

/**
 * Content component for color change actions
 */
export const ColorChangeContent: FC<ColorChangeContentProps> = ({
  oldValue,
  newValue,
}) => {
  return (
    <div className="flex items-center gap-2 mt-1">
      {oldValue ? (
        <div className="flex items-center gap-1.5">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: oldValue }}
          />
          <span className="font-mono text-xs text-muted-foreground">
            {oldValue}
          </span>
        </div>
      ) : null}
      {oldValue && newValue ? (
        <span className="text-muted-foreground">→</span>
      ) : null}
      {newValue ? (
        <div className="flex items-center gap-1.5">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: newValue }}
          />
          <span className="font-mono text-xs font-medium text-foreground">
            {newValue}
          </span>
        </div>
      ) : null}
    </div>
  );
};

