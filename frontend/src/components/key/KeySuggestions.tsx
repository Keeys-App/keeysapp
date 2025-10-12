import { type FC } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Languages, Info, Sparkles, ExternalLink } from "lucide-react";

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
      {currentLanguageValue ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Current Translation ({currentLanguage})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {currentLanguageValue}
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="flex flex-col items-center justify-center py-8 text-center">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            
            <h3 className="mb-2 text-lg font-semibold">Lokalise AI</h3>
            
            <p className="mb-1 text-sm font-medium">Translate with AI</p>
            <p className="mb-6 text-sm text-muted-foreground">
              Add context for more accurate translations.
            </p>
            
            <div className="flex flex-col gap-2 w-full max-w-xs">
              <Button className="w-full" size="default">
                <Sparkles className="mr-2 h-4 w-4" />
                Translate with AI
              </Button>
              <Button variant="outline" className="w-full" size="default">
                <ExternalLink className="mr-2 h-4 w-4" />
                Explore more
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

