import { type FC } from "react";
import type { TranslationKey } from "@/types/translationKey";
import type { Language, LanguageWithLocale } from "@/types/project";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KeyLogsTimeline } from "./KeyLogsTimeline";
import { KeySettingsForm } from "./KeySettingsForm";

interface KeyManagementProps {
  selectedKey: TranslationKey | null;
  projectLanguages: (Language | LanguageWithLocale)[];
  projectId: string;
  availableTags?: string[];
}

/**
 * Component for managing a selected translation key
 */
export const KeyManagement: FC<KeyManagementProps> = ({
  selectedKey,
  projectLanguages,
  projectId,
  availableTags = [],
}) => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-auto">
        {!selectedKey ? (
          <p className="text-muted-foreground text-sm">
            Click on any translation key from the list to view and manage it
          </p>
        ) : (
          <Tabs defaultValue="history" className="h-full flex flex-col gap-0">
            <div className="px-4 flex items-center h-14 border-b">
              <TabsList>
                <TabsTrigger value="history">History</TabsTrigger>
                <TabsTrigger value="settings">Metadata</TabsTrigger>
              </TabsList>
            </div>

            <TabsContent
              value="history"
              className="flex-1 p-4 overflow-auto"
            >
              <KeyLogsTimeline keyId={selectedKey.id} />
            </TabsContent>

            <TabsContent
              value="settings"
              className="flex-1 p-4 overflow-auto"
            >
              <KeySettingsForm
                selectedKey={selectedKey}
                availableTags={availableTags}
              />
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};
