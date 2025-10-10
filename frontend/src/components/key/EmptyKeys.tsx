import type { FC } from 'react';
import { toast } from 'sonner';
import { Key, ArrowUpRightIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';

interface EmptyKeysProps {
  onCreateKey: () => void;
}

export const EmptyKeys: FC<EmptyKeysProps> = ({ onCreateKey }) => {
  return (
    <div className="flex items-center justify-center flex-1">
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <Key />
          </EmptyMedia>
          <EmptyTitle>No Translation Keys</EmptyTitle>
          <EmptyDescription>
            No keys found. Create your first translation key to get started.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <div className="flex gap-2">
            <Button onClick={onCreateKey}>Create Key</Button>
            <Button
              variant="outline"
              onClick={() => {
                // TODO: Implement import functionality
                toast.info('Import functionality coming soon!');
              }}
            >
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

