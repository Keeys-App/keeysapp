import { type FC } from 'react';
import { useQuery } from '@apollo/client';
import { Mail } from 'lucide-react';
import { PendingInvitationCard } from './PendingInvitationCard';
import {
  MY_PENDING_INVITES_QUERY,
  type MyPendingInvitesResponse,
} from '@/graphql/teams';

export const PendingInvitationsList: FC = () => {
  const { data, loading } = useQuery<MyPendingInvitesResponse>(
    MY_PENDING_INVITES_QUERY,
    {
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
    }
  );

  const invitations = data?.myPendingInvites || [];

  // Don't render anything while loading or if no invitations
  if (loading && !data) {
    return null;
  }

  if (invitations.length === 0) {
    return null;
  }

  return (
    <div className="mb-8">
      <div className="mb-4 flex items-center gap-2">
        <Mail className="h-5 w-5 text-primary" />
        <h2 className="text-xl font-semibold">Pending Invitations</h2>
        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-sm font-medium text-primary">
          {invitations.length}
        </span>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {invitations.map((invitation) => (
          <PendingInvitationCard key={invitation.id} invitation={invitation} />
        ))}
      </div>
    </div>
  );
};

