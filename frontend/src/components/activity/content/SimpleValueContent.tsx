import { type FC } from 'react';

interface SimpleValueContentProps {
  oldValue?: string;
  newValue?: string;
}

/**
 * Content component for simple value display without diff
 */
export const SimpleValueContent: FC<SimpleValueContentProps> = ({
  oldValue,
  newValue,
}) => {
  if (!newValue && !oldValue) {
    return null;
  }

  return (
    <div className="text-sm">
      <span className="font-medium text-foreground">
        {newValue || oldValue}
      </span>
    </div>
  );
};

