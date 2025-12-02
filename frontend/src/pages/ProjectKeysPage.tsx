import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { GET_PROJECT, type GetProjectData } from "@/graphql/projects";
import { GET_KEY } from "@/graphql/keys";
import { PATHS } from "@/constants/paths";
import { useAuth, useBreadcrumbs } from "@/contexts";
import { useEffect, useState, useMemo, useCallback, type FC } from "react";
import { KeyList, CreateKeyDialog, KeysAsidePanel } from "@/components/key";
import { useLanguagesStore } from "@/stores";
import { LoadingState, ErrorState, NotFoundState } from "@/components/blocks";
import type { TranslationKey } from "@/types/translationKey";
import { useLayoutStore } from "@/stores";

export const ProjectKeysPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { setBreadcrumbs } = useBreadcrumbs();
  const { isPanelOpen, setShowPanelToggle, openPanel } = useLayoutStore();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedKeyId, setSelectedKeyId] = useState<string | null>(null);
  const [editingTranslation, setEditingTranslation] = useState<{
    keyId: string;
    language: string;
  } | null>(null);

  const { data, loading, error } = useQuery<GetProjectData>(GET_PROJECT, {
    variables: { id },
    skip: !id || !isAuthenticated || authLoading,
  });

  // Query for selected key data
  const { data: keyData, loading: keyLoading } = useQuery(GET_KEY, {
    variables: { id: selectedKeyId },
    skip: !selectedKeyId,
    fetchPolicy: 'cache-first',
  });

  const project = data?.project;
  const selectedKey = keyData?.key || null;

  // Get languages from store
  const { commonLanguages } = useLanguagesStore();

  // Build enhanced language list with locale information
  const projectLanguages = useMemo(() => {
    if (!project?.languages) {
      return [];
    }
    
    return project.languages.map((langConfig) => {
      const commonLang = commonLanguages.find((l) => l.code === langConfig.code);
      
      const direction = langConfig.direction || commonLang?.direction || 'ltr';
      
      return {
        code: langConfig.code,
        name: commonLang?.name || langConfig.code,
        flag: commonLang?.flag || '🏳️',
        locale: langConfig.locale,
        direction: (direction === 'rtl' ? 'rtl' : 'ltr') as 'ltr' | 'rtl',
        pluralForms: langConfig.pluralForms || commonLang?.pluralForms || ['other'],
        default: langConfig.default,
      };
    });
  }, [project?.languages, commonLanguages]);

  // Get current editing language value and default language value
  const currentLanguageCode = editingTranslation?.language || null;
  const currentLanguage = projectLanguages.find(
    (lang) => lang.code === currentLanguageCode
  );
  const defaultLanguage = projectLanguages.find(
    (lang) => lang.code === project?.defaultLanguage
  );
  const currentTranslation = selectedKey?.translations.find(
    (t) => t.language === currentLanguageCode
  );
  const defaultTranslation = selectedKey?.translations.find(
    (t) => t.language === project?.defaultLanguage
  );

  // Show/hide panel toggle button when entering/leaving this page
  useEffect(() => {
    setShowPanelToggle(true);
    return () => {
      setShowPanelToggle(false);
    };
  }, [setShowPanelToggle]);

  useEffect(() => {
    if (project) {
      setBreadcrumbs([
        { label: "Dashboard", href: PATHS.DASHBOARD },
        { label: project.name, href: PATHS.PROJECT.replace(':id', id!) },
        { label: "Keys" },
      ]);
    } else {
      setBreadcrumbs([
        { label: "Dashboard", href: PATHS.DASHBOARD },
        { label: "Project" },
        { label: "Keys" },
      ]);
    }
  }, [project, setBreadcrumbs, id]);

  const handleBackClick = () => {
    navigate(PATHS.DASHBOARD);
  };

  const handleCreateKey = useCallback(() => {
    setIsCreateDialogOpen(true);
  }, []);

  const handleSelectKey = useCallback((key: TranslationKey) => {
    setSelectedKeyId(key.id);
    // Automatically open panel when key is selected
    openPanel();
  }, [openPanel]);

  const handleKeyDeleted = useCallback(() => {
    setSelectedKeyId(null);
  }, []);

  if (loading) {
    return <LoadingState message="Loading project..." />;
  }

  if (error) {
    return (
      <ErrorState
        message={`Error loading project: ${error.message}`}
        onBack={handleBackClick}
        backLabel="Back to Dashboard"
      />
    );
  }

  if (!project) {
    return (
      <NotFoundState
        message="Project not found"
        onBack={handleBackClick}
        backLabel="Back to Dashboard"
      />
    );
  }

  return (
    <div className="flex relative" style={{ height: 'calc(100vh - 48px)' }}>
      <div className="flex-1 border-r transition-all duration-300">
        <KeyList
          projectId={project.id}
          projectLanguages={projectLanguages}
          projectKeysCount={project.keysCount}
          onCreateKey={handleCreateKey}
          selectedKeyId={selectedKeyId}
          onSelectKey={handleSelectKey}
          editingTranslation={editingTranslation}
          onEditingTranslationChange={setEditingTranslation}
        />
      </div>

      {/* Right Panel */}
      <div
        className={`bg-background transition-all duration-300 overflow-hidden ${
          isPanelOpen ? 'w-[400px]' : 'w-0'
        }`}
      >
        {isPanelOpen ? (
          <KeysAsidePanel
            totalKeys={project.keysCount}
            keysLoading={loading}
            selectedKey={selectedKey}
            selectedKeyId={selectedKeyId}
            keyLoading={keyLoading}
            projectId={project.id}
            availableTags={project.availableTags || []}
            onKeyDeleted={handleKeyDeleted}
            currentLanguage={currentLanguage}
            currentLanguageValue={currentTranslation?.value}
            defaultLanguage={defaultLanguage}
            defaultLanguageValue={defaultTranslation?.value}
            projectLanguages={projectLanguages}
          />
        ) : null}
      </div>

      <CreateKeyDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        projectId={project.id}
        defaultLanguage={project.defaultLanguage}
        availableTags={project.availableTags || []}
        projectLanguages={projectLanguages}
      />
    </div>
  );
};

