import { useEffect, useState, useRef, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useBreadcrumbs } from '@/contexts/BreadcrumbContext';
import { useAuth } from '@/contexts/AuthContext';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import { UPDATE_PROFILE_MUTATION, CHANGE_PASSWORD_MUTATION } from '@/graphql/auth';

interface UpdateProfileResponse {
  updateProfile: {
    success: boolean;
    message: string;
    user: {
      id: string;
      email: string;
      username: string;
      isActive: boolean;
      isSuperuser: boolean;
      onboardingCompleted: boolean;
    } | null;
  };
}

interface ChangePasswordResponse {
  changePassword: {
    success: boolean;
    message: string;
  };
}

export const ProfilePage: FC = () => {
  const { setBreadcrumbs } = useBreadcrumbs();
  const { user, login, token } = useAuth();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [username, setUsername] = useState(user?.username ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const processedProfileDataRef = useRef<string | null>(null);
  const processedPasswordDataRef = useRef<string | null>(null);

  const [updateProfile, { data: profileData, error: profileError }] =
    useMutation<UpdateProfileResponse>(UPDATE_PROFILE_MUTATION);
  const [changePassword, { data: passwordData, error: passwordError }] =
    useMutation<ChangePasswordResponse>(CHANGE_PASSWORD_MUTATION);

  useEffect(() => {
    setBreadcrumbs([{ label: 'Profile' }]);
  }, [setBreadcrumbs]);

  useEffect(() => {
    if (profileData?.updateProfile) {
      const dataKey = JSON.stringify(profileData);
      if (processedProfileDataRef.current === dataKey) {
        return;
      }
      processedProfileDataRef.current = dataKey;

      const result = profileData.updateProfile;
      if (result.success && result.user && token) {
        toast(result.message);
        login(token, result.user);
      } else if (!result.success) {
        toast(result.message);
      }
    }
  }, [profileData, login, token]);

  useEffect(() => {
    if (profileError) {
      toast('Failed to update profile. Please try again.');
    }
  }, [profileError]);

  useEffect(() => {
    if (passwordData?.changePassword) {
      const dataKey = JSON.stringify(passwordData);
      if (processedPasswordDataRef.current === dataKey) {
        return;
      }
      processedPasswordDataRef.current = dataKey;

      const result = passwordData.changePassword;
      toast(result.message);
      if (result.success) {
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      }
    }
  }, [passwordData]);

  useEffect(() => {
    if (passwordError) {
      toast('Failed to change password. Please try again.');
    }
  }, [passwordError]);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim()) {
      toast('Username is required');
      return;
    }

    if (!email.trim()) {
      toast('Email is required');
      return;
    }

    await withSaving(
      async () => {
        await updateProfile({
          variables: {
            input: {
              username: username.trim(),
              email: email.trim(),
            },
          },
        });
      },
      'Updating profile...'
    );
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!currentPassword) {
      toast('Current password is required');
      return;
    }

    if (!newPassword) {
      toast('New password is required');
      return;
    }

    if (newPassword.length < 8) {
      toast('Password must be at least 8 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      toast('Passwords do not match');
      return;
    }

    await withSaving(
      async () => {
        await changePassword({
          variables: {
            input: {
              currentPassword,
              newPassword,
            },
          },
        });
      },
      'Changing password...'
    );
  };

  return (
    <div className="flex h-full items-start justify-center p-6">
      <div className="w-full max-w-lg">
        <Tabs defaultValue="account">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="account">Account</TabsTrigger>
            <TabsTrigger value="password">Password</TabsTrigger>
          </TabsList>

          <TabsContent value="account">
            <Card>
              <form onSubmit={handleProfileSubmit} className="flex flex-col gap-6">
                <CardHeader>
                  <CardTitle>Account</CardTitle>
                  <CardDescription>
                    Make changes to your account here. Click save when you're
                    done.
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-6">
                  <div className="grid gap-3">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      autoComplete="username"
                      value={username}
                      onChange={(e) => {
                        return setUsername(e.target.value);
                      }}
                      placeholder="Your username"
                      required
                      disabled={isSaving}
                    />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => {
                        return setEmail(e.target.value);
                      }}
                      placeholder="your@email.com"
                      required
                      disabled={isSaving}
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" disabled={isSaving}>
                    Save changes
                  </Button>
                </CardFooter>
              </form>
            </Card>
          </TabsContent>

          <TabsContent value="password">
            <Card>
              <form onSubmit={handlePasswordSubmit} className="flex flex-col gap-6">
                <CardHeader>
                  <CardTitle>Password</CardTitle>
                  <CardDescription>
                    Change your password here to keep your account secure.
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-6">
                  {/* Hidden username field for password managers */}
                  <input
                    type="text"
                    name="username"
                    autoComplete="username"
                    value={username}
                    readOnly
                    className="sr-only"
                    tabIndex={-1}
                    aria-hidden="true"
                  />
                  <div className="grid gap-3">
                    <Label htmlFor="currentPassword">Current password</Label>
                    <Input
                      id="currentPassword"
                      type="password"
                      autoComplete="current-password"
                      value={currentPassword}
                      onChange={(e) => {
                        return setCurrentPassword(e.target.value);
                      }}
                      placeholder="Enter current password"
                      required
                      disabled={isSaving}
                    />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="newPassword">New password</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      autoComplete="new-password"
                      value={newPassword}
                      onChange={(e) => {
                        return setNewPassword(e.target.value);
                      }}
                      placeholder="Enter new password"
                      required
                      disabled={isSaving}
                    />
                    <p className="text-xs text-muted-foreground">
                      Must be at least 8 characters
                    </p>
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="confirmPassword">Confirm new password</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      autoComplete="new-password"
                      value={confirmPassword}
                      onChange={(e) => {
                        return setConfirmPassword(e.target.value);
                      }}
                      placeholder="Confirm new password"
                      required
                      disabled={isSaving}
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" disabled={isSaving}>
                    Save password
                  </Button>
                </CardFooter>
              </form>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
