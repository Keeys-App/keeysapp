import type { FC } from 'react';
import { FolderOpen, ArrowUpRightIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';

interface EmptyProjectsProps {
  onCreateProject: () => void;
}

export const EmptyProjects: FC<EmptyProjectsProps> = ({ onCreateProject }) => {
  return (
    <div className="flex items-center justify-center flex-1">
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <FolderOpen />
          </EmptyMedia>
          <EmptyTitle>No Projects Yet</EmptyTitle>
          <EmptyDescription>
            You haven&apos;t created any projects yet. Get started by creating your first project.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <div className="flex gap-2">
            <Button onClick={onCreateProject}>Create Project</Button>
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
    </div>
  );
};

