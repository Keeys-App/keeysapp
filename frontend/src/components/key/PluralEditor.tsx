import { type FC, useState, useEffect, useMemo, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { useSavingStore } from '@/stores';
import { cn } from '@/lib/utils';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { ChevronDown, Code } from 'lucide-react';
import {
  type PluralForm,
  type PluralForms,
  parseICUPlural,
  buildICUPlural,
  getPluralFormsForLanguage,
  getPluralFormLabel,
  getPluralFormExamples,
  validatePluralForms,
} from '@/lib/icu-plural';

interface PluralEditorProps {
  value: string;
  languageCode: string;
  direction?: 'ltr' | 'rtl';
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  hasChanges: boolean;
  defaultLanguageValue?: string;
}

/**
 * Structured editor for ICU plural format.
 * Displays separate fields for each plural form (one, few, many, other).
 * Shows ICU syntax preview.
 */
export const PluralEditor: FC<PluralEditorProps> = ({
  value,
  languageCode,
  direction = 'ltr',
  onChange,
  onSave,
  onCancel,
  hasChanges,
  defaultLanguageValue,
}) => {
  const { isSaving } = useSavingStore();
  const [showPreview, setShowPreview] = useState(false);

  // Parse the initial value
  const parsedInitial = useMemo(() => parseICUPlural(value), [value]);

  // Local state for editing
  const [variable, setVariable] = useState(parsedInitial?.variable || 'count');
  const [forms, setForms] = useState<Partial<PluralForms>>(() => {
    if (parsedInitial?.forms) {
      return parsedInitial.forms;
    }
    // Initialize with empty forms for the language
    const requiredForms = getPluralFormsForLanguage(languageCode);
    const emptyForms: Partial<PluralForms> = {};
    for (const form of requiredForms) {
      emptyForms[form] = '';
    }
    return emptyForms;
  });

  // Get required forms for this language
  const requiredForms = useMemo(
    () => getPluralFormsForLanguage(languageCode),
    [languageCode]
  );

  // Build the ICU string from current state
  const builtValue = useMemo(() => {
    // Only build if we have at least 'other' form
    if (!forms.other) {
      return '';
    }
    return buildICUPlural(variable, forms as PluralForms);
  }, [variable, forms]);

  // Validation errors
  const validationErrors = useMemo(
    () => validatePluralForms(forms, languageCode),
    [forms, languageCode]
  );

  // Update parent when value changes
  useEffect(() => {
    if (builtValue && builtValue !== value) {
      onChange(builtValue);
    }
  }, [builtValue, value, onChange]);

  // Handle form change
  const handleFormChange = useCallback((form: PluralForm, formValue: string) => {
    setForms((prev) => ({
      ...prev,
      [form]: formValue,
    }));
  }, []);

  // Copy from default language
  const handleCopyFromDefault = useCallback(() => {
    if (defaultLanguageValue) {
      const parsed = parseICUPlural(defaultLanguageValue);
      if (parsed) {
        setVariable(parsed.variable);
        // Copy forms but keep the structure for current language
        const newForms: Partial<PluralForms> = {};
        for (const form of requiredForms) {
          newForms[form] = parsed.forms[form] || parsed.forms.other || '';
        }
        setForms(newForms);
      }
    }
  }, [defaultLanguageValue, requiredForms]);

  const handleSaveClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSave();
  };

  const handleCancelClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCancel();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Esc - Cancel
    if (e.key === 'Escape') {
      e.preventDefault();
      e.stopPropagation();
      onCancel();
      return;
    }

    // Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) - Save
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      e.stopPropagation();
      if (hasChanges && !isSaving && validationErrors.length === 0) {
        onSave();
      }
      return;
    }
  };

  return (
    <div className="bg-background space-y-3 p-3" onKeyDown={handleKeyDown}>
      {/* Variable name input */}
      <div className="flex items-center gap-2">
        <Label htmlFor="plural-variable" className="text-xs text-muted-foreground whitespace-nowrap">
          Variable:
        </Label>
        <Input
          id="plural-variable"
          value={variable}
          onChange={(e) => setVariable(e.target.value)}
          className="h-7 w-24 text-sm font-mono"
          placeholder="count"
        />
        <Badge variant="outline" className="ml-auto text-xs">
          Plural
        </Badge>
      </div>

      {/* Plural forms */}
      <div className="space-y-2">
        {requiredForms.map((form) => {
          const examples = getPluralFormExamples(form, languageCode);
          return (
            <div key={form} className="space-y-1">
              <div className="flex items-center gap-2">
                <Label
                  htmlFor={`plural-${form}`}
                  className="text-xs font-medium w-20"
                >
                  {getPluralFormLabel(form)}
                </Label>
                {examples ? (
                  <span className="text-xs text-muted-foreground">
                    e.g. {examples}
                  </span>
                ) : null}
              </div>
              <Textarea
                id={`plural-${form}`}
                value={forms[form] || ''}
                onChange={(e) => handleFormChange(form, e.target.value)}
                className={cn(
                  'min-h-[60px] text-sm font-mono resize-none',
                  direction === 'rtl' && 'text-right'
                )}
                dir={direction}
                placeholder={`{${variable}}`}
              />
            </div>
          );
        })}
      </div>

      {/* ICU Preview */}
      <Collapsible open={showPreview} onOpenChange={setShowPreview}>
        <CollapsibleTrigger asChild>
          <Button variant="ghost" size="sm" className="w-full justify-between">
            <span className="flex items-center gap-2">
              <Code className="h-3 w-3" />
              ICU Preview
            </span>
            <ChevronDown
              className={cn(
                'h-4 w-4 transition-transform',
                showPreview && 'rotate-180'
              )}
            />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <pre className="mt-2 p-2 bg-muted rounded text-xs font-mono overflow-x-auto whitespace-pre-wrap break-all">
            {builtValue || '(empty)'}
          </pre>
        </CollapsibleContent>
      </Collapsible>

      {/* Validation errors */}
      {validationErrors.length > 0 ? (
        <div className="text-xs text-destructive space-y-1">
          {validationErrors.map((error, i) => (
            <div key={i}>• {error}</div>
          ))}
        </div>
      ) : null}

      {/* Action buttons */}
      <div className="flex gap-2 pt-2 border-t">
        <Button
          onClick={handleSaveClick}
          disabled={isSaving || !hasChanges || validationErrors.length > 0}
          variant="default"
          size="sm"
        >
          Save
        </Button>
        <Button
          onClick={handleCancelClick}
          disabled={isSaving}
          variant="outline"
          size="sm"
        >
          Cancel
        </Button>
        {defaultLanguageValue && !forms.other ? (
          <Button
            onClick={handleCopyFromDefault}
            disabled={isSaving}
            variant="ghost"
            size="sm"
          >
            Copy from default
          </Button>
        ) : null}
      </div>
    </div>
  );
};

