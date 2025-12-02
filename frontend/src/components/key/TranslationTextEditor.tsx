import {
  type KeyboardEvent,
  useRef,
  useEffect,
  useState,
  useImperativeHandle,
  forwardRef,
} from "react";
import { cn } from "@/lib/utils";

interface TranslationTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  onKeyDown?: (e: KeyboardEvent<HTMLDivElement>) => void;
  direction?: "ltr" | "rtl";
  disabled?: boolean;
  autoFocus?: boolean;
  rows?: number;
}

export interface TranslationTextEditorRef {
  insertText: (text: string) => void;
}

/**
 * Translation text editor component with contenteditable
 * Can be extended in the future with rich text editing, autocomplete, etc.
 */
export const TranslationTextEditor = forwardRef<TranslationTextEditorRef, TranslationTextEditorProps>(({
  value,
  onChange,
  onKeyDown,
  direction = "ltr",
  disabled = false,
  autoFocus = true,
}, ref) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const onChangeRef = useRef(onChange);
  const [isFocused, setIsFocused] = useState(false);

  // Keep onChange ref up to date
  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  // Get text content preserving all whitespace including trailing spaces
  const getTextContent = (element: HTMLElement): string => {
    const text = element.innerText;
    // If the text contains only whitespace characters (spaces, tabs, newlines),
    // treat it as empty. This handles the case when user clears all content
    // but browser leaves invisible newline characters.
    if (text.trim().length === 0) {
      return "";
    }
    return text;
  };

  // Set text content preserving all whitespace
  const setTextContent = (element: HTMLElement, text: string) => {
    // Replace trailing spaces with non-breaking spaces to preserve them
    const processedText = text.replace(/( +)$/gm, (match) => 
      match.replace(/ /g, '\u00A0')
    );
    element.textContent = processedText;
  };

  // Expose insertText method via ref
  // Use empty deps array to prevent ref object recreation on every render
  useImperativeHandle(ref, () => ({
    insertText: (text: string) => {
      if (editorRef.current) {
        setTextContent(editorRef.current, text);
        onChangeRef.current(text);
        // Focus the editor after inserting text
        editorRef.current.focus();
        // Move cursor to end
        const range = document.createRange();
        const sel = window.getSelection();
        range.selectNodeContents(editorRef.current);
        range.collapse(false);
        sel?.removeAllRanges();
        sel?.addRange(range);
      }
    },
  }), []);

  // Sync external value changes to the editor
  useEffect(() => {
    if (editorRef.current && !isFocused) {
      const currentText = getTextContent(editorRef.current);
      if (currentText !== value) {
        setTextContent(editorRef.current, value);
      }
    }
  }, [value, isFocused]);

  // Auto focus on mount
  useEffect(() => {
    if (autoFocus && editorRef.current) {
      editorRef.current.focus();
      // Move cursor to end
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(editorRef.current);
      range.collapse(false);
      sel?.removeAllRanges();
      sel?.addRange(range);
    }
  }, [autoFocus]);

  const handleInput = () => {
    if (editorRef.current) {
      const newValue = getTextContent(editorRef.current);
      if (newValue !== value) {
        onChange(newValue);
      }
    }
  };

  return (
    <div
      ref={editorRef}
      contentEditable={!disabled}
      dir={direction}
      className={cn(
        "bg-background rounded-none border-none p-2 shadow-none",
        "min-h-[60px] outline-none whitespace-pre-wrap break-words",
        "focus-visible:outline-none",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      onInput={handleInput}
      onClick={(e) => e.stopPropagation()}
      onKeyDown={onKeyDown}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      suppressContentEditableWarning
    />
  );
});

TranslationTextEditor.displayName = "TranslationTextEditor";
