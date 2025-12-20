import { useState, type FC, useEffect } from 'react';
import { useMutation, useQuery } from '@apollo/client';
import { Github, Trash2, ExternalLink, Check, Lock, Globe, GitBranch } from 'lucide-react';
import { toast } from 'sonner';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  PROJECT_REPOSITORY_QUERY,
  AVAILABLE_GITHUB_REPOS_QUERY,
  TEAM_GITHUB_CONNECTIONS_QUERY,
  CONNECT_REPOSITORY_MUTATION,
  DISCONNECT_REPOSITORY_MUTATION,
  type GitHubRepo,
  type Repository,
  type GitHubConnection,
} from '@/graphql/github';

interface ConnectRepositoryCardProps {
  projectId: string;
  teamId: string;
  canManage?: boolean;
  className?: string;
}

export const ConnectRepositoryCard: FC<ConnectRepositoryCardProps> = ({
  projectId,
  teamId,
  canManage = false,
  className,
}) => {
  const [selectedRepoId, setSelectedRepoId] = useState<string>('');
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');

  // Query for connected repository
  const { data: repoData, loading: repoLoading, refetch: refetchRepo } = useQuery<{ 
    projectRepository: Repository | null 
  }>(PROJECT_REPOSITORY_QUERY, {
    variables: { projectId },
    fetchPolicy: 'cache-and-network',
  });

  // Query for available GitHub connections
  const { data: connectionsData, loading: connectionsLoading } = useQuery<{ 
    teamGithubConnections: GitHubConnection[] 
  }>(TEAM_GITHUB_CONNECTIONS_QUERY, {
    variables: { teamId },
    fetchPolicy: 'cache-and-network',
  });

  // Query for available repositories
  const { data: reposData, loading: reposLoading } = useQuery<{ 
    availableGithubRepositories: GitHubRepo[] 
  }>(AVAILABLE_GITHUB_REPOS_QUERY, {
    variables: { teamId },
    fetchPolicy: 'cache-and-network',
    skip: !connectionsData?.teamGithubConnections?.length,
  });

  // Connect mutation
  const [connectRepository, { data: connectData, error: connectError, loading: connectLoading }] = useMutation<{
    connectRepository: { success: boolean; message: string; repository: Repository | null };
  }>(CONNECT_REPOSITORY_MUTATION);

  // Disconnect mutation
  const [disconnectRepository, { data: disconnectData, error: disconnectError, loading: disconnectLoading }] = useMutation<{
    disconnectRepository: { success: boolean; message: string };
  }>(DISCONNECT_REPOSITORY_MUTATION);

  const connectedRepo = repoData?.projectRepository;
  const connections = connectionsData?.teamGithubConnections ?? [];
  const availableRepos = reposData?.availableGithubRepositories ?? [];

  // Auto-select first connection if only one
  useEffect(() => {
    if (connections.length === 1 && !selectedConnectionId) {
      setSelectedConnectionId(connections[0].id);
    }
  }, [connections, selectedConnectionId]);

  // Handle connect success
  useEffect(() => {
    if (connectData?.connectRepository) {
      const { success, message } = connectData.connectRepository;
      if (success) {
        toast('Repository connected', { description: message });
        refetchRepo();
        setSelectedRepoId('');
      } else {
        toast('Failed to connect', { description: message });
      }
    }
  }, [connectData, refetchRepo]);

  // Handle connect error
  useEffect(() => {
    if (connectError) {
      toast('Error', { description: 'Failed to connect repository. Please try again.' });
    }
  }, [connectError]);

  // Handle disconnect success
  useEffect(() => {
    if (disconnectData?.disconnectRepository) {
      const { success, message } = disconnectData.disconnectRepository;
      if (success) {
        toast('Repository disconnected', { description: message });
        refetchRepo();
      } else {
        toast('Failed to disconnect', { description: message });
      }
    }
  }, [disconnectData, refetchRepo]);

  // Handle disconnect error
  useEffect(() => {
    if (disconnectError) {
      toast('Error', { description: 'Failed to disconnect repository. Please try again.' });
    }
  }, [disconnectError]);

  const handleConnect = async () => {
    if (!selectedRepoId || !selectedConnectionId) {
      toast('Please select a repository');
      return;
    }

    await connectRepository({
      variables: {
        projectId,
        githubRepoId: selectedRepoId,
        githubConnectionId: selectedConnectionId,
      },
    });
  };

  const handleDisconnect = async () => {
    await disconnectRepository({
      variables: { projectId },
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const isLoading = repoLoading || connectionsLoading || reposLoading;

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Skeleton className="h-5 w-5" />
            <Skeleton className="h-5 w-40" />
          </div>
          <Skeleton className="h-4 w-64" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }

  // No GitHub connections available
  if (connections.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Github className="h-5 w-5" />
            <CardTitle>GitHub Repository</CardTitle>
          </div>
          <CardDescription>
            Connect a GitHub repository to enable automatic code localization.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <Github className="h-4 w-4" />
            <AlertDescription>
              No GitHub accounts connected to this team. Please connect a GitHub account in team settings first.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center gap-3">
          <Github className="h-5 w-5" />
          <CardTitle>GitHub Repository</CardTitle>
        </div>
        <CardDescription>
          Connect a GitHub repository to enable automatic code localization.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {connectedRepo ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                  <Github className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{connectedRepo.fullName}</span>
                    <Check className="h-4 w-4 text-green-500" />
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <GitBranch className="h-3 w-3" />
                    <span>{connectedRepo.defaultBranch}</span>
                    <span>•</span>
                    <span>Connected {formatDate(connectedRepo.connectedAt)}</span>
                    {connectedRepo.githubUsername ? (
                      <>
                        <span>•</span>
                        <span>via @{connectedRepo.githubUsername}</span>
                      </>
                    ) : null}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  asChild
                >
                  <a
                    href={`https://github.com/${connectedRepo.fullName}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
                {canManage ? (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Disconnect Repository?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will remove the connection to {connectedRepo.fullName} from this project.
                          Localization sync will be disabled.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleDisconnect}
                          disabled={disconnectLoading}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Disconnect
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                ) : null}
              </div>
            </div>
          </div>
        ) : canManage ? (
          <div className="space-y-4">
            {connections.length > 1 ? (
              <div className="space-y-2">
                <label className="text-sm font-medium">GitHub Account</label>
                <Select
                  value={selectedConnectionId}
                  onValueChange={setSelectedConnectionId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select GitHub account" />
                  </SelectTrigger>
                  <SelectContent>
                    {connections.map((conn) => (
                      <SelectItem key={conn.id} value={conn.id}>
                        @{conn.githubUsername}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ) : null}
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Repository</label>
              <Select
                value={selectedRepoId}
                onValueChange={setSelectedRepoId}
                disabled={!selectedConnectionId}
              >
                <SelectTrigger>
                  <SelectValue placeholder={selectedConnectionId ? "Select repository" : "Select a GitHub account first"} />
                </SelectTrigger>
                <SelectContent>
                  {availableRepos.map((repo) => (
                    <SelectItem key={repo.id} value={repo.id}>
                      <div className="flex items-center gap-2">
                        {repo.private ? (
                          <Lock className="h-3 w-3 text-muted-foreground" />
                        ) : (
                          <Globe className="h-3 w-3 text-muted-foreground" />
                        )}
                        <span>{repo.fullName}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleConnect}
              disabled={!selectedRepoId || !selectedConnectionId || connectLoading}
              className="w-full"
            >
              <Github className="mr-2 h-4 w-4" />
              Connect Repository
            </Button>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No repository connected. Ask a project admin to connect a repository.
          </p>
        )}
      </CardContent>
    </Card>
  );
};

