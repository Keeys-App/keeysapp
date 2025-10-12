import { type FC } from "react";
import { AutopilotCard, AutopilotActions } from "./AutopilotCard";

interface KeySuggestionsProps {
  currentLanguage?: string | null;
  currentLanguageValue?: string;
  defaultLanguage?: string | null;
  defaultLanguageValue?: string;
}

/**
 * Component for displaying translation suggestions and context
 * Shows the original text in the default language to help with translation
 */
export const KeySuggestions: FC<KeySuggestionsProps> = ({
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

  // If no language is being edited, show a message
  if (!currentLanguage) {
    return <AutopilotCard variant="disabled" />;
  }

  // If translation exists, show enhancement actions
  if (currentLanguageValue) {
    return (
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
  return (
    <AutopilotCard
      variant="translate"
      actions={[
        AutopilotActions.translate(handleTranslate),
        AutopilotActions.addContext(handleAddContext),
      ]}
    />
  );
};
