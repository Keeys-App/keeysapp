import { useState, useEffect, memo, useRef } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import {
  SET_TRANSLATION,
  GET_PROJECT_KEYS,
  GET_KEY_LOGS,
  GET_KEY,
} from "@/graphql/keys";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useSaving } from "@/stores";
import type { Language } from "@/types/project";
import type { TranslationKey } from "@/types/translationKey";
import { TranslationEditForm } from "./TranslationEditForm";

interface TranslationEditorProps {
  keyData: TranslationKey;
  language: Language;
  currentValue: string;
  projectId: string;
  isEditing: boolean;
  onEditingChange: (editing: boolean) => void;
  defaultLanguageValue?: string;
}

export const TranslationEditor = memo(
  function TranslationEditor({
    keyData,
    language,
    currentValue,
    projectId,
    isEditing,
    onEditingChange,
    defaultLanguageValue,
  }: TranslationEditorProps) {
    const [value, setValue] = useState(currentValue);
    const wasEditingRef = useRef(false);
    const valueToSaveRef = useRef<string | null>(null);
    const isAutoSavingRef = useRef(false);

    // Update value when currentValue changes from outside (e.g., switching keys)
    useEffect(() => {
      setValue(currentValue);
    }, [currentValue]);

    // Auto-save when editor closes (isEditing changes from true to false)
    useEffect(() => {
      if (wasEditingRef.current && !isEditing && valueToSaveRef.current !== null) {
        // Editor was closed, check if there are unsaved changes
        const trimmedValue = valueToSaveRef.current.replace(/^[\s\n\r\t]+|[\s\n\r\t]+$/g, "");
        const trimmedCurrentValue = currentValue.replace(/^[\s\n\r\t]+|[\s\n\r\t]+$/g, "");
        
        if (trimmedValue !== trimmedCurrentValue) {
          // Has changes, auto-save
          handleAutoSave(trimmedValue);
        }
        
        valueToSaveRef.current = null;
      }
      
      wasEditingRef.current = isEditing;
    }, [isEditing]); // eslint-disable-line react-hooks/exhaustive-deps

    // Track current value for auto-save
    useEffect(() => {
      if (isEditing) {
        valueToSaveRef.current = value;
      }
    }, [value, isEditing]);

    const [setTranslation, { data: translationData, error: translationError }] =
      useMutation(SET_TRANSLATION, {
        refetchQueries: [
          {
            query: GET_KEY_LOGS,
            variables: { keyId: keyData.id, limit: 50 },
          },
          {
            query: GET_KEY,
            variables: { id: keyData.id },
          },
        ],
        awaitRefetchQueries: true,
        update(cache, { data }) {
          if (data?.setTranslation) {
            // Update only the specific translation in cache
            const keyId = cache.identify({
              __typename: "KeyType",
              id: keyData.id,
            });

            cache.modify({
              id: keyId,
              fields: {
                translations(existingTranslations = []) {
                  const newTranslation = data.setTranslation;
                  const otherTranslations = existingTranslations.filter(
                    (t: any) => t.language !== newTranslation.language
                  );
                  return [...otherTranslations, newTranslation];
                },
                updatedAt() {
                  return new Date().toISOString();
                },
              },
            });

            // Invalidate key logs cache to force refetch
            cache.evict({
              id: "ROOT_QUERY",
              fieldName: "keyLogs",
              args: { keyId: keyData.id },
            });
          }
        },
      });

    const withSaving = useSaving();

    // Auto-save function (silent, no toast)
    const handleAutoSave = async (trimmedValue: string) => {
      isAutoSavingRef.current = true;
      await withSaving(async () => {
        await setTranslation({
          variables: {
            input: {
              keyId: keyData.id,
              value: trimmedValue,
              language: language.code,
            },
          },
        });
      }, `Auto-saving...`);
      // Reset flag after a short delay to ensure toast effect runs
      setTimeout(() => {
        isAutoSavingRef.current = false;
      }, 100);
    };

    // Handle translation update success
    useEffect(() => {
      if (translationData && !isAutoSavingRef.current) {
        const isDeleted = !translationData.setTranslation;
        toast(
          isDeleted
            ? "Translation deleted successfully"
            : "Translation updated successfully",
          {
            description: (
              <div>
                <div>{keyData.key}</div>
                <div>{language.name}</div>
                {!isDeleted ? (
                  <div>{translationData.setTranslation.value}</div>
                ) : null}
              </div>
            ),
          }
        );
      }
    }, [translationData, keyData.key, language.name]);

    // Handle translation update error
    useEffect(() => {
      if (translationError) {
        const message = getUserFriendlyErrorMessage(
          translationError,
          "Failed to update translation. Please try again."
        );
        toast(message);
      }
    }, [translationError]);

    const handleSave = async () => {
      isAutoSavingRef.current = false; // Ensure manual save shows toast
      valueToSaveRef.current = null; // Clear auto-save value
      // Remove all whitespace (spaces, tabs, newlines) from start and end
      const trimmedValue = value.replace(/^[\s\n\r\t]+|[\s\n\r\t]+$/g, "");

      // Allow empty value to delete translation
      await withSaving(async () => {
        await setTranslation({
          variables: {
            input: {
              keyId: keyData.id,
              value: trimmedValue,
              language: language.code,
            },
          },
        });
      }, `Saving translation...`);

      onEditingChange(false);
    };

    const handleCancel = () => {
      setValue(currentValue);
      valueToSaveRef.current = null; // Cancel auto-save
      onEditingChange(false);
    };

    const handleEdit = (e: React.MouseEvent) => {
      e.stopPropagation();
      onEditingChange(true);
    };

    // Check if there are unsaved changes
    const hasChanges = () => {
      const trimmedValue = value.replace(/^[\s\n\r\t]+|[\s\n\r\t]+$/g, "");
      const trimmedCurrentValue = currentValue.replace(/^[\s\n\r\t]+|[\s\n\r\t]+$/g, "");
      return trimmedValue !== trimmedCurrentValue;
    };

    return (
      <div className="space-y-2 break-all" onClick={(e) => e.stopPropagation()}>
        {!isEditing ? (
          <div
            dir={language.direction}
            className="cursor-pointer hover:bg-muted/70 rounded py-2 px-3 transition-colors min-h-[2rem]"
            onClick={handleEdit}
          >
            <div className="p-[1px]">
              {value ? (
                <span className="whitespace-pre-wrap">{value}</span>
              ) : (
                <span className="text-muted-foreground text-sm">
                  &lt;Empty&gt;
                </span>
              )}
            </div>
          </div>
        ) : (
          <TranslationEditForm
            value={value}
            direction={language.direction}
            onChange={setValue}
            onSave={handleSave}
            onCancel={handleCancel}
            hasChanges={hasChanges()}
            defaultLanguageValue={defaultLanguageValue}
          />
        )}
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Only re-render if current value, key ID, or editing state changed
    return (
      prevProps.currentValue === nextProps.currentValue &&
      prevProps.keyData.id === nextProps.keyData.id &&
      prevProps.language.code === nextProps.language.code &&
      prevProps.isEditing === nextProps.isEditing
    );
  }
);
