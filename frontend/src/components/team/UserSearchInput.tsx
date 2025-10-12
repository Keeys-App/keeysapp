import { FC, useState, useEffect, useCallback } from 'react';
import { useQuery } from '@apollo/client';
import { Search, Loader2 } from 'lucide-react';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { SEARCH_USERS } from '@/graphql/teams';
import type { User, SearchUsersResponse } from '@/graphql/teams';

interface UserSearchInputProps {
  onUserSelect: (user: User) => void;
  excludeUserIds?: string[];
}

export const UserSearchInput: FC<UserSearchInputProps> = ({
  onUserSelect,
  excludeUserIds = [],
}) => {
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [searchQuery]);

  const { data, loading } = useQuery<SearchUsersResponse>(SEARCH_USERS, {
    variables: { query: debouncedQuery, limit: 10 },
    skip: debouncedQuery.length < 2,
  });

  const users = data?.searchUsers || [];
  const filteredUsers = users.filter((user) => {
    return !excludeUserIds.includes(user.id);
  });

  const handleSelect = (user: User) => {
    onUserSelect(user);
    setOpen(false);
    setSearchQuery('');
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="w-full justify-start">
          <Search className="mr-2 h-4 w-4" />
          Search by email or username...
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[300px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Search users..."
            value={searchQuery}
            onValueChange={setSearchQuery}
          />
          <CommandList>
            {loading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : searchQuery.length < 2 ? (
              <CommandEmpty>Type at least 2 characters to search</CommandEmpty>
            ) : filteredUsers.length === 0 ? (
              <CommandEmpty>No users found</CommandEmpty>
            ) : (
              <CommandGroup>
                {filteredUsers.map((user) => {
                  return (
                    <CommandItem
                      key={user.id}
                      value={user.id}
                      onSelect={() => {
                        return handleSelect(user);
                      }}
                      className="cursor-pointer"
                    >
                      <div className="flex flex-col">
                        <span className="font-medium">{user.username}</span>
                        <span className="text-xs text-muted-foreground">
                          {user.email}
                        </span>
                      </div>
                    </CommandItem>
                  );
                })}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

