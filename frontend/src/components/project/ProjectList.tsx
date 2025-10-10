import { useState, type FC } from "react";
import { useQuery, useMutation } from "@apollo/client";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  GET_PROJECTS,
  DELETE_PROJECT,
  type GetProjectsData,
  type Project,
} from "@/graphql/projects";
import { ProjectCard } from "./ProjectCard";
import { CreateProjectCard } from "./CreateProjectCard";
import { EmptyProjects } from "./EmptyProjects";
import { ImportProjectDialog } from "./ImportProjectDialog";
import { DeleteConfirmationDialog } from "@/components/blocks";
import { useAuth } from "@/contexts/AuthContext";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { PATHS } from "@/constants/paths";
import { Button } from "@/components/ui/button";

export const ProjectList: FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);

  const { data, loading, error, refetch } = useQuery<GetProjectsData>(GET_PROJECTS, {
    skip: !isAuthenticated || authLoading,
  });

  const [deleteProject, { loading: deleting }] = useMutation(DELETE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
    onCompleted: () => {
      setDeleteDialogOpen(false);
      setProjectToDelete(null);
      toast("Project deleted successfully");
    },
    onError: (error) => {
      const message = getUserFriendlyErrorMessage(error, 'Failed to delete project. Please try again.');
      toast.error(message);
    },
  });

  const handleEdit = (project: Project) => {
    navigate(PATHS.PROJECT_EDIT.replace(':id', project.id));
  };

  const handleDelete = (project: Project) => {
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!projectToDelete) {
      return;
    }
    await deleteProject({ variables: { id: projectToDelete.id } });
  };

  const handleImportSuccess = () => {
    refetch();
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
        <p className="text-lg text-destructive">
          Error loading projects. Please try again.
        </p>
      </div>
    );
  }

  const projects = data?.projects || [];

  return (
    <>
      {projects.length === 0 ? (
        <div className="flex flex-col gap-4">
          <div className="flex justify-end p-4">
            <Button
              variant="outline"
              onClick={() => {
                return setImportDialogOpen(true);
              }}
            >
              Import Project
            </Button>
          </div>
          <EmptyProjects
            onCreateProject={() => {
              return navigate(PATHS.PROJECT_CREATE);
            }}
          />
        </div>
      ) : (
        <div className="flex flex-col gap-4 p-4">
          <div className="flex justify-end">
            <Button
              variant="outline"
              onClick={() => {
                return setImportDialogOpen(true);
              }}
            >
              Import Project
            </Button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {/* Existing Projects */}
            {projects.map((project) => {
              return (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                />
              );
            })}

            {/* Create Project Card */}
            <CreateProjectCard
              onClick={() => {
                return navigate(PATHS.PROJECT_CREATE);
              }}
            />
          </div>
        </div>
      )}

      {/* Import Project Dialog */}
      <ImportProjectDialog
        open={importDialogOpen}
        onOpenChange={setImportDialogOpen}
        onImportSuccess={handleImportSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title="Delete Project"
        description={
          <>
            Are you sure you want to delete{" "}
            <strong>{projectToDelete?.name}</strong>? This action cannot be
            undone and will delete all project data including translations.
          </>
        }
        onConfirm={confirmDelete}
        confirmButtonText="Delete Project"
        isDeleting={deleting}
      />
    </>
  );
};
