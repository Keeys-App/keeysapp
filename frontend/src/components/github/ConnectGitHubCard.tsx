import { type FC, useEffect } from 'react';
import { useMutation, useQuery } from '@apollo/client';
import { Github, Trash2, ExternalLink, Check, User } from 'lucide-react';
import { toast } from 'sonner';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
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
import { Skeleton } from '@/components/ui/skeleton';
import {
  TEAM_GITHUB_CONNECTIONS_QUERY,
  GET_GITHUB_AUTH_URL_MUTATION,
  DISCONNECT_GITHUB_MUTATION,
  type GitHubConnection,
} from '@/graphql/github';

interface ConnectGitHubCardProps {
  teamId: string;
  canManage?: boolean;
  className?: string;
}

export const ConnectGitHubCard: FC<ConnectGitHubCardProps> = ({
  teamId,
  canManage = false,
  className,
}) => {
  const { data, loading, refetch } = useQuery<{ teamGithubConnections: GitHubConnection[] }>(
    TEAM_GITHUB_CONNECTIONS_QUERY,
    {
      variables: { teamId },
      fetchPolicy: 'cache-and-network',
    }
  );

  const [getAuthUrl, { loading: authLoading }] = useMutation<{
    getGithubAuthUrl: { authorizationUrl: string; state: string };
  }>(GET_GITHUB_AUTH_URL_MUTATION);

  const [disconnectGithub, { data: disconnectData, error: disconnectError, loading: disconnectLoading }] = useMutation<{
    disconnectGithub: { success: boolean; message: string };
  }>(DISCONNECT_GITHUB_MUTATION);

  const connections = data?.teamGithubConnections ?? [];

  useEffect(() => {
    if (disconnectData?.disconnectGithub) {
      const { success, message } = disconnectData.disconnectGithub;
      if (success) {
        toast('GitHub disconnected', { description: message });
        refetch();
      } else {
        toast('Failed to disconnect', { description: message });
      }
    }
  }, [disconnectData, refetch]);

  useEffect(() => {
    if (disconnectError) {
      toast('Error', { description: 'Failed to disconnect GitHub. Please try again.' });
    }
  }, [disconnectError]);

  const handleConnect = async () => {
    try {
      const result = await getAuthUrl({
        variables: { teamId },
      });
      if (result.data?.getGithubAuthUrl.authorizationUrl) {
        // Redirect to GitHub OAuth
        window.location.href = result.data.getGithubAuthUrl.authorizationUrl;
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to initiate GitHub connection';
      toast('Error', { description: message });
    }
  };

  const handleDisconnect = async (connectionId: string) => {
    await disconnectGithub({
      variables: { connectionId },
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
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
          <Skeleton className="h-10 w-32" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center gap-3">
          <Github className="h-5 w-5" />
          <CardTitle>GitHub Integration</CardTitle>
        </div>
        <CardDescription>
          Connect GitHub to enable automatic code localization for this team.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {connections.length > 0 ? (
          <div className="space-y-4">
            {connections.map((connection) => (
              <div
                key={connection.id}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    {connection.githubAvatarUrl ? (
                      <AvatarImage src={connection.githubAvatarUrl} alt={connection.githubUsername} />
                    ) : null}
                    <AvatarFallback>
                      <Github className="h-5 w-5" />
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">@{connection.githubUsername}</span>
                      <Check className="h-4 w-4 text-green-500" />
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>Connected {formatDate(connection.connectedAt)}</span>
                      {connection.connectedByUsername ? (
                        <>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {connection.connectedByUsername}
                          </span>
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
                      href={`https://github.com/${connection.githubUsername}`}
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
                          <AlertDialogTitle>Disconnect GitHub?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This will remove the connection to @{connection.githubUsername} from this team.
                            All team members will lose access to this GitHub account.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => handleDisconnect(connection.id)}
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
            ))}
            
            {canManage ? (
              <Button
                variant="outline"
                onClick={handleConnect}
                disabled={authLoading}
                className="w-full"
              >
                <Github className="mr-2 h-4 w-4" />
                Connect Another Account
              </Button>
            ) : null}
          </div>
        ) : (
          <div className="space-y-4">
            {canManage ? (
              <>
                <div className="text-sm text-muted-foreground">
                  <p className="mb-2">We will request access to:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Read repository contents</li>
                    <li>Create branches and pull requests</li>
                    <li>Read your email (for notifications)</li>
                  </ul>
                </div>
                
                <Button
                  onClick={handleConnect}
                  disabled={authLoading}
                  className="w-full"
                >
                  <Github className="mr-2 h-4 w-4" />
                  Connect GitHub
                </Button>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                No GitHub accounts connected. Ask a team admin to connect a GitHub account.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
