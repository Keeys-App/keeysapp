import { type FC, useState, useEffect, useCallback, useMemo } from "react";
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
import { SET_TRANSLATION, GET_KEY } from "@/graphql/keys";
import { toast } from "sonner";
import { useSaving, useSavingStore } from "@/stores";
import { useTranslationEditor } from "@/contexts";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";
import { Sparkles } from "lucide-react";

type PluralForm = "zero" | "one" | "two" | "few" | "many" | "other";
type PluralValue = Partial<Record<PluralForm, string>>;

/**
 * Parse plural value from JSON string to object
 */
const parsePluralValue = (value: string): PluralValue => {
  if (!value) {
    return {};
  }
  try {
    const parsed = JSON.parse(value);
    if (typeof parsed === "object" && parsed !== null) {
      return parsed as PluralValue;
    }
    return {};
  } catch {
    return {};
  }
};

type WidgetType = "suggestion" | "context" | "context-edit" | "variants";

type SuggestionType = "translate" | "rephrase" | "shorten";

interface BaseWidget {
  id: string;
  type: WidgetType;
  isRemoving?: boolean;
}

interface SuggestionWidget extends BaseWidget {
  type: "suggestion";
  suggestionType: SuggestionType;
  text: string;
  isError?: boolean;
  reason?: string;
}

interface ContextWidget extends BaseWidget {
  type: "context";
  text: string;
}

interface ContextEditWidget extends BaseWidget {
  type: "context-edit";
  value: string;
}

interface VariantsWidget extends BaseWidget {
  type: "variants";
  variants: string[];
  selectedVariant: string;
}

type Widget =
  | SuggestionWidget
  | ContextWidget
  | ContextEditWidget
  | VariantsWidget;

interface KeyAiProps {
  currentKey: TranslationKey | null;
  isLoading?: boolean;
  currentLanguage?: Language | null;
  currentLanguageValue?: string;
  defaultLanguage?: Language | null;
  defaultLanguageValue?: string;
  /** All project languages for autotranslate feature */
  projectLanguages?: Language[];
}

/**
 * Component for displaying translation suggestions and context
 * Shows AI-powered suggestions for translation and improvement
 */
