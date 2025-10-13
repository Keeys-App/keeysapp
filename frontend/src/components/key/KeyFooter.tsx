import { Badge } from "../ui";

interface KeyFooterProps {
  description?: string | null;
  tags?: string[] | null;
}

/**
 * Component for displaying key description and tags at the bottom
 */
export function KeyFooter({ description, tags }: KeyFooterProps) {
  // If no description and no tags, don't render anything
  if (!description && (!tags || tags.length === 0)) {
    return null;
  }

  return (
    <div className="mt-auto pb-4 flex flex-col gap-4 px-4">
      {description ? (
        <p className="text-sm break-words text-muted-foreground">
          {description}
        </p>
      ) : null}
      {tags && tags.length > 0 ? (
        <div className="text-sm break-words text-muted-foreground flex gap-2 flex-wrap">
          {tags.map((tag) => (
            <Badge variant="secondary" key={tag}>
              {tag}
            </Badge>
          ))}
        </div>
      ) : null}
      
    </div>
  );
}
