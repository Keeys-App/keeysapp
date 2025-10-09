import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { useMutation } from '@apollo/client';
import { REGISTER_MUTATION } from '@/graphql/auth';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Field, FieldLabel } from '@/components/ui/field';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export const RegisterForm: FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
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

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
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
      // Handle GraphQL errors and network errors
      const errorMessage = err?.graphQLErrors?.[0]?.message || err?.message || 'An error occurred during registration';
      setError(errorMessage);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-center text-2xl">Create Account</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}

          <Field>
            <FieldLabel>Email</FieldLabel>
            <Input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              disabled={loading}
              required
              autoComplete="email"
            />
          </Field>

          <Field>
            <FieldLabel>Username</FieldLabel>
            <Input
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
            <FieldLabel>Password</FieldLabel>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
              }}
              disabled={loading}
              required
              autoComplete="new-password"
              maxLength={72}
            />
          </Field>

          <Field>
            <FieldLabel>Confirm Password</FieldLabel>
            <Input
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
              }}
              disabled={loading}
              required
              autoComplete="new-password"
              maxLength={72}
            />
          </Field>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating account...' : 'Create Account'}
          </Button>

          {onSwitchToLogin ? (
            <p className="text-center text-sm text-muted-foreground">
              Already have an account?{' '}
              <span className="text-primary cursor-pointer hover:underline" onClick={onSwitchToLogin}>
                Sign in
              </span>
            </p>
          ) : null}
        </form>
      </CardContent>
    </Card>
  );
};
