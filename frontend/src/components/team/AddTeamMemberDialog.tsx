import { useState, type FC } from 'react';
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
  existingMemberEmails?: string[]; // Not used anymore for security, kept for compatibility
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

    await withSaving(
      async () => {
        const input: AddTeamMemberInput = {
          teamId,
          userEmail: email,
          role: selectedRole as any,
        };

        try {
          await addTeamMember({ variables: { input } });
        } catch (error: any) {
          // Silently ignore errors for security
        }
        
        // SECURITY: Always show success message, even if:
        // - User doesn't exist
        // - User is already a member
        // - Any other error occurred
        // This prevents enumeration attacks
        toast('Invitation sent successfully');
        onOpenChange(false);
        setUserEmail('');
        setSelectedRole('viewer');
      },
      'Sending invitation...'
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
            Enter the email address of the user you want to invite to your team.
            If the user exists, they will be added immediately.
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

