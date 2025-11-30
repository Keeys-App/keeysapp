import { useState, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import { CREATE_TEAM, GET_TEAMS } from '@/graphql/teams';
import type { CreateTeamInput, CreateTeamResponse } from '@/graphql/teams';

interface CreateTeamStepProps {
  onNext: (teamId: string) => void;
}

export const CreateTeamStep: FC<CreateTeamStepProps> = ({ onNext }) => {
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const [createTeam] = useMutation<CreateTeamResponse>(CREATE_TEAM, {
    refetchQueries: [{ query: GET_TEAMS }],
  });

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
          onNext(result.data.createTeam.id);
        }
      },
      'Creating team...'
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
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
            autoFocus
          />
          <p className="text-sm text-muted-foreground">
            Choose a name that describes your team or organization
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description (Optional)</Label>
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
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={isSaving}>
          Continue
        </Button>
      </div>
    </form>
  );
};

