import { type FC, useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Github, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PATHS } from '@/constants/paths';

type CallbackStatus = 'processing' | 'success' | 'error';

interface CallbackResult {
  status: CallbackStatus;
  message: string;
  username?: string;
  teamId?: string;
}

export const GitHubCallbackPage: FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [result, setResult] = useState<CallbackResult>({
    status: 'processing',
    message: 'Processing GitHub connection...',
  });

  useEffect(() => {
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const username = searchParams.get('username');
    const teamId = searchParams.get('team');

    if (success === 'true') {
      setResult({
        status: 'success',
        message: `Successfully connected to GitHub${username ? ` as @${username}` : ''}!`,
        username: username ?? undefined,
        teamId: teamId ?? undefined,
      });
    } else if (error) {
      const errorMessages: Record<string, string> = {
        invalid_state: 'Invalid request. Please try again.',
        user_not_found: 'User session expired. Please sign in again.',
        token_exchange_failed: 'Failed to complete GitHub authorization. Please try again.',
        user_info_failed: 'Failed to fetch GitHub user information. Please try again.',
        connection_failed: 'Failed to save GitHub connection. Please try again.',
      };
      
      setResult({
        status: 'error',
        message: errorMessages[error] ?? 'An unexpected error occurred. Please try again.',
      });
    } else {
      // No success or error param, redirect to dashboard
      navigate(PATHS.DASHBOARD, { replace: true });
    }
  }, [searchParams, navigate]);

  const handleContinue = () => {
    if (result.teamId) {
      navigate(PATHS.TEAM_EDIT.replace(':id', result.teamId), { replace: true });
    } else {
      navigate(PATHS.DASHBOARD, { replace: true });
    }
  };

  const handleRetry = () => {
    navigate(PATHS.DASHBOARD, { replace: true });
    // Note: User can click Connect GitHub again from the dashboard
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
            {result.status === 'processing' ? (
              <Loader2 className="h-6 w-6 animate-spin" />
            ) : result.status === 'success' ? (
              <CheckCircle className="h-6 w-6 text-green-500" />
            ) : (
              <XCircle className="h-6 w-6 text-destructive" />
            )}
          </div>
          <CardTitle className="flex items-center justify-center gap-2">
            <Github className="h-5 w-5" />
            GitHub Connection
          </CardTitle>
          <CardDescription>
            {result.status === 'processing'
              ? 'Please wait...'
              : result.status === 'success'
                ? 'Connection established'
                : 'Connection failed'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-center text-sm text-muted-foreground">
            {result.message}
          </p>
          
          {result.status === 'success' ? (
            <Button onClick={handleContinue} className="w-full">
              {result.teamId ? 'Continue to Team Settings' : 'Continue to Dashboard'}
            </Button>
          ) : result.status === 'error' ? (
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleContinue} className="flex-1">
                Go to Dashboard
              </Button>
              <Button onClick={handleRetry} className="flex-1">
                Try Again
              </Button>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
};

