import { useState, useRef, type FC, type ChangeEvent, type DragEvent } from "react";
import { Upload, FileText, Clipboard, X } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface ImportFile {
  filename: string;
  content: string;
}

interface ImportUploadProps {
  onFilesLoaded: (files: ImportFile[]) => void;
}

export const ImportUpload: FC<ImportUploadProps> = ({ onFilesLoaded }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [pasteContent, setPasteContent] = useState("");
  const [loadedFiles, setLoadedFiles] = useState<ImportFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFilesRead = async (files: FileList | File[]) => {
    const filesArray = Array.from(files);
    const importFiles: ImportFile[] = [];

    for (const file of filesArray) {
      try {
        const content = await file.text();
        importFiles.push({
          filename: file.name,
          content,
        });
      } catch (error) {
        console.error(`Failed to read file ${file.name}:`, error);
      }
    }

    if (importFiles.length > 0) {
      const allFiles = [...loadedFiles, ...importFiles];
      setLoadedFiles(allFiles);
      onFilesLoaded(allFiles);
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFilesRead(files);
    }
    // Reset input to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFilesRead(files);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = (filename: string) => {
    const updated = loadedFiles.filter((f) => f.filename !== filename);
    setLoadedFiles(updated);
    onFilesLoaded(updated);
  };

  const handlePasteLoad = () => {
    if (pasteContent.trim()) {
      const file: ImportFile = {
        filename: "pasted-content.json",
        content: pasteContent,
      };
      const allFiles = [...loadedFiles, file];
      setLoadedFiles(allFiles);
      onFilesLoaded(allFiles);
      setPasteContent("");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Load Translations</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="upload" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="upload">
              <Upload className="h-4 w-4 mr-2" />
              Upload File
            </TabsTrigger>
            <TabsTrigger value="paste">
              <Clipboard className="h-4 w-4 mr-2" />
              Paste Content
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-4">
            <div
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
                isDragging
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-primary/50"
              )}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={handleBrowseClick}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".json"
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-sm font-medium mb-2">
                Drag and drop your files here
              </p>
              <p className="text-xs text-muted-foreground mb-4">
                or click to browse (multiple files supported)
              </p>
              <Button type="button" variant="outline" size="sm">
                Select Files
              </Button>
            </div>

            {loadedFiles.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm font-medium">
                  Loaded files ({loadedFiles.length}):
                </p>
                <div className="space-y-2">
                  {loadedFiles.map((file) => (
                    <div
                      key={file.filename}
                      className="flex items-center gap-2 p-2 rounded-md bg-muted/50"
                    >
                      <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <code className="text-sm flex-1 truncate">
                        {file.filename}
                      </code>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 flex-shrink-0"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveFile(file.filename);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            <p className="text-xs text-muted-foreground text-center">
              Supported formats: JSON (.json)
            </p>
          </TabsContent>

          <TabsContent value="paste" className="space-y-4">
            <Textarea
              placeholder="Paste your translation JSON here..."
              value={pasteContent}
              onChange={(e) => setPasteContent(e.target.value)}
              className="min-h-[200px] font-mono text-sm"
            />
            <Button
              onClick={handlePasteLoad}
              disabled={!pasteContent.trim()}
              className="w-full"
            >
              Load Translations
            </Button>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

