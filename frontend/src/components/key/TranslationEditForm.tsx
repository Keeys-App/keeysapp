import { type FC, useState, useEffect } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useSavingStore } from "@/stores";
import { Badge } from "../ui";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Ellipsis, Settings, TriangleAlert } from "lucide-react";

interface TranslationEditFormProps {
  value: string;
  direction?: "ltr" | "rtl";
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  hasChanges: boolean;
  defaultLanguageValue?: string;
  markReviewedOnSave?: boolean;
  onMarkReviewedOnSaveChange?: (value: boolean) => void;
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
  markReviewedOnSave: externalMarkReviewedOnSave,
  onMarkReviewedOnSaveChange,
}) => {
  const { isSaving } = useSavingStore();

  // Load initial value from localStorage or prop
  const [markReviewedOnSave, setMarkReviewedOnSave] = useState(() => {
    if (externalMarkReviewedOnSave !== undefined) {
      return externalMarkReviewedOnSave;
    }
    const stored = localStorage.getItem("markReviewedOnSave");
    return stored ? JSON.parse(stored) : false;
  });

  // Save to localStorage when changed
  useEffect(() => {
    localStorage.setItem(
      "markReviewedOnSave",
      JSON.stringify(markReviewedOnSave)
    );
    if (onMarkReviewedOnSaveChange) {
      onMarkReviewedOnSaveChange(markReviewedOnSave);
    }
  }, [markReviewedOnSave, onMarkReviewedOnSaveChange]);

  // Sync with external prop if provided
  useEffect(() => {
    if (
      externalMarkReviewedOnSave !== undefined &&
      externalMarkReviewedOnSave !== markReviewedOnSave
    ) {
      setMarkReviewedOnSave(externalMarkReviewedOnSave);
    }
  }, [externalMarkReviewedOnSave]);

  const handleMarkReviewedToggle = () => {
    setMarkReviewedOnSave(!markReviewedOnSave);
  };

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
    <div className="bg-background">
      <Textarea
        dir={direction}
        className="bg-background rounded-none border-none focus-visible:ring-0 focus-visible:ring-offset-0 p-2 shadow-none"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
        disabled={isSaving}
        rows={3}
        autoFocus
      />
      <div className="flex gap-2 p-2 border-t">
        <div className="flex-1 flex gap-2 items-center">
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
          {defaultLanguageValue && !value ? (
            <Button
              onClick={handleCopyFromDefault}
              disabled={isSaving}
              variant="ghost"
              size="sm"
            >
              Copy from default
            </Button>
          ) : null}
        </div>
        <div className="flex gap-2 items-center">
          <TriangleAlert className="!h-3.5 !w-3.5 text-orange-500" />

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge variant="outline">{value.length}</Badge>
              </TooltipTrigger>
              <TooltipContent>
                <p>Character count</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={(e) => e.stopPropagation()}
              >
                <Ellipsis className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuCheckboxItem
                checked={markReviewedOnSave}
                onCheckedChange={handleMarkReviewedToggle}
                onSelect={(e) => e.preventDefault()}
              >
                Mark reviewed on save
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
};
