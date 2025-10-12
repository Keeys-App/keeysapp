import { type FC, useState, useEffect, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { useSavingStore } from "@/stores";
import { Badge } from "../ui";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Ellipsis } from "lucide-react";
import { TranslationTextEditor } from "./TranslationTextEditor";

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

interface TextIssue {
  type: "leading_whitespace" | "trailing_whitespace";
  description: string;
}

/**
 * Check text for common issues
 */
const checkTextIssues = (text: string): TextIssue[] => {
  const issues: TextIssue[] = [];

  // Check for leading whitespace (space, tab, newline)
  if (text.length > 0 && /^[\s\n\t]/.test(text)) {
    const firstChar = text[0];
    let charType = "space";
    if (firstChar === "\n") {
      charType = "newline";
    } else if (firstChar === "\t") {
      charType = "tab";
    }
    issues.push({
      type: "leading_whitespace",
      description: `Text starts with ${charType}`,
    });
  }

  // Check for trailing whitespace (space, tab, newline)
  if (text.length > 0 && /[\s\n\t]$/.test(text)) {
    const lastChar = text[text.length - 1];
    let charType = "space";
    if (lastChar === "\n") {
      charType = "newline";
    } else if (lastChar === "\t") {
      charType = "tab";
    }
    issues.push({
      type: "trailing_whitespace",
      description: `Text ends with ${charType}`,
    });
  }

  return issues;
};

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

  // Check for text issues
  const textIssues = useMemo(() => checkTextIssues(value), [value]);

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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
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
      <TranslationTextEditor
        value={value}
        onChange={onChange}
        onKeyDown={handleKeyDown}
        direction={direction}
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
          {textIssues.length > 0 ? (
            <Popover>
              <PopoverTrigger asChild>
                <Badge className="cursor-pointer bg-destructive/10 text-destructive">
                  {textIssues.length} issues
                </Badge>
              </PopoverTrigger>
              <PopoverContent className="w-64" align="end">
                <div className="space-y-2">
                  <h2 className="font-medium">Translation Issues</h2>
                  <ul className="list-disc pl-4 text-sm">
                    {textIssues.map((issue, index) => (
                      <li key={index}>{issue.description}</li>
                    ))}
                  </ul>
                </div>
              </PopoverContent>
            </Popover>
          ) : null}

          <Badge variant="outline">{value.length}</Badge>

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
