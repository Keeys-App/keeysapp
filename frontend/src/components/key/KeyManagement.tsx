import { type FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KeyLogsTimeline } from "./KeyLogsTimeline";
import { KeySettingsForm } from "./KeySettingsForm";
import { KeySettings } from "./KeySettings";
import { KeySuggestions } from "./KeySuggestions";

interface KeyManagementProps {
  selectedKey: TranslationKey;
  projectId: string;
  availableTags?: string[];
  onKeyDeleted?: () => void;
  currentLanguage?: string | null;
  currentLanguageValue?: string;
  defaultLanguage?: string | null;
  defaultLanguageValue?: string;
}

/**
 * Tabs component for displaying different views of a translation key's details.
 * Supports multiple views: suggestions, history, metadata, and settings.
 */
export const KeyManagement: FC<KeyManagementProps> = ({
  selectedKey,
  projectId,
  availableTags = [],
  onKeyDeleted,
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  return (
    <Tabs defaultValue="suggestions" className="h-full flex flex-col">
      <TabsList className="mx-4 mt-4 mb-2 gap-0">
        <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
        <TabsTrigger value="history">History</TabsTrigger>
        <TabsTrigger value="meta">Metadata</TabsTrigger>
        <TabsTrigger value="settings">Settings</TabsTrigger>
      </TabsList>

      <TabsContent value="suggestions" className="flex-1 px-4 pb-4 overflow-auto">
        <KeySuggestions
          currentLanguage={currentLanguage}
          currentLanguageValue={currentLanguageValue}
          defaultLanguage={defaultLanguage}
          defaultLanguageValue={defaultLanguageValue}
        />
      </TabsContent>

      <TabsContent value="history" className="flex-1 px-4 pb-4 overflow-auto">
        <KeyLogsTimeline keyId={selectedKey.id} />
      </TabsContent>

      <TabsContent value="meta" className="flex-1 px-4 pb-4 overflow-auto">
        <KeySettingsForm
          selectedKey={selectedKey}
          availableTags={availableTags}
        />
      </TabsContent>

      <TabsContent
        value="settings"
        className="flex-1 px-4 pb-4 overflow-auto"
      >
        <KeySettings
          selectedKey={selectedKey}
          projectId={projectId}
          onKeyDeleted={onKeyDeleted}
        />
      </TabsContent>
    </Tabs>
  );
};

