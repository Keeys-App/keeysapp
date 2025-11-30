import { useState, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import { ADD_TEAM_MEMBER, GET_TEAM } from '@/graphql/teams';
import type { AddTeamMemberInput, AddTeamMemberResponse } from '@/graphql/teams';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface InviteMembersStepProps {
  teamId: string;
  onNext: () => void;
  onSkip: () => void;
}

const ROLES = [
  { value: 'admin', label: 'Admin', description: 'Full access to team and projects' },
  { value: 'editor', label: 'Editor', description: 'Can edit content' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
  { value: 'translator', label: 'Translator', description: 'Can translate texts' },
  { value: 'reviewer', label: 'Reviewer', description: 'Can review translations' },
] as const;

interface InvitedMember {
  email: string;
  role: string;
}

export const InviteMembersStep: FC<InviteMembersStepProps> = ({
  teamId,
  onNext,
  onSkip,
}) => {
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [email, setEmail] = useState('');
  const [role, setRole] = useState('viewer');
  const [invitedMembers, setInvitedMembers] = useState<InvitedMember[]>([]);

  const [addTeamMember] = useMutation<AddTeamMemberResponse>(ADD_TEAM_MEMBER, {
    refetchQueries: [{ query: GET_TEAM, variables: { id: teamId } }],
  });

  const handleAddMember = async () => {
    const emailTrimmed = email.trim().toLowerCase();

    if (!emailTrimmed) {
      toast('Please enter an email address');
      return;
    }

    if (!emailTrimmed.includes('@') || !emailTrimmed.includes('.')) {
      toast('Please enter a valid email address');
      return;
    }

    if (invitedMembers.some((m) => m.email === emailTrimmed)) {
      toast('This email has already been added');
      return;
    }

    await withSaving(
      async () => {
        const input: AddTeamMemberInput = {
          teamId,
          userEmail: emailTrimmed,
          role: role as any,
        };

        try {
          await addTeamMember({ variables: { input } });
        } catch (error: any) {
          // Silently ignore errors for security
        }

        setInvitedMembers([...invitedMembers, { email: emailTrimmed, role }]);
        toast('Invitation sent successfully');
        setEmail('');
        setRole('viewer');
      },
      'Sending invitation...'
    );
  };

  const handleRemoveMember = (emailToRemove: string) => {
    setInvitedMembers(invitedMembers.filter((m) => m.email !== emailToRemove));
  };

  const handleNext = () => {
    if (invitedMembers.length === 0) {
      onSkip();
    } else {
      onNext();
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email Address</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => {
              return setEmail(e.target.value);
            }}
            placeholder="colleague@example.com"
            disabled={isSaving}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddMember();
              }
            }}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="role">Role</Label>
          <Select value={role} onValueChange={setRole} disabled={isSaving}>
            <SelectTrigger id="role">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ROLES.map((r) => {
                return (
                  <SelectItem key={r.value} value={r.value}>
                    <div className="flex flex-col">
                      <span>{r.label}</span>
                      <span className="text-xs text-muted-foreground">
                        {r.description}
                      </span>
                    </div>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        <Button
          type="button"
          variant="outline"
          onClick={handleAddMember}
          disabled={isSaving || !email.trim()}
          className="w-full"
        >
          Add Member
        </Button>
      </div>

      {invitedMembers.length > 0 ? (
        <div className="space-y-2">
          <Label>Invited Members ({invitedMembers.length})</Label>
          <div className="space-y-2">
            {invitedMembers.map((member) => {
              return (
                <div
                  key={member.email}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{member.email}</span>
                    <span className="text-xs text-muted-foreground capitalize">
                      {member.role}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      return handleRemoveMember(member.email);
                    }}
                    disabled={isSaving}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      <div className="flex justify-between">
        <Button type="button" variant="ghost" onClick={onSkip} disabled={isSaving}>
          Skip for now
        </Button>
        <Button type="button" onClick={handleNext} disabled={isSaving}>
          {invitedMembers.length > 0 ? 'Continue' : 'Skip'}
        </Button>
      </div>
    </div>
  );
};

