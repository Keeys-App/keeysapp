import { useState, type FC } from "react";
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
}

/**
 * Form component for editing translation value
 */
export const TranslationEditForm: FC<TranslationEditFormProps> = ({
  value,
  direction = "ltr",
  onChange,
  onSave,
  onCancel,
  hasChanges,
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

  return (
    <div dir={direction}>
      <Textarea
        className="bg-background"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onClick={(e) => e.stopPropagation()}
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

