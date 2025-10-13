import { Search, X } from "lucide-react";
import { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput } from "../ui/input-group";
import { useKeysSearchStore } from "@/stores";
import { useState, useEffect, type FC, type ChangeEvent } from "react";
import { cn } from "@/lib/utils";
import { Spinner } from "../ui/spinner";

interface KeysSearchProps {
  resultsCount?: number | null;
  isLoading?: boolean;
}

export const KeysSearch: FC<KeysSearchProps> = ({ resultsCount, isLoading = false }) => {
  const { search, setSearch, clearSearch } = useKeysSearchStore();
  const [localValue, setLocalValue] = useState(search);
  const [isTyping, setIsTyping] = useState(false);

  // Sync local value with store
  useEffect(() => {
    setLocalValue(search);
  }, [search]);

  // Debounced search update
  useEffect(() => {
    // Only show typing indicator if there's actual input change
    if (localValue !== search) {
      setIsTyping(true);
    }
    
    const timer = setTimeout(() => {
      setSearch(localValue);
      setIsTyping(false);
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [localValue, setSearch, search]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.target.value);
  };

  const handleClear = () => {
    setLocalValue('');
    clearSearch();
  };

  const showResults = search.length > 0 && resultsCount !== null && resultsCount !== undefined;
  const showLoading = isLoading || isTyping;

  return (
    <InputGroup className="bg-background rounded-4xl py-2 w-70">
      <InputGroupAddon>
        <InputGroupButton variant="secondary" size="icon-xs" className="rounded-4xl">
          {showLoading ? <Spinner className="h-4 w-4" /> : <Search />}
        </InputGroupButton>
      </InputGroupAddon>
      <InputGroupInput 
        type="text" 
        placeholder="Search keys" 
        value={localValue}
        onChange={handleChange}
      />
      {showResults ? (
        <InputGroupAddon 
          align="inline-end"
        >
          {resultsCount} {resultsCount === 1 ? 'result' : 'results'}
        </InputGroupAddon>
      ) : null}
      {localValue.length > 0 ? (
        <InputGroupAddon align="inline-end">
          <InputGroupButton 
            variant="ghost" 
            size="icon-xs" 
            className="rounded-4xl"
            onClick={handleClear}
          >
            <X className="h-3 w-3" />
          </InputGroupButton>
        </InputGroupAddon>
      ) : null}
    </InputGroup>
  );
};
