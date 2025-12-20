import { type FC, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { GET_PROJECTS, type Project } from '@/graphql/projects';
import { ProjectForm } from '@/components/project';
import { LoadingState, ErrorState, NotFoundState } from '@/components/blocks';
import { useBreadcrumbs } from '@/contexts';
import { PATHS } from '@/constants/paths';
import { ConnectRepositoryCard } from '@/components/github';

export const EditProjectPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const { setBreadcrumbs } = useBreadcrumbs();

  const { data, loading, error } = useQuery(GET_PROJECTS);

  const project = data?.projects?.find((p: Project) => {
    return p.id === id;
  });

  useEffect(() => {
    if (project) {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: project.name, href: PATHS.PROJECT.replace(':id', id || '') },
        { label: 'Settings' },
      ]);
    } else {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: 'Project' },
        { label: 'Settings' },
      ]);
    }
  }, [project, setBreadcrumbs, id]);

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message="Failed to load project" />;
  }

  if (!project) {
    return <NotFoundState message="Project not found" />;
  }

  const teamId = project.team?.id;

  return (
    <div className="container max-w-2xl py-8 space-y-6">
      <ProjectForm mode="edit" project={project} />
      
      {/* GitHub Repository Integration */}
      {id && teamId ? (
        <ConnectRepositoryCard 
          projectId={id}
          teamId={teamId}
          canManage={project.canEdit}
        />
      ) : null}
    </div>
  );
};

