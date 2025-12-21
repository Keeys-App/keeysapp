import { useState, useEffect, useRef, type FC, type KeyboardEvent } from 'react';
import { useQuery } from '@apollo/client';
import { GitBranch, X, Loader2, Check, Star } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { REPOSITORY_BRANCHES_QUERY, type RepositoryBranch } from '@/graphql/scanner';

interface BranchPickerProps {
  projectId: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export const BranchPicker: FC<BranchPickerProps> = ({
  projectId,
  value,
  onChange,
  placeholder = 'Select or search branch',
  disabled = false,
  className,
}) => {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Query for branches
  const { data, loading } = useQuery<{
    repositoryBranches: RepositoryBranch[];
  }>(REPOSITORY_BRANCHES_QUERY, {
    variables: { projectId },
    fetchPolicy: 'cache-and-network',
  });

  const branches = data?.repositoryBranches ?? [];
  const defaultBranch = branches.find((b) => b.isDefault)?.name ?? '';

  // Filter branches locally based on input
  const filteredBranches = inputValue
    ? branches.filter((branch) => branch.name.toLowerCase().includes(inputValue.toLowerCase()))
    : branches;

  // Auto-select default branch when loaded if no value set
  useEffect(() => {
    if (defaultBranch && !value) {
      onChange(defaultBranch);
      setInputValue(defaultBranch);
    }
  }, [defaultBranch, value, onChange]);

  // Sync external value changes
  useEffect(() => {
    setInputValue(value);
  }, [value]);

  // Reset highlighted index when list changes
  useEffect(() => {
    setHighlightedIndex(-1);
  }, [filteredBranches.length]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
        setHighlightedIndex(-1);
        // Restore to current value if input doesn't match any branch
        const matchingBranch = branches.find(
          (b) => b.name.toLowerCase() === inputValue.toLowerCase()
        );
        if (!matchingBranch && value) {
          setInputValue(value);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [branches, inputValue, value]);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && listRef.current) {
      const items = listRef.current.querySelectorAll('[data-branch-item]');
      const item = items[highlightedIndex] as HTMLElement;
      if (item) {
        item.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex]);

  const handleInputChange = (newValue: string) => {
    setInputValue(newValue);
    setHighlightedIndex(-1);
    if (!open) {
      setOpen(true);
    }
  };

  const handleSelect = (branch: RepositoryBranch) => {
    setInputValue(branch.name);
    onChange(branch.name);
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
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => {
          const next = prev + 1;
          return next >= filteredBranches.length ? 0 : next;
        });
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => {
          const next = prev - 1;
          return next < 0 ? filteredBranches.length - 1 : next;
        });
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < filteredBranches.length) {
          handleSelect(filteredBranches[highlightedIndex]);
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
  };

  return (
    <div className={cn('relative', className)} ref={containerRef}>
      {/* Input */}
      <div className="relative">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <GitBranch className="h-4 w-4 text-muted-foreground" />
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
          disabled={disabled || loading}
          className={cn(
            'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors',
            'file:border-0 file:bg-transparent file:text-sm file:font-medium',
            'placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'pl-9 pr-16'
          )}
        />
        <div className="absolute inset-y-0 right-0 flex items-center gap-1 pr-2">
          {loading ? <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" /> : null}
          {inputValue && !disabled ? (
            <Button type="button" variant="ghost" size="icon" className="h-6 w-6" onClick={handleClear}>
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
              {filteredBranches.length === 0 ? (
                <div className="px-2 py-6 text-center text-sm text-muted-foreground">
                  {loading ? 'Loading branches...' : 'No branches found'}
                </div>
              ) : (
                filteredBranches.map((branch, index) => {
                  const isSelected = value === branch.name;
                  const isHighlighted = highlightedIndex === index;
                  const isDefault = branch.isDefault;

                  return (
                    <div
                      key={branch.name}
                      data-branch-item
                      onClick={() => {
                        handleSelect(branch);
                      }}
                      className={cn(
                        'flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm',
                        'hover:bg-accent/50',
                        isHighlighted && 'bg-accent text-accent-foreground',
                        isSelected && !isHighlighted && 'bg-primary/10'
                      )}>
                      <GitBranch
                        className={cn(
                          'h-4 w-4 shrink-0',
                          isSelected ? 'text-primary' : isDefault ? 'text-amber-500' : 'text-muted-foreground'
                        )}
                      />
                      <span
                        className={cn(
                          'flex-1',
                          isSelected ? 'font-medium text-primary' : isDefault && 'text-amber-600 dark:text-amber-400'
                        )}>
                        {branch.name}
                      </span>
                      {isDefault ? <Star className="h-3 w-3 shrink-0 fill-amber-400 text-amber-400" /> : null}
                      {isSelected ? <Check className="h-4 w-4 shrink-0 text-primary" /> : null}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

