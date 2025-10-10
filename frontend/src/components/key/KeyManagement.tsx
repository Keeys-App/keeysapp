import { type FC, useState, useEffect } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";
import { UPDATE_KEY, GET_KEY_LOGS } from "@/graphql/keys";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Field, FieldLabel } from "@/components/ui/field";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSaving, useSavingStore } from "@/stores";
import { TagsEditor } from "./TagsEditor";
import { KeyLogsTimeline } from "./KeyLogsTimeline";

interface KeyManagementProps {
  selectedKey: TranslationKey | null;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectId: string;
  availableTags?: string[];
}

/**
 * Component for managing a selected translation key
 */
export const KeyManagement: FC<KeyManagementProps> = ({
  selectedKey,
  projectLanguages,
  projectId,
  availableTags = [],
}) => {
  const [description, setDescription] = useState("");
  const [keyName, setKeyName] = useState("");
  const [displayKeyName, setDisplayKeyName] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [savedDescription, setSavedDescription] = useState("");
  const [savedKeyName, setSavedKeyName] = useState("");
  const [savedTags, setSavedTags] = useState<string[]>([]);

  const [updateKey, { data, error }] = useMutation(UPDATE_KEY, {
    refetchQueries: selectedKey
      ? [
          {
            query: GET_KEY_LOGS,
            variables: { keyId: selectedKey.id, limit: 50 },
          },
        ]
      : [],
  });
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Update local state when selected key changes
  useEffect(() => {
    if (selectedKey) {
      const desc = selectedKey.description || "";
      const key = selectedKey.key;
      const keyTags = selectedKey.tags || [];
      setDescription(desc);
      setKeyName(key);
      setDisplayKeyName(key);
      setTags(keyTags);
      setSavedDescription(desc);
      setSavedKeyName(key);
      setSavedTags(keyTags);
    }
  }, [selectedKey]);

  // Handle mutation success
  useEffect(() => {
    if (data) {
      toast("Key updated successfully");
      // Update display name and saved values if key was updated
      if (data.updateKey?.key) {
        setDisplayKeyName(data.updateKey.key);
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
    if (!selectedKey) {
      return;
    }

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
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 border-b h-12 box-border">
        <h2 className="text-base font-semibold">Key Management</h2>
      </div>
      <div className={`flex-1 ${selectedKey ? 'overflow-auto' : 'p-4'}`}>
        {!selectedKey ? (
          <p className="text-muted-foreground text-sm">
            Click on any translation key from the list to view and manage it
          </p>
        ) : (
          <Tabs defaultValue="history" className="h-full flex flex-col">
            <TabsList className="mx-4 mt-4">
              <TabsTrigger value="history">History</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="history" className="flex-1 px-4 pb-4 overflow-auto">
              <KeyLogsTimeline keyId={selectedKey.id} />
            </TabsContent>

            <TabsContent value="settings" className="flex-1 px-4 pb-4 overflow-auto">
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
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};
