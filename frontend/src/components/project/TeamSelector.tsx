import { FC } from 'react';
import { useQuery } from '@apollo/client';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Spinner } from '@/components/ui/spinner';
import { GET_TEAMS } from '@/graphql/teams';
import type { GetTeamsResponse } from '@/graphql/teams';

interface TeamSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const TeamSelector: FC<TeamSelectorProps> = ({ value, onChange, disabled }) => {
  const { data, loading, error } = useQuery<GetTeamsResponse>(GET_TEAMS, {
    fetchPolicy: 'cache-first',
  });

  if (loading) {
    return (
      <div className="space-y-2">
        <Label>Team *</Label>
        <div className="flex h-10 items-center justify-center rounded-md border border-input bg-background px-3">
          <Spinner className="h-4 w-4" />
        </div>
      </div>
    );
  }

  if (error || !data?.teams) {
    return (
      <div className="space-y-2">
        <Label>Team *</Label>
        <div className="rounded-md border border-destructive bg-destructive/10 px-3 py-2 text-sm text-destructive">
          Failed to load teams
        </div>
      </div>
    );
  }

  const teams = data.teams;

  if (teams.length === 0) {
    return (
      <div className="space-y-2">
        <Label>Team *</Label>
        <div className="rounded-md border border-muted bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
          No teams available. Please create a team first.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Label htmlFor="team">Team *</Label>
      <Select value={value} onValueChange={onChange} disabled={disabled}>
        <SelectTrigger id="team">
          <SelectValue placeholder="Select a team" />
        </SelectTrigger>
        <SelectContent>
          {teams.map((team) => {
            return (
              <SelectItem key={team.id} value={team.id}>
                {team.name}
              </SelectItem>
            );
          })}
        </SelectContent>
      </Select>
    </div>
  );
};

