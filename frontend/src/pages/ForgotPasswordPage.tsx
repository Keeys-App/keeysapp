import { useState, useEffect } from 'react';
import type { FC, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { REQUEST_PASSWORD_RESET_MUTATION } from '@/graphql/auth';
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
  FieldGroup,
  FieldLabel,
} from '@/components/ui/field';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircleIcon, CheckCircle2Icon, ArrowLeftIcon } from 'lucide-react';

interface RequestPasswordResetResponse {
  requestPasswordReset: {
    success: boolean;
    message: string;
  };
}

export const ForgotPasswordPage: FC = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const [requestReset, { data, error: mutationError }] = useMutation<RequestPasswordResetResponse>(
    REQUEST_PASSWORD_RESET_MUTATION
  );
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  useEffect(() => {
    if (data?.requestPasswordReset) {
      setSubmitted(true);
    }
  }, [data]);

  useEffect(() => {
    if (mutationError) {
      setError('Unable to process request. Please try again.');
    }
  }, [mutationError]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('Please enter your email address');
      return;
    }

    try {
      await withSaving(
        async () => {
          await requestReset({
            variables: {
              input: { email },
            },
          });
        },
        'Sending reset link...'
      );
    } catch {
      setError('Unable to process request. Please try again.');
    }
  };

  if (submitted) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
            <CheckCircle2Icon className="h-6 w-6 text-green-600 dark:text-green-400" />
          </div>
          <CardTitle className="text-xl">Check your email</CardTitle>
          <CardDescription>
            If an account with <strong>{email}</strong> exists, we&apos;ve sent a password reset link.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              The link will expire in 1 hour. Check your spam folder if you don&apos;t see the email.
            </p>
            <Button variant="outline" className="w-full" asChild>
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
        <CardTitle className="text-xl">Forgot your password?</CardTitle>
        <CardDescription>
          Enter your email address and we&apos;ll send you a link to reset your password.
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
                autoFocus
              />
            </Field>

            <Field>
              <Button type="submit" disabled={isSaving} className="w-full">
                Send Reset Link
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

