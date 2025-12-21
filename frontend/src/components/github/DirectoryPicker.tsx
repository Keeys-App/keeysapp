import { useState, useEffect, useRef, type FC, type KeyboardEvent } from 'react';
import { useLazyQuery } from '@apollo/client';
import { Folder, AlertCircle, X, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Button } from '@/components/ui/button';
import {
  REPOSITORY_DIRECTORIES_QUERY,
  type RepositoryDirectory,
} from '@/graphql/scanner';

interface DirectoryPickerProps {
  projectId: string;
  value: string;
  onChange: (value: string) => void;
  error?: string | null;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export const DirectoryPicker: FC<DirectoryPickerProps> = ({
  projectId,
  value,
  onChange,
  error,
  placeholder = 'Enter directory path or select from list',
  disabled = false,
  className,
}) => {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Lazy query for fetching directories
  const [fetchDirectories, { data, loading }] = useLazyQuery<{
    repositoryDirectories: RepositoryDirectory[];
  }>(REPOSITORY_DIRECTORIES_QUERY, {
    fetchPolicy: 'cache-and-network',
  });

  const directories = data?.repositoryDirectories ?? [];

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputValue.length >= 0) {
        fetchDirectories({
          variables: {
            projectId,
            prefix: inputValue || null,
          },
        });
      }
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [inputValue, projectId, fetchDirectories]);

  // Sync external value changes
  useEffect(() => {
    setInputValue(value);
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (newValue: string) => {
    setInputValue(newValue);
    onChange(newValue);
    if (!open) {
      setOpen(true);
    }
  };

  const handleSelect = (directory: RepositoryDirectory) => {
    setInputValue(directory.path);
    onChange(directory.path);
    setOpen(false);
    inputRef.current?.focus();
  };

  const handleClear = () => {
    setInputValue('');
    onChange('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Escape') {
      setOpen(false);
      inputRef.current?.focus();
    } else if (e.key === 'Enter' && !open) {
      // If dropdown closed and Enter pressed, don't do anything special
      e.preventDefault();
    }
  };

  const handleFocus = () => {
    setOpen(true);
    // Fetch directories on focus if not already fetched
    fetchDirectories({
      variables: {
        projectId,
        prefix: inputValue || null,
      },
    });
  };

  // Filter directories based on input
  const filteredDirectories = inputValue
    ? directories.filter(
        (dir) =>
          dir.path.toLowerCase().includes(inputValue.toLowerCase()) ||
          dir.name.toLowerCase().includes(inputValue.toLowerCase())
      )
    : directories;

  return (
    <div className={cn('relative', className)} ref={containerRef}>
      <Command
        shouldFilter={false}
        onKeyDown={handleKeyDown}
        className="overflow-visible bg-transparent"
        loop
      >
        {/* Custom input styled like regular Input */}
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Folder className="h-4 w-4 text-muted-foreground" />
          </div>
          <input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => {
              handleInputChange(e.target.value);
            }}
            onFocus={handleFocus}
            placeholder={placeholder}
            disabled={disabled}
            className={cn(
              'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors',
              'file:border-0 file:bg-transparent file:text-sm file:font-medium',
              'placeholder:text-muted-foreground',
              'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
              'disabled:cursor-not-allowed disabled:opacity-50',
              'pl-9 pr-16',
              error && 'border-red-500 focus-visible:ring-red-500'
            )}
            // cmdk will handle arrow navigation
            cmdk-input=""
          />
          <div className="absolute inset-y-0 right-0 flex items-center gap-1 pr-2">
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            ) : null}
            {inputValue && !disabled ? (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={handleClear}
              >
                <X className="h-3 w-3" />
                <span className="sr-only">Clear</span>
              </Button>
            ) : null}
          </div>
        </div>

        {/* Dropdown list */}
        {open && !disabled ? (
          <div className="relative mt-1">
            <div className="absolute top-0 z-50 w-full rounded-md border bg-popover text-popover-foreground shadow-md outline-none animate-in fade-in-0 zoom-in-95">
              <CommandList className="max-h-[300px]">
                {filteredDirectories.length === 0 ? (
                  <CommandEmpty>
                    {loading ? 'Loading directories...' : 'No directories found'}
                  </CommandEmpty>
                ) : null}
                <CommandGroup>
                  {filteredDirectories.map((directory) => (
                    <CommandItem
                      key={directory.path}
                      value={directory.path}
                      onSelect={() => {
                        handleSelect(directory);
                      }}
                      className="flex cursor-pointer items-center gap-2"
                    >
                      <Folder className="h-4 w-4 text-muted-foreground" />
                      <div className="flex flex-col">
                        <span className="font-medium">{directory.name}</span>
                        <span className="text-xs text-muted-foreground">
                          /{directory.path}
                        </span>
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              </CommandList>
            </div>
          </div>
        ) : null}
      </Command>

      {/* Error message */}
      {error ? (
        <div className="mt-1.5 flex items-center gap-1.5 text-sm text-red-500">
          <AlertCircle className="h-3.5 w-3.5" />
          <span>{error}</span>
        </div>
      ) : null}

      {/* Help text */}
      {!error ? (
        <p className="mt-1.5 text-xs text-muted-foreground">
          Leave empty to scan the entire repository
        </p>
      ) : null}
    </div>
  );
};

