import type { FC } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useQuery, useMutation } from '@apollo/client';
import {
  INVITE_INFO_QUERY,
  ACCEPT_INVITE_MUTATION,
  DECLINE_INVITE_MUTATION,
  type InviteInfoResponse,
  type AcceptInviteResponse,
  type DeclineInviteResponse,
} from '@/graphql/teams';
import { useAuth } from '@/contexts';
import { useOnboardingStore, useSaving, useSavingStore, useTeamStore } from '@/stores';
import { PATHS } from '@/constants/paths';
import { getUserFriendlyErrorMessage } from '@/lib/utils';
import { toast } from 'sonner';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Users, UserPlus, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';

export const InvitePage: FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, isLoading: authLoading } = useAuth();
  const { setReturnUrl } = useOnboardingStore();
  const { setSelectedTeamId } = useTeamStore();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Fetch invite info
  const { data, loading, error } = useQuery<InviteInfoResponse>(INVITE_INFO_QUERY, {
    variables: { code },
    skip: !code,
  });

  const [acceptInvite] = useMutation<AcceptInviteResponse>(ACCEPT_INVITE_MUTATION);
  const [declineInvite] = useMutation<DeclineInviteResponse>(DECLINE_INVITE_MUTATION);

  const inviteInfo = data?.inviteInfo;

  // Check if current user email matches invite email
  const emailMatches = user && inviteInfo && user.email.toLowerCase() === inviteInfo.invitedEmail.toLowerCase();

  const handleGoToAuth = (mode: 'login' | 'register') => {
    // Save current URL to return after auth
    setReturnUrl(location.pathname);
    navigate(PATHS.AUTH, { state: { mode } });
  };

  const handleAccept = async () => {
    if (!code) {
      return;
    }

    try {
      await withSaving(async () => {
        const { data: result } = await acceptInvite({
          variables: { code },
        });

        if (result?.acceptInvite) {
          toast('Invitation accepted!', {
            description: `You are now a member of ${inviteInfo?.teamName}`,
          });
          // Set the team as selected and navigate to teams list
          setSelectedTeamId(result.acceptInvite.id);
          navigate(PATHS.TEAMS);
        } else {
          toast('Failed to accept invitation');
        }
      }, 'Accepting invitation...');
    } catch (err: unknown) {
      toast(getUserFriendlyErrorMessage(err as Error));
    }
  };

  const handleDecline = async () => {
    if (!code) {
      return;
    }

    try {
      await withSaving(async () => {
        const { data: result } = await declineInvite({
          variables: { code },
        });

        if (result?.declineInvite) {
          toast('Invitation declined');
          navigate(PATHS.DASHBOARD);
        } else {
          toast('Failed to decline invitation');
        }
      }, 'Declining invitation...');
    } catch (err: unknown) {
      toast(getUserFriendlyErrorMessage(err as Error));
    }
  };

  // Show loading state
  if (loading || authLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Spinner className="h-8 w-8" />
        </CardContent>
      </Card>
    );
  }

  // Show error or not found
  if (error || !inviteInfo) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Invitation Not Found
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This invitation link is invalid or has expired.
          </p>
        </CardContent>
        <CardFooter>
          <Button variant="outline" onClick={() => navigate(PATHS.AUTH)}>
            Go to Login
          </Button>
        </CardFooter>
      </Card>
    );
  }

  // Check if invite is no longer pending
  if (inviteInfo.status !== 'PENDING') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {inviteInfo.status === 'ACCEPTED' ? (
              <CheckCircle2 className="h-5 w-5 text-green-500" />
            ) : (
              <XCircle className="h-5 w-5 text-muted-foreground" />
            )}
            Invitation {inviteInfo.status === 'ACCEPTED' ? 'Accepted' : 'Declined'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This invitation has already been {inviteInfo.status.toLowerCase()}.
          </p>
        </CardContent>
        <CardFooter>
          <Button variant="outline" onClick={() => navigate(isAuthenticated ? PATHS.DASHBOARD : PATHS.AUTH)}>
            {isAuthenticated ? 'Go to Dashboard' : 'Go to Login'}
          </Button>
        </CardFooter>
      </Card>
    );
  }

  // Main invite card
  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
          <UserPlus className="h-6 w-6 text-primary" />
        </div>
        <CardTitle>Team Invitation</CardTitle>
        <CardDescription>
          You&apos;ve been invited to join a team
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Team Info */}
        <div className="rounded-lg border p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-muted-foreground" />
            <span className="font-semibold text-lg">{inviteInfo.teamName}</span>
          </div>
          {inviteInfo.teamDescription ? (
            <p className="text-sm text-muted-foreground">{inviteInfo.teamDescription}</p>
          ) : null}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Invited by</span>
            <span>{inviteInfo.inviterName}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Your role</span>
            <Badge variant="secondary" className="capitalize">
              {inviteInfo.role}
            </Badge>
          </div>
        </div>

        {/* Auth state dependent content */}
        {!isAuthenticated ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Sign in required</AlertTitle>
            <AlertDescription>
              Please sign in or create an account to accept this invitation.
              The invitation is for <strong>{inviteInfo.invitedEmail}</strong>.
            </AlertDescription>
          </Alert>
        ) : !emailMatches ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Email mismatch</AlertTitle>
            <AlertDescription>
              This invitation is for <strong>{inviteInfo.invitedEmail}</strong>, 
              but you are signed in as <strong>{user?.email}</strong>.
              Please sign in with the correct account.
            </AlertDescription>
          </Alert>
        ) : null}
      </CardContent>

      <CardFooter className="flex flex-col gap-3">
        {!isAuthenticated ? (
          <>
            <Button className="w-full" onClick={() => handleGoToAuth('login')}>
              Sign In
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => handleGoToAuth('register')}
            >
              Create Account
            </Button>
          </>
        ) : emailMatches ? (
          <>
            <Button
              className="w-full"
              onClick={handleAccept}
              disabled={isSaving}
            >
              Accept Invitation
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={handleDecline}
              disabled={isSaving}
            >
              Decline
            </Button>
          </>
        ) : (
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {
              // Clear auth and redirect to login
              localStorage.removeItem('authToken');
              localStorage.removeItem('authUser');
              setReturnUrl(location.pathname);
              navigate(PATHS.AUTH);
              window.location.reload();
            }}
          >
            Sign in with different account
          </Button>
        )}
      </CardFooter>
    </Card>
  );
};

