import type { FC } from "react";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Language } from "@/types/project";
import type { ExportFormat, ExportOptions } from "./utils/exportFormats";

interface ExportSettingsProps {
  languages: Language[];
  options: ExportOptions;
  onOptionsChange: (options: ExportOptions) => void;
}

export const ExportSettings: FC<ExportSettingsProps> = ({
  languages,
  options,
  onOptionsChange,
}) => {
  const handleLanguageChange = (language: string) => {
    onOptionsChange({ ...options, language });
  };

  const handleFormatChange = (format: ExportFormat) => {
    onOptionsChange({ ...options, format });
  };

  const handleIndentChange = (indent: string) => {
    onOptionsChange({ ...options, indent: parseInt(indent) });
  };

  const handleSortKeysChange = (sortKeys: boolean) => {
    onOptionsChange({ ...options, sortKeys });
  };

  const handleFillEmptyFromSourceChange = (fillEmptyFromSource: boolean) => {
    onOptionsChange({ ...options, fillEmptyFromSource });
  };

  // Get source language name for display
  const sourceLanguageName = languages.find(
    (lang) => lang.code === options.sourceLanguage
  )?.name || options.sourceLanguage;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Export Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Language Selection */}
        <div className="space-y-2">
          <Label htmlFor="language">Language</Label>
          <Select value={options.language} onValueChange={handleLanguageChange}>
            <SelectTrigger id="language">
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              {languages.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  {lang.flag} {lang.name}
                  {lang.code === options.sourceLanguage ? " (source)" : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
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

        {/* Indent Size - only for JSON formats */}
        {options.format === "i18n" ? (
          <div className="space-y-2">
            <Label htmlFor="indent">Indent Size</Label>
            <Select
              value={options.indent.toString()}
              onValueChange={handleIndentChange}
            >
              <SelectTrigger id="indent">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2">2 spaces</SelectItem>
                <SelectItem value="4">4 spaces</SelectItem>
                <SelectItem value="0">Minified</SelectItem>
              </SelectContent>
            </Select>
          </div>
        ) : null}

        {/* Sort Keys */}
        <div className="flex items-center justify-between">
          <Label htmlFor="sort-keys" className="cursor-pointer">
            Sort keys alphabetically
          </Label>
          <Switch
            id="sort-keys"
            checked={options.sortKeys}
            onCheckedChange={handleSortKeysChange}
          />
        </div>

        {/* Fill Empty From Source - only show for non-source languages */}
        {options.language !== options.sourceLanguage ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="fill-empty" className="cursor-pointer">
                Fill empty from source
              </Label>
              <Switch
                id="fill-empty"
                checked={options.fillEmptyFromSource}
                onCheckedChange={handleFillEmptyFromSourceChange}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Use {sourceLanguageName} value when translation is missing
            </p>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
};

