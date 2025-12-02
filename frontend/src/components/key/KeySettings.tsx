import { type FC, useState, useEffect, useRef } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import { Trash2, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useSaving, useSavingStore } from "@/stores";
import type { TranslationKey } from "@/types/translationKey";
import { Item } from "../ui/item";
import { useKeyActions } from "@/hooks/useKeyActions";
import { DeleteKeyDialog } from "./DeleteKeyDialog";
import { UPDATE_KEY } from "@/graphql/keys";

interface KeySettingsProps {
  selectedKey: TranslationKey | null;
  isLoading?: boolean;
  projectId: string;
  onKeyDeleted?: () => void;
}

/**
 * Component for managing key settings (deletion, etc.)
 */
export const KeySettings: FC<KeySettingsProps> = ({
  selectedKey,
  isLoading = false,
  projectId,
  onKeyDeleted,
}) => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isPlural, setIsPlural] = useState(selectedKey?.isPlural || false);
  const { isSaving } = useSavingStore();
  const withSaving = useSaving();
  
  // Track the last processed mutation result
  const lastProcessedDataRef = useRef<unknown>(null);
  
  const { isDeleting, handleDelete } = useKeyActions({
    keyData: selectedKey || undefined,
    projectId,
    onKeyDeleted,
    onDeleteSuccess: () => setIsDeleteDialogOpen(false),
  });

  const [updateKey, { data: updateKeyData, error: updateKeyError }] = useMutation(UPDATE_KEY);

  // Sync local state with selected key
  useEffect(() => {
    if (selectedKey) {
      setIsPlural(selectedKey.isPlural || false);
    }
  }, [selectedKey]);

  // Handle mutation success
  useEffect(() => {
    if (updateKeyData && updateKeyData !== lastProcessedDataRef.current) {
      lastProcessedDataRef.current = updateKeyData;
      if (updateKeyData.updateKey) {
        toast("Key settings updated");
      }
    }
  }, [updateKeyData]);

  // Handle mutation error
  useEffect(() => {
    if (updateKeyError) {
      toast("Failed to update key settings");
      // Revert to previous state
      if (selectedKey) {
        setIsPlural(selectedKey.isPlural || false);
      }
    }
  }, [updateKeyError, selectedKey]);

  const handlePluralChange = async (checked: boolean) => {
    if (!selectedKey) {
      return;
    }
    
    setIsPlural(checked);
    
    await withSaving(async () => {
      await updateKey({
        variables: {
          input: {
            id: selectedKey.id,
            isPlural: checked,
          },
        },
      });
    }, "Updating key settings...");
  };

  const handleDeleteClick = () => {
    setIsDeleteDialogOpen(true);
  };

  if (!selectedKey) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Plural Settings */}
      <Item variant="outline">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold">Key Type</h3>
          <div className="flex items-center gap-2">
            <Checkbox
              id="settings-is-plural"
              checked={isPlural}
              onCheckedChange={(checked) => {
                return handlePluralChange(checked === true);
              }}
              disabled={isSaving}
            />
            <label
              htmlFor="settings-is-plural"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
            >
              Plural key
            </label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>Enable plural forms for this key (e.g., "1 item" vs "5 items")</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </Item>

      {/* Danger Zone */}
      <Item variant="outline">
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-destructive">Danger Zone</h3>
          <p className="text-sm text-muted-foreground">
            Deleting a key will permanently remove it and all its translations.
            This action cannot be undone.
          </p>
        </div>

        <Button
          variant="destructive"
          size="sm"
          onClick={handleDeleteClick}
          disabled={isSaving}
          className="w-full"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Key
        </Button>

        <DeleteKeyDialog
          open={isDeleteDialogOpen}
          onOpenChange={setIsDeleteDialogOpen}
          keyName={selectedKey.key}
          onConfirm={handleDelete}
          isDeleting={isDeleting}
        />
      </Item>
    </div>
  );
};
