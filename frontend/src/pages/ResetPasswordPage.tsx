import { useState, useEffect } from 'react';
import type { FC, FormEvent } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { RESET_PASSWORD_MUTATION } from '@/graphql/auth';
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
import { AlertCircleIcon, CheckCircle2Icon, ArrowLeftIcon, XCircleIcon } from 'lucide-react';

interface ResetPasswordResponse {
  resetPassword: {
    success: boolean;
    message: string;
  };
}

export const ResetPasswordPage: FC = () => {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const [resetPassword, { data, error: mutationError }] = useMutation<ResetPasswordResponse>(
    RESET_PASSWORD_MUTATION
  );
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  useEffect(() => {
    if (data?.resetPassword) {
      if (data.resetPassword.success) {
        setSuccess(true);
      } else {
        setError(data.resetPassword.message);
      }
    }
  }, [data]);

  useEffect(() => {
    if (mutationError) {
      setError('Unable to reset password. Please try again.');
    }
  }, [mutationError]);

  // Redirect if no token provided
  useEffect(() => {
    if (!token) {
      navigate(PATHS.AUTH, { replace: true });
    }
  }, [token, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!password || !confirmPassword) {
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
      await withSaving(
        async () => {
          await resetPassword({
            variables: {
              input: {
                token,
                newPassword: password,
              },
            },
          });
        },
        'Resetting password...'
      );
    } catch {
      setError('Unable to reset password. Please try again.');
    }
  };

  if (success) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
            <CheckCircle2Icon className="h-6 w-6 text-green-600 dark:text-green-400" />
          </div>
          <CardTitle className="text-xl">Password Reset Successful</CardTitle>
          <CardDescription>
            Your password has been reset successfully. You can now sign in with your new password.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button className="w-full" asChild>
            <Link to={PATHS.AUTH}>
              Sign In
            </Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Check if error indicates invalid/expired token
  const isTokenError = error.includes('invalid') || error.includes('expired');

  if (isTokenError) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
            <XCircleIcon className="h-6 w-6 text-red-600 dark:text-red-400" />
          </div>
          <CardTitle className="text-xl">Link Expired</CardTitle>
          <CardDescription>
            {error}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Button className="w-full" asChild>
              <Link to={PATHS.FORGOT_PASSWORD}>
                Request New Link
              </Link>
            </Button>
            <Button variant="ghost" className="w-full" asChild>
              <Link to={PATHS.AUTH}>
                <ArrowLeftIcon className="mr-2 h-4 w-4" />
                Back to Sign In
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-xl">Reset your password</CardTitle>
        <CardDescription>
          Enter your new password below.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            {error ? (
              <Alert variant="destructive">
                <AlertCircleIcon />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}

            <Field>
              <FieldLabel htmlFor="password">New Password</FieldLabel>
              <Input
                id="password"
                type="password"
                placeholder="Enter new password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
                disabled={isSaving}
                required
                autoComplete="new-password"
                autoFocus
                maxLength={72}
              />
              <FieldDescription>
                Must be at least 8 characters long
              </FieldDescription>
            </Field>

            <Field>
              <FieldLabel htmlFor="confirmPassword">Confirm Password</FieldLabel>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                }}
                disabled={isSaving}
                required
                autoComplete="new-password"
                maxLength={72}
              />
            </Field>

            <Field>
              <Button type="submit" disabled={isSaving} className="w-full">
                Reset Password
              </Button>
              <Button variant="ghost" className="w-full" asChild>
                <Link to={PATHS.AUTH}>
                  <ArrowLeftIcon className="mr-2 h-4 w-4" />
                  Back to Sign In
                </Link>
              </Button>
            </Field>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
};

