import { type FC } from 'react';
import { getColorName } from '@/types/project';

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
  const oldColorName = getColorName(oldValue);
  const newColorName = getColorName(newValue);

  return (
    <div className="flex items-center gap-2 mt-1">
      {oldValue ? (
        <div className="flex items-center gap-1.5">
          <div
            className="w-3 h-3 rounded"
            style={{ backgroundColor: oldValue }}
          />
          <span className="text-xs text-muted-foreground">
            {oldColorName || oldValue}
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
          <span className="text-xs font-medium text-foreground">
            {newColorName || newValue}
          </span>
        </div>
      ) : null}
    </div>
  );
};

