import type { FC } from 'react';
import { Check } from 'lucide-react';
import { DEFAULT_PROJECT_COLORS, getColorName } from '@/types/project';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  colors?: string[];
  disabled?: boolean;
}

/**
 * ColorPicker component - displays a palette of color options.
 * Shows a check icon on the selected color and color name in tooltip.
 */
export const ColorPicker: FC<ColorPickerProps> = ({
  value,
  onChange,
  colors = DEFAULT_PROJECT_COLORS,
  disabled = false,
}) => {
  return (
    <TooltipProvider>
      <div className="flex gap-2 flex-wrap">
        {colors.map((c) => {
          const isSelected = value === c;
          const colorName = getColorName(c);
          return (
            <Tooltip key={c}>
              <TooltipTrigger asChild>
                <button
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
              </TooltipTrigger>
              <TooltipContent>
                <p>{colorName || c}</p>
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </TooltipProvider>
  );
};

