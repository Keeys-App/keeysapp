import { type FC, useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, ChevronsUpDown, PlusCircle, Users } from 'lucide-react';
import { useQuery } from '@apollo/client';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Spinner } from '@/components/ui/spinner';
import { GET_TEAMS } from '@/graphql/teams';
import type { GetTeamsResponse, Team } from '@/graphql/teams';

interface TeamSwitcherProps {
  selectedTeamId?: string;
  onTeamChange?: (teamId: string | undefined) => void;
}

export const TeamSwitcher: FC<TeamSwitcherProps> = ({
  selectedTeamId,
  onTeamChange,
}) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();
  const { data, loading } = useQuery<GetTeamsResponse>(GET_TEAMS, {
    fetchPolicy: 'cache-and-network',
    nextFetchPolicy: 'cache-first',
  });

  const teams = data?.teams || [];
  const selectedTeam = teams.find((team) => {
    return team.id === selectedTeamId;
  });

  // Auto-select first team if none selected and teams are loaded
  // Use ref to prevent infinite loops
  const hasAutoSelectedRef = useRef(false);
  
  useEffect(() => {
    if (!loading && teams.length > 0 && !selectedTeamId && onTeamChange && !hasAutoSelectedRef.current) {
      hasAutoSelectedRef.current = true;
      onTeamChange(teams[0].id);
    }
  }, [loading, teams, selectedTeamId, onTeamChange]);

  // Clear search when popover closes
  useEffect(() => {
    if (!open) {
      setSearch('');
    }
  }, [open]);

  const handleSelect = (team: Team) => {
    if (onTeamChange) {
      onTeamChange(team.id);
    }
    setOpen(false);
    // Navigate to dashboard to show projects of selected team
    navigate('/');
  };

  const handleCreateTeam = () => {
    setOpen(false);
    navigate('/team/create');
  };

  if (loading) {
    return (
      <div className="flex h-9 w-[200px] items-center justify-center rounded-md border border-input bg-transparent px-3">
        <Spinner className="h-4 w-4" />
      </div>
    );
  }

  if (teams.length === 0) {
    return (
      <Button
        variant="outline"
        className="w-[200px] justify-between"
        onClick={() => {
          return navigate('/team/create');
        }}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <PlusCircle className="h-4 w-4 shrink-0" />
          <span className="truncate">Create Team</span>
        </div>
      </Button>
    );
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild className="p-0">
        <button
          role="combobox"
          aria-expanded={open}
          aria-label="Select a team"
          className="h-8 px-2 rounded-md cursor-pointer flex items-center justify-between text-sm gap-2 mr-2 hover:bg-accent/50"
        >
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="truncate">
              {selectedTeam ? selectedTeam.name : 'Select team...'}
            </span>
          </div>
          <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 opacity-50" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput 
            placeholder="Search team..." 
            value={search}
            onValueChange={setSearch}
          />
          <CommandList>
            <CommandEmpty>No team found.</CommandEmpty>
            <CommandGroup>
              {teams.map((team) => {
                return (
                  <CommandItem
                    key={team.id}
                    value={team.id}
                    onSelect={() => {
                      return handleSelect(team);
                    }}
                    className="cursor-pointer"
                  >
                    <Check
                      className={cn(
                        'mr-2 h-4 w-4',
                        selectedTeamId === team.id ? 'opacity-100' : 'opacity-0'
                      )}
                    />
                    <div className="flex flex-1 items-center justify-between">
                      <span className="truncate">{team.name}</span>
                      {team.canManage ? (
                        <span className="ml-2 text-xs text-muted-foreground">
                          Admin
                        </span>
                      ) : null}
                    </div>
                  </CommandItem>
                );
              })}
            </CommandGroup>
            {!search ? (
              <>
                <CommandSeparator />
                <CommandGroup>
                  <CommandItem
                    onSelect={handleCreateTeam}
                    className="cursor-pointer"
                  >
                    <PlusCircle className="mr-2 h-4 w-4" />
                    Create Team
                  </CommandItem>
                </CommandGroup>
              </>
            ) : null}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

