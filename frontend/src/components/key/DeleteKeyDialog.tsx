import { type FC } from "react";
import { DeleteConfirmationDialog } from "@/components/blocks/DeleteConfirmationDialog";

interface DeleteKeyDialogProps {
  /**
   * Controls the open state of the dialog
   */
  open: boolean;
  /**
   * Callback when the open state changes
   */
  onOpenChange: (open: boolean) => void;
  /**
   * The name of the key to delete
   */
  keyName: string;
  /**
   * Callback when the delete action is confirmed
   */
  onConfirm: () => void;
  /**
   * Whether the delete action is in progress
   */
  isDeleting?: boolean;
}

/**
 * Dialog component for confirming key deletion
 * Reusable across different contexts (KeyHeader, KeySettings, etc.)
 */
export const DeleteKeyDialog: FC<DeleteKeyDialogProps> = ({
  open,
  onOpenChange,
  keyName,
  onConfirm,
  isDeleting = false,
}) => {
  return (
    <DeleteConfirmationDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Delete Translation Key"
      description={
        <div className="space-y-2">
          <p>
            Are you sure you want to delete the key{" "}
            <span className="font-mono font-semibold">{keyName}</span>?
          </p>
          <p className="text-destructive">
            This will permanently delete all translations for this key. This
            action cannot be undone.
          </p>
        </div>
      }
      onConfirm={onConfirm}
      confirmButtonText="Delete Key"
      isDeleting={isDeleting}
    />
  );
};

