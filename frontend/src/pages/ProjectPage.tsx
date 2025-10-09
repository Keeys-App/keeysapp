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
      Keys
    </div>
  );
};
