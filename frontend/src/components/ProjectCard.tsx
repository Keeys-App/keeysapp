import type { FC } from 'react';
import { Card, Flex, Heading, Text, Badge, Box, DropdownMenu, IconButton } from '@radix-ui/themes';
import { DotsHorizontalIcon, Pencil1Icon, TrashIcon, PersonIcon } from '@radix-ui/react-icons';
import type { Project } from '../types/project';
import { ProjectStatus } from '../types/project';

interface ProjectCardProps {
  project: Project;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
  onClick?: (project: Project) => void;
}

export const ProjectCard: FC<ProjectCardProps> = ({
  project,
  onEdit,
  onDelete,
  onClick,
}) => {
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
        return 'green';
      case ProjectStatus.ARCHIVED:
        return 'gray';
      case ProjectStatus.DRAFT:
        return 'yellow';
      default:
        return 'blue';
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
      style={{
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        position: 'relative',
      }}
      onClick={handleCardClick}
    >
      {/* Color bar */}
      <Box
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          backgroundColor: project.color,
          borderRadius: '8px 8px 0 0',
        }}
      />

      <Flex direction="column" gap="3" pt="2">
        {/* Header with title and actions */}
        <Flex justify="between" align="start">
          <Flex direction="column" gap="1" style={{ flex: 1 }}>
            <Heading size="4">{project.name}</Heading>
            {project.description ? (
              <Text size="2" color="gray" style={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}>
                {project.description}
              </Text>
            ) : null}
          </Flex>

          {project.canEdit ? (
            <DropdownMenu.Root>
              <DropdownMenu.Trigger>
                <IconButton
                  variant="ghost"
                  size="1"
                  onClick={(e) => {
                    e.stopPropagation();
                  }}
                >
                  <DotsHorizontalIcon />
                </IconButton>
              </DropdownMenu.Trigger>
              <DropdownMenu.Content>
                <DropdownMenu.Item onClick={handleEdit}>
                  <Pencil1Icon /> Edit
                </DropdownMenu.Item>
                <DropdownMenu.Separator />
                <DropdownMenu.Item color="red" onClick={handleDelete}>
                  <TrashIcon /> Delete
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Root>
          ) : null}
        </Flex>

        {/* Languages */}
        {project.languages.length > 0 ? (
          <Flex gap="2" wrap="wrap">
            {project.languages.slice(0, 5).map((lang) => {
              return (
                <Badge key={lang} variant="soft" size="1">
                  {lang.toUpperCase()}
                </Badge>
              );
            })}
            {project.languages.length > 5 ? (
              <Badge variant="soft" size="1" color="gray">
                +{project.languages.length - 5} more
              </Badge>
            ) : null}
          </Flex>
        ) : null}

        {/* Footer with status and members */}
        <Flex justify="between" align="center" pt="2">
          <Badge color={getStatusColor(project.status)} variant="soft" size="1">
            {getStatusLabel(project.status)}
          </Badge>

          <Flex align="center" gap="1">
            <PersonIcon width="14" height="14" />
            <Text size="1" color="gray">
              {project.members.length + 1}
            </Text>
          </Flex>
        </Flex>
      </Flex>
    </Card>
  );
};

