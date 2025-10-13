import { FC, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useBreadcrumbs } from '@/contexts/BreadcrumbContext';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import { CREATE_TEAM, GET_TEAMS } from '@/graphql/teams';
import type { CreateTeamInput, CreateTeamResponse } from '@/graphql/teams';

export const CreateTeamPage: FC = () => {
  const navigate = useNavigate();
  const { setBreadcrumbs } = useBreadcrumbs();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const [createTeam] = useMutation<CreateTeamResponse>(CREATE_TEAM, {
    refetchQueries: [{ query: GET_TEAMS }],
  });

  useEffect(() => {
    setBreadcrumbs([
      { label: 'Teams', href: '/teams' },
      { label: 'Create Team' },
    ]);
  }, [setBreadcrumbs]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast('Team name is required');
      return;
    }

    await withSaving(
      async () => {
        const input: CreateTeamInput = {
          name: name.trim(),
          description: description.trim() || undefined,
        };

        const result = await createTeam({ variables: { input } });

        if (result.data?.createTeam) {
          toast('Team created successfully');
          navigate(`/team/${result.data.createTeam.id}`);
        }
      },
      'Creating team...'
    );
  };

  return (
    <div className="flex h-full items-center justify-center p-6">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Create New Team</CardTitle>
          <CardDescription>
            Create a team to collaborate with others on projects
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
                  return navigate('/teams');
                }}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSaving}>
                Create Team
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

