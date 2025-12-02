import { createContext, useContext, useState, useCallback, type FC, type ReactNode } from "react";
import type { TranslationTextEditorRef } from "@/components/key/TranslationTextEditor";

type PluralForm = "zero" | "one" | "two" | "few" | "many" | "other";

interface TranslationEditorContextValue {
  editorRef: TranslationTextEditorRef | null;
  setEditorRef: (ref: TranslationTextEditorRef | null) => void;
  // Plural form being edited (null if not editing plural or editing non-plural key)
  editingPluralForm: PluralForm | null;
  setEditingPluralForm: (form: PluralForm | null) => void;
}

const TranslationEditorContext = createContext<TranslationEditorContextValue | null>(null);

export const TranslationEditorProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [editorRef, setEditorRef] = useState<TranslationTextEditorRef | null>(null);
  const [editingPluralForm, setEditingPluralFormState] = useState<PluralForm | null>(null);

  // Stable callback for setting plural form
  const setEditingPluralForm = useCallback((form: PluralForm | null) => {
    setEditingPluralFormState(form);
  }, []);

  return (
    <TranslationEditorContext.Provider value={{ 
      editorRef, 
      setEditorRef,
      editingPluralForm,
      setEditingPluralForm
    }}>
      {children}
    </TranslationEditorContext.Provider>
  );
};

export const useTranslationEditor = () => {
  const context = useContext(TranslationEditorContext);
  if (!context) {
    throw new Error("useTranslationEditor must be used within TranslationEditorProvider");
  }
  return context;
};
