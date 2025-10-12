import { FC, useState, useEffect } from 'react';
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
  const navigate = useNavigate();
  const { data, loading } = useQuery<GetTeamsResponse>(GET_TEAMS);

  const teams = data?.teams || [];
  const selectedTeam = teams.find((team) => {
    return team.id === selectedTeamId;
  });

  // Auto-select first team if none selected and teams are loaded
  useEffect(() => {
    if (!loading && teams.length > 0 && !selectedTeamId && onTeamChange) {
      onTeamChange(teams[0].id);
    }
  }, [loading, teams, selectedTeamId, onTeamChange]);

  const handleSelect = (team: Team) => {
    if (onTeamChange) {
      onTeamChange(team.id);
    }
    setOpen(false);
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
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label="Select a team"
          className="w-[200px] justify-between"
        >
          <div className="flex items-center gap-2 overflow-hidden">
            <Users className="h-4 w-4 shrink-0" />
            <span className="truncate">
              {selectedTeam ? selectedTeam.name : 'Select team...'}
            </span>
          </div>
          <ChevronsUpDown className="ml-auto h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search team..." />
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
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

