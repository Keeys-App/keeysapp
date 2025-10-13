import { type FC, useState } from "react";
import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSavingStore } from "@/stores";
import type { TranslationKey } from "@/types/translationKey";
import { Item } from "../ui/item";
import { useKeyActions } from "@/hooks/useKeyActions";
import { DeleteKeyDialog } from "./DeleteKeyDialog";

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
  const { isSaving } = useSavingStore();
  
  const { isDeleting, handleDelete } = useKeyActions({
    keyData: selectedKey,
    projectId,
    onKeyDeleted,
    onDeleteSuccess: () => setIsDeleteDialogOpen(false),
  });

  const handleDeleteClick = () => {
    setIsDeleteDialogOpen(true);
  };

  return (
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
  );
};
