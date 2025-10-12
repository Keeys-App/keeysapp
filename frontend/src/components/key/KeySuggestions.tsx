import { type FC } from "react";
import { AutopilotCard, AutopilotActions } from "./AutopilotCard";
import { Item } from "../ui/item";
import { Button } from "../ui/button";
import type { TranslationKey } from "@/types/translationKey";
import type { Language } from "@/types/project";

interface KeySuggestionsProps {
  currentKey: TranslationKey;
  currentLanguage?: Language | null;
  currentLanguageValue?: string;
  defaultLanguage?: Language | null;
  defaultLanguageValue?: string;
}

/**
 * Component for displaying translation suggestions and context
 * Shows the original text in the default language to help with translation
 */
export const KeySuggestions: FC<KeySuggestionsProps> = ({
  currentKey,
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  // Placeholder handlers (TODO: implement actual functionality)
  const handleTranslate = () => {
    console.log("Translate");
  };

  const handleRephrase = () => {
    console.log("Rephrase");
  };

  const handleShorten = () => {
    console.log("Shorten");
  };

  const handleSuggestVariants = () => {
    console.log("Suggest variants");
  };

  const handleAddContext = () => {
    console.log("Add context");
  };

  let card: React.ReactNode | null = null;

  // If no language is being edited, show a message
  if (!currentLanguage) {
    card = <AutopilotCard variant="disabled" />;
  }

  // If translation exists, show enhancement actions
  if (currentLanguageValue) {
    card = (
      <AutopilotCard
        variant="enhance"
        actions={[
          AutopilotActions.rephrase(handleRephrase),
          AutopilotActions.shorten(handleShorten),
          AutopilotActions.suggestVariants(handleSuggestVariants),
          AutopilotActions.addContext(handleAddContext),
        ]}
      />
    );
  }

  // Show translate action for empty translation
  card = (
    <AutopilotCard
      variant="translate"
      actions={[
        AutopilotActions.translate(handleTranslate),
        AutopilotActions.addContext(handleAddContext),
      ]}
    />
  );

  const autopilotAction = AutopilotActions.shorten(handleTranslate);
  const autopilotAction2 = AutopilotActions.addContext(handleTranslate);

  return (
    <div className="space-y-4">
      Target: {currentKey.key} ({currentLanguage?.name})
      
      {card}

      <Item
        variant="outline"
        className="from-indigo-500/10 dark:from-indigo-500/20 to-25% to-transparent dark:to-transparent bg-gradient-to-br"
      >
        <div className="flex items-center gap-2">
          <autopilotAction.icon className="w-4 h-4 flex-shrink-0" />
          <div className="font-medium">{autopilotAction.label}</div>
        </div>

        <div>
          Unrestricted access to the Space, its content, and settings. Can add,
          modify, and delete projects and members, as well as make changes to
          billing and plans
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            Use suggestion
          </Button>
          <Button variant="ghost" size="sm">
            Discard
          </Button>
        </div>
      </Item>

      <Item variant="outline">
        <div className="flex items-center gap-2">
          <autopilotAction2.icon className="w-4 h-4 flex-shrink-0" />
          <div className="font-medium">{autopilotAction2.label}</div>
        </div>
        <div>
          Unrestricted access to the Space, its content, and settings. Can add,
          modify, and delete projects and members, as well as make changes to
          billing and plans
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">Remove context</Button>
        </div>
      </Item>
    </div>
  );
};
