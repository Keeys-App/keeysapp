import type { FC } from "react";
import { Link } from "react-router-dom";
import { MoreHorizontal, Pencil, Trash2, Users, Languages } from "lucide-react";
import type { Project } from "@/types/project";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ProjectStatus } from "@/components/blocks";
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
      <Card className="relative cursor-pointer transition-all group overflow-hidden">
        <CardHeader>
          <CardTitle>{project.name}</CardTitle>
          <CardDescription>{project.description}</CardDescription>
          <CardAction>
            {project.canEdit ? (
              <DropdownMenu>
                <DropdownMenuTrigger
                  asChild
                  onClick={(e) => e.stopPropagation()}
                >
                  <Button
                    variant="secondary"
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
          </CardAction>
        </CardHeader>

        <CardContent>
          <p>Card Content</p>
        </CardContent>

        <CardFooter>
          <ProjectStatus status={project.status} />
          {project.color}
        </CardFooter>

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
      </Card>
    </Link>
  );
};
