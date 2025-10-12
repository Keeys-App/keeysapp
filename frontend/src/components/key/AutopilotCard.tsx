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

type AutopilotVariant = "disabled" | "translate" | "enhance";

interface AutopilotAction {
  label: string;
  icon: LucideIcon;
  variant: "default" | "outline";
  onClick?: () => void;
}

interface AutopilotCardProps {
  /**
   * Variant of the autopilot card
   * - disabled: No language selected
   * - translate: Translation is empty, show translate action
   * - enhance: Translation exists, show enhancement actions
   */
  variant: AutopilotVariant;
  
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
  
  /**
   * Custom icon color class (defaults based on variant)
   */
  iconColorClass?: string;
  
  /**
   * Custom background color class for icon (defaults based on variant)
   */
  iconBgClass?: string;
}

/**
 * Universal Autopilot card component
 * Displays AI-powered suggestions and actions for translations
 */
export const AutopilotCard: FC<AutopilotCardProps> = ({
  variant,
  title = "Autopilot",
  description,
  actions = [],
  iconColorClass,
  iconBgClass,
}) => {
  // Default colors based on variant
  const defaultIconColor =
    variant === "disabled" ? "text-gray-500/70" : "text-indigo-500";
  const defaultIconBg =
    variant === "disabled" ? "bg-gray-500/10" : "bg-indigo-500/10";

  // Default descriptions based on variant
  const defaultDescription = description || getDefaultDescription(variant);

  return (
    <Item variant="outline">
      <ItemMedia>
        <div
          className={cn(
            "flex items-center gap-2 p-1 rounded-md",
            iconBgClass || defaultIconBg
          )}
        >
          <Sparkle className={iconColorClass || defaultIconColor} />
        </div>
      </ItemMedia>
      <ItemContent>
        <ItemTitle>{title}</ItemTitle>
        <ItemDescription className="text-balance">
          {defaultDescription}
        </ItemDescription>
        {actions.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {actions.map((action, index) => (
              <Button
                key={index}
                size="sm"
                variant="outline"
                className={cn(action.variant === "default" && "!bg-indigo-500 !shadow-transparent !border-transparent !text-white hover:!bg-indigo-500/90")}
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
 * Get default description based on variant
 */
function getDefaultDescription(variant: AutopilotVariant): string {
  switch (variant) {
    case "disabled":
      return "Select a translation field to edit to see suggestions";
    case "translate":
      return "Translate with AI based on the default language.";
    case "enhance":
      return "Enhance the quality of this translation using AI.";
    default:
      return "";
  }
}

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

