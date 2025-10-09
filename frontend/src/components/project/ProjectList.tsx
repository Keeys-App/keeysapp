import { useState, type FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, FolderOpen, ArrowUpRightIcon } from 'lucide-react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_PROJECTS, DELETE_PROJECT, type GetProjectsData, type Project } from '@/graphql/projects';
import { ProjectCard } from './ProjectCard';
import { CreateProjectDialog } from './CreateProjectDialog';
import { EditProjectDialog } from './EditProjectDialog';
import { PATHS } from '@/constants/paths';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

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
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <p className="text-lg text-muted-foreground">Loading projects...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <p className="text-lg text-destructive">Error loading projects. Please try again.</p>
      </div>
    );
  }

  const projects = data?.projects || [];

  return (
    <>
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h2 className="text-3xl font-bold">Projects</h2>
        </div>

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <FolderOpen />
              </EmptyMedia>
              <EmptyTitle>No Projects Yet</EmptyTitle>
              <EmptyDescription>
                You haven&apos;t created any projects yet. Get started by
                creating your first project.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent>
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    return setCreateDialogOpen(true);
                  }}
                >
                  Create Project
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    // TODO: Implement import functionality
                    alert('Import functionality coming soon!');
                  }}
                >
                  Import Project
                </Button>
              </div>
            </EmptyContent>
            <Button
              variant="link"
              className="text-muted-foreground cursor-pointer"
              size="sm"
              onClick={() => {
                // TODO: Link to documentation
              }}
            >
              Learn More <ArrowUpRightIcon />
            </Button>
          </Empty>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {/* Create Project Card */}
            <div
              className="bg-card border-dashed hover:bg-accent hover:border-primary flex min-h-[180px] cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 p-6 transition-colors"
              onClick={() => {
                return setCreateDialogOpen(true);
              }}
            >
              <div className="bg-muted flex size-12 items-center justify-center rounded-lg">
                <Plus className="text-muted-foreground size-6" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold">Create Project</h3>
                <p className="text-muted-foreground text-sm">
                  Add a new project
                </p>
              </div>
            </div>

            {/* Existing Projects */}
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
          </div>
        )}
      </div>

      {/* Create Project Dialog */}
      <CreateProjectDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />

      {/* Edit Project Dialog */}
      <EditProjectDialog open={editDialogOpen} onOpenChange={setEditDialogOpen} project={selectedProject} />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{projectToDelete?.name}</strong>? This action cannot be undone
              and will delete all project data including translations.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} disabled={deleting} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              {deleting ? 'Deleting...' : 'Delete Project'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};
