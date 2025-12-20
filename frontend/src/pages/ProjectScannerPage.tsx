import { type FC, useEffect } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { GET_PROJECTS, type Project } from '@/graphql/projects';
import { PROJECT_REPOSITORY_QUERY } from '@/graphql/github';
import { ProjectSettingsTabs } from '@/components/project';
import { ScanRepositoryCard } from '@/components/github';
import { LoadingState, ErrorState, NotFoundState } from '@/components/blocks';
import { useBreadcrumbs } from '@/contexts';
import { PATHS } from '@/constants/paths';

export const ProjectScannerPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const { setBreadcrumbs } = useBreadcrumbs();

  const { data, loading, error } = useQuery(GET_PROJECTS);
  
  // Query for repository connection status
  const { data: repoData, loading: repoLoading } = useQuery(PROJECT_REPOSITORY_QUERY, {
    variables: { projectId: id },
    skip: !id,
  });

  const project = data?.projects?.find((p: Project) => {
    return p.id === id;
  });
  
  const hasRepository = !!repoData?.projectRepository;

  useEffect(() => {
    if (project) {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: project.name, href: PATHS.PROJECT.replace(':id', id || '') },
        { label: 'Find Keys' },
      ]);
    } else {
      setBreadcrumbs([
        { label: 'Dashboard', href: PATHS.DASHBOARD },
        { label: 'Project' },
        { label: 'Find Keys' },
      ]);
    }
  }, [project, setBreadcrumbs, id]);

  if (loading || repoLoading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message="Failed to load project" />;
  }

  if (!project) {
    return <NotFoundState message="Project not found" />;
  }

  // Redirect to repository page if no repository connected
  if (!hasRepository) {
    return <Navigate to={PATHS.PROJECT_REPOSITORY.replace(':id', id || '')} replace />;
  }

  return (
    <div className="container max-w-4xl py-8">
      <ProjectSettingsTabs projectId={id || ''} hasRepository={hasRepository} />
      
      <ScanRepositoryCard
        projectId={id || ''}
        hasRepository={hasRepository}
        canManage={project.canEdit}
      />
    </div>
  );
};

