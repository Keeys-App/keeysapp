import { Plus } from "lucide-react";
import type { FC } from "react";

interface CreateProjectCardProps {
  onClick: () => void;
}

/**
 * Card component for creating a new project
 */
export const CreateProjectCard: FC<CreateProjectCardProps> = ({ onClick }) => {
  return (
    <div
      className="bg-card flex h-[160px] cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border p-6 transition-colors hover:bg-accent"
      onClick={onClick}
    >
      <div className="bg-muted flex size-12 items-center justify-center rounded-lg">
        <Plus className="text-muted-foreground size-6" />
      </div>
      <div className="text-center">
        <h3 className="font-semibold">Create Project</h3>
        <p className="text-muted-foreground text-sm">Add a new project</p>
      </div>
    </div>
  );
};

