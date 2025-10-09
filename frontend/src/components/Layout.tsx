import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Button, Flex, Heading, IconButton, Avatar, Text } from '@radix-ui/themes';
import { SunIcon, MoonIcon, ExitIcon } from '@radix-ui/react-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

export const Layout: FC = () => {
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
        <Box style={{ marginTop: '2rem' }}>
          <Outlet />
        </Box>
      </Flex>
    </Box>
  );
};

