import { useState, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { MoreHorizontal, Trash2, Shield, Mail, Send } from 'lucide-react';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useSaving, useSavingStore } from '@/stores';
import { useAuth } from '@/contexts/AuthContext';
import {
  REMOVE_TEAM_MEMBER,
  UPDATE_TEAM_MEMBER_ROLE,
  RESEND_INVITE_MUTATION,
  GET_TEAM,
} from '@/graphql/teams';
import type { Team, TeamMember, RemoveTeamMemberInput, UpdateTeamMemberRoleInput } from '@/graphql/teams';

interface TeamMembersListProps {
  team: Team;
}

const ROLE_LABELS: Record<string, { label: string; variant: any }> = {
  admin: { label: 'Admin', variant: 'default' },
  editor: { label: 'Editor', variant: 'secondary' },
  viewer: { label: 'Viewer', variant: 'outline' },
  translator: { label: 'Translator', variant: 'secondary' },
  reviewer: { label: 'Reviewer', variant: 'secondary' },
};

const ROLES = [
  { value: 'admin', label: 'Admin' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Viewer' },
  { value: 'translator', label: 'Translator' },
  { value: 'reviewer', label: 'Reviewer' },
] as const;

export const TeamMembersList: FC<TeamMembersListProps> = ({ team }) => {
  const [memberToRemove, setMemberToRemove] = useState<TeamMember | null>(null);
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();
  const { user: currentUser } = useAuth();

  const [removeMember] = useMutation(REMOVE_TEAM_MEMBER, {
    refetchQueries: [{ query: GET_TEAM, variables: { id: team.id } }],
  });

  const [updateMemberRole] = useMutation(UPDATE_TEAM_MEMBER_ROLE, {
    refetchQueries: [{ query: GET_TEAM, variables: { id: team.id } }],
  });

  const [resendInvite] = useMutation(RESEND_INVITE_MUTATION);

  const handleResendInvite = async (invitationId: string) => {
    await withSaving(
      async () => {
        const { data } = await resendInvite({
          variables: { invitationId },
        });

        if (data?.resendInvite) {
          toast('Invitation resent successfully');
        } else {
          toast('Failed to resend invitation');
        }
      },
      'Resending invitation...'
    );
  };

  const handleRemoveMember = async () => {
    if (!memberToRemove) {
      return;
    }

    await withSaving(
      async () => {
        const input: RemoveTeamMemberInput = {
          teamId: team.id,
          userId: memberToRemove.user.id,
        };

        await removeMember({ variables: { input } });
        toast('Team member removed');
        setMemberToRemove(null);
      },
      'Removing member...'
    );
  };

  const handleChangeRole = async (member: TeamMember, newRole: string) => {
    await withSaving(
      async () => {
        const input: UpdateTeamMemberRoleInput = {
          teamId: team.id,
          userId: member.user.id,
          role: newRole as any,
        };

        await updateMemberRole({ variables: { input } });
        toast('Role updated');
      },
      'Updating role...'
    );
  };

  const allMembers = [
    // Owner as first member
    {
      type: 'owner' as const,
      user: team.owner,
      role: 'owner',
      createdAt: team.createdAt,
    },
    // Regular members
    ...team.members.map((m) => {
      return { ...m, type: 'member' as const };
    }),
    // Pending invitations
    ...team.invitations.map((inv) => {
      return {
        type: 'invitation' as const,
        invitation: inv,
        role: inv.role,
        createdAt: inv.createdAt,
      };
    }),
  ];

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>User</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {allMembers.map((item, index) => {
            if (item.type === 'owner') {
              const isCurrentUser = currentUser?.id === item.user.id;
              
              return (
                <TableRow key="owner">
                  <TableCell>
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{item.user.username}</span>
                        {isCurrentUser ? (
                          <Badge variant="outline" className="text-xs">You</Badge>
                        ) : null}
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {item.user.email}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="default">
                      <Shield className="mr-1 h-3 w-3" />
                      Owner
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="default" className="bg-green-500/10 text-green-700 border-green-500/20">
                      Active
                    </Badge>
                  </TableCell>
                  <TableCell></TableCell>
                </TableRow>
              );
            }

            if (item.type === 'invitation') {
              const inv = item.invitation!;
              const roleInfo = ROLE_LABELS[inv.role] || { label: inv.role, variant: 'outline' };

              return (
                <TableRow key={`invitation-${inv.id}`} className="bg-muted/30">
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium text-muted-foreground">
                        {inv.invitedEmail}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={roleInfo.variant}>{roleInfo.label}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-700 border-yellow-500/20">
                      <Mail className="mr-1 h-3 w-3" />
                      Pending Invite
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {team.canManage ? (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" disabled={isSaving}>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => handleResendInvite(inv.id)}
                          >
                            <Send className="mr-2 h-4 w-4" />
                            Resend Invite
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => {
                              // TODO: Cancel invitation
                              toast('Canceling invitations will be implemented soon');
                            }}
                            className="text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Cancel Invite
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    ) : null}
                  </TableCell>
                </TableRow>
              );
            }

            // Regular member
            const member = item as TeamMember & { type: 'member' };
            const roleInfo = ROLE_LABELS[member.role] || { label: member.role, variant: 'outline' };
            const isCurrentUser = currentUser?.id === member.user.id;

            return (
              <TableRow key={member.user.id}>
                <TableCell>
                  <div className="flex flex-col">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{member.user.username}</span>
                      {isCurrentUser ? (
                        <Badge variant="outline" className="text-xs">You</Badge>
                      ) : null}
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {member.user.email}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={roleInfo.variant}>{roleInfo.label}</Badge>
                </TableCell>
                <TableCell>
                  <Badge variant="default" className="bg-green-500/10 text-green-700 border-green-500/20">
                    Active
                  </Badge>
                </TableCell>
                <TableCell>
                  {team.canManage ? (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" disabled={isSaving}>
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuSub>
                          <DropdownMenuSubTrigger>
                            Change Role
                          </DropdownMenuSubTrigger>
                          <DropdownMenuSubContent>
                            {ROLES.map((role) => {
                              return (
                                <DropdownMenuItem
                                  key={role.value}
                                  onClick={() => {
                                    return handleChangeRole(member, role.value);
                                  }}
                                  disabled={member.role === role.value}
                                >
                                  {role.label}
                                </DropdownMenuItem>
                              );
                            })}
                          </DropdownMenuSubContent>
                        </DropdownMenuSub>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => {
                            return setMemberToRemove(member);
                          }}
                          className="text-destructive"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Remove
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  ) : null}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <AlertDialog
        open={!!memberToRemove}
        onOpenChange={(open) => {
          if (!open) {
            setMemberToRemove(null);
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Team Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove{' '}
              <strong>{memberToRemove?.user.username}</strong> from the team?
              They will lose access to all team projects.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isSaving}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRemoveMember} disabled={isSaving}>
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

