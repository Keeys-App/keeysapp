import { type FC, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
  Sparkle,
  ListRestart,
  ArrowDownWideNarrow,
  ListStart,
  Wand,
  BookPlus,
  type LucideIcon,
} from "lucide-react";
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle,
  ItemMedia,
} from "../ui/item";
import { cn } from "@/lib/utils";

interface AutopilotAction {
  label: string;
  icon: LucideIcon;
  variant: "default" | "outline";
  onClick?: () => void;
}

interface AutopilotCardProps {
  /**
   * Whether the card is in disabled state (no language selected)
   */
  isDisabled?: boolean;

  /**
   * Whether an AI operation is in progress
   */
  isPending?: boolean;

  /**
   * Custom title (defaults to "Autopilot")
   */
  title?: string;

  /**
   * Custom description
   */
  description?: string;

  /**
   * Actions to display (buttons)
   */
  actions?: AutopilotAction[];
}

/**
 * Universal Autopilot card component
 * Displays AI-powered suggestions and actions for translations
 */
export const AutopilotCard: FC<AutopilotCardProps> = ({
  isDisabled = false,
  title = "Autopilot",
  description,
  actions = [],
  isPending,
}) => {
  // Colors based on disabled flag
  const iconColor = isDisabled ? "text-gray-500/70" : "text-indigo-500";
  const iconBg = isDisabled ? "bg-gray-500/10" : "bg-indigo-500/10";

  // Default description when disabled
  const defaultDescription = description || (isDisabled ? "Select a translation field to edit to see suggestions" : undefined);

  return (
    <Item variant="outline">
      <ItemMedia>
        <div
          className={cn(
            "flex items-center gap-2 p-1 rounded-md",
            iconBg
          )}
        >
          <div className={cn(isPending && "animate-pulse")}>
            <Sparkle className={iconColor} />
          </div>
        </div>
      </ItemMedia>
      <ItemContent>
        <ItemTitle>{isPending ? 'Generating...' : title}</ItemTitle>
        <ItemDescription>
          {defaultDescription}
        </ItemDescription>
        {actions.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {actions.map((action, index) => (
              <Button
                key={index}
                size="sm"
                variant="outline"
                disabled={isPending}
                className={cn(
                  action.variant === "default" &&
                    "!bg-indigo-500 !shadow-transparent !border-transparent !text-white hover:!bg-indigo-500/90"
                )}
                onClick={action.onClick}
              >
                {action.icon ? <action.icon /> : null}
                {action.label}
              </Button>
            ))}
          </div>
        ) : null}
      </ItemContent>
    </Item>
  );
};

/**
 * Preset action configurations
 */
export const AutopilotActions = {
  translate: (onClick?: () => void): AutopilotAction => ({
    label: "Translate",
    icon: Wand,
    onClick,
    variant: "default",
  }),

  rephrase: (onClick?: () => void): AutopilotAction => ({
    label: "Rephrase",
    icon: ListRestart,
    onClick,
    variant: "outline",
  }),

  shorten: (onClick?: () => void): AutopilotAction => ({
    label: "Shorten",
    icon: ArrowDownWideNarrow,
    onClick,
    variant: "outline",
  }),

  suggestVariants: (onClick?: () => void): AutopilotAction => ({
    label: "Suggest variants",
    icon: ListStart,
    onClick,
    variant: "outline",
  }),

  addContext: (onClick?: () => void): AutopilotAction => ({
    label: "Add context",
    icon: BookPlus,
    onClick,
    variant: "outline",
  }),
};
