import { type FC, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { useQuery } from '@apollo/client';
import { Button } from '@/components/ui/button';
import { TeamCard } from '@/components/team/TeamCard';
import { EmptyTeams } from '@/components/team/EmptyTeams';
import { Spinner } from '@/components/ui/spinner';
import { useBreadcrumbs } from '@/contexts/BreadcrumbContext';
import { GET_TEAMS } from '@/graphql/teams';
import type { GetTeamsResponse } from '@/graphql/teams';
import { PATHS } from '@/constants/paths';

export const TeamsPage: FC = () => {
  const navigate = useNavigate();
  const { setBreadcrumbs } = useBreadcrumbs();
  const { data, loading, error } = useQuery<GetTeamsResponse>(GET_TEAMS, {
    fetchPolicy: 'cache-and-network',
    nextFetchPolicy: 'cache-first',
  });

  useEffect(() => {
    setBreadcrumbs([{ label: 'Teams' }]);
  }, [setBreadcrumbs]);

  // Only show spinner if loading AND no data from cache
  if (loading && !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-destructive">Failed to load teams</p>
      </div>
    );
  }

  const teams = data?.teams || [];

  // Show empty state when no teams exist
  if (teams.length === 0) {
    return (
      <EmptyTeams
        onCreateTeam={() => {
          return navigate(PATHS.TEAM_CREATE);
        }}
      />
    );
  }

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Teams</h1>
          <p className="text-muted-foreground">
            Manage your teams and collaborate with others
          </p>
        </div>
        <Button onClick={() => {
          return navigate(PATHS.TEAM_CREATE);
        }}>
          <Plus className="mr-2 h-4 w-4" />
          Create Team
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {teams.map((team) => {
          return <TeamCard key={team.id} team={team} />;
        })}
      </div>
    </div>
  );
};

