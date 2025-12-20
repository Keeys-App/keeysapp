import { useEffect, useState, type FC } from 'react';
import { useParams, useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@apollo/client';
import { Bot, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useBreadcrumbs } from '@/contexts/BreadcrumbContext';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import {
  GET_TEAM,
  UPDATE_TEAM,
  GET_TEAMS,
  UPDATE_TEAM_AI_SETTINGS,
  GET_AVAILABLE_AI_MODELS,
} from '@/graphql/teams';
import type {
  GetTeamResponse,
  UpdateTeamInput,
  UpdateTeamResponse,
  UpdateTeamAISettingsInput,
  UpdateTeamAISettingsResponse,
  GetAvailableAIModelsResponse,
} from '@/graphql/teams';
import { ConnectGitHubCard } from '@/components/github';
import { PATHS } from '@/constants/paths';

export const EditTeamPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { setBreadcrumbs } = useBreadcrumbs();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [aiProvider, setAiProvider] = useState<string>('');
  const [aiModel, setAiModel] = useState<string>('');

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

  const { data: aiModelsData } = useQuery<GetAvailableAIModelsResponse>(
    GET_AVAILABLE_AI_MODELS
  );

  const [updateTeam] = useMutation<UpdateTeamResponse>(UPDATE_TEAM, {
    refetchQueries: [
      { query: GET_TEAMS },
      { query: GET_TEAM, variables: { id } },
    ],
  });

  const [updateAiSettings] = useMutation<UpdateTeamAISettingsResponse>(
    UPDATE_TEAM_AI_SETTINGS,
    {
      refetchQueries: [
        { query: GET_TEAMS },
        { query: GET_TEAM, variables: { id } },
      ],
    }
  );

  const team = data?.team;
  const availableProviders = aiModelsData?.availableAiModels || [];

  // Get models for selected provider
  const modelsForProvider = availableProviders.find(
    (p) => p.provider === aiProvider
  )?.models || [];

  useEffect(() => {
    if (team) {
      setName(team.name);
      setDescription(team.description || '');
      setAiProvider(team.aiProvider || '');
      setAiModel(team.aiModel || '');
      setBreadcrumbs([
        { label: 'Teams', href: '/teams' },
        { label: team.name, href: `/team/${team.id}` },
        { label: 'Edit' },
      ]);
    }
  }, [team, setBreadcrumbs]);

  // Reset model when provider changes
  useEffect(() => {
    if (aiProvider && team && aiProvider !== team.aiProvider) {
      // When provider changes, reset model
      setAiModel('');
    }
  }, [aiProvider, team]);

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

  const handleSaveAiSettings = async () => {
    if (!id) {
      return;
    }

    await withSaving(
      async () => {
        const input: UpdateTeamAISettingsInput = {
          teamId: id,
          aiProvider: aiProvider || undefined,
          aiModel: aiModel || undefined,
        };

        const result = await updateAiSettings({ variables: { input } });

        if (result.data?.updateTeamAiSettings) {
          toast('AI settings updated successfully');
        }
      },
      'Updating AI settings...'
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

      {/* AI Settings Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            <CardTitle>AI Settings</CardTitle>
          </div>
          <CardDescription>
            Configure the AI model used for translations and other AI features
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="aiProvider">AI Provider</Label>
            <Select
              value={aiProvider || '__default__'}
              onValueChange={(value) => {
                setAiProvider(value === '__default__' ? '' : value);
              }}
              disabled={isSaving}
            >
              <SelectTrigger id="aiProvider">
                <SelectValue placeholder="Select AI provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__default__">Use default</SelectItem>
                {availableProviders.map((provider) => (
                  <SelectItem key={provider.provider} value={provider.provider}>
                    {provider.provider}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="aiModel">AI Model</Label>
            <Select
              value={aiModel || '__default__'}
              onValueChange={(value) => {
                setAiModel(value === '__default__' ? '' : value);
              }}
              disabled={isSaving || !aiProvider}
            >
              <SelectTrigger id="aiModel">
                <SelectValue
                  placeholder={
                    aiProvider
                      ? 'Select model'
                      : 'Select a provider first'
                  }
                />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__default__">Use default</SelectItem>
                {modelsForProvider.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name} - {model.description}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              asChild
            >
              <Link to={PATHS.TEAM_USAGE.replace(':id', id || '')}>
                <BarChart3 className="h-4 w-4 mr-2" />
                View Token Usage
              </Link>
            </Button>
            <Button
              onClick={handleSaveAiSettings}
              disabled={isSaving}
            >
              Save AI Settings
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* GitHub Integration Card */}
      {id ? (
        <ConnectGitHubCard teamId={id} canManage={true} />
      ) : null}
    </div>
  );
};

