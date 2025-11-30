import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode, FC } from 'react';
import { apolloClient } from '../lib/apollo';
import { useOnboardingStore } from '@/stores';

interface User {
  id: string;  // UUID for security (prevents enumeration attacks)
  email: string;
  username: string;
  isActive: boolean;
  isSuperuser: boolean;
  onboardingCompleted: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { setOnboardingComplete } = useOnboardingStore();

  // Load token and user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('authUser');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        // Sync onboarding status from backend user data
        if (parsedUser.onboardingCompleted) {
          setOnboardingComplete(true);
        }
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        // Clear corrupted data
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
      }
    }

    setIsLoading(false);
  }, [setOnboardingComplete]);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('authToken', newToken);
    localStorage.setItem('authUser', JSON.stringify(newUser));
    // Sync onboarding status from backend
    if (newUser.onboardingCompleted) {
      setOnboardingComplete(true);
    }
  };

  const logout = async () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
    // Clear Apollo Client cache to prevent stale data
    await apolloClient.clearStore();
  };

  const value = {
    user,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

