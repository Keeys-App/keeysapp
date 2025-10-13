import { type FC } from 'react';
import { Mail } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface UserSearchInputProps {
  value: string;
  onChange: (email: string) => void;
  disabled?: boolean;
}

export const UserSearchInput: FC<UserSearchInputProps> = ({
  value,
  onChange,
  disabled,
}) => {
  return (
    <div className="space-y-2">
      <Label htmlFor="user-email">User Email *</Label>
      <div className="relative">
        <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          id="user-email"
          type="email"
          placeholder="user@example.com"
          value={value}
          onChange={(e) => {
            return onChange(e.target.value);
          }}
          disabled={disabled}
          className="pl-9"
        />
      </div>
      <p className="text-xs text-muted-foreground">
        Enter the email address of the user you want to add to the team.
      </p>
    </div>
  );
};

