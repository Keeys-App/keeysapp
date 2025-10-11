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
      <div className="px-4 py-3 border-b h-12 box-border">
        <h2 className="text-base font-semibold">Key Management</h2>
      </div>
      <div className={`flex-1 ${selectedKey ? 'overflow-auto' : 'p-4'}`}>
        {!selectedKey ? (
          <p className="text-muted-foreground text-sm">
            Click on any translation key from the list to view and manage it
          </p>
        ) : (
          <Tabs defaultValue="history" className="h-full flex flex-col">
            <TabsList className="mx-4 mt-4">
              <TabsTrigger value="history">History</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
              <TabsTrigger value="review">Review</TabsTrigger>
            </TabsList>

            <TabsContent value="history" className="flex-1 px-4 pb-4 overflow-auto">
              <KeyLogsTimeline keyId={selectedKey.id} />
            </TabsContent>

            <TabsContent value="settings" className="flex-1 px-4 pb-4 overflow-auto">
              <KeySettingsForm 
                selectedKey={selectedKey} 
                availableTags={availableTags} 
              />
            </TabsContent>

            <TabsContent value="review" className="flex-1 px-4 pb-4 overflow-auto">
              <div className="text-muted-foreground text-sm">
                Review content coming soon
              </div>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};
