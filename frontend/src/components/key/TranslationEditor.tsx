import { useState, useEffect, memo } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import {
  SET_TRANSLATION,
  GET_PROJECT_KEYS,
  GET_KEY_LOGS,
  GET_KEY,
} from "@/graphql/keys";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useSaving, useSavingStore } from "@/stores";
import type { Language } from "@/types/project";
import type { TranslationKey } from "@/types/translationKey";
import { Badge } from "../ui";

interface TranslationEditorProps {
  keyData: TranslationKey;
  language: Language;
  currentValue: string;
  projectId: string;
  isEditing: boolean;
  onEditingChange: (editing: boolean) => void;
}

export const TranslationEditor = memo(
  function TranslationEditor({
    keyData,
    language,
    currentValue,
    projectId,
    isEditing,
    onEditingChange,
  }: TranslationEditorProps) {
    const [value, setValue] = useState(currentValue);

    // Update value when currentValue changes from outside (e.g., switching keys)
    useEffect(() => {
      setValue(currentValue);
    }, [currentValue]);

    // Close editor when switching keys (when keyData.id changes)
    useEffect(() => {
      if (isEditing) {
        onEditingChange(false);
      }
    }, [keyData.id]); // eslint-disable-line react-hooks/exhaustive-deps

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
    const { isSaving } = useSavingStore();

    // Handle translation update success
    useEffect(() => {
      if (translationData) {
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

    const handleSave = async (e: React.MouseEvent) => {
      e.stopPropagation();
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

    const handleCancel = (e: React.MouseEvent) => {
      e.stopPropagation();
      setValue(currentValue);
      onEditingChange(false);
    };

    const handleEdit = (e: React.MouseEvent) => {
      e.stopPropagation();
      onEditingChange(true);
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
          <div dir={language.direction}>
            <Textarea
              className="bg-background"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              disabled={isSaving}
              rows={3}
              autoFocus
            />
            <div className="flex gap-2 mt-2">
              <Button
                onClick={handleSave}
                disabled={isSaving}
                variant="default"
                size="sm"
              >
                Save
              </Button>
              <Button
                onClick={handleCancel}
                disabled={isSaving}
                variant="outline"
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
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
