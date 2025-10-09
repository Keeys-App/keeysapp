import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { Flex, Heading, Text, Button, Box, Grid } from '@radix-ui/themes';
import { ArrowLeftIcon } from '@radix-ui/react-icons';
import { GET_PROJECT, type GetProjectData } from '../graphql/projects';
import { PATHS } from '../constants/paths';
import { useAuth } from '../contexts/AuthContext';
import type { FC } from 'react';

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
      <Flex direction="column" align="center" justify="center" style={{ minHeight: '50vh' }}>
        <Text size="3" color="gray">
          Loading project...
        </Text>
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex direction="column" align="center" justify="center" style={{ minHeight: '50vh' }}>
        <Text size="3" color="red">
          Error loading project: {error.message}
        </Text>
        <Button onClick={handleBackClick} style={{ marginTop: '1rem' }}>
          <ArrowLeftIcon /> Back to Dashboard
        </Button>
      </Flex>
    );
  }

  if (!data?.project) {
    return (
      <Flex direction="column" align="center" justify="center" style={{ minHeight: '50vh' }}>
        <Text size="3" color="gray">
          Project not found
        </Text>
        <Button onClick={handleBackClick} style={{ marginTop: '1rem' }}>
          <ArrowLeftIcon /> Back to Dashboard
        </Button>
      </Flex>
    );
  }

  const project = data.project;

  return (
    <Box>
      {/* Header */}
      <Flex direction="column" gap="4" mb="6">
        <Flex align="center" gap="3">
          <Button variant="ghost" onClick={handleBackClick}>
            <ArrowLeftIcon /> Back
          </Button>
          <Box
            style={{
              width: '4px',
              height: '32px',
              backgroundColor: project.color,
              borderRadius: '2px',
            }}
          />
          <Flex direction="column" gap="1">
            <Heading size="6">{project.name}</Heading>
            {project.description ? (
              <Text size="3" color="gray">
                {project.description}
              </Text>
            ) : null}
          </Flex>
        </Flex>
      </Flex>

      {/* Project Keys Section */}
      <Box>
        <Heading size="4" mb="4">
          Translation Keys
        </Heading>
        
        {/* Placeholder for keys list - will be implemented later */}
        <Grid columns={{ initial: '1', sm: '2', md: '3' }} gap="3">
          <Box
            style={{
              padding: '2rem',
              border: '2px dashed var(--gray-6)',
              borderRadius: '8px',
              textAlign: 'center',
            }}
          >
            <Text size="3" color="gray">
              Keys list will be implemented here
            </Text>
          </Box>
        </Grid>
      </Box>
    </Box>
  );
};
