import type { FC } from "react";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { ParsedTranslation } from "./utils/importFormats";

interface ImportPreviewProps {
  translations: ParsedTranslation[];
  error?: string;
  existingKeys?: string[];
}

export const ImportPreview: FC<ImportPreviewProps> = ({
  translations,
  error,
  existingKeys = [],
}) => {
  const newKeys = translations.filter((t) => !existingKeys.includes(t.key));
  const updatedKeys = translations.filter((t) => existingKeys.includes(t.key));

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-destructive" />
            Parse Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (translations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No translations to preview yet
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-500" />
            Preview
          </CardTitle>
          <div className="flex gap-2">
            {newKeys.length > 0 ? (
              <Badge variant="default">{newKeys.length} new</Badge>
            ) : null}
            {updatedKeys.length > 0 ? (
              <Badge variant="secondary">{updatedKeys.length} updates</Badge>
            ) : null}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              Total translations: {translations.length}
            </span>
          </div>

          {updatedKeys.length > 0 ? (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {updatedKeys.length} existing key(s) will be updated
              </AlertDescription>
            </Alert>
          ) : null}

          <ScrollArea className="h-[400px] rounded-md border">
            <div className="p-4 space-y-2">
              {translations.map((translation, index) => {
                const isExisting = existingKeys.includes(translation.key);
                return (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-3 rounded-lg bg-muted/50"
                  >
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <code className="text-sm font-mono font-semibold">
                          {translation.key}
                        </code>
                        {isExisting ? (
                          <Badge variant="outline" className="text-xs">
                            update
                          </Badge>
                        ) : (
                          <Badge variant="default" className="text-xs">
                            new
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {translation.value}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
};

