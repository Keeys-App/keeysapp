import { type FC, useState, useEffect } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import { Trash2 } from "lucide-react";
import { DELETE_KEY, GET_PROJECT_KEYS } from "@/graphql/keys";
import { Button } from "@/components/ui/button";
import { DeleteConfirmationDialog } from "@/components/blocks/DeleteConfirmationDialog";
import { useSaving, useSavingStore } from "@/stores";
import type { TranslationKey } from "@/types/translationKey";

interface KeySettingsProps {
  selectedKey: TranslationKey;
  projectId: string;
  onKeyDeleted?: () => void;
}

/**
 * Component for managing key settings (deletion, etc.)
 */
export const KeySettings: FC<KeySettingsProps> = ({
  selectedKey,
  projectId,
  onKeyDeleted,
}) => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deleteKey, { data, error, loading }] = useMutation(DELETE_KEY, {
    refetchQueries: [
      {
        query: GET_PROJECT_KEYS,
        variables: { projectId },
      },
    ],
    awaitRefetchQueries: true,
  });
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Handle mutation success
  useEffect(() => {
    if (data) {
      toast("Key deleted successfully");
      setIsDeleteDialogOpen(false);
      if (onKeyDeleted) {
        onKeyDeleted();
      }
    }
  }, [data, onKeyDeleted]);

  // Handle mutation error
  useEffect(() => {
    if (error) {
      toast("Failed to delete key");
    }
  }, [error]);

  const handleDeleteClick = () => {
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    await withSaving(
      async () => {
        await deleteKey({
          variables: {
            id: selectedKey.id,
          },
        });
      },
      "Deleting key..."
    );
  };

  return (
    <div className="space-y-6 mt-4">
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-destructive">Danger Zone</h3>
        <p className="text-sm text-muted-foreground">
          Deleting a key will permanently remove it and all its translations. This action cannot be undone.
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

      <DeleteConfirmationDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        title="Delete Translation Key"
        description={
          <div className="space-y-2">
            <p>
              Are you sure you want to delete the key{" "}
              <span className="font-mono font-semibold">{selectedKey.key}</span>?
            </p>
            <p className="text-destructive">
              This will permanently delete all translations for this key. This action cannot be undone.
            </p>
          </div>
        }
        onConfirm={handleConfirmDelete}
        confirmButtonText="Delete Key"
        isDeleting={loading}
      />
    </div>
  );
};

