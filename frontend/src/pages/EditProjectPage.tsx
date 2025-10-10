import { type FC } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { GET_PROJECTS, type Project } from '@/graphql/projects';
import { ProjectForm } from '@/components/project';
import { LoadingState, ErrorState, NotFoundState } from '@/components/blocks';

export const EditProjectPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, loading, error } = useQuery(GET_PROJECTS);

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message="Failed to load project" />;
  }

  const project = data?.projects?.find((p: Project) => {
    return p.id === id;
  });

  if (!project) {
    return <NotFoundState message="Project not found" />;
  }

  return <ProjectForm mode="edit" project={project} onSuccess={() => navigate(`/project/${id}`)} />;
};

