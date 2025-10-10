import { useState, type FC } from 'react';
import { X, Edit2, Check } from 'lucide-react';
import { LANGUAGE_CONFIGS } from '@/types/project';
import type { LanguageConfigInput } from '@/graphql/projects';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Combobox, type ComboboxOption } from '@/components/blocks';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface LanguageConfigEditorProps {
  languages: LanguageConfigInput[];
  onChange: (languages: LanguageConfigInput[]) => void;
  disabled?: boolean;
}

export const LanguageConfigEditor: FC<LanguageConfigEditorProps> = ({
  languages,
  onChange,
  disabled = false,
}) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editingLocale, setEditingLocale] = useState('');

  // Prepare language options for Combobox
  const availableLanguageOptions: ComboboxOption[] = LANGUAGE_CONFIGS
    .filter((lang) => {
      return !languages.some((l) => {
        return l.code === lang.code;
      });
    })
    .map((lang) => {
      return {
        value: lang.code,
        label: `${lang.flag} ${lang.name} (${lang.code})`,
      };
    });

  const handleAddLanguage = (langCode: string) => {
    const langConfig = LANGUAGE_CONFIGS.find((l) => {
      return l.code === langCode;
    });
    if (langConfig) {
      onChange([
        ...languages,
        {
          code: langConfig.code,
          locale: langConfig.locale,
        },
      ]);
    }
  };

  const handleRemoveLanguage = (index: number) => {
    const newLanguages = languages.filter((_, i) => {
      return i !== index;
    });
    onChange(newLanguages);
  };

  const handleStartEdit = (index: number) => {
    setEditingIndex(index);
    setEditingLocale(languages[index].locale);
  };

  const handleSaveEdit = () => {
    if (editingIndex !== null && editingLocale.trim()) {
      const newLanguages = [...languages];
      newLanguages[editingIndex] = {
        ...newLanguages[editingIndex],
        locale: editingLocale.trim(),
      };
      onChange(newLanguages);
      setEditingIndex(null);
      setEditingLocale('');
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditingLocale('');
  };

  const getLanguageInfo = (code: string) => {
    return LANGUAGE_CONFIGS.find((l) => {
      return l.code === code;
    });
  };

  return (
    <div className="space-y-3">
      {/* Selected languages */}
      {languages.length > 0 ? (
        <div className="space-y-2">
          {languages.map((lang, index) => {
            const langInfo = getLanguageInfo(lang.code);
            return (
              <div
                key={`${lang.code}-${index}`}
                className="flex items-center justify-between p-3 border rounded-lg bg-card"
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-2xl">{langInfo?.flag || '🏳️'}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{langInfo?.name || lang.code}</span>
                      <Badge variant="outline" className="text-xs">
                        {lang.code}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Locale: <code className="px-1 py-0.5 bg-muted rounded">{lang.locale}</code>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      return handleStartEdit(index);
                    }}
                    disabled={disabled}
                    title="Edit locale"
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      return handleRemoveLanguage(index);
                    }}
                    disabled={disabled}
                    title="Remove language"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-sm text-muted-foreground p-4 border rounded-lg text-center">
          No languages added yet. Add languages below.
        </div>
      )}

      {/* Language selector */}
      <Combobox
        options={availableLanguageOptions}
        value=""
        onSelect={handleAddLanguage}
        placeholder="Add language..."
        searchPlaceholder="Search languages..."
        emptyText="No language found or all languages already added."
        disabled={disabled}
      />

      {/* Edit locale dialog */}
      <Dialog open={editingIndex !== null} onOpenChange={(open) => {
        if (!open) {
          handleCancelEdit();
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Locale</DialogTitle>
            <DialogDescription>
              Customize the locale for {editingIndex !== null ? languages[editingIndex].code.toUpperCase() : ''}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Locale Code</label>
              <Input
                value={editingLocale}
                onChange={(e) => {
                  return setEditingLocale(e.target.value);
                }}
                placeholder="e.g., en-US, en-GB, pt-BR"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSaveEdit();
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                Examples: en-US, en-GB, es-ES, pt-BR, zh-CN, zh-TW
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleCancelEdit}>
              Cancel
            </Button>
            <Button type="button" onClick={handleSaveEdit} disabled={!editingLocale.trim()}>
              <Check className="h-4 w-4 mr-2" />
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

