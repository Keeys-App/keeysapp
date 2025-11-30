import { useEffect, type FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { OnboardingWizard } from '@/components/onboarding';
import { useOnboardingStore } from '@/stores';
import { useAuth } from '@/contexts';

export const OnboardingPage: FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const { isOnboardingComplete } = useOnboardingStore();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/auth');
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Redirect to dashboard if onboarding is already complete
  useEffect(() => {
    if (isOnboardingComplete) {
      navigate('/');
    }
  }, [isOnboardingComplete, navigate]);

  if (isLoading || !isAuthenticated) {
    return null;
  }

  return <OnboardingWizard />;
};

