import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { useMutation } from '@apollo/client';
import { Box, Button, Card, Flex, Heading, Text, TextField, Callout } from '@radix-ui/themes';
import { REGISTER_MUTATION } from '../graphql/auth';
import { useAuth } from '../contexts/AuthContext';

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
    <Card size="3" style={{ maxWidth: 450, width: '100%' }}>
      <form onSubmit={handleSubmit}>
        <Flex direction="column" gap="4">
          <Heading size="6" align="center">Create Account</Heading>
          
          {error ? (
            <Callout.Root color="red">
              <Callout.Text>{error}</Callout.Text>
            </Callout.Root>
          ) : null}

          <Box>
            <Text as="label" size="2" weight="medium" mb="2">
              Email
            </Text>
            <TextField.Root
              size="3"
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
          </Box>

          <Box>
            <Text as="label" size="2" weight="medium" mb="2">
              Username
            </Text>
            <TextField.Root
              size="3"
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
          </Box>

          <Box>
            <Text as="label" size="2" weight="medium" mb="2">
              Password
            </Text>
            <TextField.Root
              size="3"
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
          </Box>

          <Box>
            <Text as="label" size="2" weight="medium" mb="2">
              Confirm Password
            </Text>
            <TextField.Root
              size="3"
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
          </Box>

          <Button size="3" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </Button>

          {onSwitchToLogin ? (
            <Text size="2" align="center" color="gray">
              Already have an account?{' '}
              <Text
                as="span"
                color="blue"
                style={{ cursor: 'pointer' }}
                onClick={onSwitchToLogin}
              >
                Sign in
              </Text>
            </Text>
          ) : null}
        </Flex>
      </form>
    </Card>
  );
};

