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
}

export const TranslationEditor = memo(
  function TranslationEditor({
    keyData,
    language,
    currentValue,
    projectId,
  }: TranslationEditorProps) {
    const [value, setValue] = useState(currentValue);

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

    const handleSave = async () => {
      // Remove all whitespace (spaces, tabs, newlines) from start and end
      const trimmedValue = value.replace(/^[\s\n\r\t]+|[\s\n\r\t]+$/g, '');

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
    };

    return (
      <div className="space-y-2 break-all" dir={language.direction}>
        {value || (
          <span className="text-muted-foreground text-sm">&lt;Empty&gt;</span>
        )}
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isSaving}
          rows={3}
        />
        <Button
          onClick={handleSave}
          disabled={isSaving}
          variant="outline"
          size="sm"
        >
          Save
        </Button>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Only re-render if current value or key ID changed
    return (
      prevProps.currentValue === nextProps.currentValue &&
      prevProps.keyData.id === nextProps.keyData.id &&
      prevProps.language.code === nextProps.language.code
    );
  }
);
