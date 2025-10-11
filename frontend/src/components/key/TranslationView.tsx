import { memo } from "react";

interface TranslationViewProps {
  value: string;
  direction?: "ltr" | "rtl";
  onEdit: (e: React.MouseEvent) => void;
}

/**
 * Component for displaying translation value in view mode
 * Shows the translation text or empty placeholder, clickable to edit
 */
export const TranslationView = memo(function TranslationView({
  value,
  direction,
  onEdit,
}: TranslationViewProps) {
  return (
    <div
      dir={direction}
      className="cursor-pointer hover:bg-muted/70 rounded transition-colors min-h-[2rem]"
      onClick={onEdit}
    >
      <div className="p-[1px]">
        {value ? (
          <span className="whitespace-pre-wrap">{value}</span>
        ) : (
          <span className="text-muted-foreground text-sm">
            &lt;Empty&gt;
          </span>
        )}
      </div>
    </div>
  );
});

