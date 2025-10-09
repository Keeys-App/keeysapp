import { useState, type FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flex, Button, Heading, Text, Grid, Box, AlertDialog } from '@radix-ui/themes';
import { PlusIcon } from '@radix-ui/react-icons';
import { useQuery, useMutation } from '@apollo/client';
import { GET_PROJECTS, DELETE_PROJECT, type GetProjectsData, type Project } from '../graphql/projects';
import { ProjectCard } from './ProjectCard';
import { CreateProjectDialog } from './CreateProjectDialog';
import { EditProjectDialog } from './EditProjectDialog';
import { PATHS } from '../constants/paths';
import { useAuth } from '../contexts/AuthContext';

export const ProjectList: FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);

  const { data, loading, error } = useQuery<GetProjectsData>(GET_PROJECTS, {
    skip: !isAuthenticated || authLoading,
  });

  const [deleteProject, { loading: deleting }] = useMutation(DELETE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
    onCompleted: () => {
      setDeleteDialogOpen(false);
      setProjectToDelete(null);
    },
    onError: (error) => {
      console.error('Error deleting project:', error);
      alert('Failed to delete project. Please try again.');
    },
  });

  const handleEdit = (project: Project) => {
    setSelectedProject(project);
    setEditDialogOpen(true);
  };

  const handleDelete = (project: Project) => {
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  };

  const handleProjectClick = (project: Project) => {
    navigate(PATHS.PROJECT.replace(':id', project.id));
  };

  const confirmDelete = async () => {
    if (!projectToDelete) {
      return;
    }
    await deleteProject({ variables: { id: projectToDelete.id } });
  };

  if (loading) {
    return (
      <Flex direction="column" align="center" justify="center" style={{ minHeight: '50vh' }}>
        <Text size="3" color="gray">
          Loading projects...
        </Text>
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex direction="column" align="center" justify="center" style={{ minHeight: '50vh' }}>
        <Text size="3" color="red">
          Error loading projects. Please try again.
        </Text>
      </Flex>
    );
  }

  const projects = data?.projects || [];

  return (
    <>
      <Flex direction="column" gap="4">
        {/* Header */}
        <Flex justify="between" align="center">
          <Heading size="6">Projects</Heading>
          <Button onClick={() => {
            return setCreateDialogOpen(true);
          }}>
            <PlusIcon /> New Project
          </Button>
        </Flex>

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <Flex
            direction="column"
            align="center"
            justify="center"
            gap="4"
            style={{
              minHeight: '40vh',
              border: '2px dashed var(--gray-6)',
              borderRadius: 8,
              padding: '3rem',
            }}
          >
            <Box>
              <Heading size="4" mb="2" style={{ textAlign: 'center' }}>
                No projects yet
              </Heading>
              <Text size="2" color="gray" style={{ textAlign: 'center' }}>
                Create your first project to start managing translations
              </Text>
            </Box>
            <Button size="3" onClick={() => {
              return setCreateDialogOpen(true);
            }}>
              <PlusIcon /> Create Your First Project
            </Button>
          </Flex>
        ) : (
          <Grid columns={{ initial: '1', sm: '2', md: '3' }} gap="4">
            {projects.map((project) => {
              return (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onClick={handleProjectClick}
                />
              );
            })}
          </Grid>
        )}
      </Flex>

      {/* Create Project Dialog */}
      <CreateProjectDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />

      {/* Edit Project Dialog */}
      <EditProjectDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        project={selectedProject}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog.Root open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialog.Content style={{ maxWidth: 450 }}>
          <AlertDialog.Title>Delete Project</AlertDialog.Title>
          <AlertDialog.Description size="2">
            Are you sure you want to delete <strong>{projectToDelete?.name}</strong>? This action
            cannot be undone and will delete all project data including translations.
          </AlertDialog.Description>

          <Flex gap="3" mt="4" justify="end">
            <AlertDialog.Cancel>
              <Button variant="soft" color="gray" disabled={deleting}>
                Cancel
              </Button>
            </AlertDialog.Cancel>
            <AlertDialog.Action>
              <Button variant="solid" color="red" onClick={confirmDelete} disabled={deleting}>
                {deleting ? 'Deleting...' : 'Delete Project'}
              </Button>
            </AlertDialog.Action>
          </Flex>
        </AlertDialog.Content>
      </AlertDialog.Root>
    </>
  );
};

