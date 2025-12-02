import { type FC, type ReactNode } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface CheckboxCardProps {
  id: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  title: ReactNode;
  description?: ReactNode;
  disabled?: boolean;
  className?: string;
}

export const CheckboxCard: FC<CheckboxCardProps> = ({
  id,
  checked,
  onCheckedChange,
  title,
  description,
  disabled = false,
  className,
}) => {
  return (
    <Label
      className={cn(
        "hover:bg-accent/50 flex items-start gap-3 rounded-lg border p-3 cursor-pointer",
        "has-[[aria-checked=true]]:border-blue-600 has-[[aria-checked=true]]:bg-blue-50",
        "dark:has-[[aria-checked=true]]:border-blue-900 dark:has-[[aria-checked=true]]:bg-blue-950",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
    >
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={(value) => {
          return onCheckedChange(value === true);
        }}
        disabled={disabled}
        className="data-[state=checked]:border-blue-600 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white dark:data-[state=checked]:border-blue-700 dark:data-[state=checked]:bg-blue-700"
      />
      <div className="grid gap-1.5 font-normal">
        <p className="text-sm leading-none font-medium">{title}</p>
        {description ? (
          <p className="text-muted-foreground text-sm">{description}</p>
        ) : null}
      </div>
    </Label>
  );
};

