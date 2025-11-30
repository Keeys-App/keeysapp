import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { LOGIN_MUTATION } from '@/graphql/auth';
import { useAuth } from '@/contexts/AuthContext';
import { getUserFriendlyErrorMessage } from '@/lib/utils';
import { useSaving, useSavingStore } from '@/stores';
import { PATHS } from '@/constants/paths';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from '@/components/ui/field';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircleIcon } from 'lucide-react';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export const LoginForm: FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const { login } = useAuth();
  const [loginMutation] = useMutation(LOGIN_MUTATION);
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
      await withSaving(
        async () => {
          const { data } = await loginMutation({
            variables: {
              input: {
                email,
                password,
              },
            },
          });

          if (data?.login) {
            login(data.login.accessToken, {
              id: data.login.user.id,
              email: data.login.user.email,
              username: data.login.user.username,
              isActive: data.login.user.isActive,
              isSuperuser: data.login.user.isSuperuser,
              onboardingCompleted: data.login.user.onboardingCompleted || false,
            });

            if (onSuccess) {
              onSuccess();
            }
          }
        },
        "Signing in..."
      );
    } catch (err) {
      const errorMessage = getUserFriendlyErrorMessage(err as Error, 'Login failed. Please check your credentials and try again.');
      setError(errorMessage);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-xl">Welcome back</CardTitle>
        <CardDescription>
          Sign in to your account to continue
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            {error ? (
              <Alert variant="destructive">
                <AlertCircleIcon /> 
                <AlertTitle>Authentication error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}

            <Field>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                }}
                disabled={isSaving}
                required
                autoComplete="email"
              />
            </Field>

            <Field>
              <div className="flex items-center justify-between">
                <FieldLabel htmlFor="password">Password</FieldLabel>
                <Link 
                  to={PATHS.FORGOT_PASSWORD}
                  className="text-sm text-primary hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
                disabled={isSaving}
                required
                autoComplete="current-password"
                maxLength={72}
              />
            </Field>

            <Field>
              <Button type="submit" disabled={isSaving} className="w-full" variant="default">
                Sign In
              </Button>
              {onSwitchToRegister ? (
                <FieldDescription className="text-center">
                  Don&apos;t have an account?{' '}
                  <span
                    className="text-primary cursor-pointer hover:underline"
                    onClick={onSwitchToRegister}
                  >
                    Sign up
                  </span>
                </FieldDescription>
              ) : null}
            </Field>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
};
