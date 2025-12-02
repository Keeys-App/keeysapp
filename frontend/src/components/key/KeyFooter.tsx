import { Badge } from "../ui";
import type { FC } from "react";

interface KeyFooterProps {
  description?: string | null;
  tags?: string[] | null;
  isPlural?: boolean;
}

/**
 * Component for displaying key description and tags at the bottom
 */
export const KeyFooter: FC<KeyFooterProps> = ({
  description,
  tags,
  isPlural,
}) => {
  // If no description and no tags and not plural, don't render anything
  if (!description && (!tags || tags.length === 0) && !isPlural) {
    return null;
  }

  return (
    <div className="mt-auto pb-2.5 flex flex-col gap-2 px-4">
      {description ? (
        <p className="text-sm break-words text-muted-foreground">
          {description}
        </p>
      ) : null}
      {tags && tags.length > 0 ? (
        <div className="text-sm break-words text-muted-foreground flex gap-2 flex-wrap">
          {tags?.map((tag) => (
            <Badge variant="secondary" key={tag}>
              {tag}
            </Badge>
          ))}
          {isPlural ? <Badge variant="outline">Plural</Badge> : null}
        </div>
      ) : null}
    </div>
  );
};
