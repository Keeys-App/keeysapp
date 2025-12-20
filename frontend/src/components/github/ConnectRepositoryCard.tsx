import { useState, type FC, useEffect } from 'react';
import { useMutation, useQuery, useLazyQuery } from '@apollo/client';
import {
  Github,
  Trash2,
  ExternalLink,
  Check,
  Lock,
  Globe,
  GitBranch,
  ChevronsUpDown,
  Search,
  AlertTriangle,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  PROJECT_REPOSITORY_QUERY,
  SEARCH_GITHUB_REPOS_QUERY,
  TEAM_GITHUB_CONNECTIONS_QUERY,
  CONNECT_REPOSITORY_MUTATION,
  DISCONNECT_REPOSITORY_MUTATION,
  type GitHubRepo,
  type Repository,
  type GitHubConnection,
} from '@/graphql/github';
import { Link } from 'react-router-dom';
import { PATHS } from '@/constants/paths';

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
  const [selectedRepo, setSelectedRepo] = useState<GitHubRepo | null>(null);
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');
  const [repoComboboxOpen, setRepoComboboxOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Query for connected repository
  const {
    data: repoData,
    loading: repoLoading,
    refetch: refetchRepo,
  } = useQuery<{
    projectRepository: Repository | null;
  }>(PROJECT_REPOSITORY_QUERY, {
    variables: { projectId },
    fetchPolicy: 'cache-and-network',
  });

  // Query for available GitHub connections (with token validation)
  const { data: connectionsData, loading: connectionsLoading } = useQuery<{
    teamGithubConnections: GitHubConnection[];
  }>(TEAM_GITHUB_CONNECTIONS_QUERY, {
    variables: { teamId, validate: true },
    fetchPolicy: 'cache-and-network',
  });

  // Lazy query for searching repositories
  const [searchRepos, { data: searchData, loading: searchLoading }] = useLazyQuery<{
    searchGithubRepositories: GitHubRepo[];
  }>(SEARCH_GITHUB_REPOS_QUERY, {
    fetchPolicy: 'network-only',
  });

  // Debounced search
  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timer = setTimeout(() => {
        searchRepos({ variables: { teamId, query: searchQuery } });
      }, 300);
      return () => {
        return clearTimeout(timer);
      };
    }
    return undefined;
  }, [searchQuery, teamId, searchRepos]);

  // Connect mutation
  const [connectRepository, { data: connectData, error: connectError, loading: connectLoading }] = useMutation<{
    connectRepository: { success: boolean; message: string; repository: Repository | null };
  }>(CONNECT_REPOSITORY_MUTATION, {
    refetchQueries: [{ query: PROJECT_REPOSITORY_QUERY, variables: { projectId } }],
  });

  // Disconnect mutation
  const [disconnectRepository, { data: disconnectData, error: disconnectError, loading: disconnectLoading }] =
    useMutation<{
      disconnectRepository: { success: boolean; message: string };
    }>(DISCONNECT_REPOSITORY_MUTATION, {
      refetchQueries: [{ query: PROJECT_REPOSITORY_QUERY, variables: { projectId } }],
    });

  const connectedRepo = repoData?.projectRepository;
  const connections = connectionsData?.teamGithubConnections ?? [];
  const searchResults = searchData?.searchGithubRepositories ?? [];

  // Find if the connection used for this repo has invalid token
  const connectionForRepo = connectedRepo?.githubUsername
    ? connections.find(c => c.githubUsername === connectedRepo.githubUsername)
    : null;
  const isTokenValid = connectionForRepo?.isValid !== false;

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

  const isLoading = repoLoading || connectionsLoading;

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <div className='flex items-center gap-3'>
            <Skeleton className='h-5 w-5' />
            <Skeleton className='h-5 w-40' />
          </div>
          <Skeleton className='h-4 w-64' />
        </CardHeader>
        <CardContent>
          <Skeleton className='h-10 w-full' />
        </CardContent>
      </Card>
    );
  }

  // No GitHub connections available
  if (connections.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <div className='flex items-center gap-3'>
            <Github className='h-5 w-5' />
            <CardTitle>GitHub Repository</CardTitle>
          </div>
          <CardDescription>Connect a GitHub repository to enable automatic code localization.</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <Github className='h-4 w-4' />
            <AlertDescription>
              <div>
                No GitHub accounts connected to this team. Please connect a GitHub account in{' '}
                <Link to={PATHS.TEAM_EDIT.replace(':id', teamId)} className='text-blue-500'>
                  team settings
                </Link>{' '}
                first.
              </div>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className='flex items-center gap-3'>
          <Github className='h-5 w-5' />
          <CardTitle>GitHub Repository</CardTitle>
        </div>
        <CardDescription>Connect a GitHub repository to enable automatic code localization.</CardDescription>
      </CardHeader>
      <CardContent>
        {connectedRepo ? (
          <div className='space-y-4'>
            {/* Token expired warning */}
            {!isTokenValid ? (
              <Alert variant='destructive'>
                <AlertTriangle className='h-4 w-4' />
                <AlertDescription>
                  GitHub token expired. Please reconnect in team settings to continue using repository features.
                </AlertDescription>
              </Alert>
            ) : null}

            <div className='flex items-center justify-between rounded-lg border p-4'>
              <div className='flex items-center gap-3'>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-muted'>
                  <Github className='h-5 w-5' />
                </div>
                <div>
                  <div className='flex items-center gap-2'>
                    <span className='font-medium'>{connectedRepo.fullName}</span>
                    {isTokenValid ? (
                      <Check className='h-4 w-4 text-green-500' />
                    ) : (
                      <span title='Token expired'>
                        <AlertTriangle className='h-4 w-4 text-destructive' />
                      </span>
                    )}
                  </div>
                  <div className='flex items-center gap-2 text-sm text-muted-foreground'>
                    <GitBranch className='h-3 w-3' />
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
              <div className='flex items-center gap-2'>
                <Button variant='ghost' size='sm' asChild>
                  <a href={`https://github.com/${connectedRepo.fullName}`} target='_blank' rel='noopener noreferrer'>
                    <ExternalLink className='h-4 w-4' />
                  </a>
                </Button>
                {canManage ? (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant='ghost' size='sm' className='text-destructive hover:text-destructive'>
                        <Trash2 className='h-4 w-4' />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Disconnect Repository?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will remove the connection to {connectedRepo.fullName} from this project. Localization
                          sync will be disabled.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleDisconnect}
                          disabled={disconnectLoading}
                          className='bg-destructive text-destructive-foreground hover:bg-destructive/90'>
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
          <div className='space-y-4'>
            {connections.length > 1 ? (
              <div className='space-y-2'>
                <label className='text-sm font-medium'>GitHub Account</label>
                <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
                  <SelectTrigger>
                    <SelectValue placeholder='Select GitHub account' />
                  </SelectTrigger>
                  <SelectContent>
                    {connections.map(conn => (
                      <SelectItem key={conn.id} value={conn.id}>
                        @{conn.githubUsername}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ) : null}

            <div className='space-y-2'>
              <label className='text-sm font-medium'>Repository</label>
              <Popover open={repoComboboxOpen} onOpenChange={setRepoComboboxOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant='outline'
                    role='combobox'
                    aria-expanded={repoComboboxOpen}
                    className='w-full justify-between'
                    disabled={!selectedConnectionId}>
                    {selectedRepo ? (
                      <div className='flex items-center gap-2'>
                        {selectedRepo.private ? (
                          <Lock className='h-3 w-3 text-muted-foreground' />
                        ) : (
                          <Globe className='h-3 w-3 text-muted-foreground' />
                        )}
                        <span>{selectedRepo.fullName}</span>
                      </div>
                    ) : (
                      <span className='text-muted-foreground'>
                        {selectedConnectionId ? 'Search repositories...' : 'Select a GitHub account first'}
                      </span>
                    )}
                    <ChevronsUpDown className='ml-2 h-4 w-4 shrink-0 opacity-50' />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className='w-[400px] p-0' align='start'>
                  <Command shouldFilter={false}>
                    <CommandInput
                      placeholder='Search repository...'
                      value={searchQuery}
                      onValueChange={setSearchQuery}
                    />
                    <CommandList>
                      <CommandEmpty>
                        {searchLoading ? (
                          <div className='flex items-center justify-center gap-2 py-2'>
                            <Search className='h-4 w-4 animate-pulse' />
                            <span>Searching...</span>
                          </div>
                        ) : searchQuery.length >= 2 ? (
                          'No repository found.'
                        ) : (
                          'Type at least 2 characters to search...'
                        )}
                      </CommandEmpty>
                      <CommandGroup>
                        {searchResults.map(repo => (
                          <CommandItem
                            key={repo.id}
                            value={repo.fullName}
                            onSelect={() => {
                              if (repo.id === selectedRepoId) {
                                setSelectedRepoId('');
                                setSelectedRepo(null);
                              } else {
                                setSelectedRepoId(repo.id);
                                setSelectedRepo(repo);
                              }
                              setRepoComboboxOpen(false);
                            }}>
                            {repo.private ? (
                              <Lock className='h-3 w-3 text-muted-foreground' />
                            ) : (
                              <Globe className='h-3 w-3 text-muted-foreground' />
                            )}
                            <span>{repo.fullName}</span>
                            <Check
                              className={cn(
                                'ml-auto h-4 w-4',
                                selectedRepoId === repo.id ? 'opacity-100' : 'opacity-0',
                              )}
                            />
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>

            <Button
              onClick={handleConnect}
              disabled={!selectedRepoId || !selectedConnectionId || connectLoading}
              className='w-full'>
              <Github className='mr-2 h-4 w-4' />
              Connect Repository
            </Button>
          </div>
        ) : (
          <p className='text-sm text-muted-foreground'>
            No repository connected. Ask a project admin to connect a repository.
          </p>
        )}
      </CardContent>
    </Card>
  );
};
