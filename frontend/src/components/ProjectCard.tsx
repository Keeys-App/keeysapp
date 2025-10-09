import type { FC } from 'react';
import { MoreHorizontal, Pencil, Trash2, User } from 'lucide-react';
import type { Project } from '../types/project';
import { ProjectStatus } from '../types/project';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';

interface ProjectCardProps {
  project: Project;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
  onClick?: (project: Project) => void;
}

export const ProjectCard: FC<ProjectCardProps> = ({ project, onEdit, onDelete, onClick }) => {
  const handleCardClick = () => {
    if (onClick) {
      onClick(project);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEdit) {
      onEdit(project);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(project);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case ProjectStatus.ACTIVE:
        return 'default';
      case ProjectStatus.ARCHIVED:
        return 'secondary';
      case ProjectStatus.DRAFT:
        return 'outline';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case ProjectStatus.ACTIVE:
        return 'Active';
      case ProjectStatus.ARCHIVED:
        return 'Archived';
      case ProjectStatus.DRAFT:
        return 'Draft';
      default:
        return status;
    }
  };

  return (
    <Card
      className={`relative cursor-pointer transition-all hover:shadow-md ${onClick ? '' : 'cursor-default'}`}
      onClick={handleCardClick}
    >
      {/* Color bar */}
      <div
        className="absolute top-0 left-0 right-0 h-1 rounded-t-lg"
        style={{ backgroundColor: project.color }}
      />

      <CardHeader className="pt-4">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-xl">{project.name}</CardTitle>
            {project.description ? (
              <CardDescription className="mt-1 line-clamp-2">{project.description}</CardDescription>
            ) : null}
          </div>

          {project.canEdit ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleEdit}>
                  <Pencil className="h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleDelete} className="text-destructive">
                  <Trash2 className="h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : null}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Languages */}
        {project.languages.length > 0 ? (
          <div className="flex gap-2 flex-wrap">
            {project.languages.slice(0, 5).map((lang) => {
              return (
                <Badge key={lang} variant="secondary">
                  {lang.toUpperCase()}
                </Badge>
              );
            })}
            {project.languages.length > 5 ? (
              <Badge variant="outline">+{project.languages.length - 5} more</Badge>
            ) : null}
          </div>
        ) : null}

        {/* Footer with status and members */}
        <div className="flex justify-between items-center pt-2 border-t">
          <Badge variant={getStatusColor(project.status)}>{getStatusLabel(project.status)}</Badge>

          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <User className="h-3.5 w-3.5" />
            <span>{project.members.length + 1}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
