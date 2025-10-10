import type { FC } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface KeyControlsProps {
  onCreateKey: () => void;
}

export const KeyControls: FC<KeyControlsProps> = ({ onCreateKey }) => {
  return (
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold">Translation Keys</h2>
      <Button onClick={onCreateKey}>
        <Plus className="h-4 w-4 mr-2" />
        Create Key
      </Button>
    </div>
  );
};

