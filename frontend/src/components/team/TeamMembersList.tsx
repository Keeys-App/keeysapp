import { FC, useState } from 'react';
import { useMutation } from '@apollo/client';
import { MoreHorizontal, Trash2, Shield } from 'lucide-react';
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
import {
  REMOVE_TEAM_MEMBER,
  UPDATE_TEAM_MEMBER_ROLE,
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

  const [removeMember] = useMutation(REMOVE_TEAM_MEMBER, {
    refetchQueries: [{ query: GET_TEAM, variables: { id: team.id } }],
  });

  const [updateMemberRole] = useMutation(UPDATE_TEAM_MEMBER_ROLE, {
    refetchQueries: [{ query: GET_TEAM, variables: { id: team.id } }],
  });

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
      user: team.owner,
      role: 'owner',
      createdAt: team.createdAt,
    },
    // Regular members
    ...team.members,
  ];

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>User</TableHead>
            <TableHead>Role</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {allMembers.map((member) => {
            const isOwner = member.role === 'owner';
            const roleInfo = ROLE_LABELS[member.role] || { label: member.role, variant: 'outline' };

            return (
              <TableRow key={member.user.id}>
                <TableCell>
                  <div className="flex flex-col">
                    <span className="font-medium">{member.user.username}</span>
                    <span className="text-sm text-muted-foreground">
                      {member.user.email}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={roleInfo.variant}>
                    {isOwner ? (
                      <>
                        <Shield className="mr-1 h-3 w-3" />
                        Owner
                      </>
                    ) : (
                      roleInfo.label
                    )}
                  </Badge>
                </TableCell>
                <TableCell>
                  {!isOwner && team.canManage ? (
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
                                    return handleChangeRole(member as TeamMember, role.value);
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
                            return setMemberToRemove(member as TeamMember);
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

