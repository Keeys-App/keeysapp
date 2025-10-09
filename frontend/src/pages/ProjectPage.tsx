import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { ArrowLeft } from 'lucide-react';
import { GET_PROJECT, type GetProjectData } from '@/graphql/projects';
import { PATHS } from '@/constants/paths';
import { useAuth } from '@/contexts/AuthContext';
import type { FC } from 'react';
import { Button } from '@/components/ui/button';

export const ProjectPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const { data, loading, error } = useQuery<GetProjectData>(GET_PROJECT, {
    variables: { id },
    skip: !id || !isAuthenticated || authLoading,
  });

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

  if (!data?.project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <p className="text-lg text-muted-foreground">Project not found</p>
        <Button onClick={handleBackClick}>
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Button>
      </div>
    );
  }

  const project = data.project;

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col gap-4 mb-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={handleBackClick}>
            <ArrowLeft className="h-4 w-4" /> Back
          </Button>
          <div
            className="w-1 h-8 rounded-sm"
            style={{
              backgroundColor: project.color,
            }}
          />
          <div className="flex flex-col gap-1">
            <h2 className="text-3xl font-bold">{project.name}</h2>
            {project.description ? <p className="text-lg text-muted-foreground">{project.description}</p> : null}
          </div>
        </div>
      </div>

      {/* Project Keys Section */}
      <div>
        <h3 className="text-2xl font-semibold mb-4">Translation Keys</h3>

        {/* Placeholder for keys list - will be implemented later */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <div className="p-8 border-2 border-dashed rounded-lg text-center">
            <p className="text-lg text-muted-foreground">Keys list will be implemented here</p>
          </div>
        </div>
      </div>
    </div>
  );
};
