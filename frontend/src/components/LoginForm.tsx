import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { useMutation } from '@apollo/client';
import { Box, Button, Card, Flex, Heading, Text, TextField, Callout } from '@radix-ui/themes';
import { LOGIN_MUTATION } from '../graphql/auth';
import { useAuth } from '../contexts/AuthContext';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export const LoginForm: FC<LoginFormProps> = ({ onSuccess, onSwitchToRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const [loginMutation, { loading }] = useMutation(LOGIN_MUTATION);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
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
        });
        
        if (onSuccess) {
          onSuccess();
        }
      }
    } catch (err: any) {
      // Handle GraphQL errors and network errors
      const errorMessage = err?.graphQLErrors?.[0]?.message || err?.message || 'An error occurred during login';
      setError(errorMessage);
    }
  };

  return (
    <Card size="3" style={{ maxWidth: 450, width: '100%' }}>
      <form onSubmit={handleSubmit}>
        <Flex direction="column" gap="4">
          <Heading size="6" align="center">Sign In</Heading>
          
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
              autoComplete="current-password"
              maxLength={72}
            />
          </Box>

          <Button size="3" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>

          {onSwitchToRegister ? (
            <Text size="2" align="center" color="gray">
              Don't have an account?{' '}
              <Text
                as="span"
                color="blue"
                style={{ cursor: 'pointer' }}
                onClick={onSwitchToRegister}
              >
                Sign up
              </Text>
            </Text>
          ) : null}
        </Flex>
      </form>
    </Card>
  );
};

