import { useState, useMemo, type FC } from "react";
import { useQuery, useMutation } from "@apollo/client";
import { Upload, ArrowRight, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import type { Project } from "@/types/project";
import type { TranslationKey } from "@/types/translationKey";
import { GET_PROJECT_KEYS, BATCH_IMPORT_TRANSLATIONS } from "@/graphql/keys";
import { COMMON_LANGUAGES } from "@/types/project";
import { Button } from "@/components/ui/button";
import { LoadingState, ErrorState } from "@/components/blocks";
import { ImportUpload, type ImportFile } from "./ImportUpload";
import { ImportLanguageMatcher, type FileLanguageMapping } from "./ImportLanguageMatcher";
import { ImportSettings, type ImportOptions } from "./ImportSettings";
import { ImportPreview } from "./ImportPreview";
import { parseImport, type ParsedTranslation } from "./utils/importFormats";
import { getBestLanguageMatch } from "./utils/languageDetector";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { useSaving, useSavingStore } from "@/stores";

interface ImportContentProps {
  project: Project;
}

type ImportStep = "upload" | "language" | "preview";

export const ImportContent: FC<ImportContentProps> = ({ project }) => {
  const projectLanguages = COMMON_LANGUAGES.filter((language) => {
    return project.languages.some((lang) => {
      return lang.code === language.code;
    });
  });

  const [currentStep, setCurrentStep] = useState<ImportStep>("upload");
  const [importFiles, setImportFiles] = useState<ImportFile[]>([]);
  const [fileMappings, setFileMappings] = useState<FileLanguageMapping[]>([]);
  const [importOptions, setImportOptions] = useState<ImportOptions>({
    format: "i18n",
    language: projectLanguages[0]?.code || "en",
    strategy: "merge",
  });

  const { data, loading, error } = useQuery<{ 
    projectKeys: { 
      keys: TranslationKey[];
      totalCount: number;
      hasMore: boolean;
    } 
  }>(
    GET_PROJECT_KEYS,
    {
      variables: { projectId: project.id, offset: 0, limit: 10000 },
    }
  );

  const [batchImportTranslations] = useMutation(BATCH_IMPORT_TRANSLATIONS, {
    refetchQueries: [
      { 
        query: GET_PROJECT_KEYS, 
        variables: { projectId: project.id, offset: 0, limit: 20 } 
      }
    ],
  });

  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const existingKeys = useMemo(() => {
    return data?.projectKeys?.keys?.map((key) => key.key) || [];
  }, [data?.projectKeys?.keys]);

  // Parse all files and combine translations
  const parsedData = useMemo(() => {
    const allTranslations: ParsedTranslation[] = [];
    let hasError = false;
    let errorMessage = "";

    for (const mapping of fileMappings) {
      const result = parseImport(mapping.content, importOptions.format);
      if (!result.success) {
        hasError = true;
        errorMessage = `Error in ${mapping.filename}: ${result.error}`;
        break;
      }
      allTranslations.push(...result.translations);
    }

    return {
      translations: allTranslations,
      error: hasError ? errorMessage : undefined,
    };
  }, [fileMappings, importOptions.format]);

  const handleFilesLoaded = (files: ImportFile[]) => {
    setImportFiles(files);
    
    // Create mappings with auto-detected languages
    const mappings: FileLanguageMapping[] = files.map((file) => {
      const detected = getBestLanguageMatch(file.filename);
      return {
        filename: file.filename,
        content: file.content,
        detectedLanguage: detected,
        selectedLanguage: detected || projectLanguages[0]?.code || "en",
      };
    });
    
    setFileMappings(mappings);

    // If files loaded, move to language matching step
    if (files.length > 0) {
      setCurrentStep("language");
    }
  };

  const handleLanguageChange = (filename: string, language: string) => {
    setFileMappings((prev) =>
      prev.map((mapping) =>
        mapping.filename === filename
          ? { ...mapping, selectedLanguage: language }
          : mapping
      )
    );
  };

  const handleNextToPreview = () => {
    setCurrentStep("preview");
  };

  const handleBackToLanguage = () => {
    setCurrentStep("language");
  };

  const handleBackToUpload = () => {
    setCurrentStep("upload");
    setImportFiles([]);
    setFileMappings([]);
  };

  const handleImport = async () => {
    if (parsedData.translations.length === 0) {
      return;
    }

    await withSaving(
      async () => {
        try {
          // Group translations by language
          const translationsByLanguage = new Map<string, ParsedTranslation[]>();
          
          for (const mapping of fileMappings) {
            const result = parseImport(mapping.content, importOptions.format);
            if (result.success) {
              const existing = translationsByLanguage.get(mapping.selectedLanguage) || [];
              translationsByLanguage.set(mapping.selectedLanguage, [...existing, ...result.translations]);
            }
          }

          let totalSuccess = 0;
          let totalErrors = 0;
          let totalCreated = 0;
          let totalUpdated = 0;

          // Import for each language using batch mutation
          for (const [language, translations] of translationsByLanguage) {
            try {
              const result = await batchImportTranslations({
                variables: {
                  input: {
                    projectId: project.id,
                    language: language,
                    translations: translations.map((t) => ({
                      key: t.key,
                      value: t.value,
                    })),
                    strategy: importOptions.strategy,
                  },
                },
              });

              if (result.data?.batchImportTranslations) {
                const batchResult = result.data.batchImportTranslations;
                totalSuccess += batchResult.successCount;
                totalErrors += batchResult.errorCount;
                totalCreated += batchResult.createdKeys;
                totalUpdated += batchResult.updatedKeys;

                if (batchResult.errors.length > 0) {
                  console.error(`Errors importing ${language}:`, batchResult.errors);
                }
              }
            } catch (err) {
              console.error(`Failed to import translations for ${language}:`, err);
              totalErrors += translations.length;
            }
          }

          // Show result toast
          if (totalErrors === 0) {
            toast(
              `Successfully imported ${totalSuccess} translations (${totalCreated} new, ${totalUpdated} updated)`
            );
          } else {
            toast(
              `Imported ${totalSuccess} translations with ${totalErrors} errors`
            );
          }

          // Reset state
          handleBackToUpload();
        } catch (err) {
          toast("Failed to import translations");
          console.error("Import error:", err);
        }
      },
      "Importing translations..."
    );
  };

  if (loading) {
    return <LoadingState message="Loading project data..." />;
  }

  if (error) {
    const errorMessage = getUserFriendlyErrorMessage(error, 'Failed to load project data for import. Please try again.');
    return <ErrorState message={errorMessage} />;
  }

  const canProceedToPreview = fileMappings.length > 0 && 
    fileMappings.every((m) => m.selectedLanguage);
  const canImport = parsedData.translations.length > 0 && !parsedData.error;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Import Translations</h2>
          <p className="text-sm text-muted-foreground">
            {currentStep === "upload" && "Upload your translation files"}
            {currentStep === "language" && "Match files to languages"}
            {currentStep === "preview" && "Review and import"}
          </p>
        </div>
        <div className="flex gap-2">
          {currentStep === "language" ? (
            <>
              <Button variant="outline" onClick={handleBackToUpload}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <Button
                onClick={handleNextToPreview}
                disabled={!canProceedToPreview}
              >
                Next: Preview
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </>
          ) : null}
          {currentStep === "preview" ? (
            <>
              <Button variant="outline" onClick={handleBackToLanguage}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <Button
                onClick={handleImport}
                disabled={!canImport || isSaving}
                size="lg"
                variant="outline"
              >
                <Upload className="h-4 w-4 mr-2" />
                Import Translations
              </Button>
            </>
          ) : null}
        </div>
      </div>

      {/* Step 1: Upload Files */}
      {currentStep === "upload" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <ImportSettings
              languages={projectLanguages}
              options={importOptions}
              onOptionsChange={setImportOptions}
            />
          </div>
          <div className="lg:col-span-2">
            <ImportUpload onFilesLoaded={handleFilesLoaded} />
          </div>
        </div>
      ) : null}

      {/* Step 2: Language Matching */}
      {currentStep === "language" ? (
        <ImportLanguageMatcher
          files={fileMappings}
          languages={projectLanguages}
          onLanguageChange={handleLanguageChange}
        />
      ) : null}

      {/* Step 3: Preview and Import */}
      {currentStep === "preview" ? (
        <ImportPreview
          translations={parsedData.translations}
          error={parsedData.error}
          existingKeys={existingKeys}
        />
      ) : null}
    </div>
  );
};
