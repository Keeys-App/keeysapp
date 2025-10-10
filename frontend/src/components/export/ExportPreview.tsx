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

interface ExportPreviewProps {
  code: string;
  filename: string;
}

export const ExportPreview: FC<ExportPreviewProps> = ({ code, filename }) => {
  return (
    <Card className="flex-1">
      <CardHeader>
        <CardTitle>Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <CodeBlock
          data={[
            {
              language: "json",
              filename,
              code,
            },
          ]}
          defaultValue="json"
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

