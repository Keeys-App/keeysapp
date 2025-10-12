import { type FC } from "react";
import { Button } from "@/components/ui/button";
import {
  Sparkle,
  ListRestart,
  ArrowDownWideNarrow,
  ListStart,
  Wand,
  BookOpenCheck,
  BookPlus,
} from "lucide-react";
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle,
  ItemMedia,
} from "../ui/item";

interface KeySuggestionsProps {
  currentLanguage?: string | null;
  currentLanguageValue?: string;
  defaultLanguage?: string | null;
  defaultLanguageValue?: string;
}

/**
 * Component for displaying translation suggestions and context
 * Shows the original text in the default language to help with translation
 */
export const KeySuggestions: FC<KeySuggestionsProps> = ({
  currentLanguage,
  currentLanguageValue,
  defaultLanguage,
  defaultLanguageValue,
}) => {
  // If no language is being edited, show a message
  if (!currentLanguage) {
    return (
      <Item variant="outline">
        <ItemMedia>
          <div className="flex items-center gap-2 p-1 rounded-md bg-gray-500/10">
            <Sparkle className="text-gray-500/70" />
          </div>
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Autopilot</ItemTitle>
          <ItemDescription className="text-balance">
            Select a translation field to edit to see suggestions
          </ItemDescription>
        </ItemContent>
      </Item>
    );
  }

  if (currentLanguageValue) {
    return (
      <Item variant="outline">
        <ItemMedia>
          <div className="flex items-center gap-2 p-1 rounded-md bg-indigo-500/10">
            <Sparkle className="text-indigo-500" />
          </div>
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Autopilot</ItemTitle>
          <ItemDescription className="text-balance">
            Enhance the quality of this translation using AI.
          </ItemDescription>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <Button size="sm" variant="outline">
              <ListRestart />
              Rephrase
            </Button>
            <Button size="sm" variant="outline">
              <ArrowDownWideNarrow />
              Shorten
            </Button>
            <Button size="sm" variant="outline">
              <ListStart />
              Suggest variants
            </Button>
            <Button size="sm" variant="outline">
              <BookPlus />
              Add context
            </Button>
          </div>
        </ItemContent>
      </Item>
    );
  }

  // Show context from default language
  return (
    <div className="space-y-4">
      <Item variant="outline">
        <ItemMedia>
          <div className="flex items-center gap-2 p-1 rounded-md bg-indigo-500/10">
            <Sparkle className="text-indigo-500" />
          </div>
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Autopilot</ItemTitle>
          <ItemDescription className="text-balance">
            Translate with AI based on the default language.
          </ItemDescription>
          <div className="flex items-center gap-2 mt-2">
            <Button size="sm">
              <Wand />
              Translate
            </Button>
            <Button size="sm" variant="outline">
              <BookPlus />
              Add context
            </Button>
          </div>
        </ItemContent>
      </Item>
    </div>
  );
};
