import type { FC } from 'react';
import { Box, Button, Card, Flex, Heading, Text, IconButton, Avatar } from '@radix-ui/themes';
import { SunIcon, MoonIcon, ExitIcon } from '@radix-ui/react-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

export const DashboardPage: FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <Box p="6" style={{ minHeight: '100vh' }}>
      <Flex direction="column" gap="6">
        {/* Header */}
        <Flex align="center" justify="between" style={{ width: '100%' }}>
          <Heading size="8">Locales Dashboard</Heading>
          <Flex gap="3" align="center">
            <IconButton 
              variant="ghost" 
              size="3"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {theme === 'light' ? <MoonIcon /> : <SunIcon />}
            </IconButton>
            
            <Flex gap="2" align="center">
              <Avatar
                size="2"
                fallback={user?.username.charAt(0).toUpperCase() || 'U'}
                radius="full"
              />
              <Text size="2" weight="medium">
                {user?.username}
              </Text>
            </Flex>

            <Button variant="soft" color="red" onClick={handleLogout}>
              <ExitIcon />
              Logout
            </Button>
          </Flex>
        </Flex>

        {/* Main Content */}
        <Flex direction="column" gap="4" align="center" style={{ marginTop: '2rem' }}>
          <Card size="3" style={{ maxWidth: 600, width: '100%' }}>
            <Flex direction="column" gap="4">
              <Heading size="5">Welcome, {user?.username}!</Heading>
              <Text size="3" color="gray">
                You are successfully authenticated and ready to use the application.
              </Text>
              
              <Box mt="3">
                <Text size="2" color="gray" as="div">
                  <strong>Email:</strong> {user?.email}
                </Text>
                <Text size="2" color="gray" as="div">
                  <strong>User ID:</strong> {user?.id}
                </Text>
                <Text size="2" color="gray" as="div">
                  <strong>Status:</strong> {user?.isActive ? 'Active' : 'Inactive'}
                </Text>
              </Box>
            </Flex>
          </Card>

          <Card size="3" style={{ maxWidth: 600, width: '100%' }}>
            <Flex direction="column" gap="3">
              <Heading size="4">Next Steps</Heading>
              <Text size="2" color="gray">
                This is your dashboard. Here you can manage your localization projects, 
                translations, and team members.
              </Text>
              <Text size="2" color="gray">
                Start building your features here!
              </Text>
            </Flex>
          </Card>
        </Flex>
      </Flex>
    </Box>
  );
};

