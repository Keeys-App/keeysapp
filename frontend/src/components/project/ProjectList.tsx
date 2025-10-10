import { useState, type FC } from "react";
import { useQuery, useMutation } from "@apollo/client";
import { toast } from "sonner";
import {
  GET_PROJECTS,
  DELETE_PROJECT,
  type GetProjectsData,
  type Project,
} from "@/graphql/projects";
import { ProjectCard } from "./ProjectCard";
import { CreateProjectCard } from "./CreateProjectCard";
import { CreateProjectDialog } from "./CreateProjectDialog";
import { EditProjectDialog } from "./EditProjectDialog";
import { EmptyProjects } from "./EmptyProjects";
import { DeleteConfirmationDialog } from "@/components/blocks";
import { useAuth } from "@/contexts/AuthContext";

export const ProjectList: FC = () => {
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
      toast.success("Project deleted successfully");
    },
    onError: (error) => {
      console.error("Error deleting project:", error);
      toast.error("Failed to delete project. Please try again.");
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
        <EmptyProjects
          onCreateProject={() => {
            return setCreateDialogOpen(true);
          }}
        />
      ) : (
        <div className="flex flex-col gap-4 p-4">
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
                return setCreateDialogOpen(true);
              }}
            />
          </div>
        </div>
      )}

      {/* Create Project Dialog */}
      <CreateProjectDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      {/* Edit Project Dialog */}
      <EditProjectDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        project={selectedProject}
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
