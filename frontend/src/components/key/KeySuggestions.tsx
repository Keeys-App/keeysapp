import { type FC, useState, useEffect } from "react";
import { useMutation } from "@apollo/client";
import { AutopilotCard, AutopilotActions } from "./AutopilotCard";
import {
  AutopilotSuggestion,
  AutopilotSuggestionsList,
} from "./AutopilotSuggestion";
import { AutopilotSuggestionSkeleton } from "./AutopilotSuggestionSkeleton";
import type { TranslationKey } from "@/types/translationKey";
import type { Language } from "@/types/project";
import {
  AI_TRANSLATE,
  AI_REPHRASE,
  AI_SHORTEN,
  AI_SUGGEST_VARIANTS,
  type AiTranslateData,
  type AiRephraseData,
  type AiShortenData,
  type AiSuggestVariantsData,
} from "@/graphql/ai";
import { toast } from "sonner";
import { useSaving, useSavingStore } from "@/stores";

interface KeySuggestionsProps {
  currentKey: TranslationKey;
  currentLanguage?: Language | null;
  currentLanguageValue?: string;
  defaultLanguage?: Language | null;
  defaultLanguageValue?: string;
}

/**
 * Component for displaying translation suggestions and context
 * Shows AI-powered suggestions for translation and improvement
 */
export const KeySuggestions: FC<KeySuggestionsProps> = ({
  currentKey,
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // State for AI suggestions
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [variants, setVariants] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // AI mutations
  const [translateMutation] = useMutation<AiTranslateData>(AI_TRANSLATE);
  const [rephraseMutation] = useMutation<AiRephraseData>(AI_REPHRASE);
  const [shortenMutation] = useMutation<AiShortenData>(AI_SHORTEN);
  const [variantsMutation] =
    useMutation<AiSuggestVariantsData>(AI_SUGGEST_VARIANTS);

  // Clear suggestions when language changes
  useEffect(() => {
    setSuggestion(null);
    setVariants([]);
  }, [currentLanguage?.code, currentLanguageValue]);

  const handleTranslate = async () => {
    if (!defaultLanguageValue || !currentLanguage || !defaultLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        setIsGenerating(true);
        const result = await translateMutation({
          variables: {
            input: {
              text: defaultLanguageValue,
              targetLanguage: currentLanguage.name,
              sourceLanguage: defaultLanguage.name,
              context: currentKey.description || undefined,
            },
          },
        });

        if (result.data?.aiTranslate.success && result.data.aiTranslate.text) {
          setSuggestion(result.data.aiTranslate.text);
          toast("Translation generated");
        } else {
          toast(result.data?.aiTranslate.error || "Translation failed");
        }
      } catch (error) {
        toast("Translation failed. Please try again.");
      } finally {
        setIsGenerating(false);
      }
    }, "Translating with AI...");
  };

  const handleRephrase = async () => {
    if (!currentLanguageValue || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        const result = await rephraseMutation({
          variables: {
            input: {
              text: currentLanguageValue,
              language: currentLanguage.name,
              context: currentKey.description || undefined,
            },
          },
        });

        if (result.data?.aiRephrase.success && result.data.aiRephrase.text) {
          setSuggestion(result.data.aiRephrase.text);
          toast("Rephrase generated");
        } else {
          toast(result.data?.aiRephrase.error || "Rephrase failed");
        }
      } catch (error) {
        toast("Rephrase failed. Please try again.");
      }
    }, "Rephrasing with AI...");
  };

  const handleShorten = async () => {
    if (!currentLanguageValue || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        const result = await shortenMutation({
          variables: {
            input: {
              text: currentLanguageValue,
              language: currentLanguage.name,
              context: currentKey.description || undefined,
            },
          },
        });

        if (result.data?.aiShorten.success && result.data.aiShorten.text) {
          setSuggestion(result.data.aiShorten.text);
          toast("Shortened version generated");
        } else {
          toast(result.data?.aiShorten.error || "Shorten failed");
        }
      } catch (error) {
        toast("Shorten failed. Please try again.");
      }
    }, "Shortening with AI...");
  };

  const handleSuggestVariants = async () => {
    if (!currentLanguageValue || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        const result = await variantsMutation({
          variables: {
            input: {
              text: currentLanguageValue,
              language: currentLanguage.name,
              context: currentKey.description || undefined,
              count: 3,
            },
          },
        });

        if (
          result.data?.aiSuggestVariants.success &&
          result.data.aiSuggestVariants.variants.length > 0
        ) {
          setVariants(result.data.aiSuggestVariants.variants);
          toast("Variants generated");
        } else {
          toast(
            result.data?.aiSuggestVariants.error || "Variant generation failed"
          );
        }
      } catch (error) {
        toast("Variant generation failed. Please try again.");
      }
    }, "Generating variants...");
  };

  const handleAddContext = () => {
    // TODO: Implement context editing
    toast("Context editing - coming soon");
  };

  const handleUseSuggestion = (text: string) => {
    // TODO: Apply suggestion to translation field
    toast("Apply suggestion - coming soon");
  };

  const handleDiscardSuggestion = () => {
    setSuggestion(null);
  };

  const handleDiscardVariants = () => {
    setVariants([]);
  };

  let card: React.ReactNode | null = null;

  // If no language is being edited, show a message
  if (!currentLanguage) {
    card = <AutopilotCard variant="disabled" />;
  } else if (currentLanguageValue) {
    // If translation exists, show enhancement actions
    card = (
      <AutopilotCard
        isPending={isSaving || isGenerating}
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
        isPending={isSaving || isGenerating}
        variant="translate"
        actions={[
          AutopilotActions.translate(handleTranslate),
          AutopilotActions.addContext(handleAddContext),
        ]}
      />
    );
  }

  return (
    <AutopilotSuggestionsList>
      {card}

      {/* Show single suggestion if available */}
      {suggestion ? (
        <AutopilotSuggestion
          icon={AutopilotActions.translate().icon}
          title="AI Suggestion"
          description={suggestion}
          actions={[
            {
              label: "Use suggestion",
              onClick: () => {
                handleUseSuggestion(suggestion);
              },
              variant: "outline",
            },
            {
              label: "Discard",
              onClick: handleDiscardSuggestion,
              variant: "ghost",
            },
          ]}
        />
      ) : null}

      {/* Show variants if available */}
      {variants.length > 0 ? (
        <>
          {variants.map((variant, index) => (
            <AutopilotSuggestion
              key={index}
              icon={AutopilotActions.suggestVariants().icon}
              title={`Variant ${index + 1}`}
              description={variant}
              actions={[
                {
                  label: "Use variant",
                  onClick: () => {
                    handleUseSuggestion(variant);
                  },
                  variant: "outline",
                },
              ]}
              withGradient={false}
            />
          ))}
          <AutopilotSuggestion
            icon={AutopilotActions.suggestVariants().icon}
            title="Clear variants"
            description="Remove all generated variants"
            actions={[
              {
                label: "Clear all",
                onClick: handleDiscardVariants,
                variant: "ghost",
              },
            ]}
            withGradient={false}
          />
        </>
      ) : null}

      {/* Loading skeleton (placeholder for future features) */}
      {isGenerating || isSaving ? <AutopilotSuggestionSkeleton /> : null}
    </AutopilotSuggestionsList>
  );
};
