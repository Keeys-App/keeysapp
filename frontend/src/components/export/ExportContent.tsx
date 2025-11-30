import { useState, useMemo, type FC } from "react";
import { Download } from "lucide-react";
import type { Project } from "@/types/project";
import { COMMON_LANGUAGES } from "@/types/project";
import { Button } from "@/components/ui/button";
import { LoadingState, ErrorState } from "@/components/blocks";
import { ExportSettings } from "./ExportSettings";
import { ExportPreview } from "./ExportPreview";
import type { ExportOptions } from "./utils/exportFormats";
import {
  generateExport,
  getExportFilename,
  getMimeType,
} from "./utils/exportFormats";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useAllProjectKeys } from "@/hooks/useAllProjectKeys";

interface ExportContentProps {
  project: Project;
}

export const ExportContent: FC<ExportContentProps> = ({ project }) => {
  const projectLanguages = COMMON_LANGUAGES.filter((language) => {
    return project.languages.some((lang) => {
      return lang.code === language.code;
    });
  });

  const [options, setOptions] = useState<ExportOptions>({
    format: "i18n",
    language: projectLanguages[0]?.code || "en",
    indent: 2,
    sortKeys: true,
  });

  // Load all project keys using pagination
  const { keys, loading, error, totalCount } = useAllProjectKeys(project.id);

  const exportCode = useMemo(() => {
    if (!keys || keys.length === 0) {
      return "";
    }
    return generateExport(keys, options);
  }, [keys, options]);

  const filename = useMemo(() => {
    return getExportFilename(project.name, options.language, options.format);
  }, [project.name, options.language, options.format]);

  const handleDownload = () => {
    const mimeType = getMimeType(options.format);
    const blob = new Blob([exportCode], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <LoadingState message={`Loading translations... ${keys.length > 0 ? `(${keys.length} of ${totalCount})` : ''}`} />;
  }

  if (error) {
    const errorMessage = getUserFriendlyErrorMessage(error, 'Failed to load translations for export. Please try again.');
    return <ErrorState message={errorMessage} />;
  }

  if (!keys || keys.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
        <p className="text-lg text-muted-foreground">
          No translation keys found in this project
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Download Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Export Translations</h2>
          <p className="text-sm text-muted-foreground">
            Export your translations in various formats
          </p>
        </div>
        <Button onClick={handleDownload} size="lg">
          <Download className="h-4 w-4 mr-2" />
          Download {filename}
        </Button>
      </div>

      {/* Settings and Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ExportSettings
            languages={projectLanguages}
            options={options}
            onOptionsChange={setOptions}
          />
        </div>
        <div className="lg:col-span-2">
          <ExportPreview code={exportCode} filename={filename} format={options.format} />
        </div>
      </div>
    </div>
  );
};