export const KeyAi: FC<KeyAiProps> = ({
  currentKey,
  isLoading = false,
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
  projectLanguages = [],
}) => {
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();
  const { editorRef, editingPluralForm } = useTranslationEditor();
  const [isAutotranslating, setIsAutotranslating] = useState(false);
  
  // For plural keys, parse values to get form-specific text
  const isPlural = currentKey?.isPlural ?? false;
  
  // Get the actual text to translate/work with
  const { sourceText, currentText, fullSourcePluralValue, hasSourceForForm } = useMemo(() => {
    if (!isPlural || !editingPluralForm) {
      // Non-plural key - use values as-is
      return {
        sourceText: defaultLanguageValue || "",
        currentText: currentLanguageValue || "",
        fullSourcePluralValue: null as PluralValue | null,
        hasSourceForForm: true,
      };
    }
    
    // Plural key - extract text for the specific form
    const defaultPluralValue = parsePluralValue(defaultLanguageValue || "");
    const currentPluralValue = parsePluralValue(currentLanguageValue || "");
    
    // Check if the source has the specific form we're editing
    const formText = defaultPluralValue[editingPluralForm];
    
    // If source doesn't have this form, use "other" or first available form as reference
    // This is common when translating from English (one/other) to Russian (one/few/many/other)
    let bestSourceText = formText || "";
    if (!formText) {
      // Try to find best fallback: other > one > first available
      bestSourceText = defaultPluralValue.other 
        || defaultPluralValue.one 
        || Object.values(defaultPluralValue)[0] 
        || "";
    }
    
    return {
      sourceText: bestSourceText,
      currentText: currentPluralValue[editingPluralForm] || "",
      fullSourcePluralValue: defaultPluralValue,
      hasSourceForForm: !!formText,
    };
  }, [isPlural, editingPluralForm, defaultLanguageValue, currentLanguageValue]);

  // Unified state for all widgets
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [customContext, setCustomContext] = useState<string>("");

  // AI mutations
  const [translateMutation] = useMutation<AiTranslateData>(AI_TRANSLATE);
  const [rephraseMutation] = useMutation<AiRephraseData>(AI_REPHRASE);
  const [shortenMutation] = useMutation<AiShortenData>(AI_SHORTEN);
  const [variantsMutation] =
    useMutation<AiSuggestVariantsData>(AI_SUGGEST_VARIANTS);

  // Calculate empty languages (languages without translations)
  const emptyLanguages = useMemo(() => {
    if (!currentKey || !defaultLanguage || !defaultLanguageValue) {
      return [];
    }
    
    const existingTranslations = new Set(
      currentKey.translations
        .filter((t) => t.value && t.value.trim() !== "")
        .map((t) => t.language)
    );
    
    return projectLanguages.filter(
      (lang) => !lang.default && !existingTranslations.has(lang.code)
    );
  }, [currentKey, defaultLanguage, defaultLanguageValue, projectLanguages]);

  // Mutation for saving translations
  const [setTranslation] = useMutation(SET_TRANSLATION, {
    refetchQueries: currentKey ? [{ query: GET_KEY, variables: { id: currentKey.id } }] : [],
  });

  // Autotranslate all empty languages
  const handleAutotranslateAll = async () => {
    if (!currentKey || !defaultLanguage || !defaultLanguageValue || emptyLanguages.length === 0) {
      return;
    }

    setIsAutotranslating(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const lang of emptyLanguages) {
        try {
          let translatedValue: string;

          if (isPlural) {
            // For plural keys, translate each form separately
            const sourcePluralValue = parsePluralValue(defaultLanguageValue);
            const translatedPluralValue: PluralValue = {};

            // Plural form explanations
            const pluralFormExplanations: Record<PluralForm, string> = {
              zero: "for count = 0",
              one: "for count = 1 (singular)",
              two: "for count = 2 (dual)",
              few: "for count = 2-4 (e.g. '2 задачи' in Russian)",
              many: "for count = 5-20 (e.g. '5 задач' in Russian)",
              other: "for other counts (default form)",
            };

            // Translate each plural form for this language
            for (const form of lang.pluralForms) {
              try {
                // Find best source text for this form
                const sourceFormText = sourcePluralValue[form] 
                  || sourcePluralValue.other 
                  || sourcePluralValue.one 
                  || Object.values(sourcePluralValue)[0] 
                  || "";

                if (!sourceFormText) {
                  continue;
                }

                // Context with plural form explanation
                const formContext = [
                  `Translate for "${form}" plural form (${pluralFormExplanations[form]}).`,
                  `Adapt the noun/verb endings for this specific plural form in ${lang.name}.`,
                  `Keep all {variables} unchanged.`,
                ].join(" ");

                const result = await translateMutation({
                  variables: {
                    input: {
                      text: sourceFormText,
                      targetLanguage: lang.name,
                      sourceLanguage: defaultLanguage.name,
                      context: formContext,
                    },
                  },
                });

                if (result.data?.aiTranslate.success && result.data.aiTranslate.text) {
                  translatedPluralValue[form] = result.data.aiTranslate.text;
                }
              } catch (formError) {
                // Log but continue with other forms
                console.error(`Failed to translate ${form} form for ${lang.name}:`, formError);
              }
            }

            // Serialize plural value to JSON
            const filtered = Object.fromEntries(
              Object.entries(translatedPluralValue).filter(([, v]) => v !== "")
            );
            translatedValue = Object.keys(filtered).length > 0 ? JSON.stringify(filtered) : "";
          } else {
            // For regular keys, translate directly
            const result = await translateMutation({
              variables: {
                input: {
                  text: defaultLanguageValue,
                  targetLanguage: lang.name,
                  sourceLanguage: defaultLanguage.name,
                  context: customContext || currentKey.description || undefined,
                },
              },
            });

            if (result.data?.aiTranslate.success && result.data.aiTranslate.text) {
              translatedValue = result.data.aiTranslate.text;
            } else {
              errorCount++;
              continue;
            }
          }

          if (translatedValue) {
            // Save the translation
            await setTranslation({
              variables: {
                input: {
                  keyId: currentKey.id,
                  value: translatedValue,
                  language: lang.code,
                },
              },
            });
            successCount++;
          } else {
            errorCount++;
          }
        } catch {
          errorCount++;
        }
      }

      if (successCount > 0) {
        toast(`Translated to ${successCount} language${successCount > 1 ? "s" : ""}`);
      }
      if (errorCount > 0) {
        toast(`Failed to translate ${errorCount} language${errorCount > 1 ? "s" : ""}`);
      }
    } finally {
      setIsAutotranslating(false);
    }
  };

  // Widget management functions
  const addWidget = useCallback((widget: Widget) => {
    setWidgets((prev) => [...prev, widget]);
  }, []);

  const removeWidget = useCallback((id: string) => {
    // Mark as removing for animation
    setWidgets((prev) =>
      prev.map((w) => {
        if (w.id === id) {
          return { ...w, isRemoving: true };
        }
        return w;
      })
    );

    // Remove from state after animation completes
    setTimeout(() => {
      setWidgets((prev) => prev.filter((w) => w.id !== id));
    }, 300); // Match animation duration
  }, []);

  const updateWidget = useCallback((id: string, updates: Partial<Widget>) => {
    setWidgets((prev) =>
      prev.map((w) => {
        if (w.id === id) {
          return { ...w, ...updates } as Widget;
        }
        return w;
      })
    );
  }, []);

  // Clear widgets when language or plural form changes
  useEffect(() => {
    setWidgets([]);
  }, [currentLanguage?.code, currentLanguageValue, editingPluralForm]);

  // Auto-populate context from key description when key changes
  useEffect(() => {
    if (currentKey?.description) {
      setCustomContext(currentKey.description);
    } else {
      setCustomContext("");
    }
  }, [currentKey?.id]);

  const handleTranslate = async () => {
    if (!sourceText || !currentLanguage || !defaultLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        setIsGenerating(true);
        
        // Build context for plural forms
        let translationContext = customContext || "";
        
        if (isPlural && editingPluralForm && fullSourcePluralValue) {
          // Build explanation of source plural forms
          const sourceFormsDescription = Object.entries(fullSourcePluralValue)
            .map(([form, text]) => `  - "${form}": "${text}"`)
            .join("\n");
          
          // Explain plural form usage
          const pluralFormExplanations: Record<PluralForm, string> = {
            zero: "used when count is 0",
            one: "used for singular (count = 1)",
            two: "used for dual (count = 2)",
            few: "used for small quantities (e.g., 2-4 in Russian)",
            many: "used for larger quantities (e.g., 5-20 in Russian)",
            other: "used as default/fallback for other quantities",
          };
          
          const formExplanation = pluralFormExplanations[editingPluralForm] || "";
          
          const pluralContext = [
            `ICU MESSAGEFORMAT PLURAL TRANSLATION:`,
            `This is a UI localization task using ICU MessageFormat standard.`,
            `You are translating the "${editingPluralForm}" plural form for ${currentLanguage.name}.`,
            ``,
            `ICU PLURAL FORMS:`,
            `- zero: count is 0`,
            `- one: singular (count = 1)`,
            `- two: dual (count = 2)`,
            `- few: small quantities (2-4 in Slavic languages)`,
            `- many: larger quantities (5-20 in Slavic languages)`,
            `- other: default/fallback for remaining quantities`,
            ``,
            `You are translating: "${editingPluralForm}" form (${formExplanation})`,
            ``,
            `Original ${defaultLanguage.name} plural forms:`,
            sourceFormsDescription,
            ``,
            hasSourceForForm
              ? `Translate the "${editingPluralForm}" form directly.`
              : `The source language doesn't have "${editingPluralForm}" form. Generate appropriate ${currentLanguage.name} translation based on the context above.`,
            ``,
            `CRITICAL RULES:`,
            `1. This is valid ICU localization text - ALWAYS translate it.`,
            `2. PRESERVE all ICU variables: {count}, {name}, {user}, etc. EXACTLY as-is.`,
            `3. Only translate human-readable text around variables.`,
            `4. Adapt grammar for the specific plural form in ${currentLanguage.name}.`,
            ``,
            `Examples:`,
            `- "{count} task" (one) → "{count} задача" (Russian one)`,
            `- "{count} tasks" (other) → "{count} задач" (Russian many)`,
            `- "{count} tasks" (few) → "{count} задачи" (Russian few)`,
            ``,
            `Return ONLY the translated text for "${editingPluralForm}" form.`,
          ].join("\n");
          
          translationContext = translationContext 
            ? `${translationContext}\n\n${pluralContext}`
            : pluralContext;
        }
        
        const result = await translateMutation({
          variables: {
            input: {
              text: sourceText,
              targetLanguage: currentLanguage.name,
              sourceLanguage: defaultLanguage.name,
              context: translationContext || undefined,
            },
          },
        });

        if (result.data?.aiTranslate.success && result.data.aiTranslate.text) {
          const newWidget: SuggestionWidget = {
            id: `translate-${Date.now()}`,
            type: "suggestion",
            suggestionType: "translate",
            text: result.data.aiTranslate.text,
          };
          addWidget(newWidget);
          toast("Translation generated");
        } else if (result.data?.aiTranslate.reason) {
          // AI couldn't process - show as info card
          const errorWidget: SuggestionWidget = {
            id: `translate-error-${Date.now()}`,
            type: "suggestion",
            suggestionType: "translate",
            text: result.data.aiTranslate.reason,
            isError: true,
            reason: result.data.aiTranslate.reason,
          };
          addWidget(errorWidget);
        } else {
          toast(result.data?.aiTranslate.error || "Translation failed");
        }
      } catch (error) {
        toast("Translation failed. Please try again.");
      } finally {
        setIsGenerating(false);
      }
    }, "Translating...");
  };

  const handleRephrase = async () => {
    if (!currentText || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        setIsGenerating(true);
        
        // Build context for plural forms
        let rephraseContext = customContext || "";
        
        if (isPlural && editingPluralForm) {
          const pluralContext = [
            `PLURAL FORM REPHRASING:`,
            `You are rephrasing the "${editingPluralForm}" plural form in ${currentLanguage.name}.`,
            `Return ONLY the rephrased text, NOT a JSON object.`,
          ].join("\n");
          
          rephraseContext = rephraseContext 
            ? `${rephraseContext}\n\n${pluralContext}`
            : pluralContext;
        }
        
        const result = await rephraseMutation({
          variables: {
            input: {
              text: currentText,
              language: currentLanguage.name,
              context: rephraseContext || undefined,
            },
          },
        });

        if (result.data?.aiRephrase.success && result.data.aiRephrase.text) {
          const newWidget: SuggestionWidget = {
            id: `rephrase-${Date.now()}`,
            type: "suggestion",
            suggestionType: "rephrase",
            text: result.data.aiRephrase.text,
          };
          addWidget(newWidget);
          toast("Rephrase generated");
        } else if (result.data?.aiRephrase.reason) {
          // AI couldn't process - show as info card
          const errorWidget: SuggestionWidget = {
            id: `rephrase-error-${Date.now()}`,
            type: "suggestion",
            suggestionType: "rephrase",
            text: result.data.aiRephrase.reason,
            isError: true,
            reason: result.data.aiRephrase.reason,
          };
          addWidget(errorWidget);
        } else {
          toast(result.data?.aiRephrase.error || "Rephrase failed");
        }
      } catch (error) {
        toast("Rephrase failed. Please try again.");
      } finally {
        setIsGenerating(false);
      }
    }, "Rephrasing...");
  };

  const handleShorten = async () => {
    if (!currentText || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        setIsGenerating(true);
        
        // Build context for plural forms
        let shortenContext = customContext || "";
        
        if (isPlural && editingPluralForm) {
          const pluralContext = [
            `PLURAL FORM SHORTENING:`,
            `You are shortening the "${editingPluralForm}" plural form in ${currentLanguage.name}.`,
            `Return ONLY the shortened text, NOT a JSON object.`,
          ].join("\n");
          
          shortenContext = shortenContext 
            ? `${shortenContext}\n\n${pluralContext}`
            : pluralContext;
        }
        
        const result = await shortenMutation({
          variables: {
            input: {
              text: currentText,
              language: currentLanguage.name,
              context: shortenContext || undefined,
            },
          },
        });

        if (result.data?.aiShorten.success && result.data.aiShorten.text) {
          const newWidget: SuggestionWidget = {
            id: `shorten-${Date.now()}`,
            type: "suggestion",
            suggestionType: "shorten",
            text: result.data.aiShorten.text,
          };
          addWidget(newWidget);
          toast("Shortened version generated");
        } else if (result.data?.aiShorten.reason) {
          // AI couldn't process - show as info card
          const errorWidget: SuggestionWidget = {
            id: `shorten-error-${Date.now()}`,
            type: "suggestion",
            suggestionType: "shorten",
            text: result.data.aiShorten.reason,
            isError: true,
            reason: result.data.aiShorten.reason,
          };
          addWidget(errorWidget);
        } else {
          toast(result.data?.aiShorten.error || "Shorten failed");
        }
      } catch (error) {
        toast("Shorten failed. Please try again.");
      } finally {
        setIsGenerating(false);
      }
    }, "Shortening...");
  };

  const handleSuggestVariants = async () => {
    if (!currentText || !currentLanguage) {
      return;
    }

    await withSaving(async () => {
      try {
        setIsGenerating(true);
        
        // Build context for plural forms
        let variantsContext = customContext || "";
        
        if (isPlural && editingPluralForm) {
          const pluralContext = [
            `PLURAL FORM VARIANTS:`,
            `You are generating variants for the "${editingPluralForm}" plural form in ${currentLanguage.name}.`,
            `Return ONLY text variants, NOT JSON objects.`,
          ].join("\n");
          
          variantsContext = variantsContext 
            ? `${variantsContext}\n\n${pluralContext}`
            : pluralContext;
        }
        
        const result = await variantsMutation({
          variables: {
            input: {
              text: currentText,
              language: currentLanguage.name,
              context: variantsContext || undefined,
              count: 3,
            },
          },
        });

        if (
          result.data?.aiSuggestVariants.success &&
          result.data.aiSuggestVariants.variants.length > 0
        ) {
          const variantsArray = result.data.aiSuggestVariants.variants;
          const newWidget: VariantsWidget = {
            id: `variants-${Date.now()}`,
            type: "variants",
            variants: variantsArray,
            selectedVariant: variantsArray[0], // Auto-select first variant
          };
          addWidget(newWidget);
          toast("Variants generated");
        } else if (result.data?.aiSuggestVariants.reason) {
          // AI couldn't process - show as info card
          const errorWidget: SuggestionWidget = {
            id: `variants-error-${Date.now()}`,
            type: "suggestion",
            suggestionType: "rephrase",
            text: result.data.aiSuggestVariants.reason,
            isError: true,
            reason: result.data.aiSuggestVariants.reason,
          };
          addWidget(errorWidget);
        } else {
          toast(
            result.data?.aiSuggestVariants.error || "Variant generation failed"
          );
        }
      } catch (error) {
        toast("Variant generation failed. Please try again.");
      } finally {
        setIsGenerating(false);
      }
    }, "Generating variants...");
  };

  const handleAddContext = () => {
    const editWidget: ContextEditWidget = {
      id: "context-edit",
      type: "context-edit",
      value: customContext,
    };
    addWidget(editWidget);
  };

  const handleSaveContext = (widgetId: string, value: string) => {
    setCustomContext(value.trim());
    removeWidget(widgetId);

    // If there's saved context, add context view widget
    if (value.trim()) {
      const contextWidget: ContextWidget = {
        id: "context-view",
        type: "context",
        text: value.trim(),
      };
      // Add after animation completes
      setTimeout(() => {
        addWidget(contextWidget);
      }, 300);
    }

    toast("Context saved");
  };

  const handleCancelContext = (widgetId: string) => {
    removeWidget(widgetId);
  };

  const handleDiscardContext = (widgetId: string) => {
    setCustomContext("");
    removeWidget(widgetId);
    toast("Context removed");
  };

  const handleUseSuggestion = (text: string) => {
    if (!editorRef) {
      toast("Please open the translation editor first");
      return;
    }

    // Insert text into the editor
    editorRef.insertText(text);

    toast("Suggestion applied");
  };

  const handleEditContext = (widgetId: string) => {
    // Find and replace context view widget with context edit widget
    const contextWidget = widgets.find(
      (w) => w.id === widgetId
    ) as ContextWidget;
    if (contextWidget) {
      removeWidget(widgetId);

      // Add edit widget after animation
      setTimeout(() => {
        const editWidget: ContextEditWidget = {
          id: "context-edit",
          type: "context-edit",
          value: contextWidget.text,
        };
        addWidget(editWidget);
      }, 300);
    }
  };

  // Get type-specific icon and label
  const getSuggestionMeta = (type: SuggestionType) => {
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

  // Sync context widget with customContext state on mount and key change
  useEffect(() => {
    if (customContext) {
      const hasContextWidget = widgets.some((w) => w.type === "context");
      const hasContextEditWidget = widgets.some(
        (w) => w.type === "context-edit"
      );

      if (!hasContextWidget && !hasContextEditWidget) {
        // Add context view widget if context exists but no widget is shown
        const contextWidget: ContextWidget = {
          id: "context-view",
          type: "context",
          text: customContext,
        };
        setWidgets((prev) => [...prev, contextWidget]);
      }
    }
  }, [currentKey?.id]);

  let card: React.ReactNode | null = null;

  // For plural keys, require a specific form to be selected
  const isPluralWithoutForm = isPlural && !editingPluralForm;
  
  // If no language is being edited, show autotranslate option or tip
  if (!currentLanguage) {
    if (emptyLanguages.length > 0 && defaultLanguageValue) {
      // Show autotranslate button when there are empty languages
      card = (
        <AutopilotCard
          isPending={isAutotranslating}
          title="Autotranslate"
          description={
            <>
              Translate to {emptyLanguages.length} empty language{emptyLanguages.length > 1 ? "s" : ""} using AI.
            </>
          }
          actions={[
            {
              label: `Translate all (${emptyLanguages.length})`,
              icon: Sparkles,
              onClick: handleAutotranslateAll,
              variant: "default",
            },
          ]}
        />
      );
    } else {
      card = (
        <AutopilotCard
          isDisabled
          title="Tip"
          description="Start editing any translation field to see suggestions."
        />
      );
    }
  } else if (isPluralWithoutForm) {
    // Plural key but no form selected
    card = (
      <AutopilotCard
        isDisabled
        title="Tip"
        description="Click on a plural form to edit and get AI suggestions."
      />
    );
  } else if (currentText) {
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
      sourceText
    ) {
      enhancementActions.unshift(AutopilotActions.translate(handleTranslate));
    }

    const isDefaultLanguage = currentLanguage?.code === defaultLanguage?.code;

    card = (
      <AutopilotCard
        title={isPlural && editingPluralForm ? `Suggestions (${editingPluralForm})` : "Suggestions"}
        isPending={isGenerating}
        description={
          isDefaultLanguage ? (
            <>
              Improve or rewrite the <LanguageMark language={currentLanguage} /> text
              {isPlural && editingPluralForm ? ` for "${editingPluralForm}" form` : ""}.
            </>
          ) : (
            <>
              Improve or rewrite the <LanguageMark language={currentLanguage} />{" "}
              translation{isPlural && editingPluralForm ? ` for "${editingPluralForm}" form` : ""}.
            </>
          )
        }
        actions={enhancementActions}
      />
    );
  } else if (!sourceText) {
    // No default value to translate from
    card = (
      <AutopilotCard
        isDisabled
        description={
          isPlural && editingPluralForm
            ? `Add at least one plural form in the default language first.`
            : "Add a translation in the default language first to enable suggestions."
        }
      />
    );
  } else {
    // Show translate action for empty translation
    // For plural, show hint if we're using a different form as source
    const showPluralInfo = isPlural && editingPluralForm;
    const pluralHint = showPluralInfo && !hasSourceForForm
      ? " (will generate based on available forms)"
      : "";
    
    card = (
      <AutopilotCard
        isPending={isGenerating}
        title={showPluralInfo ? `Translate (${editingPluralForm})` : undefined}
        description={
          <>
            Create a{" "}
            <LanguageMark language={currentLanguage} />{" "}
            translation{showPluralInfo ? ` for "${editingPluralForm}" form` : ""}
            {pluralHint}{" "}
            using the default{" "}
            <LanguageMark language={defaultLanguage} />{" "}
            as the source.
          </>
        }
        actions={[
          AutopilotActions.translate(handleTranslate),
          AutopilotActions.addContext(handleAddContext),
        ]}
      />
    );
  }

  // Render widget function
  const renderWidget = (widget: Widget) => {
    switch (widget.type) {
      case "suggestion": {
        const meta = getSuggestionMeta(widget.suggestionType);
        return (
          <AutopilotSuggestion
            key={widget.id}
            icon={meta.icon}
            title={widget.isError ? "Unable to process" : meta.label}
            description={widget.text}
            className={
              widget.isRemoving
                ? "animate-out fade-out slide-out-to-right-2 duration-300"
                : undefined
            }
            variant={widget.isError ? "warning" : "default"}
            actions={
              widget.isError
                ? [
                    {
                      label: "Dismiss",
                      onClick: () => {
                        removeWidget(widget.id);
                      },
                      variant: "outline",
                    },
                  ]
                : [
                    {
                      label: "Insert",
                      onClick: () => {
                        handleUseSuggestion(widget.text);
                      },
                      variant: "outline",
                    },
                    {
                      label: "Discard",
                      onClick: () => {
                        removeWidget(widget.id);
                      },
                      variant: "ghost",
                    },
                  ]
            }
          />
        );
      }

      case "context": {
        return (
          <AutopilotSuggestion
            key={widget.id}
            icon={AutopilotActions.addContext().icon}
            title="Context"
            description={widget.text}
            className={
              widget.isRemoving
                ? "animate-out fade-out slide-out-to-right-2 duration-300"
                : undefined
            }
            actions={[
              {
                label: "Edit",
                onClick: () => {
                  handleEditContext(widget.id);
                },
                variant: "outline",
              },
              {
                label: "Remove",
                onClick: () => {
                  handleDiscardContext(widget.id);
                },
                variant: "ghost",
              },
            ]}
            variant="none"
          />
        );
      }

      case "context-edit": {
        return (
          <AutopilotSuggestion
            key={widget.id}
            icon={AutopilotActions.addContext().icon}
            title="Context for AI"
            description={
              <Textarea
                placeholder="e.g., Used in the checkout flow to confirm payment. Should be formal and reassuring."
                value={widget.value}
                onChange={(e) => {
                  updateWidget(widget.id, {
                    value: e.target.value,
                  } as Partial<Widget>);
                }}
                rows={4}
                className="resize-none mt-2"
                disabled={isSaving}
                autoFocus
              />
            }
            className={
              widget.isRemoving
                ? "animate-out fade-out slide-out-to-right-2 duration-300"
                : undefined
            }
            actions={[
              {
                label: "Save",
                onClick: () => {
                  handleSaveContext(widget.id, widget.value);
                },
                variant: "outline",
              },
              {
                label: "Cancel",
                onClick: () => {
                  handleCancelContext(widget.id);
                },
                variant: "ghost",
              },
            ]}
            variant="none"
          />
        );
      }

      case "variants": {
        return (
          <AutopilotSuggestion
            key={widget.id}
            icon={AutopilotActions.suggestVariants().icon}
            title="Variants"
            description={
              <div className="space-y-3 mt-2">
                <RadioGroup
                  value={widget.selectedVariant}
                  onValueChange={(value) => {
                    updateWidget(widget.id, {
                      selectedVariant: value,
                    } as Partial<Widget>);
                  }}
                >
                  {widget.variants.map((variant, index) => (
                    <div key={index} className="flex gap-2">
                      <RadioGroupItem
                        className="mt-0.5"
                        value={variant}
                        id={`${widget.id}-variant-${index}`}
                      />
                      <label
                        className="text-sm cursor-pointer flex-1"
                        htmlFor={`${widget.id}-variant-${index}`}
                      >
                        {variant}
                      </label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            }
            className={
              widget.isRemoving
                ? "animate-out fade-out slide-out-to-right-2 duration-300"
                : undefined
            }
            actions={[
              {
                label: "Insert",
                onClick: () => {
                  if (widget.selectedVariant && editorRef) {
                    editorRef.insertText(widget.selectedVariant);
                    toast("Variant inserted into editor");
                  } else if (!editorRef) {
                    toast("Please open the translation editor first");
                  }
                },
                variant: "outline",
              },
              {
                label: "Discard all",
                onClick: () => {
                  removeWidget(widget.id);
                },
                variant: "ghost",
              },
            ]}
          />
        );
      }
    }
  };

  return (
    <AutopilotSuggestionsList>
      {card}

      {/* Render all widgets */}
      {currentLanguage && widgets.map(renderWidget)}

      {/* Loading skeleton (only when language is selected) */}
      {currentLanguage && isGenerating ? <AutopilotSuggestionSkeleton /> : null}
    </AutopilotSuggestionsList>
  );
};

const LanguageMark: FC<{ language?: Language | null }> = ({ language }) => {
  return language ? (
    <span className="text-indigo-500">{language.name}</span>
  ) : null;
};
