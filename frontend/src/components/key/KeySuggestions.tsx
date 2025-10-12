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
import { useTranslationEditor } from "@/contexts";
import { Textarea } from "@/components/ui/textarea";
import { BookPlus } from "lucide-react";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";

interface AISuggestion {
  id: string;
  text: string;
  type: "translate" | "rephrase" | "shorten";
  timestamp: number;
  isError?: boolean;
  reason?: string;
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
  const { editorRef } = useTranslationEditor();

  // State for AI suggestions
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [variants, setVariants] = useState<string[]>([]);
  const [selectedVariant, setSelectedVariant] = useState<string>("");
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
    setSelectedVariant("");
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

  // Auto-select first variant when variants are generated
  useEffect(() => {
    if (variants.length > 0 && !selectedVariant) {
      setSelectedVariant(variants[0]);
    }
  }, [variants]);

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
        } else if (result.data?.aiTranslate.reason) {
          // AI couldn't process - show as info card
          const errorSuggestion: AISuggestion = {
            id: `translate-error-${Date.now()}`,
            text: result.data.aiTranslate.reason,
            type: "translate",
            timestamp: Date.now(),
            isError: true,
            reason: result.data.aiTranslate.reason,
          };
          setSuggestions((prev) => [...prev, errorSuggestion]);
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
        } else if (result.data?.aiRephrase.reason) {
          // AI couldn't process - show as info card
          const errorSuggestion: AISuggestion = {
            id: `rephrase-error-${Date.now()}`,
            text: result.data.aiRephrase.reason,
            type: "rephrase",
            timestamp: Date.now(),
            isError: true,
            reason: result.data.aiRephrase.reason,
          };
          setSuggestions((prev) => [...prev, errorSuggestion]);
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
        } else if (result.data?.aiShorten.reason) {
          // AI couldn't process - show as info card
          const errorSuggestion: AISuggestion = {
            id: `shorten-error-${Date.now()}`,
            text: result.data.aiShorten.reason,
            type: "shorten",
            timestamp: Date.now(),
            isError: true,
            reason: result.data.aiShorten.reason,
          };
          setSuggestions((prev) => [...prev, errorSuggestion]);
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
        } else if (result.data?.aiSuggestVariants.reason) {
          // AI couldn't process - show as info card
          const errorSuggestion: AISuggestion = {
            id: `variants-error-${Date.now()}`,
            text: result.data.aiSuggestVariants.reason,
            type: "rephrase",
            timestamp: Date.now(),
            isError: true,
            reason: result.data.aiSuggestVariants.reason,
          };
          setSuggestions((prev) => [...prev, errorSuggestion]);
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

  const handleUseSuggestion = async (text: string) => {
    if (!currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        await setTranslation({
          variables: {
            input: {
              keyId: currentKey.id,
              value: text,
              language: currentLanguage.code,
              isAiGenerated: true,
            },
          },
        });

        toast("AI suggestion applied", {
          description: `Translation updated for ${currentLanguage.name}`,
        });
        
        // Clear the suggestion after using it
        setSuggestions((prev) => prev.filter((s) => s.text !== text));
      } catch (error) {
        toast("Failed to apply suggestion");
      }
    }, "Applying suggestion...");
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
    setSelectedVariant("");
  };

  const handleUseSelectedVariant = async () => {
    if (!selectedVariant || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        await setTranslation({
          variables: {
            input: {
              keyId: currentKey.id,
              value: selectedVariant,
              language: currentLanguage.code,
              isAiGenerated: true,
            },
          },
        });

        toast("AI variant applied", {
          description: `Translation updated for ${currentLanguage.name}`,
        });
        
        // Clear all variants after using one
        setVariants([]);
        setSelectedVariant("");
      } catch (error) {
        toast("Failed to apply variant");
      }
    }, "Applying variant...");
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
    const enhancementActions = [
      AutopilotActions.rephrase(handleRephrase),
      AutopilotActions.shorten(handleShorten),
      AutopilotActions.suggestVariants(handleSuggestVariants),
      AutopilotActions.addContext(handleAddContext),
    ];

    // Add Translate button if not default language and default value exists
    if (
      currentLanguage?.code !== defaultLanguage?.code &&
      defaultLanguageValue
    ) {
      enhancementActions.unshift(AutopilotActions.translate(handleTranslate));
    }

    card = (
      <AutopilotCard
        isPending={isSaving || isGenerating}
        description="Enhance the quality of this translation using AI."
        actions={enhancementActions}
      />
    );
  } else if (!defaultLanguageValue) {
    // No default value to translate from
    card = (
      <AutopilotCard
        isDisabled
        description="Add a translation in the default language first to enable AI translation."
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

      {/* Context card (single unified context) - only show when language is selected and not in disabled state */}
      {currentLanguage && (currentLanguageValue || defaultLanguageValue) && isEditingContext ? (
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
          variant="none"
        />
      ) : currentLanguage && (currentLanguageValue || defaultLanguageValue) && customContext ? (
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
          variant="none"
        />
      ) : null}

      {/* Show all accumulated suggestions (only when language is selected) */}
      {currentLanguage &&
        suggestions.map((suggestion) => {
          const meta = getSuggestionMeta(suggestion.type);
          const isRemoving = removingIds.has(suggestion.id);

          return (
            <AutopilotSuggestion
              key={suggestion.id}
              icon={meta.icon}
              title={suggestion.isError ? "Unable to process" : meta.label}
              description={suggestion.text}
              className={
                isRemoving
                  ? "animate-out fade-out slide-out-to-right-2 duration-300"
                  : undefined
              }
              variant={suggestion.isError ? "warning" : "default"}
              actions={
                suggestion.isError
                  ? [
                      {
                        label: "Dismiss",
                        onClick: () => {
                          handleDiscardSuggestion(suggestion.id);
                        },
                        variant: "outline",
                      },
                    ]
                  : [
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
                    ]
              }
            />
          );
        })}

      {/* Show variants if available (only when language is selected) */}
      {currentLanguage && variants.length > 0 ? (
        <AutopilotSuggestion
          icon={AutopilotActions.suggestVariants().icon}
          title="Variants"
          description={
            <div className="space-y-3 mt-2">
              <RadioGroup value={selectedVariant} onValueChange={setSelectedVariant}>
                {variants.map((variant, index) => (
                  <div key={index} className="flex gap-2">
                    <RadioGroupItem
                      className="mt-0.5"
                      value={variant}
                      id={`variant-${index}`}
                    />
                    <label
                      className="text-sm cursor-pointer flex-1"
                      htmlFor={`variant-${index}`}
                    >
                      {variant}
                    </label>
          </div>
                ))}
              </RadioGroup>
          </div>
          }
          actions={[
            {
              label: "Use variant",
              onClick: handleUseSelectedVariant,
              variant: "outline",
            },
            {
              label: "Discard all",
              onClick: handleDiscardVariants,
              variant: "ghost",
            },
          ]}
        />
      ) : null}

      {/* Loading skeleton (only when language is selected) */}
      {currentLanguage && isGenerating ? (
        <AutopilotSuggestionSkeleton />
      ) : null}
    </AutopilotSuggestionsList>
  );
};
