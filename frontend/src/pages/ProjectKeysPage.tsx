import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { GET_PROJECT, type GetProjectData } from "@/graphql/projects";
import { PATHS } from "@/constants/paths";
import { useAuth, useBreadcrumbs } from "@/contexts";
import { useEffect, useState, useMemo, useCallback, type FC } from "react";
import { KeyList, CreateKeyDialog, KeyManagement } from "@/components/key";
import { COMMON_LANGUAGES, LANGUAGE_CONFIGS } from "@/types/project";
import { LoadingState, ErrorState, NotFoundState } from "@/components/blocks";
import type { TranslationKey } from "@/types/translationKey";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { PanelRightClose, PanelRightOpen } from "lucide-react";

export const ProjectKeysPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { setBreadcrumbs } = useBreadcrumbs();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedKey, setSelectedKey] = useState<TranslationKey | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(() => {
    const saved = localStorage.getItem('keyManagementPanelOpen');
    return saved !== null ? saved === 'true' : true;
  });

  const { data, loading, error } = useQuery<GetProjectData>(GET_PROJECT, {
    variables: { id },
    skip: !id || !isAuthenticated || authLoading,
  });

  const project = data?.project;

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
    setSelectedKey(key);
  }, []);

  // Build enhanced language list with locale information
  const projectLanguages = useMemo(() => {
    if (!project?.languages) {
      return [];
    }
    
    return project.languages.map((langConfig) => {
      const commonLang = COMMON_LANGUAGES.find((l) => {
        return l.code === langConfig.code;
      });
      
      return {
        code: langConfig.code,
        name: commonLang?.name || langConfig.code,
        flag: commonLang?.flag || '🏳️',
        locale: langConfig.locale,
      };
    });
  }, [project?.languages]);

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
          onCreateKey={handleCreateKey}
          selectedKey={selectedKey}
          onSelectKey={handleSelectKey}
        />
      </div>

      {/* Toggle Button */}
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="absolute cursor-pointer right-2 top-2 z-20 bg-background/80 backdrop-blur-sm hover:bg-muted"
              onClick={() => {
                const newState = !isPanelOpen;
                setIsPanelOpen(newState);
                localStorage.setItem('keyManagementPanelOpen', String(newState));
              }}
            >
              {isPanelOpen ? (
                <PanelRightClose className="h-4 w-4" />
              ) : (
                <PanelRightOpen className="h-4 w-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {isPanelOpen ? 'Hide management panel' : 'Show management panel'}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      {/* Right Panel */}
      <div
        className={`bg-background transition-all duration-300 overflow-hidden ${
          isPanelOpen ? 'w-[400px]' : 'w-0'
        }`}
      >
        {isPanelOpen ? (
          <KeyManagement
            selectedKey={selectedKey}
            projectLanguages={projectLanguages}
            projectId={project.id}
            availableTags={project.availableTags || []}
          />
        ) : null}
      </div>

      <CreateKeyDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        projectId={project.id}
        defaultLanguage={project.defaultLanguage}
        availableTags={project.availableTags || []}
      />
    </div>
  );
};

