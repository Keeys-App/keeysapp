import { memo, type ReactNode } from "react";

interface TranslationViewProps {
  value: string;
  direction?: "ltr" | "rtl";
  onEdit: (e: React.MouseEvent) => void;
  /** Optional label to show on the left (e.g., plural form badge) */
  label?: ReactNode;
}

/**
 * Component for displaying translation value in view mode
 * Shows the translation text or empty placeholder, clickable to edit
 */
export const TranslationView = memo(function TranslationView({
  value,
  direction,
  onEdit,
  label,
}: TranslationViewProps) {
  // If label is provided, render in grid layout (for plural forms)
  if (label) {
    return (
      <>
        <div className="capitalize text-muted-foreground border-b p-2 border-r flex items-start">
          {label}
        </div>
        <div
          dir={direction}
          className="cursor-pointer border-b hover:bg-muted/70 transition-colors min-h-[2rem]"
          onClick={onEdit}
        >
          <div className="p-2">
            {value ? (
              <span className="whitespace-pre-wrap">{value}</span>
            ) : (
              <span className="text-muted-foreground text-sm">&lt;Empty&gt;</span>
            )}
          </div>
        </div>
      </>
    );
  }

  // Otherwise render just the content (for regular translations)
  return (
    <div
      dir={direction}
      className="cursor-pointer h-full hover:bg-muted/70 transition-colors min-h-[2rem]"
      onClick={onEdit}
    >
      <div className="p-2">
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
