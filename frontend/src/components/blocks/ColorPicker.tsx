import type { FC } from 'react';
import { Check } from 'lucide-react';
import { DEFAULT_PROJECT_COLORS } from '@/types/project';
import { cn } from '@/lib/utils';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  colors?: string[];
  disabled?: boolean;
}

/**
 * ColorPicker component - displays a palette of color options.
 * Shows a check icon on the selected color.
 */
export const ColorPicker: FC<ColorPickerProps> = ({
  value,
  onChange,
  colors = DEFAULT_PROJECT_COLORS,
  disabled = false,
}) => {
  return (
    <div className="flex gap-2 flex-wrap">
      {colors.map((c) => {
        const isSelected = value === c;
        return (
          <button
            key={c}
            type="button"
            onClick={() => {
              return onChange(c);
            }}
            disabled={disabled}
            className={cn(
              'w-8 h-8 rounded-lg transition-all flex items-center justify-center cursor-pointer hover:scale-110',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
              isSelected && 'scale-110'
            )}
            style={{
              backgroundColor: c,
              border: isSelected ? '3px solid hsl(var(--primary))' : '2px solid hsl(var(--border))',
            }}
          >
            {isSelected ? (
              <Check className="h-4 w-4 text-white drop-shadow-md" strokeWidth={3} />
            ) : null}
          </button>
        );
      })}
    </div>
  );
};

