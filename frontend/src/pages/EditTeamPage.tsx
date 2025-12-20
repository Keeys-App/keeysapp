import { useEffect, useState, type FC } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation } from '@apollo/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { useBreadcrumbs } from '@/contexts/BreadcrumbContext';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import {
  GET_TEAM,
  UPDATE_TEAM,
  GET_TEAMS,
} from '@/graphql/teams';
import type { GetTeamResponse, UpdateTeamInput, UpdateTeamResponse } from '@/graphql/teams';
import { ConnectGitHubCard } from '@/components/github';

export const EditTeamPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { setBreadcrumbs } = useBreadcrumbs();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  // Handle GitHub App installation callback
  useEffect(() => {
    const githubInstalled = searchParams.get('github_installed');
    const githubUpdated = searchParams.get('github_updated');
    
    if (githubInstalled === 'true') {
      toast('GitHub App installed!', {
        description: 'You can now access your repositories.',
      });
      // Remove query param
      searchParams.delete('github_installed');
      setSearchParams(searchParams, { replace: true });
    }
    
    if (githubUpdated === 'true') {
      toast('GitHub App updated', {
        description: 'Repository access has been updated.',
      });
      searchParams.delete('github_updated');
      setSearchParams(searchParams, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  const { data, loading } = useQuery<GetTeamResponse>(GET_TEAM, {
    variables: { id },
    skip: !id,
  });

  const [updateTeam] = useMutation<UpdateTeamResponse>(UPDATE_TEAM, {
    refetchQueries: [
      { query: GET_TEAMS },
      { query: GET_TEAM, variables: { id } },
    ],
  });

  const team = data?.team;

  useEffect(() => {
    if (team) {
      setName(team.name);
      setDescription(team.description || '');
      setBreadcrumbs([
        { label: 'Teams', href: '/teams' },
        { label: team.name, href: `/team/${team.id}` },
        { label: 'Edit' },
      ]);
    }
  }, [team, setBreadcrumbs]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast('Team name is required');
      return;
    }

    if (!id) {
      return;
    }

    await withSaving(
      async () => {
        const input: UpdateTeamInput = {
          id,
          name: name.trim(),
          description: description.trim() || undefined,
        };

        const result = await updateTeam({ variables: { input } });

        if (result.data?.updateTeam) {
          toast('Team updated successfully');
          navigate(`/team/${id}`);
        }
      },
      'Updating team...'
    );
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (!team) {
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

  if (!team.canManage) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-destructive mb-4">You don't have permission to edit this team</p>
          <Button onClick={() => {
            return navigate(`/team/${id}`);
          }}>
            Back to Team
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-2xl py-8 space-y-6">
      {/* Team Settings Card */}
      <Card>
        <CardHeader>
          <CardTitle>Team Settings</CardTitle>
          <CardDescription>
            Update your team's name and description
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Team Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => {
                  return setName(e.target.value);
                }}
                placeholder="My Team"
                required
                disabled={isSaving}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => {
                  return setDescription(e.target.value);
                }}
                placeholder="Brief description of your team..."
                rows={3}
                disabled={isSaving}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  return navigate(`/team/${id}`);
                }}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSaving}>
                Save Changes
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* GitHub Integration Card */}
      {id ? (
        <ConnectGitHubCard teamId={id} canManage={true} />
      ) : null}
    </div>
  );
};

