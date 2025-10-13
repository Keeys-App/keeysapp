import { cn } from "@/lib/utils";
import { Copy, type LucideIcon, X } from "lucide-react";
import { InputGroupButton } from "../ui";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import type { FC } from "react";

interface KeyHeaderProps {
  keyName: string;
  isSelected: boolean;
}

/**
 * Component for displaying a translation key name
 */
export function KeyHeader({ keyName, isSelected }: KeyHeaderProps) {
  return (
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
        <div className="group-hover/key:flex gap-2 hidden">
          <Button tooltip="Delete key" Icon={X} onClick={() => {}} />
          <Button tooltip="Duplicate key" Icon={Copy} onClick={() => {}} />
        </div>
      </div>
    </div>
  );
}

interface ButtonProps {
  tooltip: string;
  Icon: LucideIcon;
  onClick: () => void;
}

const Button: FC<ButtonProps> = ({ tooltip, Icon, onClick }: ButtonProps) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <InputGroupButton
            onClick={onClick}
            variant="outline"
            className="rounded-full cursor-pointer"
            size="icon-xs"
          >
            <Icon className="!h-3.5 !w-3.5" />
          </InputGroupButton>
        </TooltipTrigger>
        <TooltipContent>{tooltip}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
