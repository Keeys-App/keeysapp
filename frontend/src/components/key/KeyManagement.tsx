import { type FC, useState, useEffect } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";
import { UPDATE_KEY } from "@/graphql/keys";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useSaving, useSavingStore } from "@/stores";

interface KeyManagementProps {
  selectedKey: TranslationKey | null;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectId: string;
}

/**
 * Component for managing a selected translation key
 */
export const KeyManagement: FC<KeyManagementProps> = ({
  selectedKey,
  projectLanguages,
  projectId,
}) => {
  const [description, setDescription] = useState("");
  const [keyName, setKeyName] = useState("");

  const [updateKey, { data, error }] = useMutation(UPDATE_KEY);
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Update local state when selected key changes
  useEffect(() => {
    if (selectedKey) {
      setDescription(selectedKey.description || "");
      setKeyName(selectedKey.key);
    }
  }, [selectedKey]);

  // Handle mutation success
  useEffect(() => {
    if (data) {
      toast("Key updated successfully");
    }
  }, [data]);

  // Handle mutation error
  useEffect(() => {
    if (error) {
      toast("Failed to update key");
    }
  }, [error]);

  const handleUpdateDescription = async () => {
    if (!selectedKey) {
      return;
    }

    await withSaving(
      async () => {
        await updateKey({
          variables: {
            input: {
              id: selectedKey.id,
              description: description,
            },
          },
        });
      },
      "Updating description..."
    );
  };

  const handleUpdateKeyName = async () => {
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
              key: keyName,
            },
          },
        });
      },
      "Updating key name..."
    );
  };

  if (!selectedKey) {
    return (
      <div className="h-full flex flex-col">
        <div className="px-4 py-3">
          <h2 className="text-base font-semibold">Key Management</h2>
        </div>
        <div className="flex-1 p-4">
          <p className="text-muted-foreground text-sm">
            Click on any translation key from the list to view and manage it
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3">
        <h2 className="text-base font-semibold">Key Management</h2>
        <div className="text-sm mt-1 text-muted-foreground font-mono w-full break-words pr-8">
          {selectedKey.key}
        </div>
      </div>
      <div className="flex-1 p-4 overflow-auto">
        <Tabs defaultValue="meta" className="w-full">
          <TabsList>
            <TabsTrigger value="meta">Meta</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="meta" className="space-y-4 mt-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter key description..."
                className="min-h-[120px]"
              />
              <Button
                onClick={handleUpdateDescription}
                disabled={isSaving || description === selectedKey.description}
                size="sm"
                variant="outline"
              >
                Save Description
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4 mt-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Key Name</label>
              <Textarea
                value={keyName}
                onChange={(e) => setKeyName(e.target.value)}
                placeholder="Enter key name..."
                className="min-h-[80px] font-mono"
              />
              <Button
                onClick={handleUpdateKeyName}
                disabled={isSaving || keyName === selectedKey.key || !keyName.trim()}
                size="sm"
                variant="outline"
              >
                Update Key Name
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
