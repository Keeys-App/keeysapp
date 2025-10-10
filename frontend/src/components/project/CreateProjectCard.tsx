import { Plus } from "lucide-react";
import type { FC } from "react";
import {
  Item,
  ItemContent,
  ItemTitle,
  ItemDescription,
  ItemMedia,
} from "@/components/ui/item";

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
      className="cursor-pointer hover:bg-accent/50"
      onClick={onClick}
    >
      <ItemMedia variant="icon">
        <Plus className="text-muted-foreground size-6" />
      </ItemMedia>
      <ItemContent>
        <ItemTitle>Create new Project</ItemTitle>
        <ItemDescription>Add a new project</ItemDescription>
      </ItemContent>
    </Item>
  );
};
