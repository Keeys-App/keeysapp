import { useState, useEffect } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import { SET_TRANSLATION, GET_PROJECT_KEYS } from "@/graphql/keys";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useSaving, useSavingStore } from "@/stores";
import type { Language } from "@/types/project";
import type { TranslationKey } from "@/types/translationKey";

interface TranslationEditorProps {
  keyData: TranslationKey;
  language: Language;
  currentValue: string;
  projectId: string;
}

export function TranslationEditor({
  keyData,
  language,
  currentValue,
  projectId,
}: TranslationEditorProps) {
  const [value, setValue] = useState(currentValue);

  const [setTranslation, { data: translationData, error: translationError }] = useMutation(SET_TRANSLATION, {
    refetchQueries: [{ query: GET_PROJECT_KEYS, variables: { projectId } }],
  });

  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Handle translation update success
  useEffect(() => {
    if (translationData) {
      toast("Translation updated successfully", {
        description: (
          <div>
            <div>{keyData.key}</div>
            <div>{language.name}</div>
            <div>{value}</div>
          </div>
        ),
      });
    }
  }, [translationData, keyData.key, language.name, value]);

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
    const trimmedValue = value.trim();

    // Allow empty value to delete translation
    await withSaving(
      async () => {
        await setTranslation({
          variables: {
            input: {
              keyId: keyData.id,
              value: trimmedValue,
              language: language.code,
            },
          },
        });
      },
      `Saving translation...`
    );
  };

  return (
    <div className="">
      <Textarea value={value} onChange={(e) => setValue(e.target.value)} disabled={isSaving} />
      <Button onClick={handleSave} disabled={isSaving} variant="outline">
        Save
      </Button>
    </div>
  );
}
