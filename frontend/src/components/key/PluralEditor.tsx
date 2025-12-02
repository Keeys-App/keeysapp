import type { TranslationTextEditorRef } from "./TranslationTextEditor";
import { type FC, useMemo, useCallback, useRef, useEffect, useState } from "react";
import type { Language, LanguageWithLocale } from "@/types/project";
import { Badge } from "../ui";
import { useTranslationEditor } from "@/contexts";
import { TranslationView } from "./TranslationView";
import { TranslationEditForm } from "./TranslationEditForm";

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
  // Track which specific form is being edited
  const [editingFormState, setEditingFormState] = useState<PluralForm | null>(null);
  const onEditorReadyRef = useRef(onEditorReady);
  const { setEditingPluralForm } = useTranslationEditor();

  // Wrapper to sync local state with context
  const setEditingForm = useCallback((form: PluralForm | null) => {
    setEditingFormState(form);
    setEditingPluralForm(form);
  }, [setEditingPluralForm]);

  // Update ref when callback changes
  useEffect(() => {
    onEditorReadyRef.current = onEditorReady;
  }, [onEditorReady]);

  // Sync editingForm with isEditing prop
  useEffect(() => {
    if (!isEditing && editingFormState !== null) {
      setEditingForm(null);
    }
  }, [isEditing, editingFormState, setEditingForm]);
  
  // Clear plural form in context on unmount
  useEffect(() => {
    return () => {
      setEditingPluralForm(null);
    };
  }, [setEditingPluralForm]);

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

  const handleEditForm = useCallback(
    (form: PluralForm) => {
      setEditingForm(form);
      onEditingChange(true);
    },
    [onEditingChange, setEditingForm]
  );

  const handleSave = useCallback(() => {
    onSave();
    setEditingForm(null);
  }, [onSave, setEditingForm]);

  const handleCancel = useCallback(() => {
    onCancel();
    setEditingForm(null);
  }, [onCancel, setEditingForm]);

  // Handle editor ready - notify parent
  const handleEditorReady = useCallback(
    (ref: TranslationTextEditorRef | null) => {
      if (onEditorReadyRef.current) {
        onEditorReadyRef.current(ref);
      }
    },
    []
  );

  return (
    <div className="bg-background">
      <div className="grid grid-cols-[auto_1fr] -mb-[1px]">
        {language.pluralForms.map((form) => {
          const formValue = pluralValue[form] || "";
          const isFormEditing = editingFormState === form;
          const formLabel = <Badge className="capitalize">{form}</Badge>;

          if (isFormEditing) {
            return (
              <TranslationEditForm
                key={form}
                label={formLabel}
                value={formValue}
                direction={direction}
                onChange={(v) => handleFormChange(form, v)}
                onSave={handleSave}
                onCancel={handleCancel}
                hasChanges={hasChanges}
                onEditorReady={handleEditorReady}
                compact
              />
            );
          }

          return (
            <TranslationView
              key={form}
              label={formLabel}
              value={formValue}
              direction={direction}
              onEdit={() => handleEditForm(form)}
            />
          );
        })}
      </div>
    </div>
  );
};
