import { type FC } from "react";
import { AutopilotCard, AutopilotActions } from "./AutopilotCard";
import {
  AutopilotSuggestion,
  AutopilotSuggestionsList,
} from "./AutopilotSuggestion";
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
  } else if (currentLanguageValue) {
    // If translation exists, show enhancement actions
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
  } else {
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
  }

  const autopilotAction = AutopilotActions.shorten(handleTranslate);
  const autopilotAction2 = AutopilotActions.addContext(handleTranslate);

  return (
    <AutopilotSuggestionsList>
      {card}

      <AutopilotSuggestion
        icon={autopilotAction.icon}
        title={autopilotAction.label}
        description="Unrestricted access to the Space, its content, and settings. Can add, modify, and delete projects and members, as well as make changes to billing and plans"
        actions={[
          {
            label: "Use suggestion",
            onClick: handleTranslate,
            variant: "outline",
          },
          {
            label: "Discard",
            onClick: handleTranslate,
            variant: "ghost",
          },
        ]}
      />

      <AutopilotSuggestion
        icon={autopilotAction2.icon}
        title={autopilotAction2.label}
        description="Unrestricted access to the Space, its content, and settings. Can add, modify, and delete projects and members, as well as make changes to billing and plans"
        actions={[
          {
            label: "Remove context",
            onClick: handleTranslate,
            variant: "outline",
          },
        ]}
        withGradient={false}
      />
    </AutopilotSuggestionsList>
  );
};
