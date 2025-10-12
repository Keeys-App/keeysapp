import { type ReactNode, type FC } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface DeleteConfirmationDialogProps {
  /**
   * Controls the open state of the dialog
   */
  open: boolean;
  /**
   * Callback when the open state changes
   */
  onOpenChange: (open: boolean) => void;
  /**
   * Title of the dialog
   */
  title: string;
  /**
   * Description or warning message. Can be a string or React node for custom formatting
   */
  description: ReactNode;
  /**
   * Callback when the delete action is confirmed
   */
  onConfirm: () => void;
  /**
   * Text for the confirm button. Defaults to "Delete"
   */
  confirmButtonText?: string;
  /**
   * Text for the cancel button. Defaults to "Cancel"
   */
  cancelButtonText?: string;
  /**
   * Whether the delete action is in progress
   */
  isDeleting?: boolean;
}

/**
 * Reusable delete confirmation dialog component
 * Can be used for any delete action across the application
 */
export const DeleteConfirmationDialog: FC<DeleteConfirmationDialogProps> = ({
  open,
  onOpenChange,
  title,
  description,
  onConfirm,
  confirmButtonText = "Delete",
  cancelButtonText = "Cancel",
  isDeleting = false,
}) => {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription asChild>
            <div className="text-muted-foreground text-sm">{description}</div>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting}>
            {cancelButtonText}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            disabled={isDeleting}
            className="bg-destructive text-white hover:bg-destructive/90"
          >
            {isDeleting ? "Deleting..." : confirmButtonText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

