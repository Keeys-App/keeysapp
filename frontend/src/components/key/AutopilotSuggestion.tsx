import { type FC, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Item } from "@/components/ui/item";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface AutopilotSuggestionAction {
  label: string;
  onClick: () => void;
  variant?: "default" | "outline" | "ghost";
}

interface AutopilotSuggestionProps {
  /**
   * Icon component to display
   */
  icon: LucideIcon;

  /**
   * Title of the suggestion
   */
  title: string;

  /**
   * Description or suggested content
   */
  description: string | ReactNode;

  /**
   * Actions (buttons) to display
   */
  actions: AutopilotSuggestionAction[];

  /**
   * Whether to show gradient background
   */
  withGradient?: boolean;

  /**
   * Custom className for the Item
   */
  className?: string;
}

/**
 * Component for displaying individual Autopilot suggestions
 * Shows suggested translations or improvements with actions
 */
export const AutopilotSuggestion: FC<AutopilotSuggestionProps> = ({
  icon: Icon,
  title,
  description,
  actions,
  withGradient = true,
  className,
}) => {
  return (
    <Item
      variant="outline"
      className={cn(
        "animate-in fade-in slide-in-from-bottom-2 duration-300",
        withGradient &&
          "from-indigo-500/10 dark:from-indigo-500/20 to-25% to-transparent dark:to-transparent bg-gradient-to-br",
        className
      )}
    >
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4 flex-shrink-0" />
        <div className="font-medium">{title}</div>
      </div>

      <div>{description}</div>

      {actions.length > 0 ? (
        <div className="flex items-center gap-2">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || "outline"}
              size="sm"
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}
        </div>
      ) : null}
    </Item>
  );
};

/**
 * Container for multiple Autopilot suggestions
 */
interface AutopilotSuggestionsListProps {
  children: ReactNode;
  className?: string;
}

export const AutopilotSuggestionsList: FC<AutopilotSuggestionsListProps> = ({
  children,
  className,
}) => {
  return <div className={cn("space-y-4", className)}>{children}</div>;
};

