import { type FC, type ReactNode } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

type CheckboxCardVariant = "default" | "purple";

const variantStyles: Record<
  CheckboxCardVariant,
  { label: string; checkbox: string }
> = {
  default: {
    label: cn(
      "has-[[aria-checked=true]]:border-blue-600/40 has-[[aria-checked=true]]:bg-blue-500/10",
      "dark:has-[[aria-checked=true]]:border-blue-500/40 dark:has-[[aria-checked=true]]:bg-blue-500/10"
    ),
    checkbox: cn(
      "data-[state=checked]:border-blue-600/40 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white",
      "dark:data-[state=checked]:border-blue-500/40 dark:data-[state=checked]:bg-blue-500"
    ),
  },
  purple: {
    label: cn(
      "has-[[aria-checked=true]]:border-purple-600/40 has-[[aria-checked=true]]:bg-purple-500/10",
      "dark:has-[[aria-checked=true]]:border-purple-500/40 dark:has-[[aria-checked=true]]:bg-purple-500/10"
    ),
    checkbox: cn(
      "data-[state=checked]:border-purple-600/40 data-[state=checked]:bg-purple-600 data-[state=checked]:text-white",
      "dark:data-[state=checked]:border-purple-500/40 dark:data-[state=checked]:bg-purple-500"
    ),
  },
};

interface CheckboxCardProps {
  id: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  title: ReactNode;
  description?: ReactNode;
  disabled?: boolean;
  disabledReason?: string;
  variant?: CheckboxCardVariant;
  className?: string;
}

export const CheckboxCard: FC<CheckboxCardProps> = ({
  id,
  checked,
  onCheckedChange,
  title,
  description,
  disabled = false,
  disabledReason,
  variant = "default",
  className,
}) => {
  const styles = variantStyles[variant];

  const card = (
    <Label
      className={cn(
        "hover:bg-accent/50 flex items-start gap-3 rounded-lg border p-3 cursor-pointer",
        styles.label,
        disabled && "opacity-50 cursor-not-allowed hover:bg-transparent",
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
        className={styles.checkbox}
      />
      <div className="grid gap-1.5 font-normal">
        <p className="text-sm leading-none font-medium">{title}</p>
        {description ? (
          <p className="text-muted-foreground text-sm">{description}</p>
        ) : null}
      </div>
    </Label>
  );

  if (disabled && disabledReason) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div>{card}</div>
          </TooltipTrigger>
          <TooltipContent>
            <p>{disabledReason}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return card;
};

