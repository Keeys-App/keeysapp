import type { FC } from "react";
import { Link } from "react-router-dom";
import { MoreHorizontal, Pencil, Trash2, Users, Languages } from "lucide-react";
import type { Project } from "@/types/project";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ProjectStatus, getProjectStatusInfo } from "@/components/blocks";
import { PATHS } from "@/constants/paths";

interface ProjectCardProps {
  project: Project;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
}

export const ProjectCard: FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete,
}) => {
  const handleEdit = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (onEdit) {
      onEdit(project);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (onDelete) {
      onDelete(project);
    }
  };

  const projectUrl = PATHS.PROJECT.replace(":id", project.id);

  return (
    <Link to={projectUrl} className="block">
      <Card className="relative cursor-pointer transition-all hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600 group overflow-hidden">
        <div className="p-6 space-y-4">
          {/* Header with title and menu */}
          <div className="flex justify-between items-start gap-3">
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-medium text-gray-600 dark:text-gray-400 truncate">
                {project.name}
              </h3>
            </div>

            {project.canEdit ? (
              <DropdownMenu>
                <DropdownMenuTrigger
                  asChild
                  onClick={(e) => e.stopPropagation()}
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={handleEdit}>
                    <Pencil className="h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={handleDelete}
                    className="text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : null}
          </div>

          {/* Main metric - Languages count */}
          <div className="space-y-2">
            <div className="flex items-baseline gap-3">
              <div className="text-4xl font-bold tracking-tight">
                {project.languages.length}
              </div>
              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                <Languages className="h-3 w-3 mr-1" />
                {project.languages.length === 1 ? "language" : "languages"}
              </Badge>
            </div>

            {/* Status trend */}
            <ProjectStatus status={project.status} />
          </div>

          {/* Bottom info */}
          <div className="pt-2 space-y-1">
            {project.description ? (
              <p className="text-sm text-gray-500 dark:text-gray-500 line-clamp-2">
                {project.description}
              </p>
            ) : null}
            <div className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-500">
              <Users className="h-3.5 w-3.5" />
              <span>
                {project.members.length + 1}{" "}
                {project.members.length === 0 ? "member" : "members"}
              </span>
            </div>
          </div>
        </div>

        {/* Subtle color accent */}
        <div
          className="absolute bottom-0 left-0 right-0 h-1"
          style={{ backgroundColor: project.color }}
        />
      </Card>
    </Link>
  );
};
