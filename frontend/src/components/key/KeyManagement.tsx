import { type FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KeyLogsTimeline } from "./KeyLogsTimeline";
import { KeySettingsForm } from "./KeySettingsForm";
import { KeySettings } from "./KeySettings";

interface KeyManagementProps {
  selectedKey: TranslationKey | null;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectId: string;
  availableTags?: string[];
  onKeyDeleted?: () => void;
}

/**
 * Component for managing a selected translation key
 */
export const KeyManagement: FC<KeyManagementProps> = ({
  selectedKey,
  projectLanguages,
  projectId,
  availableTags = [],
  onKeyDeleted,
}) => {
  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 border-b h-12 box-border">
        <h2 className="text-base font-semibold">
          {selectedKey?.key ? "Key Management" : "Activity"}
        </h2>
      </div>
      <div className="flex-1 overflow-auto">
        {!selectedKey ? (
          <p className="text-muted-foreground text-sm p-4">
            Click on any translation key from the list to view and manage it
          </p>
        ) : (
          <Tabs defaultValue="history" className="h-full flex flex-col">
            <TabsList className="mx-4 mt-4 mb-2 gap-0">
              <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
              <TabsTrigger value="meta">Metadata</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <TabsContent
              value="history"
              className="flex-1 px-4 pb-4 overflow-auto"
            >
              <KeyLogsTimeline keyId={selectedKey.id} />
            </TabsContent>

            <TabsContent
              value="meta"
              className="flex-1 px-4 pb-4 overflow-auto"
            >
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
        )}
      </div>
    </div>
  );
};
