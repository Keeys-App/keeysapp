import { cn } from "@/lib/utils";

interface KeyHeaderProps {
  keyName: string;
  description?: string | null;
  isSelected: boolean;
}

/**
 * Component for displaying a translation key name and description
 */
export function KeyHeader({ keyName, description, isSelected }: KeyHeaderProps) {
  return (
    <>
      <div className="font-mono text-sm break-words sticky bg-background top-0 z-10 py-2 px-4">
        <div
          className={cn(
            "transition-colors relative",
            isSelected && "text-primary"
          )}
        >
          {isSelected ? <div className="h-3 w-1 bg-primary rounded absolute top-[3px] left-[-9px]" /> : null}
          {keyName}
        </div>
      </div>
      {description ? (
        <p className="text-sm break-words text-muted-foreground px-4 pb-2">
          {description}
        </p>
      ) : null}
    </>
  );
}

