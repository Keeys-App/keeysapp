import { type FC, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { GET_PROJECTS, type Project } from '@/graphql/projects';
import { PROJECT_REPOSITORY_QUERY } from '@/graphql/github';
import { ProjectSettingsTabs } from '@/components/project';
import { ConnectRepositoryCard } from '@/components/github';
import { LoadingState, ErrorState, NotFoundState } from '@/components/blocks';
import { useBreadcrumbs } from '@/contexts';
import { PATHS } from '@/constants/paths';

export const ProjectRepositoryPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const { setBreadcrumbs } = useBreadcrumbs();

  const { data, loading, error } = useQuery(GET_PROJECTS);
  
  // Query for repository connection status
  const { data: repoData } = useQuery(PROJECT_REPOSITORY_QUERY, {
    variables: { projectId: id },
    skip: !id,
  });

  const project = data?.projects?.find((p: Project) => {
    return p.id === id;
  });
  
  const hasRepository = !!repoData?.projectRepository;
  const teamId = project?.team?.id;

  useEffect(() => {
    if (project) {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: project.name, href: PATHS.PROJECT.replace(':id', id || '') },
        { label: 'Repository' },
      ]);
    } else {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: 'Project' },
        { label: 'Repository' },
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

  return (
    <div className="container max-w-2xl py-8">
      <ProjectSettingsTabs projectId={id || ''} hasRepository={hasRepository} />
      
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

