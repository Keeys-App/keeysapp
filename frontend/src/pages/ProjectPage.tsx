import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { ArrowLeft } from 'lucide-react';
import { GET_PROJECT, type GetProjectData } from '@/graphql/projects';
import { PATHS } from '@/constants/paths';
import { useAuth, useBreadcrumbs } from '@/contexts';
import { useEffect, type FC } from 'react';
import { Button } from '@/components/ui/button';
import { KeyList, CreateKeyForm } from '@/components/key';

export const ProjectPage: FC = () => {
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
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: project.name },
      ]);
    } else {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: 'Project' },
      ]);
    }
  }, [project, setBreadcrumbs]);

  const handleBackClick = () => {
    navigate(PATHS.DASHBOARD);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <p className="text-lg text-muted-foreground">Loading project...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <p className="text-lg text-destructive">Error loading project: {error.message}</p>
        <Button onClick={handleBackClick}>
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Button>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <p className="text-lg text-muted-foreground">Project not found</p>
        <Button onClick={handleBackClick}>
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
          {project.description ? (
            <p className="text-muted-foreground mt-2">{project.description}</p>
          ) : null}
        </div>
      </div>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Translation Keys</h2>
        <CreateKeyForm projectId={project.id} />
        <KeyList projectId={project.id} projectLanguages={project.languages || []} />
      </div>
    </div>
  );
};
