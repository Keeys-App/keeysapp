import { useState, useEffect, memo, useRef } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import {
  SET_TRANSLATION,
  GET_KEY_LOGS,
  GET_KEY,
  APPROVE_TRANSLATION,
} from "@/graphql/keys";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useSaving } from "@/stores";
import { useTranslationEditor } from "@/contexts";
import type { Language, LanguageWithLocale } from "@/types/project";
import type { TranslationKey } from "@/types/translationKey";
import { TranslationEditForm } from "./TranslationEditForm";
import { TranslationView } from "./TranslationView";
import type { TranslationTextEditorRef } from "./TranslationTextEditor";
import { PluralEditor } from "./PluralEditor";

interface TranslationEditorProps {
  keyData: TranslationKey;
  language: Language | LanguageWithLocale;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectId: string;
  isEditing: boolean;
  onEditingChange: (editing: boolean) => void;
}

export const TranslationEditor = memo(
  function TranslationEditor({
    keyData,
    language,
    projectLanguages,
    isEditing,
    onEditingChange,
  }: TranslationEditorProps) {
    // Find current translation value
    const translation = keyData.translations.find(
      (t) => t.language === language.code
    );
    const currentValue = translation?.value || "";

    // Find default language translation
    const defaultLanguage = projectLanguages.find((l) => l.default);
    const defaultTranslation = defaultLanguage
      ? keyData.translations.find((t) => t.language === defaultLanguage.code)
      : null;
    const defaultLanguageValue =
      !language.default && defaultTranslation?.value
        ? defaultTranslation.value
        : undefined;

    const [value, setValue] = useState(currentValue);
    const [markReviewedOnSave, setMarkReviewedOnSave] = useState(() => {
      const stored = localStorage.getItem("markReviewedOnSave");
      return stored ? JSON.parse(stored) : false;
    });
    const wasEditingRef = useRef(false);
    const valueToSaveRef = useRef<string | null>(null);
    const isAutoSavingRef = useRef(false);
    const { setEditorRef } = useTranslationEditor();

    // Register/unregister editor ref in context when editing starts/stops
    const handleEditorReady = (ref: TranslationTextEditorRef | null) => {
      setEditorRef(ref);
    };

    // Update value when currentValue changes from outside (e.g., switching keys)
    useEffect(() => {
      setValue(currentValue);
    }, [currentValue]);

    // Auto-save when editor closes (isEditing changes from true to false)
    useEffect(() => {
      if (
        wasEditingRef.current &&
        !isEditing &&
        valueToSaveRef.current !== null
      ) {
        // Editor was closed, check if there are unsaved changes
        if (valueToSaveRef.current !== currentValue) {
          // Has changes, auto-save
          handleAutoSave(valueToSaveRef.current);
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

    const [approveTranslation, { data: approveData, error: approveError }] =
      useMutation(APPROVE_TRANSLATION, {
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
      });

    const withSaving = useSaving();

    // Auto-save function (silent, no toast)
    const handleAutoSave = async (valueToSave: string) => {
      isAutoSavingRef.current = true;
      await withSaving(async () => {
        await setTranslation({
          variables: {
            input: {
              keyId: keyData.id,
              value: valueToSave,
              language: language.code,
            },
          },
        });
      }, `Saving...`);
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
            description: language.name,
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

    // Handle approve error
    useEffect(() => {
      if (approveError) {
        const message = getUserFriendlyErrorMessage(
          approveError,
          "Failed to mark as reviewed. Please try again."
        );
        toast(message);
      }
    }, [approveError]);

    const handleSave = async () => {
      isAutoSavingRef.current = false; // Ensure manual save shows toast
      valueToSaveRef.current = null; // Clear auto-save value

      // Allow empty value to delete translation
      await withSaving(async () => {
        await setTranslation({
          variables: {
            input: {
              keyId: keyData.id,
              value: value,
              language: language.code,
            },
          },
        });

        // Mark as reviewed if option is enabled and value is not empty
        if (markReviewedOnSave && value) {
          await approveTranslation({
            variables: {
              input: {
                keyId: keyData.id,
                language: language.code,
              },
            },
          });
        }
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
      return value !== currentValue;
    };

    return (
      <div
        className="space-y-2 text-sm break-all"
        onClick={(e) => e.stopPropagation()}
      >
        {keyData.isPlural ? (
          <PluralEditor />
        ) : (
          <>
            {!isEditing ? (
              <TranslationView
                value={value}
                direction={language.direction}
                onEdit={handleEdit}
              />
            ) : (
              <TranslationEditForm
                value={value}
                direction={language.direction}
                onChange={setValue}
                onSave={handleSave}
                onCancel={handleCancel}
                hasChanges={hasChanges()}
                defaultLanguageValue={defaultLanguageValue}
                markReviewedOnSave={markReviewedOnSave}
                onMarkReviewedOnSaveChange={setMarkReviewedOnSave}
                onEditorReady={handleEditorReady}
              />
            )}
          </>
        )}
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Only re-render if key ID, language, or editing state changed
    // Also check if translation value changed
    const prevTranslation = prevProps.keyData.translations.find(
      (t) => t.language === prevProps.language.code
    );
    const nextTranslation = nextProps.keyData.translations.find(
      (t) => t.language === nextProps.language.code
    );

    return (
      prevProps.keyData.id === nextProps.keyData.id &&
      prevProps.language.code === nextProps.language.code &&
      prevProps.isEditing === nextProps.isEditing &&
      prevTranslation?.value === nextTranslation?.value
    );
  }
);
