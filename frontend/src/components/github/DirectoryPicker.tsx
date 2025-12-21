import { useState, useEffect, useRef, type FC, type KeyboardEvent } from 'react';
import { useLazyQuery } from '@apollo/client';
import { Folder, AlertCircle, X, Loader2, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
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
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Lazy query for fetching directories
  const [fetchDirectories, { data, loading }] = useLazyQuery<{
    repositoryDirectories: RepositoryDirectory[];
  }>(REPOSITORY_DIRECTORIES_QUERY, {
    fetchPolicy: 'cache-and-network',
  });

  const directories = data?.repositoryDirectories ?? [];

  // Filter directories based on input
  const filteredDirectories = inputValue
    ? directories.filter(
        (dir) =>
          dir.path.toLowerCase().includes(inputValue.toLowerCase()) ||
          dir.name.toLowerCase().includes(inputValue.toLowerCase())
      )
    : directories;

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

  // Reset highlighted index when list changes
  useEffect(() => {
    setHighlightedIndex(-1);
  }, [filteredDirectories.length]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && listRef.current) {
      const items = listRef.current.querySelectorAll('[data-directory-item]');
      const item = items[highlightedIndex] as HTMLElement;
      if (item) {
        item.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex]);

  const handleInputChange = (newValue: string) => {
    setInputValue(newValue);
    onChange(newValue);
    setHighlightedIndex(-1);
    if (!open) {
      setOpen(true);
    }
  };

  const handleSelect = (directory: RepositoryDirectory) => {
    setInputValue(directory.path);
    onChange(directory.path);
    setOpen(false);
    setHighlightedIndex(-1);
    inputRef.current?.focus();
  };

  const handleClear = () => {
    setInputValue('');
    onChange('');
    setHighlightedIndex(-1);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!open) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        setOpen(true);
        fetchDirectories({
          variables: {
            projectId,
            prefix: inputValue || null,
          },
        });
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => {
          const next = prev + 1;
          return next >= filteredDirectories.length ? 0 : next;
        });
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => {
          const next = prev - 1;
          return next < 0 ? filteredDirectories.length - 1 : next;
        });
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < filteredDirectories.length) {
          handleSelect(filteredDirectories[highlightedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setOpen(false);
        setHighlightedIndex(-1);
        break;
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

  return (
    <div className={cn('relative', className)} ref={containerRef}>
      {/* Input */}
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
          onKeyDown={handleKeyDown}
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
          <div className="absolute top-0 z-50 max-h-[300px] w-full overflow-auto rounded-md border bg-popover text-popover-foreground shadow-md outline-none animate-in fade-in-0 zoom-in-95">
            <div ref={listRef} className="p-1">
              {filteredDirectories.length === 0 ? (
                <div className="px-2 py-6 text-center text-sm text-muted-foreground">
                  {loading ? 'Loading directories...' : 'No directories found'}
                </div>
              ) : (
                filteredDirectories.map((directory, index) => {
                  const isExactMatch = inputValue.toLowerCase() === directory.path.toLowerCase();
                  const isHighlighted = highlightedIndex === index;
                  
                  return (
                    <div
                      key={directory.path}
                      data-directory-item
                      onClick={() => {
                        handleSelect(directory);
                      }}
                      className={cn(
                        'flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm',
                        'hover:bg-accent/50',
                        isHighlighted && 'bg-accent text-accent-foreground',
                        isExactMatch && !isHighlighted && 'bg-primary/10'
                      )}
                    >
                      <Folder className={cn(
                        'h-4 w-4 shrink-0',
                        isExactMatch ? 'text-primary' : 'text-muted-foreground'
                      )} />
                      <div className="flex flex-1 flex-col overflow-hidden">
                        <span className={cn(
                          'font-medium',
                          isExactMatch && 'text-primary'
                        )}>
                          {directory.name}
                        </span>
                        <span className="truncate text-xs text-muted-foreground">
                          /{directory.path}
                        </span>
                      </div>
                      {isExactMatch ? (
                        <Check className="h-4 w-4 shrink-0 text-primary" />
                      ) : null}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      ) : null}

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

