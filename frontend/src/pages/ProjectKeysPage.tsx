import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { GET_PROJECT, type GetProjectData } from "@/graphql/projects";
import { PATHS } from "@/constants/paths";
import { useAuth, useBreadcrumbs } from "@/contexts";
import { useEffect, useState, type FC } from "react";
import { KeyList, CreateKeyDialog } from "@/components/key";
import { COMMON_LANGUAGES } from "@/types/project";
import { LoadingState, ErrorState, NotFoundState } from "@/components/blocks";

export const ProjectKeysPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { setBreadcrumbs } = useBreadcrumbs();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

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

  const handleCreateKey = () => {
    setIsCreateDialogOpen(true);
  };

  const projectLanguages = COMMON_LANGUAGES.filter((language) => {
    return project?.languages.some((lang) => {
      return lang.code === language.code;
    });
  });

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
    <div className="h-full">
      <KeyList
        projectId={project.id}
        projectLanguages={projectLanguages}
        onCreateKey={handleCreateKey}
      />

      <CreateKeyDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        projectId={project.id}
      />
    </div>
  );
};

