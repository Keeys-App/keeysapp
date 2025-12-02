import type { TranslationTextEditorRef } from "./TranslationTextEditor";
import type { FC } from "react";
import type { Language, LanguageWithLocale } from "@/types/project";

interface PluralEditorProps {
  language: Language | LanguageWithLocale;
  value: string;
  direction?: "ltr" | "rtl";
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  hasChanges: boolean;
  defaultLanguageValue?: string;
  markReviewedOnSave?: boolean;
  onMarkReviewedOnSaveChange?: (value: boolean) => void;
  onEditorReady?: (ref: TranslationTextEditorRef | null) => void;
}

export const PluralEditor: FC<PluralEditorProps> = ({
  language,
  value,
  direction,
  onChange,
  onSave,
  onCancel,
  hasChanges,
  defaultLanguageValue,
  markReviewedOnSave,
  onMarkReviewedOnSaveChange,
  onEditorReady,
}) => {
  return (
    <div>
      {language.pluralForms.map((form) => {
        return <div key={form}>{form}</div>;
      })}
    </div>
  );
};
