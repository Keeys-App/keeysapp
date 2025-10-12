import { createContext, useContext, useState, type FC, type ReactNode } from "react";
import type { TranslationTextEditorRef } from "@/components/key/TranslationTextEditor";

interface TranslationEditorContextValue {
  editorRef: TranslationTextEditorRef | null;
  setEditorRef: (ref: TranslationTextEditorRef | null) => void;
}

const TranslationEditorContext = createContext<TranslationEditorContextValue | null>(null);

export const TranslationEditorProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [editorRef, setEditorRef] = useState<TranslationTextEditorRef | null>(null);

  return (
    <TranslationEditorContext.Provider value={{ editorRef, setEditorRef }}>
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

