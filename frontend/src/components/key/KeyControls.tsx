import type { FC } from "react";
import { Button } from "@/components/ui/button";

interface KeyControlsProps {
  projectId: string;
  onCreateKey: () => void;
}

export const KeyControls: FC<KeyControlsProps> = ({
  projectId,
  onCreateKey,
}) => {
  return (
    <div className="h-14 py-1 px-2 flex gap-2 items-center justify-end bg-muted border-b">
      <Button size="sm" onClick={onCreateKey}>Add key</Button>
    </div>
  );
};
