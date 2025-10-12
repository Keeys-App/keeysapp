import { type FC, type KeyboardEvent } from "react";
import { Textarea } from "@/components/ui/textarea";

interface TranslationTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  onKeyDown?: (e: KeyboardEvent<HTMLTextAreaElement>) => void;
  direction?: "ltr" | "rtl";
  disabled?: boolean;
  autoFocus?: boolean;
  rows?: number;
}

/**
 * Translation text editor component
 * Can be extended in the future with rich text editing, autocomplete, etc.
 */
export const TranslationTextEditor: FC<TranslationTextEditorProps> = ({
  value,
  onChange,
  onKeyDown,
  direction = "ltr",
  disabled = false,
  autoFocus = true,
  rows = 3,
}) => {
  return (
    <Textarea
      dir={direction}
      className="bg-background rounded-none border-none focus-visible:ring-0 focus-visible:ring-offset-0 p-2 shadow-none"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onClick={(e) => e.stopPropagation()}
      onKeyDown={onKeyDown}
      disabled={disabled}
      rows={rows}
      autoFocus={autoFocus}
    />
  );
};

