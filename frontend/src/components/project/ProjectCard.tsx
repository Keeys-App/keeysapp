import type { FC } from "react";
import { Link } from "react-router-dom";
import {
  MoreHorizontal,
  Pencil,
  Trash2,
  Users,
  Languages,
  Users2,
} from "lucide-react";
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
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
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
      <Card className="relative cursor-pointer h-full transition-all group overflow-hidden shadow-none">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <div
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: project.color }}
              />
            </div>
            {project.name}
          </CardTitle>
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
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground">
              {project.keysCount} keys
            </span>
          </div>
          <div className="flex items-center gap-5 text-sm font-medium text-gray-500">
            <ProjectStatus status={project.status} />
            <div className="flex items-center gap-1">
              <Users2 className="h-4 w-4" />
              {project.members.length + 1}
            </div>
            <div className="flex items-center gap-1">
              <Languages className="h-4 w-4" />
              {project.languages.length}
            </div>
          </div>
        </CardContent>

        <CardFooter>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="w-full">
                  <Progress value={project.translationProgress} className="h-2" />
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-sm">
                  <span className="font-semibold">{project.translationProgress}%</span> translated
                </p>
                <p className="text-xs text-muted">
                  {project.keysCount} keys × {project.languages.length} languages
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardFooter>
      </Card>
    </Link>
  );
};
