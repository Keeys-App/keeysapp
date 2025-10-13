import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';
import { useKeysSearchStore } from '@/stores';
import type { FC } from 'react';

interface EmptySearchResultsProps {
  searchQuery: string;
}

export const EmptySearchResults: FC<EmptySearchResultsProps> = ({ searchQuery }) => {
  const { clearSearch } = useKeysSearchStore();

  return (
    <div className="flex items-center justify-center flex-1">
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <Search />
          </EmptyMedia>
          <EmptyTitle>No Results Found</EmptyTitle>
          <EmptyDescription>
            No translation keys match your search for "{searchQuery}". Try a different search term.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button onClick={clearSearch} variant="outline">
            Clear Search
          </Button>
        </EmptyContent>
      </Empty>
    </div>
  );
};

