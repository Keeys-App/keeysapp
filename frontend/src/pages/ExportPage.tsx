import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { ArrowLeft } from "lucide-react";
import { GET_PROJECT, type GetProjectData } from "@/graphql/projects";
import { PATHS } from "@/constants/paths";
import { useAuth, useBreadcrumbs } from "@/contexts";
import { useEffect, type FC } from "react";
import { Button } from "@/components/ui/button";
import { ExportContent } from "@/components/export";
import { LoadingState, ErrorState, NotFoundState } from "@/components/blocks";

export const ExportPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { setBreadcrumbs } = useBreadcrumbs();

  const { data, loading, error } = useQuery<GetProjectData>(GET_PROJECT, {
    variables: { id },
    skip: !id || !isAuthenticated || authLoading,
  });

  const project = data?.project;

  useEffect(() => {
    if (project) {
      setBreadcrumbs([
        { label: "Dashboard", href: PATHS.DASHBOARD },
        { label: project.name, href: PATHS.PROJECT.replace(":id", id || "") },
        { label: "Export" },
      ]);
    } else {
      setBreadcrumbs([
        { label: "Dashboard", href: PATHS.DASHBOARD },
        { label: "Project" },
        { label: "Export" },
      ]);
    }
  }, [project, setBreadcrumbs, id]);

  const handleBackClick = () => {
    navigate(PATHS.PROJECT.replace(":id", id || ""));
  };

  if (loading) {
    return <LoadingState message="Loading project..." />;
  }

  if (error) {
    return (
      <ErrorState
        message={`Error loading project: ${error.message}`}
        onBack={handleBackClick}
        backLabel="Back to Project"
      />
    );
  }

  if (!project) {
    return (
      <NotFoundState
        message="Project not found"
        onBack={handleBackClick}
        backLabel="Back to Project"
      />
    );
  }

  return (
    <div className="container mx-auto p-4">
      <ExportContent project={project} />
    </div>
  );
};
