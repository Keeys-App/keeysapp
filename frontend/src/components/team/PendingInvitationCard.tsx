import { type FC, useEffect } from 'react';
import { useMutation } from '@apollo/client';
import { UserPlus, Check, X, Clock } from 'lucide-react';
import { toast } from 'sonner';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  ACCEPT_INVITE_MUTATION,
  DECLINE_INVITE_MUTATION,
  GET_TEAMS,
  MY_PENDING_INVITES_QUERY,
  type AcceptInviteResponse,
  type DeclineInviteResponse,
  type PendingInvite,
} from '@/graphql/teams';
import { useSaving, useSavingStore, useTeamStore } from '@/stores';
import { getUserFriendlyErrorMessage } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

interface PendingInvitationCardProps {
  invitation: PendingInvite;
}

export const PendingInvitationCard: FC<PendingInvitationCardProps> = ({
  invitation,
}) => {
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();
  const { setSelectedTeamId } = useTeamStore();

  const [acceptInvite, { data: acceptData, error: acceptError }] =
    useMutation<AcceptInviteResponse>(ACCEPT_INVITE_MUTATION, {
      refetchQueries: [
        { query: GET_TEAMS },
        { query: MY_PENDING_INVITES_QUERY },
      ],
    });

  const [declineInvite, { data: declineData, error: declineError }] =
    useMutation<DeclineInviteResponse>(DECLINE_INVITE_MUTATION, {
      refetchQueries: [{ query: MY_PENDING_INVITES_QUERY }],
    });

  useEffect(() => {
    if (acceptData?.acceptInvite) {
      toast('Invitation accepted!', {
        description: `You are now a member of ${invitation.teamName}`,
      });
      setSelectedTeamId(acceptData.acceptInvite.id);
    }
  }, [acceptData, invitation.teamName, setSelectedTeamId]);

  useEffect(() => {
    if (declineData?.declineInvite) {
      toast('Invitation declined');
    }
  }, [declineData]);

  useEffect(() => {
    if (acceptError) {
      toast(getUserFriendlyErrorMessage(acceptError));
    }
  }, [acceptError]);

  useEffect(() => {
    if (declineError) {
      toast(getUserFriendlyErrorMessage(declineError));
    }
  }, [declineError]);

  const handleAccept = async () => {
    await withSaving(async () => {
      await acceptInvite({ variables: { code: invitation.id } });
    }, 'Accepting invitation...');
  };

  const handleDecline = async () => {
    await withSaving(async () => {
      await declineInvite({ variables: { code: invitation.id } });
    }, 'Declining invitation...');
  };

  return (
    <Card className="border-dashed border-primary/30 bg-primary/5">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">{invitation.teamName}</CardTitle>
          </div>
          <Badge variant="outline" className="text-primary border-primary/50">
            <Clock className="mr-1 h-3 w-3" />
            Pending
          </Badge>
        </div>
        {invitation.teamDescription ? (
          <CardDescription>{invitation.teamDescription}</CardDescription>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
          <span>Invited by {invitation.inviterName}</span>
          <span>•</span>
          <span>Role: <Badge variant="secondary" className="capitalize ml-1">{invitation.role}</Badge></span>
          <span>•</span>
          <span>{formatDistanceToNow(new Date(invitation.createdAt), { addSuffix: true })}</span>
        </div>
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={handleAccept}
            disabled={isSaving}
          >
            <Check className="mr-1 h-4 w-4" />
            Accept
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleDecline}
            disabled={isSaving}
          >
            <X className="mr-1 h-4 w-4" />
            Decline
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

