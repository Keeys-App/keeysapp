import type { FC } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { FileText, CheckCircle2 } from "lucide-react";
import type { Language } from "@/types/project";

export interface FileLanguageMapping {
  filename: string;
  detectedLanguage: string | null;
  selectedLanguage: string;
  content: string;
}

interface ImportLanguageMatcherProps {
  files: FileLanguageMapping[];
  languages: Language[];
  onLanguageChange: (filename: string, language: string) => void;
}

export const ImportLanguageMatcher: FC<ImportLanguageMatcherProps> = ({
  files,
  languages,
  onLanguageChange,
}) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Language Matching</CardTitle>
          <Badge variant="secondary">
            {files.length} file{files.length !== 1 ? "s" : ""}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Select the target language for each file. Languages are auto-detected
            from filenames when possible.
          </p>

          <div className="space-y-4">
            {files.map((file, index) => {
              const isDetected = file.detectedLanguage !== null;
              const isMatched = file.selectedLanguage === file.detectedLanguage;

              return (
                <div
                  key={file.filename}
                  className="flex items-start gap-4 p-4 rounded-lg border bg-muted/30"
                >
                  <div className="flex-shrink-0 mt-1">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                  </div>
                  
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono font-semibold">
                        {file.filename}
                      </code>
                      {isDetected ? (
                        <Badge
                          variant={isMatched ? "default" : "secondary"}
                          className="text-xs"
                        >
                          {isMatched ? (
                            <>
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Auto-detected
                            </>
                          ) : (
                            "Detected: " + file.detectedLanguage
                          )}
                        </Badge>
                      ) : null}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`lang-${index}`} className="text-sm">
                        Target Language
                      </Label>
                      <Select
                        value={file.selectedLanguage}
                        onValueChange={(value) =>
                          onLanguageChange(file.filename, value)
                        }
                      >
                        <SelectTrigger id={`lang-${index}`}>
                          <SelectValue placeholder="Select language" />
                        </SelectTrigger>
                        <SelectContent>
                          {languages.map((lang) => (
                            <SelectItem key={lang.code} value={lang.code}>
                              {lang.flag} {lang.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

