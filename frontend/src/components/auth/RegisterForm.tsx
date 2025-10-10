import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { useMutation } from '@apollo/client';
import { REGISTER_MUTATION } from '@/graphql/auth';
import { useAuth } from '@/contexts/AuthContext';
import { getUserFriendlyErrorMessage } from '@/lib/utils';
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

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export const RegisterForm: FC<RegisterFormProps> = ({
  onSuccess,
  onSwitchToLogin,
}) => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const { login } = useAuth();
  const [registerMutation, { loading }] = useMutation(REGISTER_MUTATION);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !username || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (password.length > 72) {
      setError('Password must be no more than 72 characters long');
      return;
    }

    try {
      const { data } = await registerMutation({
        variables: {
          input: {
            email,
            username,
            password,
          },
        },
      });

      if (data?.register) {
        login(data.register.accessToken, {
          id: data.register.user.id,
          email: data.register.user.email,
          username: data.register.user.username,
          isActive: data.register.user.isActive,
          isSuperuser: data.register.user.isSuperuser,
        });

        if (onSuccess) {
          onSuccess();
        }
      }
    } catch (err: any) {
      const errorMessage = getUserFriendlyErrorMessage(err, 'Registration failed. Please try again.');
      setError(errorMessage);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-xl">Create an account</CardTitle>
        <CardDescription>
          Enter your information below to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            {error ? (
              <Alert variant="destructive">
                <AlertCircleIcon /> 
                <AlertTitle>Registration error</AlertTitle>
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
                disabled={loading}
                required
                autoComplete="email"
              />
              <FieldDescription>
                We&apos;ll use this to contact you. We will not share your
                email with anyone else.
              </FieldDescription>
            </Field>

            <Field>
              <FieldLabel htmlFor="username">Username</FieldLabel>
              <Input
                id="username"
                type="text"
                placeholder="johndoe"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                }}
                disabled={loading}
                required
                autoComplete="username"
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="password">Password</FieldLabel>
              <Input
                id="password"
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
                disabled={loading}
                required
                autoComplete="new-password"
                maxLength={72}
              />
              <FieldDescription>
                Must be at least 8 characters long.
              </FieldDescription>
            </Field>

            <Field>
              <FieldLabel htmlFor="confirmPassword">
                Confirm Password
              </FieldLabel>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                }}
                disabled={loading}
                required
                autoComplete="new-password"
                maxLength={72}
              />
              <FieldDescription>Please confirm your password.</FieldDescription>
            </Field>

            <Field>
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
              {onSwitchToLogin ? (
                <FieldDescription className="text-center">
                  Already have an account?{' '}
                  <span
                    className="text-primary cursor-pointer hover:underline"
                    onClick={onSwitchToLogin}
                  >
                    Sign in
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
