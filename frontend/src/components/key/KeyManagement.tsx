import { type FC, useState, useEffect } from "react";
import type { TranslationKey } from "@/types/translationKey";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KeyLogsTimeline } from "./KeyLogsTimeline";
import { KeyMetadata } from "./KeyMetadata";
import { KeySettings } from "./KeySettings";
import { KeyAi } from "./KeyAi";
import type { Language } from "@/types/project";

interface KeyManagementProps {
  selectedKey: TranslationKey;
  projectId: string;
  availableTags?: string[];
  onKeyDeleted?: () => void;
  currentLanguage?: Language | null;
  currentLanguageValue?: string;
  defaultLanguage?: Language | null;
  defaultLanguageValue?: string;
}

const ACTIVE_TAB_STORAGE_KEY = "keyManagementActiveTab";

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
  // Load saved tab from localStorage or default to "ai"
  const [activeTab, setActiveTab] = useState<string>(() => {
    const saved = localStorage.getItem(ACTIVE_TAB_STORAGE_KEY);
    return saved || "ai";
  });

  // Save active tab to localStorage when it changes
  useEffect(() => {
    localStorage.setItem(ACTIVE_TAB_STORAGE_KEY, activeTab);
  }, [activeTab]);

  return (
    <Tabs
      value={activeTab}
      onValueChange={setActiveTab}
      className="h-full flex flex-col"
    >
      <TabsList className="mb-2 gap-0 w-full">
        <TabsTrigger value="ai">Autopilot</TabsTrigger>
        <TabsTrigger value="history">History</TabsTrigger>
        <TabsTrigger value="meta">Metadata</TabsTrigger>
        <TabsTrigger value="settings">Settings</TabsTrigger>
      </TabsList>

      <TabsContent value="ai" className="flex-1 overflow-auto">
        <KeyAi
          currentKey={selectedKey}
          currentLanguage={currentLanguage}
          currentLanguageValue={currentLanguageValue}
          defaultLanguage={defaultLanguage}
          defaultLanguageValue={defaultLanguageValue}
        />
      </TabsContent>

      <TabsContent value="history" className="flex-1 overflow-auto">
        <KeyLogsTimeline keyId={selectedKey.id} />
      </TabsContent>

      <TabsContent value="meta" className="flex-1 overflow-auto">
        <KeyMetadata selectedKey={selectedKey} availableTags={availableTags} />
      </TabsContent>

      <TabsContent value="settings" className="flex-1 overflow-auto">
        <KeySettings
          selectedKey={selectedKey}
          projectId={projectId}
          onKeyDeleted={onKeyDeleted}
        />
      </TabsContent>
    </Tabs>
  );
};

