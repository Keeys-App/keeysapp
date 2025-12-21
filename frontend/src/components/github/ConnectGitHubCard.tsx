import { type FC, useEffect } from 'react';
import { useMutation, useQuery } from '@apollo/client';
import { Github, Trash2, ExternalLink, Check, User, AlertTriangle, Settings, RefreshCw } from 'lucide-react';
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  TEAM_GITHUB_CONNECTIONS_QUERY,
  GET_GITHUB_AUTH_URL_MUTATION,
  DISCONNECT_GITHUB_MUTATION,
  GITHUB_APP_INFO_QUERY,
  type GitHubConnection,
  type GitHubAppInfo,
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
      variables: { teamId, validate: true },
      fetchPolicy: 'cache-and-network',
    }
  );

  const { data: appInfoData, loading: appInfoLoading } = useQuery<{ githubAppInfo: GitHubAppInfo }>(
    GITHUB_APP_INFO_QUERY,
    {
      variables: { teamId },
      fetchPolicy: 'cache-and-network',
      skip: !data?.teamGithubConnections?.length,
    }
  );

  const [getAuthUrl, { loading: authLoading }] = useMutation<{
    getGithubAuthUrl: { authorizationUrl: string; state: string };
  }>(GET_GITHUB_AUTH_URL_MUTATION);

  const [disconnectGithub, { data: disconnectData, error: disconnectError, loading: disconnectLoading }] = useMutation<{
    disconnectGithub: { success: boolean; message: string };
  }>(DISCONNECT_GITHUB_MUTATION);

  const connections = data?.teamGithubConnections ?? [];
  const appInfo = appInfoData?.githubAppInfo;

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

  const hasValidConnection = connections.some(c => c.isValid);

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
                      {connection.isValid === false ? (
                        <span title="Token expired or revoked">
                          <AlertTriangle className="h-4 w-4 text-destructive" />
                        </span>
                      ) : (
                        <Check className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      {connection.isValid === false ? (
                        <span className="text-destructive font-medium">Token expired - please reconnect</span>
                      ) : (
                        <span>Connected {formatDate(connection.connectedAt)}</span>
                      )}
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
            
            {/* Installation warning */}
            {!appInfoLoading && appInfo && !appInfo.hasInstallation && appInfo.installationUrl && hasValidConnection ? (
              <Alert variant="default" className="border-yellow-500/50 bg-yellow-500/10">
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                <AlertDescription className="flex flex-col gap-3">
                  <span>
                    GitHub App is not installed. Install it to access private repositories.
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    asChild
                    className="w-fit"
                  >
                    <a href={appInfo.installationUrl} target="_blank" rel="noopener noreferrer">
                      <Settings className="mr-2 h-4 w-4" />
                      Install GitHub App
                    </a>
                  </Button>
                </AlertDescription>
              </Alert>
            ) : null}

            {/* Show installation info if exists */}
            {appInfo?.hasInstallation ? (
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  App installed on: {appInfo.installations.map((i) => i.accountLogin).join(', ')}
                  {appInfo.installations[0]?.repositorySelection === 'selected' ? (
                    <span className="text-yellow-600"> (selected repos only)</span>
                  ) : null}
                </span>
                {canManage && appInfo.installations[0]?.htmlUrl ? (
                  <Button
                    variant="outline"
                    size="sm"
                    asChild
                  >
                    <a
                      href={appInfo.installations[0].htmlUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <RefreshCw className="mr-2 h-3 w-3" />
                      Change
                    </a>
                  </Button>
                ) : null}
              </div>
            ) : null}
            
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
                <div className="text-sm text-muted-foreground space-y-3">
                  <p className="font-medium">Two steps to connect:</p>
                  <ol className="list-decimal list-inside space-y-2">
                    <li>
                      <strong>Install GitHub App</strong> — choose which repositories to allow access
                    </li>
                    <li>
                      <strong>Authorize</strong> — grant permission to act on your behalf
                    </li>
                  </ol>
                </div>
                
                <div className="flex flex-col gap-2">
                  <Button
                    onClick={handleConnect}
                    disabled={authLoading}
                    className="w-full"
                  >
                    <Github className="mr-2 h-4 w-4" />
                    Connect GitHub
                  </Button>
                </div>
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
