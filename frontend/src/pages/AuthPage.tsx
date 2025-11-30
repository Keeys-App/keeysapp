import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useLazyQuery } from '@apollo/client';
import { LoginForm, RegisterForm } from '@/components/auth';
import { useAuth } from '@/contexts/AuthContext';
import { GET_TEAMS, type GetTeamsResponse } from '@/graphql/teams';
import { PATHS } from '@/constants/paths';
import { useOnboardingStore } from '@/stores';

export const AuthPage: FC = () => {
  const location = useLocation();
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { resetOnboarding, returnUrl, setReturnUrl } = useOnboardingStore();

  const [getTeams] = useLazyQuery<GetTeamsResponse>(GET_TEAMS);

  // Check location state for mode (login/register from invite page)
  useEffect(() => {
    const state = location.state as { mode?: 'login' | 'register' } | null;
    if (state?.mode === 'register') {
      setIsLogin(false);
    } else if (state?.mode === 'login') {
      setIsLogin(true);
    }
  }, [location.state]);

  // Redirect already authenticated users away from auth page (on initial load)
  useEffect(() => {
    if (isAuthenticated) {
      // User is already logged in and landed on auth page
      // Redirect to return URL or dashboard
      if (returnUrl) {
        const url = returnUrl;
        setReturnUrl(null);
        navigate(url, { replace: true });
      } else {
        navigate(PATHS.DASHBOARD, { replace: true });
      }
    }
    // Only run on mount - subsequent changes handled by onSuccess callbacks
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Helper to handle redirect after auth
  const handleAuthRedirect = async (isNewRegistration: boolean) => {
    // If there's a return URL (e.g., from invite page), prioritize it
    if (returnUrl) {
      const url = returnUrl;
      setReturnUrl(null);
      navigate(url);
      return;
    }

    // For login, just go to dashboard
    if (!isNewRegistration) {
      navigate(PATHS.DASHBOARD);
      return;
    }

    // For registration without return URL - check onboarding
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
    } catch {
      // On error, redirect to onboarding to be safe
      navigate(PATHS.ONBOARDING);
    }
  };

  const handleLoginSuccess = () => {
    handleAuthRedirect(false);
  };

  const handleRegisterSuccess = () => {
    handleAuthRedirect(true);
  };

  // Don't render if already authenticated (will redirect)
  if (isAuthenticated) {
    return null;
  }

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
