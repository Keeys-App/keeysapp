import { type FC } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Languages, Info } from "lucide-react";

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
      <div className="mt-4">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Select a translation field to edit to see suggestions and context
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // If editing the default language, show different message
  if (currentLanguage === defaultLanguage) {
    return (
      <div className="mt-4 space-y-4">
        <Alert>
          <Languages className="h-4 w-4" />
          <AlertDescription>
            You are editing the default language. This text will be used as a reference for other translations.
          </AlertDescription>
        </Alert>

        {currentLanguageValue ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Current Value</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {currentLanguageValue}
              </p>
            </CardContent>
          </Card>
        ) : null}
      </div>
    );
  }

  // Show context from default language
  return (
    <div className="mt-4 space-y-4">
      {defaultLanguageValue ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Languages className="h-4 w-4" />
              Original Text ({defaultLanguage})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">
              {defaultLanguageValue}
            </p>
          </CardContent>
        </Card>
      ) : null}

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
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            This translation is empty. Use the original text above as a reference.
          </AlertDescription>
        </Alert>
      )}

      {/* Placeholder for future AI suggestions */}
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            AI Suggestions (Coming Soon)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            Intelligent translation suggestions will appear here in future updates.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

