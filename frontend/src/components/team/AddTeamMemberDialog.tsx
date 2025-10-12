import { FC, useState } from 'react';
import { useMutation } from '@apollo/client';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useSaving, useSavingStore } from '@/stores';
import { UserSearchInput } from './UserSearchInput';
import { ADD_TEAM_MEMBER, GET_TEAM } from '@/graphql/teams';
import type { AddTeamMemberInput, AddTeamMemberResponse } from '@/graphql/teams';

interface AddTeamMemberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  teamId: string;
  existingMemberEmails?: string[];
}

const ROLES = [
  { value: 'admin', label: 'Admin', description: 'Full access to team and projects' },
  { value: 'editor', label: 'Editor', description: 'Can edit content' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
  { value: 'translator', label: 'Translator', description: 'Can translate texts' },
  { value: 'reviewer', label: 'Reviewer', description: 'Can review translations' },
] as const;

export const AddTeamMemberDialog: FC<AddTeamMemberDialogProps> = ({
  open,
  onOpenChange,
  teamId,
  existingMemberEmails = [],
}) => {
  const [userEmail, setUserEmail] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('viewer');
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [addTeamMember] = useMutation<AddTeamMemberResponse>(ADD_TEAM_MEMBER, {
    refetchQueries: [{ query: GET_TEAM, variables: { id: teamId } }],
  });

  const handleSubmit = async () => {
    const email = userEmail.trim().toLowerCase();
    
    if (!email) {
      toast('Please enter an email address');
      return;
    }

    // Basic email validation
    if (!email.includes('@') || !email.includes('.')) {
      toast('Please enter a valid email address');
      return;
    }

    // Check if user is already a member
    if (existingMemberEmails.includes(email)) {
      toast('This user is already a member of the team');
      return;
    }

    await withSaving(
      async () => {
        const input: AddTeamMemberInput = {
          teamId,
          userEmail: email,
          role: selectedRole as any,
        };

        try {
          const result = await addTeamMember({ variables: { input } });

          if (result.data?.addTeamMember) {
            toast('Team member added successfully');
            onOpenChange(false);
            setUserEmail('');
            setSelectedRole('viewer');
          } else {
            toast('User not found or could not be added');
          }
        } catch (error: any) {
          if (error.message?.includes('not found')) {
            toast('User with this email not found');
          } else {
            toast('Failed to add team member');
          }
        }
      },
      'Adding team member...'
    );
  };

  const handleClose = () => {
    if (!isSaving) {
      setUserEmail('');
      setSelectedRole('viewer');
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Team Member</DialogTitle>
          <DialogDescription>
            Enter the email address of the user you want to add to your team.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <UserSearchInput
            value={userEmail}
            onChange={setUserEmail}
            disabled={isSaving}
          />

          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select value={selectedRole} onValueChange={setSelectedRole} disabled={isSaving}>
              <SelectTrigger id="role">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ROLES.map((role) => {
                  return (
                    <SelectItem key={role.value} value={role.value}>
                      <div className="flex flex-col">
                        <span>{role.label}</span>
                        <span className="text-xs text-muted-foreground">
                          {role.description}
                        </span>
                      </div>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isSaving}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSaving || !userEmail.trim()}>
            Add Member
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

