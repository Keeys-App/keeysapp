import { useState } from 'react';
import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLazyQuery } from '@apollo/client';
import { LoginForm, RegisterForm } from '@/components/auth';
import { useAuth } from '@/contexts/AuthContext';
import { GET_TEAMS, type GetTeamsResponse } from '@/graphql/teams';
import { PATHS } from '@/constants/paths';
import { useOnboardingStore } from '@/stores';

export const AuthPage: FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { resetOnboarding } = useOnboardingStore();

  const [getTeams] = useLazyQuery<GetTeamsResponse>(GET_TEAMS);

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    navigate('/');
    return null;
  }

  const handleLoginSuccess = () => {
    navigate('/');
  };

  const handleRegisterSuccess = async () => {
    // Reset onboarding state for new registration
    resetOnboarding();

    // Check if user has any teams
    try {
      const { data } = await getTeams();
      if (!data?.teams || data.teams.length === 0) {
        // No teams - redirect to onboarding
        navigate(PATHS.ONBOARDING);
      } else {
        // Has teams - redirect to dashboard
        navigate(PATHS.DASHBOARD);
      }
    } catch (error) {
      // On error, redirect to onboarding to be safe
      navigate(PATHS.ONBOARDING);
    }
  };

  return (
    <>
      {isLogin ? (
        <LoginForm
          onSuccess={handleLoginSuccess}
          onSwitchToRegister={() => {
            setIsLogin(false);
          }}
        />
      ) : (
        <RegisterForm
          onSuccess={handleRegisterSuccess}
          onSwitchToLogin={() => {
            setIsLogin(true);
          }}
        />
      )}
    </>
  );
};
