import { type FC } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Languages, Info, Sparkles, ExternalLink, Sparkle } from "lucide-react";
import {
  Item,
  ItemHeader,
  ItemContent,
  ItemDescription,
  ItemTitle,
  ItemMedia,
} from "../ui/item";

interface KeySuggestionsProps {
  currentLanguage?: string | null;
  currentLanguageValue?: string;
  defaultLanguage?: string | null;
  defaultLanguageValue?: string;
}

/**
 * Component for displaying translation suggestions and context
 * Shows the original text in the default language to help with translation
 */
export const KeySuggestions: FC<KeySuggestionsProps> = ({
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  // If no language is being edited, show a message
  if (!currentLanguage) {
    return (
      <div>
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Select a translation field to edit to see suggestions and context
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Show context from default language
  return (
    <div className="space-y-4">
      <Item variant="outline">
        <ItemMedia>
          <div className="flex items-center gap-2 p-1 rounded-md bg-indigo-500/10">
            <Sparkle className="text-indigo-500" />
          </div>
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Autopilot</ItemTitle>
          <ItemDescription className="text-balance">
            Translate with AI based on the default language.
          </ItemDescription>
          <div className="flex items-center gap-2 mt-2">
            <Button size="sm">Translate</Button>
            <Button size="sm" variant="outline">
              Add context
            </Button>
          </div>
        </ItemContent>
      </Item>
    </div>
  );
};
