import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpRightIcon, SquareAsterisk } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';
import { PATHS } from '@/constants/paths';

interface EmptyKeysProps {
  projectId: string;
  onCreateKey: () => void;
}

export const EmptyKeys: FC<EmptyKeysProps> = ({ projectId, onCreateKey }) => {
  const navigate = useNavigate();

  const handleImportClick = () => {
    navigate(PATHS.IMPORT.replace(':id', projectId));
  };
  return (
    <div className="flex items-center justify-center flex-1">
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <SquareAsterisk />
          </EmptyMedia>
          <EmptyTitle>No Translation Keys</EmptyTitle>
          <EmptyDescription>
            No keys found. Create your first translation key to get started.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <div className="flex gap-2">
            <Button onClick={onCreateKey}>Create Key</Button>
            <Button variant="outline" onClick={handleImportClick}>
              Import Keys
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

