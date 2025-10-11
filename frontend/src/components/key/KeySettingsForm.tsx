import { type FC, useState, useEffect } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import type { TranslationKey } from "@/types/translationKey";
import { UPDATE_KEY, GET_KEY_LOGS } from "@/graphql/keys";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Field, FieldLabel } from "@/components/ui/field";
import { useSaving, useSavingStore } from "@/stores";
import { TagsEditor } from "./TagsEditor";

interface KeySettingsFormProps {
  selectedKey: TranslationKey;
  availableTags?: string[];
}

/**
 * Form for editing key settings (name, description, tags)
 */
export const KeySettingsForm: FC<KeySettingsFormProps> = ({
  selectedKey,
  availableTags = [],
}) => {
  const [description, setDescription] = useState("");
  const [keyName, setKeyName] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [savedDescription, setSavedDescription] = useState("");
  const [savedKeyName, setSavedKeyName] = useState("");
  const [savedTags, setSavedTags] = useState<string[]>([]);

  const [updateKey, { data, error }] = useMutation(UPDATE_KEY, {
    refetchQueries: [
      {
        query: GET_KEY_LOGS,
        variables: { keyId: selectedKey.id, limit: 50 },
      },
    ],
  });
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Update local state when selected key changes
  useEffect(() => {
    const desc = selectedKey.description || "";
    const key = selectedKey.key;
    const keyTags = selectedKey.tags || [];
    setDescription(desc);
    setKeyName(key);
    setTags(keyTags);
    setSavedDescription(desc);
    setSavedKeyName(key);
    setSavedTags(keyTags);
  }, [selectedKey]);

  // Handle mutation success
  useEffect(() => {
    if (data) {
      toast("Key updated successfully");
      // Update saved values if key was updated
      if (data.updateKey?.key) {
        setSavedKeyName(data.updateKey.key);
      }
      if (data.updateKey?.description !== undefined) {
        setSavedDescription(data.updateKey.description || "");
      }
      if (data.updateKey?.tags !== undefined) {
        setSavedTags(data.updateKey.tags || []);
      }
    }
  }, [data]);

  // Handle mutation error
  useEffect(() => {
    if (error) {
      toast("Failed to update key");
    }
  }, [error]);

  const handleSaveChanges = async () => {
    if (!keyName.trim()) {
      toast("Key name cannot be empty");
      return;
    }

    await withSaving(
      async () => {
        await updateKey({
          variables: {
            input: {
              id: selectedKey.id,
              key: keyName !== savedKeyName ? keyName : undefined,
              description: description !== savedDescription ? description : undefined,
              tags: JSON.stringify([...tags].sort()) !== JSON.stringify([...savedTags].sort()) ? tags : undefined,
            },
          },
        });
      },
      "Saving changes..."
    );
  };

  const hasChanges = 
    description !== savedDescription ||
    keyName !== savedKeyName ||
    JSON.stringify([...tags].sort()) !== JSON.stringify([...savedTags].sort());

  return (
    <div className="space-y-4">
      <Field>
        <FieldLabel>Key Name</FieldLabel>
        <Textarea
          value={keyName}
          onChange={(e) => {
            return setKeyName(e.target.value);
          }}
          placeholder="Enter key name..."
          className="min-h-[80px] font-mono"
          disabled={isSaving}
        />
      </Field>

      <Field>
        <FieldLabel>Description</FieldLabel>
        <Textarea
          value={description}
          onChange={(e) => {
            return setDescription(e.target.value);
          }}
          placeholder="Enter key description..."
          className="min-h-[120px]"
          disabled={isSaving}
        />
      </Field>
      
      <Field>
        <FieldLabel>Tags</FieldLabel>
        <TagsEditor
          selectedTags={tags}
          availableTags={availableTags}
          onChange={setTags}
          disabled={isSaving}
          placeholder="Select or create tags..."
        />
      </Field>

      <Button
        onClick={handleSaveChanges}
        disabled={isSaving || !hasChanges || !keyName.trim()}
        size="sm"
        className="w-full"
      >
        Save Changes
      </Button>
    </div>
  );
};

