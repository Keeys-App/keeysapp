import { type FC } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useSavingStore } from "@/stores";

interface TranslationEditFormProps {
  value: string;
  direction?: "ltr" | "rtl";
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  hasChanges: boolean;
  defaultLanguageValue?: string;
}

/**
 * Form component for editing translation value
 * Keyboard shortcuts:
 * - Esc: Cancel
 * - Cmd+Enter (Mac) / Ctrl+Enter (Windows/Linux): Save
 */
export const TranslationEditForm: FC<TranslationEditFormProps> = ({
  value,
  direction = "ltr",
  onChange,
  onSave,
  onCancel,
  hasChanges,
  defaultLanguageValue,
}) => {
  const { isSaving } = useSavingStore();

  const handleSaveClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSave();
  };

  const handleCancelClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCancel();
  };

  const handleCopyFromDefault = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (defaultLanguageValue) {
      onChange(defaultLanguageValue);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Esc - Cancel
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      onCancel();
      return;
    }

    // Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) - Save
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      e.stopPropagation();
      if (hasChanges && !isSaving) {
        onSave();
      }
      return;
    }
  };

  return (
    <div dir={direction}>
      <Textarea
        className="bg-background"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
        disabled={isSaving}
        rows={3}
        autoFocus
      />
      <div className="flex gap-2 mt-2">
        <Button
          onClick={handleSaveClick}
          disabled={isSaving || !hasChanges}
          variant="default"
          size="sm"
        >
          Save
        </Button>
        {defaultLanguageValue ? (
          <Button
            onClick={handleCopyFromDefault}
            disabled={isSaving}
            variant="outline"
            size="sm"
          >
            Copy from default
          </Button>
        ) : null}
        <Button
          onClick={handleCancelClick}
          disabled={isSaving}
          variant="outline"
          size="sm"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
};

