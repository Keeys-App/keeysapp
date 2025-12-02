import type { TranslationTextEditorRef } from "./TranslationTextEditor";
import { Fragment, type FC, useMemo, useCallback, useRef, useEffect } from "react";
import type { Language, LanguageWithLocale } from "@/types/project";
import { Badge } from "../ui";
import { TranslationTextEditor } from "./TranslationTextEditor";
import { Button } from "@/components/ui/button";
import { useSavingStore } from "@/stores";

type PluralForm = "zero" | "one" | "two" | "few" | "many" | "other";
type PluralValue = Partial<Record<PluralForm, string>>;

interface PluralEditorProps {
  language: Language | LanguageWithLocale;
  value: string;
  direction?: "ltr" | "rtl";
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  hasChanges: boolean;
  isEditing: boolean;
  onEditingChange: (editing: boolean) => void;
  defaultLanguageValue?: string;
  markReviewedOnSave?: boolean;
  onMarkReviewedOnSaveChange?: (value: boolean) => void;
  onEditorReady?: (ref: TranslationTextEditorRef | null) => void;
}

/**
 * Single plural form view component (read-only)
 */
interface PluralFormViewProps {
  form: PluralForm;
  value: string;
  direction: "ltr" | "rtl";
  onEdit: () => void;
}

const PluralFormView: FC<PluralFormViewProps> = ({
  form,
  value,
  direction,
  onEdit,
}) => {
  return (
    <Fragment>
      <div className="capitalize text-muted-foreground border-b p-2 border-r flex items-start">
        <Badge className="capitalize">{form}</Badge>
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
    </Fragment>
  );
};

/**
 * Single plural form editor component
 */
interface PluralFormEditorProps {
  form: PluralForm;
  value: string;
  direction: "ltr" | "rtl";
  onChange: (value: string) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLDivElement>) => void;
  autoFocus: boolean;
  onEditorReady?: (ref: TranslationTextEditorRef | null) => void;
}

const PluralFormEditor: FC<PluralFormEditorProps> = ({
  form,
  value,
  direction,
  onChange,
  onKeyDown,
  autoFocus,
  onEditorReady,
}) => {
  const editorRef = useRef<TranslationTextEditorRef | null>(null);
  const onEditorReadyRef = useRef(onEditorReady);

  // Update ref when callback changes
  useEffect(() => {
    onEditorReadyRef.current = onEditorReady;
  }, [onEditorReady]);

  // Callback ref that notifies parent when ref is set
  const handleRef = useCallback((node: TranslationTextEditorRef | null) => {
    if (editorRef.current !== node) {
      editorRef.current = node;
      if (onEditorReadyRef.current) {
        onEditorReadyRef.current(node);
      }
    }
  }, []);

  return (
    <Fragment>
      <div className="capitalize text-muted-foreground border-b p-2 border-r flex items-start pt-2">
        <Badge className="capitalize">{form}</Badge>
      </div>
      <div className="border-b">
        <TranslationTextEditor
          ref={handleRef}
          value={value}
          onChange={onChange}
          onKeyDown={onKeyDown}
          direction={direction}
          disabled={false}
          autoFocus={autoFocus}
        />
      </div>
    </Fragment>
  );
};

/**
 * Parse plural value from string (JSON) to object
 */
const parsePluralValue = (value: string): PluralValue => {
  if (!value) {
    return {};
  }
  try {
    const parsed = JSON.parse(value);
    if (typeof parsed === "object" && parsed !== null) {
      return parsed as PluralValue;
    }
    return {};
  } catch {
    // If not valid JSON, return empty object
    return {};
  }
};

/**
 * Serialize plural value object to JSON string
 */
const serializePluralValue = (obj: PluralValue): string => {
  // Remove empty values
  const filtered = Object.fromEntries(
    Object.entries(obj).filter(([, v]) => v !== "")
  );
  if (Object.keys(filtered).length === 0) {
    return "";
  }
  return JSON.stringify(filtered);
};

export const PluralEditor: FC<PluralEditorProps> = ({
  language,
  value,
  direction = "ltr",
  onChange,
  onSave,
  onCancel,
  hasChanges,
  isEditing,
  onEditingChange,
  onEditorReady,
}) => {
  const { isSaving } = useSavingStore();
  const onEditorReadyRef = useRef(onEditorReady);
  const firstFormRef = useRef<TranslationTextEditorRef | null>(null);

  // Update ref when callback changes
  useEffect(() => {
    onEditorReadyRef.current = onEditorReady;
  }, [onEditorReady]);

  // Parse current value as plural object
  const pluralValue = useMemo(() => parsePluralValue(value), [value]);

  // Handle change for a specific plural form
  const handleFormChange = useCallback(
    (form: PluralForm, formValue: string) => {
      const newPluralValue = {
        ...pluralValue,
        [form]: formValue,
      };
      onChange(serializePluralValue(newPluralValue));
    },
    [pluralValue, onChange]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
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
    },
    [onCancel, onSave, hasChanges, isSaving]
  );

  const handleSaveClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSave();
  };

  const handleCancelClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCancel();
  };

  const handleEdit = () => {
    onEditingChange(true);
  };

  // Handle first form editor ready - notify parent
  const handleFirstFormEditorReady = useCallback(
    (ref: TranslationTextEditorRef | null) => {
      if (firstFormRef.current !== ref) {
        firstFormRef.current = ref;
        if (onEditorReadyRef.current) {
          onEditorReadyRef.current(ref);
        }
      }
    },
    []
  );

  // View mode - show all forms as read-only
  if (!isEditing) {
    return (
      <div className="bg-background">
        <div className="grid grid-cols-[auto_1fr] -mb-[1px]">
          {language.pluralForms.map((form) => {
            const formValue = pluralValue[form] || "";
            return (
              <PluralFormView
                key={form}
                form={form}
                value={formValue}
                direction={direction}
                onEdit={handleEdit}
              />
            );
          })}
        </div>
      </div>
    );
  }

  // Edit mode - show all forms as editable
  return (
    <div className="bg-background">
      <div className="grid grid-cols-[auto_1fr] -mb-[1px]">
        {language.pluralForms.map((form, index) => {
          const formValue = pluralValue[form] || "";
          const isFirst = index === 0;

          return (
            <PluralFormEditor
              key={form}
              form={form}
              value={formValue}
              direction={direction}
              onChange={(v) => handleFormChange(form, v)}
              onKeyDown={handleKeyDown}
              autoFocus={isFirst}
              onEditorReady={isFirst ? handleFirstFormEditorReady : undefined}
            />
          );
        })}
      </div>
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
        </div>
        <div className="flex gap-2 items-center">
          <Badge variant="outline">
            {Object.values(pluralValue).join("").length}
          </Badge>
        </div>
      </div>
    </div>
  );
};
