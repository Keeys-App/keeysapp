import type { FC } from "react";
import { Link } from "react-router-dom";
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import type { Project } from "@/types/project";
import {
  Item,
  ItemMedia,
  ItemContent,
  ItemTitle,
  ItemDescription,
  ItemFooter,
  ItemActions,
} from "@/components/ui/item";
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
    <Item variant="outline" asChild>
      <Link to={projectUrl}>
        <ItemMedia>
          <div
            className="h-3 w-3 rounded-full"
            style={{ backgroundColor: project.color }}
          />
        </ItemMedia>

        <ItemContent>
          <ItemTitle>{project.name}</ItemTitle>
          <ItemDescription>
            {project.description || "No description"}
          </ItemDescription>
          <div className="flex flex-wrap items-center gap-x-3 text-sm text-muted-foreground mt-1">
            <ProjectStatus status={project.status} />
            <span>{project.keysCount} keys</span>
            <span>{project.members.length + 1} mem</span>
            <span>{project.languages.length} lan</span>
          </div>
        </ItemContent>

        {project.canEdit ? (
          <ItemActions>
            <DropdownMenu>
              <DropdownMenuTrigger
                asChild
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                }}
              >
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
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
          </ItemActions>
        ) : null}

        <ItemFooter>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="w-full">
                  <Progress value={project.translationProgress} className="h-1.5" />
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-sm">
                  <span className="font-semibold">{project.translationProgress}%</span> translated
                </p>
                <p className="text-xs text-muted-foreground">
                  {project.keysCount} keys × {project.languages.length} languages
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </ItemFooter>
      </Link>
    </Item>
  );
};
