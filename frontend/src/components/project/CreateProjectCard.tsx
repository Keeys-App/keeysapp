import { Plus } from "lucide-react";
import type { FC } from "react";
import { Item, ItemContent, ItemTitle, ItemDescription } from "@/components/ui/item";

interface CreateProjectCardProps {
  onClick: () => void;
}

/**
 * Card component for creating a new project
 */
export const CreateProjectCard: FC<CreateProjectCardProps> = ({ onClick }) => {
  return (
    <Item 
      variant="outline" 
      className="cursor-pointer justify-center items-center text-center hover:bg-accent/50"
      onClick={onClick}
    >
      <div className="flex flex-col items-center gap-3">
        <div className="bg-muted flex size-12 items-center justify-center rounded-lg">
          <Plus className="text-muted-foreground size-6" />
        </div>
        <div>
          <ItemTitle className="justify-center">Create Project</ItemTitle>
          <ItemDescription>Add a new project</ItemDescription>
        </div>
      </div>
    </Item>
  );
};

