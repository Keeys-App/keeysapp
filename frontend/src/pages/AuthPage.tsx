import { useState } from 'react';
import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginForm, RegisterForm } from '@/components/auth';
import { useAuth } from '@/contexts/AuthContext';

export const AuthPage: FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    navigate('/');
    return null;
  }

  const handleSuccess = () => {
    navigate('/');
  };

  return (
    <>
      {isLogin ? (
        <LoginForm
          onSuccess={handleSuccess}
          onSwitchToRegister={() => {
            setIsLogin(false);
          }}
        />
      ) : (
        <RegisterForm
          onSuccess={handleSuccess}
          onSwitchToLogin={() => {
            setIsLogin(true);
          }}
        />
      )}
    </>
  );
};
