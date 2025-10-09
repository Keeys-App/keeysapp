import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Box, Flex, Spinner } from '@radix-ui/themes';
import type { FC, ReactNode } from 'react';
import { PATHS } from '../constants/paths';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute: FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Flex align="center" justify="center" style={{ minHeight: '100vh' }}>
        <Spinner size="3" />
      </Flex>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={PATHS.AUTH} replace />;
  }

  return <Box>{children}</Box>;
};

