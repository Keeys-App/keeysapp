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
import { Textarea } from "@/components/ui/textarea";
import { BookPlus } from "lucide-react";

interface AISuggestion {
  id: string;
  text: string;
  type: "translate" | "rephrase" | "shorten";
  timestamp: number;
}

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
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [variants, setVariants] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [removingIds, setRemovingIds] = useState<Set<string>>(new Set());
  
  // Custom context (separate from key.description)
  const [customContext, setCustomContext] = useState<string>("");
  const [isEditingContext, setIsEditingContext] = useState(false);
  const [contextValue, setContextValue] = useState("");

  // AI mutations
  const [translateMutation] = useMutation<AiTranslateData>(AI_TRANSLATE);
  const [rephraseMutation] = useMutation<AiRephraseData>(AI_REPHRASE);
  const [shortenMutation] = useMutation<AiShortenData>(AI_SHORTEN);
  const [variantsMutation] =
    useMutation<AiSuggestVariantsData>(AI_SUGGEST_VARIANTS);

  // Clear suggestions when language changes
  useEffect(() => {
    setSuggestions([]);
    setVariants([]);
    setRemovingIds(new Set());
  }, [currentLanguage?.code, currentLanguageValue]);

  // Auto-populate context from key description when key changes
  useEffect(() => {
    if (currentKey.description) {
      setCustomContext(currentKey.description);
    } else {
      setCustomContext("");
    }
  }, [currentKey.id]);

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
              context: customContext || undefined,
            },
          },
        });

        if (result.data?.aiTranslate.success && result.data.aiTranslate.text) {
          const newSuggestion: AISuggestion = {
            id: `translate-${Date.now()}`,
            text: result.data.aiTranslate.text,
            type: "translate",
            timestamp: Date.now(),
          };
          setSuggestions((prev) => [...prev, newSuggestion]);
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
              context: customContext || undefined,
            },
          },
        });

        if (result.data?.aiRephrase.success && result.data.aiRephrase.text) {
          const newSuggestion: AISuggestion = {
            id: `rephrase-${Date.now()}`,
            text: result.data.aiRephrase.text,
            type: "rephrase",
            timestamp: Date.now(),
          };
          setSuggestions((prev) => [...prev, newSuggestion]);
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
              context: customContext || undefined,
            },
          },
        });

        if (result.data?.aiShorten.success && result.data.aiShorten.text) {
          const newSuggestion: AISuggestion = {
            id: `shorten-${Date.now()}`,
            text: result.data.aiShorten.text,
            type: "shorten",
            timestamp: Date.now(),
          };
          setSuggestions((prev) => [...prev, newSuggestion]);
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
              context: customContext || undefined,
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
    setContextValue(customContext);
    setIsEditingContext(true);
  };

  const handleSaveContext = () => {
    setCustomContext(contextValue.trim());
    setIsEditingContext(false);
    toast("Context saved");
  };

  const handleCancelContext = () => {
    setContextValue(customContext);
    setIsEditingContext(false);
  };

  const handleDiscardContext = () => {
    setCustomContext("");
    toast("Context removed");
  };


  const handleUseSuggestion = (text: string) => {
    // TODO: Apply suggestion to translation field
    toast("Apply suggestion - coming soon");
  };

  const handleDiscardSuggestion = (id: string) => {
    // Mark as removing for animation
    setRemovingIds((prev) => new Set(prev).add(id));
    
    // Remove from state after animation completes
    setTimeout(() => {
      setSuggestions((prev) => prev.filter((s) => s.id !== id));
      setRemovingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }, 300); // Match animation duration
  };

  const handleClearAllSuggestions = () => {
    // Mark all as removing
    const allIds = new Set(suggestions.map((s) => s.id));
    setRemovingIds(allIds);
    
    // Clear after animation
    setTimeout(() => {
      setSuggestions([]);
      setRemovingIds(new Set());
    }, 300);
  };

  const handleDiscardVariants = () => {
    setVariants([]);
  };

  // Get type-specific icon and label
  const getSuggestionMeta = (type: AISuggestion["type"]) => {
    switch (type) {
      case "translate":
        return {
          icon: AutopilotActions.translate().icon,
          label: "Translation",
        };
      case "rephrase":
        return {
          icon: AutopilotActions.rephrase().icon,
          label: "Rephrased",
        };
      case "shorten":
        return {
          icon: AutopilotActions.shorten().icon,
          label: "Shortened",
        };
    }
  };

  let card: React.ReactNode | null = null;

  // If no language is being edited, show disabled state
  if (!currentLanguage) {
    card = <AutopilotCard isDisabled />;
  } else if (currentLanguageValue) {
    // If translation exists, show enhancement actions
    card = (
      <AutopilotCard
        isPending={isSaving || isGenerating}
        description="Enhance the quality of this translation using AI."
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
        description="Translate with AI based on the default language."
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

      {/* Context card (single unified context) - only show when language is selected */}
      {currentLanguage && isEditingContext ? (
        // Edit mode
        <AutopilotSuggestion
          icon={BookPlus}
          title="Context for AI"
          description={
            <Textarea
              placeholder="e.g., Used in the checkout flow to confirm payment. Should be formal and reassuring."
              value={contextValue}
              onChange={(e) => {
                setContextValue(e.target.value);
              }}
              rows={4}
              className="resize-none mt-2"
              disabled={isSaving}
              autoFocus
            />
          }
          actions={[
            {
              label: "Save",
              onClick: handleSaveContext,
              variant: "outline",
            },
            {
              label: "Cancel",
              onClick: handleCancelContext,
              variant: "ghost",
            },
          ]}
          withGradient={false}
        />
      ) : currentLanguage && customContext ? (
        // View mode (saved context)
        <AutopilotSuggestion
          icon={BookPlus}
          title="Context"
          description={customContext}
          actions={[
            {
              label: "Edit",
              onClick: handleAddContext,
              variant: "outline",
            },
            {
              label: "Discard",
              onClick: handleDiscardContext,
              variant: "ghost",
            },
          ]}
          withGradient={false}
        />
      ) : null}

      {/* Show all accumulated suggestions (only when language is selected) */}
      {currentLanguage && suggestions.map((suggestion) => {
        const meta = getSuggestionMeta(suggestion.type);
        const isRemoving = removingIds.has(suggestion.id);
        
        return (
          <AutopilotSuggestion
            key={suggestion.id}
            icon={meta.icon}
            title={meta.label}
            description={suggestion.text}
            className={
              isRemoving
                ? "animate-out fade-out slide-out-to-right-2 duration-300"
                : undefined
            }
            actions={[
              {
                label: "Use suggestion",
                onClick: () => {
                  handleUseSuggestion(suggestion.text);
                },
                variant: "outline",
              },
              {
                label: "Discard",
                onClick: () => {
                  handleDiscardSuggestion(suggestion.id);
                },
                variant: "ghost",
              },
            ]}
          />
        );
      })}

      {/* Show variants if available (only when language is selected) */}
      {currentLanguage && variants.length > 0 ? (
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

      {/* Loading skeleton (only when language is selected) */}
      {currentLanguage && (isGenerating || isSaving) ? <AutopilotSuggestionSkeleton /> : null}
    </AutopilotSuggestionsList>
  );
};
