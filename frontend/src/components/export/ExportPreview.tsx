import type { FC } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CodeBlock,
  CodeBlockBody,
  CodeBlockContent,
  CodeBlockCopyButton,
  CodeBlockHeader,
  CodeBlockItem,
} from "@/components/ui/shadcn-io/code-block";
import type { BundledLanguage } from "@/components/ui/shadcn-io/code-block";
import type { ExportFormat } from "./utils/exportFormats";

interface ExportPreviewProps {
  code: string;
  filename: string;
  format?: ExportFormat;
}

/**
 * Get syntax highlighting language for export format
 */
function getLanguageForFormat(format?: ExportFormat): BundledLanguage {
  switch (format) {
    case "ios-strings":
      return "swift"; // Swift syntax works well for .strings files (comments and strings)
    case "i18n":
    default:
      return "json";
  }
}

export const ExportPreview: FC<ExportPreviewProps> = ({ code, filename, format }) => {
  const language = getLanguageForFormat(format);
  
  return (
    <Card className="flex-1">
      <CardHeader>
        <CardTitle>Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <CodeBlock
          key={`${format}-${language}`}
          data={[
            {
              language,
              filename,
              code,
            },
          ]}
          defaultValue={language}
        >
          <CodeBlockHeader>
            <div className="flex-1 text-sm font-medium text-muted-foreground">
              {filename}
            </div>
            <CodeBlockCopyButton />
          </CodeBlockHeader>
          <CodeBlockBody>
            {(item) => (
              <CodeBlockItem key={item.language} value={item.language}>
                <CodeBlockContent language={item.language as BundledLanguage}>
                  {item.code}
                </CodeBlockContent>
              </CodeBlockItem>
            )}
          </CodeBlockBody>
        </CodeBlock>
      </CardContent>
    </Card>
  );
};

