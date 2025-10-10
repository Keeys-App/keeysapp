import { type FC, useState } from "react";
import { CheckIcon } from "lucide-react";
import {
  Tags,
  TagsContent,
  TagsEmpty,
  TagsGroup,
  TagsInput,
  TagsItem,
  TagsList,
  TagsTrigger,
  TagsValue,
} from "@/components/ui/tags";

interface TagsEditorProps {
  selectedTags: string[];
  availableTags: string[];
  onChange: (tags: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * Component for editing tags with auto-complete from available tags.
 * Supports creating new tags on the fly.
 */
export const TagsEditor: FC<TagsEditorProps> = ({
  selectedTags,
  availableTags,
  onChange,
  disabled = false,
  placeholder = "Select tags...",
}) => {
  const [searchValue, setSearchValue] = useState("");

  const handleRemove = (tag: string) => {
    if (disabled) {
      return;
    }
    onChange(selectedTags.filter((t) => {
      return t !== tag;
    }));
  };

  const handleSelect = (tag: string) => {
    if (disabled) {
      return;
    }
    if (selectedTags.includes(tag)) {
      handleRemove(tag);
      return;
    }
    onChange([...selectedTags, tag]);
  };

  // Filter available tags based on search and exclude already selected
  const filteredTags = availableTags.filter((tag) => {
    if (selectedTags.includes(tag)) {
      return false;
    }
    if (!searchValue) {
      return true;
    }
    return tag.toLowerCase().includes(searchValue.toLowerCase());
  });

  // Check if search value is a new tag (not in available tags)
  const isNewTag = searchValue.trim() &&
    !availableTags.some((tag) => {
      return tag.toLowerCase() === searchValue.trim().toLowerCase();
    }) &&
    !selectedTags.some((tag) => {
      return tag.toLowerCase() === searchValue.trim().toLowerCase();
    });

  return (
    <Tags className="w-full">
      <TagsTrigger disabled={disabled}>
        {selectedTags.length > 0 ? (
          selectedTags.map((tag) => {
            return (
              <TagsValue key={tag} onRemove={() => {
                return handleRemove(tag);
              }}>
                {tag}
              </TagsValue>
            );
          })
        ) : (
          <span className="px-2 py-px text-muted-foreground">{placeholder}</span>
        )}
      </TagsTrigger>
      <TagsContent>
        <TagsInput
          placeholder="Search or create tag..."
          value={searchValue}
          onValueChange={setSearchValue}
        />
        <TagsList>
          {filteredTags.length === 0 && !isNewTag ? (
            <TagsEmpty>No tags found.</TagsEmpty>
          ) : null}
          <TagsGroup>
            {/* Show "Create new tag" option if search value is new */}
            {isNewTag ? (
              <TagsItem
                key="__new__"
                onSelect={() => {
                  handleSelect(searchValue.trim());
                  setSearchValue("");
                }}
                value={searchValue.trim()}
              >
                <span className="font-medium">Create &quot;{searchValue.trim()}&quot;</span>
              </TagsItem>
            ) : null}
            
            {/* Show filtered available tags */}
            {filteredTags.map((tag) => {
              return (
                <TagsItem
                  key={tag}
                  onSelect={() => {
                    handleSelect(tag);
                    setSearchValue("");
                  }}
                  value={tag}
                >
                  {tag}
                  {selectedTags.includes(tag) ? (
                    <CheckIcon className="text-muted-foreground" size={14} />
                  ) : null}
                </TagsItem>
              );
            })}
          </TagsGroup>
        </TagsList>
      </TagsContent>
    </Tags>
  );
};

