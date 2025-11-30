import type { FC } from "react";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Language } from "@/types/project";
import type { ImportFormat } from "./utils/importFormats";

export type ImportStrategy = "merge" | "replace";

export interface ImportOptions {
  format: ImportFormat;
  language: string;
  strategy: ImportStrategy;
}

interface ImportSettingsProps {
  languages: Language[];
  options: ImportOptions;
  onOptionsChange: (options: ImportOptions) => void;
}

export const ImportSettings: FC<ImportSettingsProps> = ({
  languages,
  options,
  onOptionsChange,
}) => {
  const handleLanguageChange = (language: string) => {
    onOptionsChange({ ...options, language });
  };

  const handleFormatChange = (format: ImportFormat) => {
    onOptionsChange({ ...options, format });
  };

  const handleStrategyChange = (strategy: ImportStrategy) => {
    onOptionsChange({ ...options, strategy });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Language Selection */}
        <div className="space-y-2">
          <Label htmlFor="language">Target Language</Label>
          <Select value={options.language} onValueChange={handleLanguageChange}>
            <SelectTrigger id="language">
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              {languages.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  {lang.flag} {lang.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            Select the language for imported translations
          </p>
        </div>

        {/* Format Selection */}
        <div className="space-y-2">
          <Label htmlFor="format">Format</Label>
          <Select value={options.format} onValueChange={handleFormatChange}>
            <SelectTrigger id="format">
              <SelectValue placeholder="Select format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="i18n">i18n (JSON)</SelectItem>
              <SelectItem value="ios-strings">iOS Strings (.strings)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Import Strategy */}
        <div className="space-y-3">
          <Label>Import Strategy</Label>
          <RadioGroup
            value={options.strategy}
            onValueChange={handleStrategyChange}
          >
            <div className="flex items-start space-x-2">
              <RadioGroupItem value="merge" id="merge" className="mt-1" />
              <div className="flex-1">
                <Label htmlFor="merge" className="font-normal cursor-pointer">
                  Merge
                </Label>
                <p className="text-xs text-muted-foreground">
                  Add new keys and update existing ones. Keeps keys not in the
                  import.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <RadioGroupItem value="replace" id="replace" className="mt-1" />
              <div className="flex-1">
                <Label htmlFor="replace" className="font-normal cursor-pointer">
                  Replace
                </Label>
                <p className="text-xs text-muted-foreground">
                  Replace all translations for this language with imported ones.
                </p>
              </div>
            </div>
          </RadioGroup>
        </div>
      </CardContent>
    </Card>
  );
};

