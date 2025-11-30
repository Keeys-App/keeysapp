import type { FC } from 'react';
import { Users, ArrowUpRightIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';

interface EmptyTeamsProps {
  onCreateTeam: () => void;
}

export const EmptyTeams: FC<EmptyTeamsProps> = ({ onCreateTeam }) => {
  return (
    <div className="flex items-center justify-center flex-1">
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <Users />
          </EmptyMedia>
          <EmptyTitle>No Teams Yet</EmptyTitle>
          <EmptyDescription>
            Create your first team to start collaborating on translation projects with your colleagues.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button onClick={onCreateTeam}>Create Your First Team</Button>
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

