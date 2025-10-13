import { useEffect, useState, type FC } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { Plus, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { useBreadcrumbs } from '@/contexts/BreadcrumbContext';
import { TeamMembersList } from '@/components/team/TeamMembersList';
import { AddTeamMemberDialog } from '@/components/team/AddTeamMemberDialog';
import { GET_TEAM } from '@/graphql/teams';
import type { GetTeamResponse } from '@/graphql/teams';

export const TeamPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setBreadcrumbs } = useBreadcrumbs();
  const [addMemberDialogOpen, setAddMemberDialogOpen] = useState(false);

  const { data, loading, error } = useQuery<GetTeamResponse>(GET_TEAM, {
    variables: { id },
    skip: !id,
    fetchPolicy: 'cache-and-network',
    nextFetchPolicy: 'cache-first',
  });

  const team = data?.team;

  useEffect(() => {
    if (team) {
      setBreadcrumbs([
        { label: 'Teams', href: '/teams' },
        { label: team.name },
      ]);
    }
  }, [team, setBreadcrumbs]);

  // Only show spinner if loading AND no cached data
  if (loading && !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-destructive mb-4">Team not found</p>
          <Button onClick={() => {
            return navigate('/teams');
          }}>
            Back to Teams
          </Button>
        </div>
      </div>
    );
  }

  const existingMemberEmails = [
    team.owner.email.toLowerCase(),
    ...team.members.map((m) => {
      return m.user.email.toLowerCase();
    }),
  ];

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{team.name}</h1>
          {team.description ? (
            <p className="text-muted-foreground mt-1">{team.description}</p>
          ) : null}
        </div>
        {team.canManage ? (
          <Button
            variant="outline"
            onClick={() => {
              return navigate(`/team/${team.id}/edit`);
            }}
          >
            <Settings className="mr-2 h-4 w-4" />
            Edit Team
          </Button>
        ) : null}
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Team Members</CardTitle>
                <CardDescription>
                  Manage who has access to this team
                </CardDescription>
              </div>
              {team.canManage ? (
                <Button
                  onClick={() => {
                    return setAddMemberDialogOpen(true);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Member
                </Button>
              ) : null}
            </div>
          </CardHeader>
          <CardContent>
            <TeamMembersList team={team} />
          </CardContent>
        </Card>
      </div>

      {team.canManage ? (
        <AddTeamMemberDialog
          open={addMemberDialogOpen}
          onOpenChange={setAddMemberDialogOpen}
          teamId={team.id}
          existingMemberEmails={existingMemberEmails}
        />
      ) : null}
    </div>
  );
};

