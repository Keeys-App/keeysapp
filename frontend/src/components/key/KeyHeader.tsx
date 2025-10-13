import { cn } from "@/lib/utils";
import { Copy, type LucideIcon, Trash2 } from "lucide-react";
import { InputGroupButton } from "../ui";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import { useState, type FC } from "react";
import { useKeyActions } from "@/hooks/useKeyActions";
import { DeleteKeyDialog } from "./DeleteKeyDialog";
import type { TranslationKey } from "@/types/translationKey";

interface KeyHeaderProps {
  keyName: string;
  isSelected: boolean;
  keyData: TranslationKey;
  projectId: string;
  onKeyDeleted?: () => void;
}

/**
 * Component for displaying a translation key name
 */
export function KeyHeader({ keyName, isSelected, keyData, projectId, onKeyDeleted }: KeyHeaderProps) {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  
  const {
    isDeleting,
    isSaving,
    handleDelete,
    handleDuplicate,
  } = useKeyActions({ 
    keyData, 
    projectId, 
    onKeyDeleted,
    onDeleteSuccess: () => setIsDeleteDialogOpen(false),
  });

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsDeleteDialogOpen(true);
  };

  const handleDuplicateClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await handleDuplicate();
  };

  return (
    <>
      <div className="font-mono text-sm break-words sticky bg-background top-0 z-10 py-2 px-4">
        <div
          className={cn(
            "transition-colors relative",
            isSelected && "text-primary"
          )}
        >
          {isSelected ? (
            <div className="h-3 w-1 bg-primary rounded absolute top-[3px] left-[-9px]" />
          ) : null}
          {keyName}
        </div>
        <div className="mt-3 mb-2 h-6">
          <div className={cn("group-hover/key:flex gap-2 hidden", isSelected && "flex")}>
            <Button 
              tooltip="Delete key" 
              Icon={Trash2} 
              onClick={handleDeleteClick}
              disabled={isSaving}
            />
            <Button 
              tooltip="Duplicate key" 
              Icon={Copy} 
              onClick={handleDuplicateClick}
              disabled={isSaving}
            />
          </div>
        </div>
      </div>

      <DeleteKeyDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        keyName={keyData.key}
        onConfirm={handleDelete}
        isDeleting={isDeleting}
      />
    </>
  );
}

interface ButtonProps {
  tooltip: string;
  Icon: LucideIcon;
  onClick: (e: React.MouseEvent) => void;
  disabled?: boolean;
}

const Button: FC<ButtonProps> = ({ tooltip, Icon, onClick, disabled }: ButtonProps) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <InputGroupButton
            onClick={onClick}
            variant="outline"
            className="rounded-full cursor-pointer"
            size="icon-xs"
            disabled={disabled}
          >
            <Icon className="!h-3.5 !w-3.5" />
          </InputGroupButton>
        </TooltipTrigger>
        <TooltipContent>{tooltip}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
