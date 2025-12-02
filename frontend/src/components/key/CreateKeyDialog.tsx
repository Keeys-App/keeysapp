import { useState, useEffect, useRef, type FC } from "react";
import { useMutation, useLazyQuery, gql } from "@apollo/client";
import { toast } from "sonner";
import { Sparkles } from "lucide-react";
import { CREATE_KEY, CHECK_KEY_EXISTS } from "@/graphql/keys";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useSaving, useSavingStore } from "@/stores";
import type { LanguageWithLocale } from "@/types/project";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Field, FieldLabel, FieldError } from "@/components/ui/field";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CheckboxCard } from "@/components/blocks";
import { TagsEditor } from "./TagsEditor";

interface CreateKeyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  defaultLanguage?: string | null;
  availableTags?: string[];
  projectLanguages?: LanguageWithLocale[];
}

export const CreateKeyDialog: FC<CreateKeyDialogProps> = ({
  open,
  onOpenChange,
  projectId,
  defaultLanguage,
  availableTags = [],
  projectLanguages = [],
}) => {
  const [key, setKey] = useState("");
  const [description, setDescription] = useState("");
  const [defaultValue, setDefaultValue] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [isPlural, setIsPlural] = useState(false);
  const [addAnother, setAddAnother] = useState(false);
  const [autopilot, setAutopilot] = useState(false);
  const [isDuplicate, setIsDuplicate] = useState(false);
  const [lastCheckedKey, setLastCheckedKey] = useState<string>("");

  // Check if autopilot should be shown (more than 1 language in project)
  const showAutopilot = projectLanguages.length > 1 && !!defaultLanguage;

  // Uncheck autopilot when default value is cleared
  useEffect(() => {
    if (!defaultValue.trim()) {
      setAutopilot(false);
    }
  }, [defaultValue]);

  // Track the last processed mutation result to avoid duplicate toasts
  const lastProcessedDataRef = useRef<any>(null);

  // Lazy query to check if key exists
  const [
    checkKeyExists,
    { loading: checkingKey, data: checkKeyData, error: checkKeyError },
  ] = useLazyQuery(CHECK_KEY_EXISTS, {
    fetchPolicy: "no-cache", // Don't use cache at all
  });

  // Handle check key exists result
  useEffect(() => {
    if (checkKeyData?.checkKeyExists !== undefined) {
      setIsDuplicate(checkKeyData.checkKeyExists);
      setLastCheckedKey(key.trim()); // Mark this key as checked
    }
  }, [checkKeyData, key]);

  // Handle check key exists error
  useEffect(() => {
    if (checkKeyError) {
      setIsDuplicate(false);
      setLastCheckedKey(key.trim()); // Mark as checked even on error
    }
  }, [checkKeyError, key]);

  // Debounced check for key existence
  useEffect(() => {
    const trimmedKey = key.trim();

    if (!trimmedKey || !open) {
      setIsDuplicate(false);
      setLastCheckedKey("");
      return;
    }

    // Reset states while waiting for new check
    setIsDuplicate(false);
    setLastCheckedKey(""); // Clear last checked key - new check is starting

    const timeoutId = setTimeout(() => {
      checkKeyExists({
        variables: {
          projectId,
          key: trimmedKey,
        },
      });
    }, 300); // Debounce for 300ms

    return () => {
      return clearTimeout(timeoutId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, projectId, open]);

  // Reset form when dialog closes
  useEffect(() => {
    if (!open) {
      setKey("");
      setDescription("");
      setDefaultValue("");
      setTags([]);
      setIsPlural(false);
      setIsDuplicate(false);
      setLastCheckedKey("");
      // Reset processed data ref when dialog closes
      lastProcessedDataRef.current = null;
    }
  }, [open]);

  // Check if form is valid and ready to submit
  const isFormValid = key.trim() !== "" && !isDuplicate; // Ensure current key has been checked

  const [createKey, { data: createKeyData, error: createKeyError }] =
    useMutation(CREATE_KEY, {
      update(cache, { data }) {
        if (data?.createKey) {
          // Add new key to the cache
          cache.modify({
            fields: {
              projectKeys(
                existingData = { keys: [], totalCount: 0, hasMore: false }
              ) {
                const newKeyRef = cache.writeFragment({
                  data: data.createKey,
                  fragment: gql`
                    fragment NewKey on TranslationKey {
                      id
                      key
                      description
                      tags
                      isPlural
                      translations {
                        language
                        value
                        reviewStatus
                        createdAt
                        updatedAt
                      }
                      createdAt
                      updatedAt
                    }
                  `,
                });

                return {
                  ...existingData,
                  keys: [newKeyRef, ...(existingData.keys || [])],
                  totalCount: (existingData.totalCount || 0) + 1,
                };
              },
            },
          });
        }
      },
    });

  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Handle create key success
  useEffect(() => {
    if (createKeyData && createKeyData !== lastProcessedDataRef.current) {
      // Mark this data as processed
      lastProcessedDataRef.current = createKeyData;

      // If createKey is null, the creation failed (likely due to duplicate key)
      if (!createKeyData.createKey) {
        toast("Key already exists. Please choose a different name.");
        setIsDuplicate(true);
        return;
      }

      const keyValue = key;

      // Reset form
      setKey("");
      setDescription("");
      setDefaultValue("");
      setTags([]);
      setIsPlural(false);
      setIsDuplicate(false);
      setLastCheckedKey(""); // Reset last checked key

      // Close dialog only if "Add another key" is not checked
      if (!addAnother) {
        onOpenChange(false);
      }

      toast("Key created successfully", {
        description: keyValue,
      });
    }
  }, [createKeyData, addAnother, onOpenChange, key]);

  // Handle create key error
  useEffect(() => {
    if (createKeyError) {
      const message = getUserFriendlyErrorMessage(
        createKeyError,
        "Failed to create key. Please try again."
      );
      toast(message);
    }
  }, [createKeyError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Don't submit if still checking or if form is invalid
    if (!isFormValid || checkingKey) {
      return;
    }

    if (!key.trim()) {
      toast("Please enter a key");
      return;
    }

    if (isDuplicate) {
      toast("This key already exists in the project");
      return;
    }

    // Build translations object if default value is provided
    const translations =
      defaultLanguage && defaultValue.trim()
        ? { [defaultLanguage]: defaultValue.trim() }
        : undefined;

    // Determine if autopilot should run (only if there's a default value and autopilot is enabled)
    const shouldRunAutopilot = !!(autopilot && translations && showAutopilot);

    await withSaving(
      async () => {
        await createKey({
          variables: {
            input: {
              projectId,
              key: key.trim(),
              description: description.trim() || undefined,
              tags: tags.length > 0 ? tags : undefined,
              isPlural: isPlural || undefined,
              translations,
              autopilot: shouldRunAutopilot,
            },
          },
        });
      },
      shouldRunAutopilot ? "Creating key and translating..." : "Creating key..."
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Key</DialogTitle>
          <DialogDescription>
            Add a new translation key to your project.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Tabs defaultValue="key" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="key">Key</TabsTrigger>
              <TabsTrigger value="metadata">Metadata</TabsTrigger>
            </TabsList>

            <TabsContent value="key" className="space-y-4">
              {/* Key */}
              <Field>
                <FieldLabel>Key</FieldLabel>
                <Input
                  placeholder="BUTTON.SUBMIT"
                  value={key}
                  className="font-mono"
                  onChange={(e) => {
                    return setKey(e.target.value);
                  }}
                  disabled={isSaving}
                  required
                />
                {isDuplicate ? (
                  <FieldError>
                    This key already exists in the project
                  </FieldError>
                ) : null}
              </Field>

              {/* Default Language Value */}
              {defaultLanguage ? (
                <Field>
                  <FieldLabel>
                    Default Value ({defaultLanguage.toUpperCase()})
                  </FieldLabel>
                  <Textarea
                    placeholder={`Enter translation...`}
                    value={defaultValue}
                    onChange={(e) => {
                      return setDefaultValue(e.target.value);
                    }}
                    disabled={isSaving}
                    rows={3}
                  />
                </Field>
              ) : null}

              {/* Plural */}
              <CheckboxCard
                id="is-plural"
                checked={isPlural}
                onCheckedChange={setIsPlural}
                disabled={isSaving}
                title="Plural key"
                description='Enable plural forms for this key'
              />

              {/* Autopilot checkbox */}
              {showAutopilot ? (
                <CheckboxCard
                  id="autopilot"
                  checked={autopilot}
                  onCheckedChange={setAutopilot}
                  disabled={isSaving || !defaultValue.trim()}
                  disabledReason="Enter a default value first to enable autopilot"
                  variant="purple"
                  title={
                    <span className="flex items-center gap-1.5">
                      <Sparkles className="h-3.5 w-3.5 text-purple-600" />
                      Autopilot
                    </span>
                  }
                  description="Automatically translate to all project languages using AI when default value is provided"
                />
              ) : null}
            </TabsContent>

            <TabsContent value="metadata" className="space-y-4">
              {/* Description */}
              <Field>
                <FieldLabel>Description</FieldLabel>
                <Textarea
                  placeholder="Describe the purpose of this key..."
                  value={description}
                  onChange={(e) => {
                    return setDescription(e.target.value);
                  }}
                  disabled={isSaving}
                  rows={5}
                />
              </Field>

              {/* Tags */}
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
            </TabsContent>
          </Tabs>

          <DialogFooter className="flex-col gap-4 sm:flex-col">
            {/* Buttons row */}
            <div className="flex items-center justify-between w-full">
              {/* Add Another Key */}
              <div className="flex items-center gap-2">
                <Checkbox
                  id="add-another"
                  checked={addAnother}
                  onCheckedChange={(checked) => {
                    return setAddAnother(checked === true);
                  }}
                  disabled={isSaving}
                />
                <label
                  htmlFor="add-another"
                  className="text-sm font-medium leading-none cursor-pointer"
                >
                  Add another key
                </label>
              </div>

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    return onOpenChange(false);
                  }}
                  disabled={isSaving}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={!isFormValid || isSaving}>
                  Create Key
                </Button>
              </div>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
